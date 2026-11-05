"""360 longitudes, two directions, with altitude-bounded terrain search.

Run: MPLCONFIGDIR=/tmp/lunar-sling-mpl-cache .env/hub/bin/python -m
     llo_catcher.analysis.terrain.sweep_equator
The initial demo and its figures are never rewritten by this entry point.
"""
from concurrent.futures import ProcessPoolExecutor
from dataclasses import asdict
from pathlib import Path
from collections import Counter
import csv
import hashlib
import json
import math
import numpy as np
from scipy.optimize import brentq
from .impact_demo import (Inputs,release_solution,state,ground_coordinates,
                          clearance,MU,MOON_OMEGA,RADIUS)
from .terrain_band import TerrainBand

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'results'/'sweep_1deg'
_TERRAIN=None


def possible_contact_intervals(solution,ceiling_radius_m):
    """All times r <= maximum terrain radius; others cannot contact this DEM.

    These are exact two-body altitude bounds, not a coarsened terrain survey.
    """
    a=solution['semimajor_axis_m'];e=solution['eccentricity']
    n=np.sqrt(MU/a**3);horizon=solution['period_s']*solution['max_orbits']
    if ceiling_radius_m<solution['periapsis_radius_m']:return []
    if ceiling_radius_m>=solution['apoapsis_radius_m']:return [(0.,horizon)]
    E=float(np.arccos(np.clip((1-ceiling_radius_m/a)/e,-1,1)))
    intervals=[]
    for k in range(math.ceil(solution['max_orbits'])+1):
        lo,hi=2*np.pi*k-E,2*np.pi*k+E
        t0=max(0.,(lo-e*np.sin(lo))/n)
        t1=min(horizon,(hi-e*np.sin(hi))/n)
        if t1>t0:intervals.append((float(t0),float(t1)))
    return intervals


def first_impact_bounded(solution,terrain,spatial_step_m=.25):
    duration=solution['max_orbits']*solution['period_s']
    intervals=possible_contact_intervals(solution,RADIUS+terrain.max_height_m+1.)
    dt=spatial_step_m/solution['inertial_release_speed_m_s']
    for t0,t1 in intervals:
        count=int(np.ceil((t1-t0)/dt))
        for start in range(0,count,8192):
            times=np.minimum(t0+np.arange(start,min(start+8192,count)+1)*dt,t1)
            gaps=clearance(solution,times,terrain)
            hit=np.flatnonzero(gaps<=0)
            if len(hit):
                k=int(hit[0]);lo=times[max(0,k-1)];hi=times[k]
                if k==0:
                    if start==0:raise ValueError('Contact interval starts below terrain')
                    lo=max(t0,lo-dt)
                ti=brentq(lambda t:float(clearance(solution,t,terrain)),lo,hi,xtol=1e-9)
                lat,lon,_=ground_coordinates(solution,ti)
                pos,vel=state(solution,ti)
                vground=vel-np.cross([0.,0.,MOON_OMEGA],pos)
                cosine=np.cos(np.radians(lat))*np.cos(np.radians(float(lon)-solution['longitude_deg_east']))
                return dict(status='outbound_collision' if ti<solution['ideal_catch_time_s'] else 'arrested_after_missed_capture',
                    impact_time_s=float(ti),impact_orbits=float(ti/solution['period_s']),
                    impact_latitude_deg=float(lat),impact_longitude_deg_east=float(lon),
                    impact_ground_speed_m_s=float(np.linalg.norm(vground)),
                    impact_distance_from_hub_m=float(RADIUS*np.arccos(np.clip(cosine,-1,1))),
                    horizon_s=duration,search_spatial_step_m=spatial_step_m,
                    possible_contact_intervals_s=intervals)
    return dict(status='not_arrested',impact_time_s=None,horizon_s=duration,
                completed_orbits=solution['max_orbits'],search_spatial_step_m=spatial_step_m,
                possible_contact_intervals_s=intervals)


def initialize_worker():
    global _TERRAIN
    _TERRAIN=TerrainBand()


def calculate_longitude(longitude):
    inputs=Inputs();arms=[]
    for sign in [1,-1]:
        sol=release_solution(_TERRAIN,longitude,sign,inputs)
        coarse=first_impact_bounded(sol,_TERRAIN,.5)
        fine=first_impact_bounded(sol,_TERRAIN,.25)
        if coarse['status']!=fine['status']:
            raise RuntimeError(f'Classification refinement mismatch at {longitude}, {sign}')
        delta=None
        if fine['impact_time_s'] is not None:
            delta=abs(fine['impact_time_s']-coarse['impact_time_s'])
            if delta>.001:raise RuntimeError(f'Contact time refinement mismatch: {longitude}, {sign}, {delta}')
        sol['outcome']=fine
        sol['refinement_05_to_025m_impact_time_change_s']=delta
        sol['outbound_clear']=fine['status']!='outbound_collision'
        sol['return_impact_given_outbound_clear']=(fine['status']=='arrested_after_missed_capture') if sol['outbound_clear'] else None
        arms.append(sol)
    return dict(longitude_deg_east=longitude,arms=arms,
        both_outbound_clear=all(a['outbound_clear'] for a in arms),
        both_arrested_after_missed_capture=all(a['return_impact_given_outbound_clear'] is True for a in arms))


def summarize(cases):
    result={}
    for index,direction in enumerate(['prograde','retrograde']):
        count=Counter(c['arms'][index]['outcome']['status'] for c in cases)
        clear=len(cases)-count['outbound_collision'];arrest=count['arrested_after_missed_capture']
        result[direction]=dict(total=len(cases),outbound_collision=count['outbound_collision'],outbound_clear=clear,
            arrested_after_missed_capture=arrest,not_arrested=count['not_arrested'],
            outbound_clear_fraction=clear/len(cases),
            conditional_return_impact_fraction=arrest/clear if clear else None,
            outbound_clear_longitudes=[c['longitude_deg_east'] for c in cases if c['arms'][index]['outbound_clear']],
            return_impact_longitudes=[c['longitude_deg_east'] for c in cases if c['arms'][index]['return_impact_given_outbound_clear'] is True],
            not_arrested_longitudes=[c['longitude_deg_east'] for c in cases if c['arms'][index]['outcome']['status']=='not_arrested'])
    result['paired']=dict(total=len(cases),both_outbound_clear=sum(c['both_outbound_clear'] for c in cases),
        both_arrested_after_missed_capture=sum(c['both_arrested_after_missed_capture'] for c in cases),
        both_outbound_clear_longitudes=[c['longitude_deg_east'] for c in cases if c['both_outbound_clear']],
        both_arrested_longitudes=[c['longitude_deg_east'] for c in cases if c['both_arrested_after_missed_capture']])
    return result


def run():
    OUT.mkdir(parents=True,exist_ok=True)
    originals={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (ROOT/'demo_results').iterdir() if p.is_file()}
    cases=[]
    with ProcessPoolExecutor(max_workers=4,initializer=initialize_worker) as pool:
        for case in pool.map(calculate_longitude,range(360),chunksize=1):
            cases.append(case)
            if len(cases)%10==0:print(f"Completed {len(cases)}/360; outbound-clear arms so far {sum(a['outbound_clear'] for c in cases for a in c['arms'])}",flush=True)
            # Checkpoint every case so a long sweep remains reviewable.
            with (OUT/'progress.jsonl').open('a' if len(cases)>1 else 'w') as f:f.write(json.dumps(case)+'\n')
    result=dict(inputs=asdict(Inputs()),longitude_spacing_deg=1,total_longitudes=360,total_trajectories=720,
        model='Central gravity, uniform rotation, bilinear SLDEM2015 terrain; no release errors',
        reference_radius_m=RADIUS,mu_m3_s2=MU,moon_spin_rad_s=MOON_OMEGA,
        code_sha256={name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in ['sweep_equator.py','impact_demo.py','terrain_band.py']},
        band_manifest_sha256=hashlib.sha256((ROOT/'band_manifest.json').read_bytes()).hexdigest(),
        initial_demo_preserved_sha256=originals,summary=summarize(cases),scenarios=cases)
    (OUT/'results.json').write_text(json.dumps(result,indent=2)+'\n')
    (OUT/'summary.json').write_text(json.dumps(result['summary'],indent=2)+'\n')
    write_csv(cases)
    plot(result)
    report(result)
    assert originals=={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (ROOT/'demo_results').iterdir() if p.is_file()}
    print(json.dumps(result['summary'],indent=2),flush=True)


def write_csv(cases):
    fields=['hub_longitude_deg_east','direction','outbound_clear','return_impact_given_outbound_clear','status','impact_time_s','impact_orbits','impact_latitude_deg','impact_longitude_deg_east','impact_ground_speed_m_s','release_horizontal_offset_m','catch_relative_speed_m_s','ideal_catch_time_s','period_s','refinement_05_to_025m_impact_time_change_s']
    with (OUT/'trajectories.csv').open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=fields);writer.writeheader()
        for c in cases:
            for a in c['arms']:
                row={**a,**a['outcome'],'hub_longitude_deg_east':c['longitude_deg_east']}
                writer.writerow({k:row.get(k) for k in fields})


def plot(result):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.colors import ListedColormap,BoundaryNorm
    from matplotlib.patches import Patch
    colors=['#d8d8d8','#b85543','#53866a']
    stages=np.zeros((4,360),dtype=int)
    outcomes=np.zeros((2,360),dtype=int)
    outcome_codes={'outbound_collision':0,'arrested_after_missed_capture':1,'not_arrested':2}
    for c in result['scenarios']:
        lon=c['longitude_deg_east']
        for k,a in enumerate(c['arms']):
            stages[k,lon]=2 if a['outbound_clear'] else 1
            stages[k+2,lon]=0 if not a['outbound_clear'] else (2 if a['return_impact_given_outbound_clear'] else 1)
            outcomes[k,lon]=outcome_codes[a['outcome']['status']]
    fig,axes=plt.subplots(2,1,figsize=(15,6),gridspec_kw={'height_ratios':[2,1.35]},layout='constrained')
    ax=axes[0]
    ax.imshow(stages,aspect='auto',interpolation='nearest',extent=(-.5,359.5,3.5,-.5),cmap=ListedColormap(colors),norm=BoundaryNorm([-.5,.5,1.5,2.5],3))
    ax.set_yticks(range(4),['Prograde: departure clear','Retrograde: departure clear','Prograde: return impact | clear','Retrograde: return impact | clear'])
    ax.set_xticks(range(0,360,30));ax.set_xlabel('Launcher-center longitude (degrees east); one column per 1° sample')
    ax.set_title('360 equatorial launcher locations: sequential criteria',fontsize=15)
    ax.axhline(1.5,color='white',lw=3)
    ax.legend(handles=[Patch(color=colors[2],label='Yes'),Patch(color=colors[1],label='No'),Patch(color=colors[0],label='Not applicable: departure failed')],loc='upper center',bbox_to_anchor=(.5,-.23),ncol=3,frameon=False)
    ax=axes[1];ax.axis('off')
    st=result['summary'];txt=[]
    for d in ['prograde','retrograde']:
        x=st[d];cond='N/A' if x['conditional_return_impact_fraction'] is None else f"{100*x['conditional_return_impact_fraction']:.1f}%"
        txt.append(f"{d.capitalize()}: {x['outbound_clear']}/360 departures clear; {x['arrested_after_missed_capture']}/{x['outbound_clear']} clear departures hit on return ({cond}).")
    p=st['paired'];txt.append(f"Paired sites: {p['both_outbound_clear']}/360 clear in both directions; {p['both_arrested_after_missed_capture']}/360 meet both return-impact requirements.")
    txt+=['25 km prograde / 35 km retrograde catchers · 2.7796 RPM · 3 m local release clearance',
          'Correct launch + missed capture; first impact or 1.5 payload orbits. Central gravity + rotating DEM.']
    ax.text(.01,.82,'\n'.join(txt),transform=ax.transAxes,fontsize=11,va='top',linespacing=1.8)
    fig.savefig(OUT/'criteria_by_longitude.png',dpi=180);fig.savefig(OUT/'criteria_by_longitude.svg');plt.close(fig)
    # A single unconditional outcome per arm prevents mixing denominators.
    fig,ax=plt.subplots(figsize=(10,4.8),layout='constrained')
    labels=['Outbound collision','Return impact after missed capture','Not arrested at cutoff']
    keys=['outbound_collision','arrested_after_missed_capture','not_arrested']
    palette=['#b85543','#53866a','#4d7da5'];left=np.zeros(2)
    for key,label,color in zip(keys,labels,palette):
        values=np.array([st[d][key] for d in ['prograde','retrograde']])
        ax.barh([1,0],values,left=left,color=color,label=label,height=.55)
        for y,v,l in zip([1,0],values,left):
            if v>=15:ax.text(l+v/2,y,f'{v}',ha='center',va='center',color='white',fontweight='bold')
        left+=values
    ax.set_yticks([1,0],['Prograde','Retrograde']);ax.set_xlim(0,360);ax.set_xlabel('Number of launcher longitudes (360 per direction)')
    ax.set_title('Overall outcome counts — each trajectory appears exactly once')
    ax.legend(loc='upper center',bbox_to_anchor=(.5,-.18),ncol=1,frameon=False)
    fig.savefig(OUT/'overall_counts.png',dpi=180);fig.savefig(OUT/'overall_counts.svg');plt.close(fig)


def report(result):
    st=result['summary']
    lines=['# One-degree equatorial missed-capture sweep','',
        '**360 hub longitudes, 0–359° E, with two trajectories each: 720 total.** All other inputs match the preserved eight-site demo. This is a uniform longitude grid, not every possible site.',
        '', '## Sequential statistics','',
        'Departure success means the entire trajectory is terrain-clear up to its intended catcher encounter. Only then is return arrest evaluated. A return success means first terrain contact after missed capture and before 1.5 payload orbital periods. `Not arrested` means no contact by that cutoff; later fate is outside scope.',
        '', '| Quantity | Prograde | Retrograde |','| --- | ---: | ---: |']
    for label,key in [('Total sites','total'),('Outbound collision','outbound_collision'),('Departure clear','outbound_clear'),('Return impact, conditional on clear departure','arrested_after_missed_capture'),('Not arrested at cutoff, conditional on clear departure','not_arrested')]:
        lines.append(f"| {label} | {st['prograde'][key]} | {st['retrograde'][key]} |")
    for label,key in [('Departure-clear percentage of all 360 sites','outbound_clear_fraction'),('Return-impact percentage of clear departures','conditional_return_impact_fraction')]:
        vals=['N/A (no clear departures)' if st[d][key] is None else f"{100*st[d][key]:.2f}%" for d in ['prograde','retrograde']]
        lines.append(f"| {label} | {vals[0]} | {vals[1]} |")
    pair=st['paired']
    lines+=['',f"**Both directions clear:** {pair['both_outbound_clear']}/360 sites. **Both directions clear and both hit after missed capture:** {pair['both_arrested_after_missed_capture']}/360 sites.",'',
        '![Sequential criteria by longitude](criteria_by_longitude.png)','',
        'Green = criterion met; red = not met. Gray return cells mean the departure failed, so the conditional return criterion is not applicable. Each column is one longitude. A gray return cell is not a surviving orbit or a failed return arrest.','',
        '![Overall outcome counts](overall_counts.png)','',
        '## Longitudes for follow-up','']
    for d in ['prograde','retrograde']:
        for label,key in [('clear departures','outbound_clear_longitudes'),('return impacts after missed capture','return_impact_longitudes'),('not arrested at cutoff','not_arrested_longitudes')]:
            value=', '.join(str(x)+'° E' for x in st[d][key]) or 'None'
            lines.append(f"- **{d.capitalize()} {label}:** {value}.")
    lines+=['',f"**Paired clear longitudes:** {', '.join(map(str,pair['both_outbound_clear_longitudes'])) or 'None'}.",
        f"**Paired arrest longitudes:** {', '.join(map(str,pair['both_arrested_longitudes'])) or 'None'}.",'',
        '## Model, refinement and preservation','',
        'Catcher targets are 25 km prograde and 35 km retrograde, circular and equatorial above the 1,737.4 km DEM sphere. The common rate is 2.7796279 RPM; each arm radius is solved for its first equator-node intercept. Each east/west horizontal release is 3 m above its own local terrain, with zero payout velocity. The two-body Kepler trajectory is evaluated against the uniformly rotating, bilinearly interpolated SLDEM2015 corridor.',
        '', 'Terrain search skips only intervals proven above the maximum elevation anywhere in the downloaded corridor. It uses analytic orbital altitude bounds, not a coarser DEM. Each trajectory is checked at 0.5 m and 0.25 m spatial sampling near possible contact; classifications must agree and contact times must agree within 0.001 s. Detailed per-case refinement differences are in the JSON/CSV.',
        '', 'The earlier 20 m/10 m demo trials missed one shallow intersection, so the broad sweep retains the finer search. Finite sampling is not a proof about every grazing contact. Grid spacing (~59 m) and typical vertical uncertainty (~3–4 m) limit physical interpretation of the 3 m clearance. Gravity harmonics, libration, release errors, site grading and detailed launcher/cable clearance are not modeled.',
        '', 'No extra longitudes, altered clearance heights or redesigned launches were added to this sweep. The [initial demo snapshot](../INITIAL_DEMO.md) and all six original report/data/figure files were checked by SHA-256 before and after this run and remain unchanged.',
        '', '## Data and reproduction','',
        '- [Full per-case states and outcomes](results.json)',
        '- [720-row trajectory table](trajectories.csv)',
        '- [Summary counts and longitude lists](summary.json)',
        '- [Criteria chart SVG](criteria_by_longitude.svg)',
        '- [Overall-count chart SVG](overall_counts.svg)',
        '- [Data sources and coordinate conventions](../../README.md)',
        '', '```bash',
        'MPLCONFIGDIR=/tmp/lunar-sling-mpl-cache .env/hub/bin/python -m llo_catcher.analysis.terrain.sweep_equator',
        '```','',
        'Raw terrain remains in the ignored local cache; the small results and figures are retained in this directory. The JSON includes source-code and terrain-manifest hashes.']
    (OUT/'README.md').write_text('\n'.join(lines)+'\n')


if __name__=='__main__':run()
