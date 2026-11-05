"""Refine fixed-10-m launch corridors near eight successful one-degree samples."""
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor
import json,csv
import numpy as np
from scipy.optimize import brentq
from llo_catcher.analysis.single_equatorial_release import calculate as c
OUT=Path(__file__).resolve().parent
SEEDS=[144,220,264,267,283,293,294,295]
WINDOWS=[(143,145),(219,221),(263,265),(266,268),(282,284),(292,296)]
KM_PER_DEG=c.RADIUS*np.pi/180/1000

def sample(lon):
    go=c.minimum_outbound(lon,10.)
    gr=None
    if go>0:
        o=c.orbit(lon,10.);intervals=c.intervals(o,True)
        gr=min((float(c.profile(o,lo,hi)[1].min()) for lo,hi in intervals),default=o['rp']-c.RADIUS-float(c._GROUND.max()))
    return dict(longitude_deg_east=lon,outbound_minimum_clearance_m=go,return_minimum_clearance_m=gr,
        status='outbound_collision' if go<=0 else ('return_impact' if gr<=0 else 'not_arrested'))

def score(lon,kind):
    r=sample(lon);go=r['outbound_minimum_clearance_m']
    return go if kind=='outbound' or go<=0 else min(go,-r['return_minimum_clearance_m'])

def passes(r,kind):return r['status']!='outbound_collision' if kind=='outbound' else r['status']=='return_impact'

def ranges(rows,kind):
    found=[]
    for lo,hi in WINDOWS:
        sub=[r for r in rows if lo<=r['longitude_deg_east']<=hi]
        mask=[passes(r,kind) for r in sub];start=None
        for i,good in enumerate(mask):
            if good and (i==0 or not mask[i-1]):
                start=sub[i]['longitude_deg_east'] if i==0 else brentq(lambda x:score(x,kind),sub[i-1]['longitude_deg_east'],sub[i]['longitude_deg_east'],xtol=1e-10)
            if good and (i==len(mask)-1 or not mask[i+1]):
                end=sub[i]['longitude_deg_east'] if i==len(mask)-1 else brentq(lambda x:score(x,kind),sub[i]['longitude_deg_east'],sub[i+1]['longitude_deg_east'],xtol=1e-10)
                found.append(dict(start_deg_east=start,end_deg_east=end,length_km=(end-start)*KM_PER_DEG,
                    window_start_deg=lo,window_end_deg=hi,seeds_inside=[s for s in SEEDS if start<s<end],clipped_to_window=(start==lo or end==hi)))
    return found

def audit_144():
    o=c.orbit(144,10.);lo,hi=c.intervals(o)[0];xs,gaps=c.profile(o,lo,hi)
    # Exclude first 1 degree to identify a later mountain bottleneck.
    sel=np.flatnonzero(xs>np.radians(1));k=sel[np.argmin(gaps[sel])]
    rad,t,_,_=c.at_longitude(xs[k],o)
    rows=[]
    for lon in [144,145,150,180,195,210,220,240]:
        r,t0,_,_=c.at_longitude(np.radians(lon-144),o);g=float(c.terrain(np.radians(lon)))
        rows.append(dict(longitude_deg_east=lon,terrain_elevation_m=g,payload_elevation_m=float(r-c.RADIUS),clearance_m=float(r-c.RADIUS-g),elapsed_min=float(t0/60)))
    regional=np.flatnonzero(xs>np.radians(10));j=regional[np.argmin(gaps[regional])]
    rj,tj,_,_=c.at_longitude(xs[j],o)
    return dict(regional_mountain=dict(longitude_deg=float(144+np.degrees(xs[j])),
        clearance_m=float(gaps[j]),payload_elevation_m=float(rj-c.RADIUS),
        terrain_elevation_m=float(c.terrain(o['lon']+xs[j])),elapsed_min=float(tj/60)),
        checkpoints=rows,lowest_clearance_after_first_degree_m=float(gaps[k]),
        bottleneck_longitude_deg=float(144+np.degrees(xs[k])),bottleneck_time_min=float(t/60),
        bottleneck_payload_elevation_m=float(rad-c.RADIUS),bottleneck_terrain_elevation_m=float(c.terrain(o['lon']+xs[k])),
        outcome=c.classify((144,10.,True)))

def run():
    c.initialize();cache={};convergence=[];final_ranges={}
    with ProcessPoolExecutor(max_workers=4,initializer=c.initialize) as pool:
        for ppd in [512,1024,2048,4096]:
            grid=sorted(set(float(x/ppd) for lo,hi in WINDOWS for x in range(lo*ppd,hi*ppd+1)))
            missing=[x for x in grid if x not in cache]
            for j,row in enumerate(pool.map(sample,missing,chunksize=8)):
                cache[row['longitude_deg_east']]=row
                if (j+1)%2000==0:print(f'{ppd} samples/degree: {j+1}/{len(missing)} new samples',flush=True)
            rows=[cache[x] for x in grid]
            # Expand scope explicitly rather than silently clipping a continuous corridor.
            assert all(cache[float(edge)]['status']=='outbound_collision' for window in WINDOWS for edge in window),'Viable window edge: expand windows'
            final_ranges={kind:ranges(rows,kind) for kind in ['outbound','both']}
            convergence.append(dict(samples_per_degree=ppd,spacing_m=1000*KM_PER_DEG/ppd,site_count=len(rows),
                outbound_length_km=sum(r['length_km'] for r in final_ranges['outbound']),
                both_length_km=sum(r['length_km'] for r in final_ranges['both']),outbound_intervals=len(final_ranges['outbound']),both_intervals=len(final_ranges['both'])))
            print('LEVEL',json.dumps(convergence[-1]),flush=True)
    result=dict(seeds=SEEDS,windows=WINDOWS,release_height_m=10.,km_per_degree=KM_PER_DEG,
        scope='Local +/-1 degree windows around each seed, overlapping windows merged; no global completeness claim',
        grid_convergence=convergence,outbound_ranges=final_ranges['outbound'],both_ranges=final_ranges['both'],
        seed_connected_both_ranges=[r for r in final_ranges['both'] if r['seeds_inside']],audit_144=audit_144())
    result['totals']=dict(outbound_km=sum(r['length_km'] for r in final_ranges['outbound']),both_km=sum(r['length_km'] for r in final_ranges['both']),
        seed_connected_both_km=sum(r['length_km'] for r in result['seed_connected_both_ranges']))
    (OUT/'results.json').write_text(json.dumps(result,indent=2)+'\n')
    for name,data in [('samples.csv',rows),('outbound_ranges.csv',final_ranges['outbound']),('both_ranges.csv',final_ranges['both'])]:
        with (OUT/name).open('w') as f:
            w=csv.DictWriter(f,fieldnames=list(data[0]));w.writeheader();w.writerows(data)
    plot(result,rows)
    print('TOTALS',json.dumps(result['totals']),flush=True)

def plot(result,rows):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig,ax=plt.subplots(figsize=(12,5.7),layout='constrained');o=c.orbit(144,10.)
    lon=np.arange(144,240,1/512);ground=c.terrain(np.radians(lon))/1000
    r,_,_,_=c.at_longitude(np.radians(lon-144),o)
    ax.plot(lon,ground,color='#82745f',lw=1,label='Equatorial terrain');ax.plot(lon,(r-c.RADIUS)/1000,color='#265e80',lw=2,label='Payload released at 144° E, 10 m above local ground')
    b=result['audit_144']['regional_mountain'];x=b['longitude_deg'];y=b['payload_elevation_m']/1000
    ax.scatter([x],[y],color='#265e80',s=35);ax.annotate(f'Later mountain range: {b["clearance_m"]:.1f} m clearance',xy=(x,y),xytext=(160,13),arrowprops=dict(arrowstyle='->'),fontsize=10)
    ax.set_xlim(144,240);ax.set_xlabel('Longitude east (degrees)');ax.set_ylabel('Elevation above reference sphere (km)');ax.set_title('Why 144° E clears: compare terrain with the rising orbital trajectory');ax.grid(alpha=.2);ax.legend(loc='upper left')
    fig.savefig(OUT/'trajectory_144.png',dpi=160,bbox_inches='tight');fig.savefig(OUT/'trajectory_144.svg',bbox_inches='tight');plt.close(fig)
    fig,axes=plt.subplots(6,1,figsize=(12,14),layout='constrained')
    for ax,(lo,hi) in zip(axes,WINDOWS):
        lon=np.arange(lo,hi+1/512,1/512);ground=c.terrain(np.radians(lon))/1000
        ax.plot(lon,ground,color='#82745f',lw=.8)
        for rr in result['outbound_ranges']:
            if rr['window_start_deg']==lo:ax.axvspan(rr['start_deg_east'],rr['end_deg_east'],color='#4d7da5',alpha=.4)
        for rr in result['both_ranges']:
            if rr['window_start_deg']==lo:ax.axvspan(rr['start_deg_east'],rr['end_deg_east'],color='#24785b',alpha=.75)
        seeds=[s for s in SEEDS if lo<s<hi];ax.scatter(seeds,c.terrain(np.radians(seeds))/1000,color='black',s=18,zorder=5)
        ax.set_xlim(lo,hi);ax.set_ylabel('Elevation (km)');ax.set_title(f'{lo}°–{hi}° E',loc='left',fontsize=10);ax.grid(alpha=.15)
    axes[-1].set_xlabel('Release longitude (degrees east)')
    fig.suptitle('Local 10 m launch corridors near the eight seed sites\nGreen: outbound clear + impact after missed capture; blue only: outbound clear, no impact by cutoff\nBlack dots: original seed sites; shaded ranges use refined boundaries',fontsize=12)
    fig.savefig(OUT/'local_corridors.png',dpi=160,bbox_inches='tight');fig.savefig(OUT/'local_corridors.svg',bbox_inches='tight');plt.close(fig)

if __name__=='__main__':run()
