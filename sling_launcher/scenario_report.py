"""Static scientific figures and detailed, generated scenario records."""
from dataclasses import replace
from pathlib import Path
import csv, hashlib, json, platform
import numpy as np
import scipy
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from .scenario_study import Scenario, geometry, calculate

ROOT=Path(__file__).parent
OUT=ROOT/'results'/'speed_constrained'
ACCELERATIONS=(4,10,30,60,100,125,300,1000,2500,4000,4200)
SPEEDS=(50,80)

def save(fig,path):
    fig.tight_layout();fig.savefig(path.with_suffix('.svg'),bbox_inches='tight');fig.savefig(path.with_suffix('.png'),dpi=130,bbox_inches='tight');plt.close(fig)
    svg=path.with_suffix('.svg');svg.write_text('\n'.join(line.rstrip() for line in svg.read_text().splitlines())+'\n')

def cycle_plot(r,path):
    fig,ax=plt.subplots(3,1,figsize=(10,9),sharex=True);offset=0
    for p in r['history']:
        t=(p['t']+offset)/60
        ax[0].plot(t,p['wheel']/1e6,color='#2364aa',label='Wheel mechanical' if offset==0 else None)
        ax[0].plot(t,p['radial']/1e6,color='#d37820',label='Reel mechanical (+ input)' if offset==0 else None)
        ax[1].plot(t,p['solar0']/1e6,color='#8051a3',label='No recovery' if offset==0 else None)
        ax[1].plot(t,p['solarr']/1e6,color='#268568',label='70% instantaneous recovery' if offset==0 else None)
        ax[2].plot(t,p['omega']*r['track_radius_m'],color='#2364aa')
        for axis in ax:
            axis.axvline(t[0],color='.75',lw=.7);axis.grid(alpha=.2)
        ax[0].text((t[0]+t[-1])/2,1.02,p['name'],ha='center',transform=ax[0].get_xaxis_transform(),fontsize=9)
        offset+=p['t'][-1]
    ax[0].set_ylabel('Shaft power (MW)');ax[1].set_ylabel('Solar input (MW)');ax[2].set_ylabel('Rover speed (m/s)');ax[2].set_xlabel('Cycle time (min)')
    for axis in ax[:2]:axis.legend(loc='best',fontsize=9)
    fig.suptitle(f"{r['inputs']['acceleration_g']} g · {r['inputs']['rover_mph']} mph · {r['inputs']['passes']} pass(es)\nQuasi-static branches; release transient excluded",fontsize=13,y=1.02)
    save(fig,path)

def shape_plot(geo,path):
    cable,branches,h,_=geo;fig,ax=plt.subplots(1,2,figsize=(12,4.5))
    for axis,b,name in zip(ax,branches,['Loaded payout','Unloaded return']):
        for f in [.1,.25,.4,.6,1.]:
            i=int(np.argmin(abs(b['f']-f)));p=b['shapes'][i]
            axis.plot(p['r']/1000,(h-p['drop'])/1000,label=f"{100*b['f'][i]:.0f}% out")
        rr=np.linspace(cable.radius,cable.tip_radius,601)
        from .environment import LunarEnvironment
        R=LunarEnvironment().reference_radius_m
        axis.plot(rr/1000,(np.sqrt(R*R-rr*rr)-R)/1000,'k--',label='Reference terrain')
        axis.set(xlabel='Radius from rotation axis (km)',ylabel='Height above hub tangent plane (km)',title=name)
        axis.legend(fontsize=8);axis.grid(alpha=.2)
    fig.suptitle('Finite-angle cable shapes; vertical scale exaggerated',y=1.02)
    save(fig,path)

def scenario_text(r):
    c=r['inputs'];rows=[]
    def metric(label,value,unit):rows.append(f'| {label} | {value:,.3f} {unit} |')
    for label,key,unit in [('Track radius (dependent)','track_radius_m','m'),('Release radius','release_radius_m','m'),
      ('Each cable material length','cable_length_m','m'),('Apex height, including 3 m clearance','pole_apex_height_m','m'),
      ('Vertical leg / nominal pole height','vertical_leg_m','m'),('45° trailing leg length','leg_45deg_m','m'),
      ('Release tip speed relative to site','release_speed_m_s','m/s'),('Peak payload proper acceleration','peak_payload_proper_g','Earth g'),
      ('Ballast, total two frames','ballast_total_kg','kg'),('Ballast lunar weight','ballast_lunar_weight_n','N'),
      ('Ballast allocated per powered wheel','ballast_per_powered_wheel_kg','kg'),('Powered-wheel normal load, average','powered_wheel_normal_n','N'),
      ('Powered contact area at assumed 100 kPa','powered_contact_area_at_100kpa_m2','m²'),
      ('Required compact-frame radial support half-width','compact_frame_required_radial_halfwidth_m','m'),
      ('Extra inward ballast restraint per frame','extra_ballast_radial_force_per_frame_n','N'),
      ('Main tie endpoint tension envelope','main_tie_endpoint_n','N'),('Main tie sag estimate','main_tie_sag_estimate_m','m'),
      ('Fiber volume stored per spool (before packing allowance)','empty_spool_fiber_volume_per_side_m3','m³'),
      ('Root cable equivalent solid diameter','max_cable_solid_equivalent_diameter_m','m'),
      ('Empty cable tip equilibrium shift at release','release_empty_tip_displacement_m','m'),
      ('Two-cable release shape energy discontinuity','release_shape_energy_discontinuity_j','J'),
      ('Flight to catcher','catcher_flight_s','s'),('Catcher encounter relative speed','catcher_relative_speed_m_s','m/s')]:metric(label,r[key],unit)
    lines=[f"# {c['acceleration_g']} g, {c['rover_mph']} mph, {c['passes']} catcher pass(es)",'',
      'A conditional engineering scenario, **not a qualified buildable design**. Inputs and all outputs: [metrics.json](metrics.json). Full time history: [history.csv](history.csv). [Equations and limits](../../../METHOD.md). [All scenarios](../../../README.md).','',
      'Payload: 1,000 kg useful + 1,000 kg equal-radius rock countermass. Acceleration label means release centripetal acceleration; the vector peak is separately reported. Track radius is derived, never optimized independently.','',
      '## Geometry and mechanical demands','', '| Metric | Result |','| --- | ---: |',*rows,'',
      f"The 45° same-track geometric fit test **{'passes' if r['frame_45deg_same_track_fits'] else 'FAILS'}** (height must be smaller than track diameter). Passing is only a necessary condition; wheel size, frame interference, and contact moments remain unresolved.",
      '', '## Mass composition','',
      '| Category | Permanent import kg | Local permanent kg | Status |','| --- | ---: | ---: | --- |',
      f"| B04: two outward Kevlar cables | {r['total_outward_cable_kg']:,.1f} | — | Fiber only, static total-stress taper |",
      f"| B05: apex-to-apex main tie | {r['main_tie_conditional_kg']:,.1f} | — | Conditional tensile sizing; restraint geometry unresolved |",
      f"| B16: solar, no recovery | {r['solar_no_recovery_kg']:,.1f} | — | Assumed installed array 100 W/kg |",
      f"| B16: solar, 70% recovery (alternative) | {r['solar_recovery_kg']:,.1f} | — | Same W/kg assumption; instantaneous recovery only |",
      f"| B21: wheel rock ballast | — | {r['ballast_total_kg']:,.1f} | Tangential traction model, no unsized hardware weight credit |",
      '| B01–B03: poles, braces, apex joints | **Unsized** | — | Radial bending and tipping unresolved; old axial-only pole masses withdrawn |',
      '| B06–B07: stabilizers, terminations, guides, sheath | Unsized | — | Small stabilizer force is not demonstrated |',
      '| B08–B10: 4 powered + 4 passive wheels, drives, steering | Unsized | — | Capacity and speed qualification needed |',
      '| B11: 2 operating reels and drives | Unsized | — | Cable inventory volume and power given; bend life and drums unresolved |',
      '| B12–B13: pivot and anchors | Unsized | — | Stabilizing load path unresolved |',
      '| B14–B15: climbers and their service hardware | Not used | — | This branch uses spooling instead |',
      '| B17–B20: conversion, control, thermal, ballast retention | Unsized | — | These are not zero-mass equipment |','',
      f"Accounted imported subtotal / useful payload: **{r['accounted_imported_subtotal_no_recovery_kg']/c['payload_kg']:.1f}** without recovery, **{r['accounted_imported_subtotal_recovery_kg']/c['payload_kg']:.1f}** with recovery. These are **incomplete subtotals, not launcher mass ratios**. Pole/total imported mass is explicitly null in JSON. Solar stays on the ground; other unsized moving hardware and this tie subtotal are not fed back into the cycle inertia/normal-load solution.",
      '', 'B22 rock expendable: 1,000 kg per release; B23 useful payload: 1,000 kg. Equal-radius rock **does not impact the reference sphere** in this calculation, so disposal is not closed. Loading/release machinery and prepared-road construction remain excluded.',
      '', '## Timeline and power','', '| Segment | Minutes | Peak wheel input MW | Peak reel input MW | Available reel braking MW |','| --- | ---: | ---: | ---: | ---: |']
    for p in r['phases']:lines.append(f"| {p['phase']} | {p['duration_s']/60:.3f} | {p['peak_wheel_w']/1e6:.3f} | {p['peak_reel_input_w']/1e6:.3f} | {p['peak_reel_braking_w']/1e6:.3f} |")
    lines += ['',f"Peak direct solar: **{r['peak_solar_no_recovery_w']/1e6:.3f} / {r['peak_solar_recovery_w']/1e6:.3f} MW** (none / 70% recovery). Cycle solar energy: {r['solar_cycle_no_recovery_j']/1e9:.3f} / {r['solar_cycle_recovery_j']/1e9:.3f} GJ. Recovery has no effect on required mechanical traction. Four wheel drives share the wheel demand only under equal load sharing; two reels share the reel demand.",
      '',f"Peak ground force occurs in {r['peak_traction_location']['phase']} at {100*r['peak_traction_location']['deployed_fraction']:.2f}% deployment. Rover speed is {r['min_rover_speed_m_s']:.3f}–{r['max_rover_speed_m_s']:.3f} m/s: cruise equals the specified operating speed; slowing during loading/buffer closes phase without exceeding it.",
      '', 'The release transient is **not fitted into this timeline**. The reported empty-cable displacement compares equilibria, not a predicted recoil trajectory. Its energy discontinuity is excluded from branch energy/power totals and could require a dwell or a slower cadence. Loading is a fixed 5-minute allowance, not a demonstrated service mechanism. Daylight only; no night operation or stored-energy credit.',
      '', '![Cycle powers and rover speed](cycle.svg)','', '![Finite-angle shapes](../shapes.svg)','']
    return '\n'.join(lines)


def overview(results):
    fig,axes=plt.subplots(2,2,figsize=(11,8))
    for mph in SPEEDS:
        rs=[r for r in results if r['inputs']['rover_mph']==mph and r['inputs']['passes']==1];x=[r['inputs']['acceleration_g'] for r in rs]
        for ax,key,scale,label in zip(axes.flat,['track_radius_m','release_radius_m','pole_apex_height_m','halfwidth_over_track_radius'],[1,1/1000,1,1],['Track radius (m)','Release radius (km)','Apex height (m)','Required support half-width / track radius']):
            ax.loglog(x,[r[key]*scale for r in rs],'o-',label=f'{mph} mph');ax.set(xlabel='Release centripetal acceleration (Earth g)',ylabel=label);ax.grid(alpha=.25,which='both');ax.legend()
    axes[1,1].axhline(1,color='black',ls='--');fig.suptitle('Dependent geometry and compact-frame overturning diagnostic')
    save(fig,OUT/'geometry_sweep')
    fig,axes=plt.subplots(1,2,figsize=(12,4.5))
    for mph in SPEEDS:
        for passes in [1,2]:
            rs=[r for r in results if r['inputs']['rover_mph']==mph and r['inputs']['passes']==passes];x=[r['inputs']['acceleration_g'] for r in rs]
            label=f'{mph} mph, {passes} pass(es)'
            axes[0].semilogx(x,[r['ballast_total_kg']/1000 for r in rs],'o-',label=label)
            axes[1].semilogx(x,[r['peak_solar_recovery_w']/1e6 for r in rs],'o-',label=label)
    axes[0].set_ylabel('Total local ballast (tonnes)');axes[1].set_ylabel('Peak solar, 70% recovery (MW)')
    for ax in axes:ax.set_xlabel('Release centripetal acceleration (Earth g)');ax.grid(alpha=.25);ax.legend(fontsize=8)
    fig.suptitle('Time and rover speed dominate these conditional demands')
    save(fig,OUT/'ballast_power_sweep')
    fig,axes=plt.subplots(1,2,figsize=(12,4.5),sharey=True)
    for ax,mph in zip(axes,SPEEDS):
        rs=[r for r in results if r['inputs']['rover_mph']==mph and r['inputs']['passes']==1];x=np.arange(len(rs));bottom=np.zeros(len(rs))
        for key,label in [('total_outward_cable_kg','Outward cables'),('main_tie_conditional_kg','Main tie'),('solar_recovery_kg','Solar (70% recovery)')]:
            y=np.array([r[key]/1000 for r in rs]);ax.bar(x,y,bottom=bottom,label=label);bottom+=y
        ax.set(xticks=x,xticklabels=ACCELERATIONS,xlabel='Release centripetal acceleration (Earth g)',title=f'{mph} mph, one pass');ax.legend(fontsize=8)
    axes[0].set_ylabel('Accounted imported mass (tonnes)')
    fig.suptitle('Incomplete mass subtotals — poles, drives, wheels and other hardware UNSIZED')
    save(fig,OUT/'accounted_mass')


def produce():
    OUT.mkdir(parents=True,exist_ok=True);results=[]
    plt.rcParams.update({'font.size':10,'svg.hashsalt':'lunar-sling-checkpoint'})
    for mph in SPEEDS:
        for acc in ACCELERATIONS:
            c=Scenario(acceleration_g=acc,rover_mph=mph);geo=geometry(c)
            parent=OUT/f'{mph}mph'/f'{acc:03d}g';parent.mkdir(parents=True,exist_ok=True);shape_plot(geo,parent/'shapes')
            for passes in [1,2]:
                r=calculate(replace(c,passes=passes),geo,history=True);path=parent/f'{passes}_pass';path.mkdir(exist_ok=True)
                cycle_plot(r,path/'cycle')
                with (path/'history.csv').open('w') as f:
                    f.write('phase,time_s,deployed_fraction,omega_rad_s,wheel_mechanical_w,reel_mechanical_w,solar_no_recovery_w,solar_recovery_w,ground_force_n\n');offset=0
                    for p in r['history']:
                        for i in range(0,len(p['t']),8):
                            t=p['t'][i]
                            f.write(','.join([p['name'],str(t+offset)]+[str(p[k][i]) for k in ['f','omega','wheel','radial','solar0','solarr','force']])+'\n')
                        offset+=p['t'][-1]
                del r['history'];(path/'metrics.json').write_text(json.dumps(r,indent=2)+'\n');(path/'README.md').write_text(scenario_text(r));results.append(r)
            print(f'{mph} mph {acc} g: height {r["pole_apex_height_m"]:.2f} m',flush=True)
    overview(results)
    from scipy.optimize import brentq
    bounds={}
    for mph,lo,hi in [(50,2500,2700),(80,4000,4300)]:
        def residual(acc):
            cable,_,height,_=geometry(Scenario(acceleration_g=acc,rover_mph=mph,shape_fractions=81,shape_nodes=201))
            return height-2*cable.radius
        bounds[str(mph)]=dict(upper_45deg_chord_boundary_g=float(brentq(residual,lo,hi,xtol=.01)),description='Necessary geometry bound only; equality collides with opposite frame')
    (OUT/'geometry_bounds.json').write_text(json.dumps(bounds,indent=2)+'\n')
    (OUT/'all_scenarios.json').write_text(json.dumps(results,indent=2)+'\n')
    scalar_keys=[k for k,v in results[0].items() if isinstance(v,(int,float,bool)) or v is None]
    with (OUT/'summary.csv').open('w') as f:
        writer=csv.DictWriter(f,fieldnames=['rover_mph','passes']+scalar_keys,lineterminator='\n');writer.writeheader()
        for r in results:writer.writerow(dict(rover_mph=r['inputs']['rover_mph'],passes=r['inputs']['passes'],**{k:r[k] for k in scalar_keys}))
    manifest=dict(python=platform.python_version(),numpy=np.__version__,scipy=scipy.__version__,matplotlib=matplotlib.__version__,
                  accelerations_g=ACCELERATIONS,rover_speeds_mph=SPEEDS,
                  source_sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in ROOT.glob('*.py')})
    (OUT/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    lines=['# Speed-constrained scenario catalogue','',
      '**Current numerical checkpoint.** Track radius is a dependent output. These are conditional scenarios, not feasible machine designs. [Higher-level checkpoint](../../CHECKPOINT.md) · [Method and limits](METHOD.md) · [JSON](all_scenarios.json) · [CSV](summary.csv) · [Reproduction manifest](manifest.json).','',
      '1,000 kg useful payload; 1,000 kg countermass; 50 / 80 mph; 4–4,200 Earth g (the highest rows deliberately bracket a geometric failure boundary); one / two catcher passes. All cases have a 5-minute loading allowance and a 5-minute final buffer. Cruise speed equals the chosen rover speed.','',
      '| Speed mph | Release g | Track radius m | Release radius km | Apex height m | Ballast t, 1 / 2 passes | Solar MW, 70% recovery, 1 / 2 passes | 45° frame fits track? | Detailed scenarios |',
      '| ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |']
    for r,s in zip(results[::2],results[1::2]):
        mph=r['inputs']['rover_mph'];acc=r['inputs']['acceleration_g'];base=f'{mph}mph/{acc:03d}g'
        lines.append(f"| {mph} | {acc} | {r['track_radius_m']:.2f} | {r['release_radius_m']/1000:.3f} | {r['pole_apex_height_m']:.2f} | {r['ballast_total_kg']/1000:.1f} / {s['ballast_total_kg']/1000:.1f} | {r['peak_solar_recovery_w']/1e6:.2f} / {s['peak_solar_recovery_w']/1e6:.2f} | {'Necessary test passes' if r['frame_45deg_same_track_fits'] else '**FAIL**'} | [one pass]({base}/1_pass/README.md), [two passes]({base}/2_pass/README.md) |")
    lines += ['', '**No row establishes complete buildability.** Even where the 45° chord fits, compact-frame radial moment balance is not closed, release recoil is unresolved, and equal-radius rock disposal fails. High-g rows are useful diagnostics, not candidate designs.',
      '', '![Geometry](geometry_sweep.svg)','', '![Ballast and power](ballast_power_sweep.svg)','', '![Accounted mass](accounted_mass.svg)','']
    (OUT/'README.md').write_text('\n'.join(lines))
    return results
