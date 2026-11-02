"""Reproduce sourced component curves and a coupled, conditional mass trade."""
from pathlib import Path
from dataclasses import asdict,replace
import csv,hashlib,json,platform
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from .component_sizing import TIRES,MOTORS,GEARS,WHEEL_MASS_FIT,WHEEL_LOAD_FIT,GEAR_MASS_FIT,HardwareAssumptions,variants,wheel,drive,pole
from .scenario_study import Scenario,geometry,calculate
from .hardware_study import evaluate

ROOT=Path(__file__).parent;OUT=ROOT/'results/hardware_mass'
ACC=(4,10,20,30,40,50,60,65,70,75,80,85,90,95,100,110,125,150,180,220,300,600,1000,2500,4200)

def save(fig,name):
    fig.tight_layout();fig.savefig(OUT/f'{name}.png',dpi=150,bbox_inches='tight');fig.savefig(OUT/f'{name}.svg',bbox_inches='tight');plt.close(fig)
    p=OUT/f'{name}.svg';p.write_text('\n'.join(line.rstrip() for line in p.read_text().splitlines())+'\n')

def curves():
    fig,axes=plt.subplots(2,2,figsize=(12,9));cfg=HardwareAssumptions()
    d=np.geomspace(1,12,200);k,p=WHEEL_MASS_FIT
    ax=axes[0,0];ax.loglog(d,k*d**p,'--',label='Tire analog fit');ax.loglog(d,cfg.wheel_install_factor*k*d**p,label='Installed wheel estimate')
    ax.scatter([t['diameter_m'] for t in TIRES],[t['mass_kg'] for t in TIRES],c='black',label='Michelin data')
    ax.set(xlabel='Wheel diameter (m)',ylabel='Mass per wheel (kg)',title='Wheel mass grows with traction/load footprint')
    ax=axes[0,1];power=np.geomspace(50,50000,200)
    ax.loglog(power,power*cfg.motor_kg_per_kw*cfg.motor_install_factor,label='Dana-based installed curve')
    ax.loglog(power,power*4.55*1.3,'--',label='ABB-based heavier curve')
    ax.scatter([m['continuous_kw'] for m in MOTORS],[m['motor_kg'] for m in MOTORS],c='black',label='Dana continuous-duty data')
    ax.scatter([1000],[4550],marker='s',label='ABB 1 MW benchmark')
    ax.set(xlabel='Continuous nameplate power (kW)',ylabel='Motor mass (kg)',title='Motor curve; gearing and inverter separate')
    ax=axes[1,0];torque=np.geomspace(1e5,1e8,200);k,p=GEAR_MASS_FIT
    ax.loglog(torque/1e6,k*torque**p,label='Flender dry-mass fit');ax.loglog(torque/1e6,cfg.gearbox_install_factor*k*(torque*cfg.gearbox_service_factor)**p,'--',label='Installed + 1.5 torque service factor')
    ax.scatter([t/1e6 for t,m in GEARS],[m for t,m in GEARS],c='black',label='Flender P3DP data')
    ax.set(xlabel='Output torque (MNm)',ylabel='Gearbox mass (kg)',title='Torque curve; power floor checked separately')
    ax=axes[1,1];Ls=np.geomspace(3,100,60)
    for radial in [1e5,1e6,1e7]:
        vals=[pole(L,1e6,radial,10.,0.,1.6229,cfg)['mass_with_joints_kg'] for L in Ls]
        ax.loglog(Ls,vals,label=f'Radial tip force {radial/1e6:g} MN')
    ax.set(xlabel='Pole length (m)',ylabel='One pole incl. joints (kg)',title='Beam sizing: 1 MN axial, 10 m/s² radial body acceleration')
    for ax in axes.flat:ax.grid(alpha=.2,which='both');ax.legend(fontsize=8)
    fig.suptitle('Component mass curves: source anchors and explicit engineering extrapolation',y=1.02)
    save(fig,'component_curves')

def plots(rows):
    fig,axes=plt.subplots(2,2,figsize=(12,9),sharex=True,sharey='row')
    colors={1:'#2368a0',2:'#25805b'}
    for col,mph in enumerate([50,80]):
        for passes in [1,2]:
            for profile,style,alpha in [('reference','-',1),('lighter','--',.65),('heavier',':',.65)]:
                rs=[r for r in rows if r['rover_mph']==mph and r['passes']==passes and r['assumptions']['name']==profile]
                x=[r['acceleration_g'] for r in rs]
                for i,key in enumerate(['imported_ratio','physical_ratio']):
                    y=[r.get(key) if r.get(key) is not None else np.nan for r in rs]
                    if any(np.isfinite(y)):
                        axes[i,col].loglog(x,y,style,color=colors[passes],alpha=alpha,marker='o' if profile=='reference' else ('s' if profile=='heavier' else None),markersize=3,label=f'{passes} pass, {profile}')
                    if profile=='reference':
                        bad=[r for r in rs if r['converged'] and not(r['frame_chord_fits'] and r['reel_envelopes_fit'] and r['wheel_envelopes_fit'] and r['pole_source_domain_ok'])]
                        axes[i,col].scatter([r['acceleration_g'] for r in bad],[r[key] for r in bad],marker='x',color='#c24642',zorder=5)
                        good=[r for r in rs if r['converged']]
                        if good and i==0:
                            best=min(good,key=lambda r:r[key]);axes[i,col].scatter([best['acceleration_g']],[best[key]],marker='*',s=150,color=colors[passes],edgecolor='black',zorder=6)
        for i in range(2):
            axes[i,col].axvline(6.234 if mph==50 else 3.895,color='.4',ls=':',lw=1)
            axes[i,col].set_title(f'{mph} mph');axes[i,col].grid(alpha=.2,which='both');axes[i,col].set_xlim(3.5,4500)
            axes[i,col].legend(fontsize=8)
    axes[0,0].set_ylabel('Estimated imported permanent mass / payload')
    axes[1,0].set_ylabel('Estimated total permanent mass / payload\nIncludes remaining local ballast')
    for ax in axes[1]:ax.set_xlabel('Release centripetal acceleration (Earth g)')
    fig.suptitle('Hardware-inclusive mass trade — conditional estimates, not stable/qualified designs\nGaps denote failed mass feedback; heavier branch may have no closed solution',y=1.03)
    fig.text(.5,-.025,'Dotted: road-only radial limit. Red ×: reference section/fit screen fails.\nAll points require unresolved stabilizing reactions.',ha='center',fontsize=9)
    save(fig,'mass_trade')
    fig,axes=plt.subplots(2,2,figsize=(12,9),sharex=True)
    groups=[('Poles',['poles']),('Wheels + steering',['wheels','steering']),('Wheel drive systems',['wheel_motors','wheel_inverters','wheel_gearboxes']),
            ('Reel systems',['reel_mechanical','reel_motors','reel_inverters','reel_gearboxes']),('Solar',['solar']),('Thermal',['thermal']),('Cables + other',['outward_cables','main_tie','retention','fittings_sheath','controls'])]
    for col,mph in enumerate([50,80]):
        rs=[r for r in rows if r['rover_mph']==mph and r['passes']==1 and r['assumptions']['name']=='reference' and r['converged']]
        x=[r['acceleration_g'] for r in rs]
        for label,keys in groups:axes[0,col].loglog(x,[sum(r['masses_kg'][k] for k in keys)/1000 for r in rs],label=label)
        axes[0,col].set_title(f'{mph} mph, one pass');axes[0,col].legend(fontsize=8);axes[0,col].set_ylabel('Imported component mass (tonnes)')
        for index,label in [(0,'Each vertical leg (A and B)'),(1,'Each trailing leg (A and B)')]:
            axes[1,col].loglog(x,[r['pole_legs'][index]['mass_with_joints_kg']/1000 for r in rs],'o-',label=label)
        axes[1,col].set_ylabel('Mass per leg including joints (tonnes)');axes[1,col].set_xlabel('Release centripetal acceleration (Earth g)');axes[1,col].legend(fontsize=8)
    for ax in axes.flat:ax.grid(alpha=.2,which='both')
    fig.suptitle('What changes the trade: four legs and load-/power-sized hardware',y=1.02)
    save(fig,'mass_composition')
    fig,axes=plt.subplots(2,2,figsize=(12,8),sharex=True)
    for col,mph in enumerate([50,80]):
        rs=[r for r in rows if r['rover_mph']==mph and r['passes']==1 and r['assumptions']['name']=='reference' and r['converged']];x=[r['acceleration_g'] for r in rs]
        for key,label in [('clearance_height_m','Cable clearance minimum'),('apex_height_m','Hardware-aware apex'),('track_radius_m','Track radius')]:axes[0,col].loglog(x,[r[key] for r in rs],'o-',label=label)
        axes[0,col].loglog(x,[r['powered_wheel']['diameter_m'] for r in rs],label='Powered-wheel diameter')
        for fun,label in [(lambda r:r['required_support_lever_m']/r['available_support_lever_m'],'Radial moment demand / support'),(lambda r:r['reel']['outer_radius_m']/r['track_radius_m'],'Reel radius / track radius'),(lambda r:r['pole_legs'][0]['length_m']/(2*r['track_radius_m']),'45° foot chord / track diameter')]:
            axes[1,col].loglog(x,[fun(r) for r in rs],'o-',label=label)
        axes[1,col].axhline(1,color='black',ls='--');axes[0,col].set_title(f'{mph} mph, one pass')
        for ax in axes[:,col]:ax.grid(alpha=.2,which='both');ax.legend(fontsize=8)
        axes[1,col].set_xlabel('Release centripetal acceleration (Earth g)')
    axes[0,0].set_ylabel('Dimension (m)');axes[1,0].set_ylabel('Screen ratio; above 1 requires redesign')
    fig.suptitle('Hardware changes the height and practical limits; no stable design claimed',y=1.02)
    save(fig,'hardware_limits')


def write_tables(rows):
    lines=['# Reference hardware estimates for every scenario','',
      'Masses are tonnes. Each named leg includes its allocated joint/bracing allowance. Failed fixed points have no completed system total; their first-iteration four-leg estimates are retained in JSON only as diagnostics. Pivot/stabilizer mass is excluded by instruction.','',
      '| mph | g | passes | A vertical | A trailing | B vertical | B trailing | 8 wheels | 4 wheel motors | Imported / payload | Physical / payload | Status |',
      '| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |']
    for r in rows:
        if r['assumptions']['name']!='reference':continue
        if not r['converged']:
            lines.append(f"| {r['rover_mph']} | {r['acceleration_g']} | {r['passes']} | — | — | — | — | — | — | — | — | Mass feedback fails |")
        else:
            legs=' | '.join(f"{p['mass_with_joints_kg']/1000:.2f}" for p in r['pole_legs'])
            status='Conditional; reactions unresolved'
            if not r['pole_source_domain_ok']:status='Pole source/beam domain exceeded'
            if not(r['frame_chord_fits'] and r['reel_envelopes_fit'] and r['wheel_envelopes_fit']):status='Hardware geometry fails'
            lines.append(f"| {r['rover_mph']} | {r['acceleration_g']} | {r['passes']} | {legs} | {r['masses_kg']['wheels']/1000:.1f} | {r['masses_kg']['wheel_motors']/1000:.1f} | {r['imported_ratio']:.1f} | {r['physical_ratio']:.1f} | {status} |")
    (OUT/'SCENARIOS.md').write_text('\n'.join(lines)+'\n')
    with (OUT/'four_leg_estimates.csv').open('w') as f:
        keys=['profile','rover_mph','acceleration_g','passes','converged','id','length_m','diameter_m','wall_m','bare_mass_kg','mass_with_joints_kg','axial_n','bending_moment_nm','deflection_m','plate_thickness_within_source']
        w=csv.DictWriter(f,keys,lineterminator='\n');w.writeheader()
        for r in rows:
            for p in (r.get('pole_legs',[]) if r['converged'] else r.get('initial_load_pole_estimates',[])):
                d={k:p[k] for k in keys if k in p};d.update(profile=r['assumptions']['name'],**{k:r[k] for k in ['rover_mph','acceleration_g','passes','converged']});w.writerow(d)


def produce():
    OUT.mkdir(exist_ok=True);rows=[];plt.rcParams.update({'svg.hashsalt':'hardware-mass','font.size':10})
    for mph in [50,80]:
        for acc in ACC:
            c=Scenario(acceleration_g=acc,rover_mph=mph);geo=geometry(c)
            for passes in [1,2]:
                base=calculate(replace(c,passes=passes),geo,history=True)
                for config in variants():rows.append(evaluate(base,geo,config,radial_policy='upper_only'))
            ref=rows[-5]
            print(f'{mph} mph {acc} g complete',flush=True)
    (OUT/'all_estimates.json').write_text(json.dumps(rows,indent=2)+'\n')
    minima=[]
    for mph in [50,80]:
        for passes in [1,2]:
            for profile in ['lighter','reference','heavier']:
                candidates=[r for r in rows if r['rover_mph']==mph and r['passes']==passes and r['assumptions']['name']==profile and r['converged']]
                if candidates:
                    best=min(candidates,key=lambda r:r['imported_ratio'])
                    minima.append(dict(rover_mph=mph,passes=passes,profile=profile,acceleration_g=best['acceleration_g'],imported_ratio=best['imported_ratio'],physical_ratio=best['physical_ratio'],flags=best['flags'],feasible_design=False))
                else:minima.append(dict(rover_mph=mph,passes=passes,profile=profile,acceleration_g=None,reason='no closed mass fixed point among samples'))
    (OUT/'sampled_minima.json').write_text(json.dumps(minima,indent=2)+'\n')
    (OUT/'source_anchors.json').write_text(json.dumps(dict(tires=TIRES,motors=MOTORS,gear_torque_nm_dry_kg=GEARS,fit_coefficients=dict(wheel_mass=WHEEL_MASS_FIT,wheel_load=WHEEL_LOAD_FIT,gear_mass=GEAR_MASS_FIT)),indent=2)+'\n')
    write_tables(rows);curves();plots(rows)
    manifest=dict(python=platform.python_version(),numpy=np.__version__,matplotlib=matplotlib.__version__,
      accelerations_g=ACC,source_sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in ROOT.glob('*.py')})
    (OUT/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps(minima,indent=2))

if __name__=='__main__':produce()
