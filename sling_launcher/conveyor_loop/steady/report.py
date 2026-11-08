"""Run the first steady conveyor screen and write reproducible figures/data."""
from pathlib import Path
from dataclasses import replace
import json, csv, platform
import numpy as np
import scipy
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from matplotlib.patches import Circle
from .model import Inputs, solve, evaluate
OUT=Path(__file__).parent/'results'

def main():
    OUT.mkdir(exist_ok=True); base=Inputs(); rows=[]; histories={}
    cases=[(f'zylon_load_{q:.2f}',replace(base,payload_per_m=q*base.bare_density)) for q in [0,.1,.2,.3,.4,.6,1.]]
    cases += [(f'zylon_feed_{u:g}',replace(base,feed_speed=u)) for u in [1,10,20]]
    cases += [(f'kevlar_load_{q:.2f}',replace(base,density=1450,payload_per_m=q*1.45)) for q in [0,.2]]
    for name,c in cases:
        sol,L=solve(c); row,h=evaluate(c,sol,L); row['name']=name
        row['working_stress_GPa']=2.9 if c.density==1560 else 1.5
        row['utilization']=row['max_stress_GPa']/row['working_stress_GPa']
        rows.append(row); histories[name]=h; np.savez_compressed(OUT/f'{name}.npz',**h)
        print(name,round(row['max_stress_GPa'],4),round(row['capstan_mu_proxy'],4),flush=True)
    (OUT/'summary.json').write_text(json.dumps(rows,indent=2)+'\n')
    flat=[{k:v for k,v in r.items() if k!='inputs'}|{f'input_{k}':v for k,v in r['inputs'].items()} for r in rows]
    with (OUT/'summary.csv').open('w') as f:
        w=csv.DictWriter(f,fieldnames=flat[0]);w.writeheader();w.writerows(flat)
    plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False,'svg.fonttype':'none'})
    fig,axes=plt.subplots(3,1,figsize=(12,7),layout='constrained')
    for ax,q in zip(axes,[0,.2,1.]):
        name=f'zylon_load_{q:.2f}';h=histories[name];xy=h['xy_m'].T/1000
        seg=np.stack([xy[:-1],xy[1:]],axis=1)
        lc=LineCollection(seg,cmap='viridis',norm=plt.Normalize(0,4.5),linewidth=3)
        lc.set_array(h['stress_Pa'][:-1]/1e9);ax.add_collection(lc)
        ax.add_patch(Circle((base.station_radius/1000,0),base.wheel_radius/1000,facecolor='#a58b68',edgecolor='#54442d'))
        ax.plot(0,0,'o',color='#222222',ms=4);ax.set_xlim(-.16,6.05);ax.set_ylim(-1.65,.22);ax.set_aspect('equal')
        ax.set_title(f'Outbound payload / bare-line density = {q:g}   |   peak stress {rows[[r["name"] for r in rows].index(name)]["max_stress_GPa"]:.2f} GPa',loc='left',fontsize=10)
        ax.set_ylabel('Sideways (km)');ax.grid(alpha=.15)
        if q==.2:
            for frac in [.25,.75]:
                i=int(frac*(len(xy)-1)); d=xy[i+40]-xy[i]
                ax.annotate('',xy=xy[i]+d*3,xytext=xy[i],arrowprops=dict(arrowstyle='->',color='#884b25',lw=2))
            ax.annotate('Free turn; no pulley',xy=xy[np.argmax(np.linalg.norm(xy,axis=1))],xytext=(4.3,-1.1),arrowprops={'arrowstyle':'-','color':'.4'})
    axes[-1].set_xlabel('Outward from hub (km) — equal horizontal and vertical scale')
    fig.colorbar(lc,ax=axes,label='Tensile stress (GPa)',shrink=.85)
    fig.suptitle('Calculated steady conveyor shapes · Zylon HM screen · 5 m/s feed',fontsize=14)
    for ext in ['png','svg']:fig.savefig(OUT/f'shapes.{ext}',dpi=180)
    plt.close(fig)
    fig,axes=plt.subplots(2,2,figsize=(12,8),layout='constrained')
    colors=['#606060','#527e68','#a2673d']
    for q,color in zip([0,.2,1.],colors):
        h=histories[f'zylon_load_{q:.2f}'];axes[0,0].plot(h['arc_m']/1000,h['stress_Pa']/1e9,color=color,label=f'payload / line = {q:g}')
    axes[0,0].axhline(2.9,ls='--',color='#9c4848',label='Zylon screening allowance')
    axes[0,0].set(xlabel='Distance along free line (km)',ylabel='Stress (GPa)',title='Outbound → free turn → return');axes[0,0].legend(fontsize=8)
    loaded=rows[:7];q=np.array([r['inputs']['payload_per_m']/base.bare_density for r in loaded])
    axes[0,1].plot(q,[r['utilization'] for r in loaded],'o-',color='#527e68');axes[0,1].axhline(1,color='#9c4848',ls='--');axes[0,1].set(xlabel='Outbound payload / bare-line density',ylabel='Peak stress / 2.9 GPa',title='Zylon: screening strength boundary')
    axes[1,0].plot(q,[r['capstan_mu_proxy'] for r in loaded],'o-',color='#a2673d');axes[1,0].set(xlabel='Outbound payload / bare-line density',ylabel='Required friction coefficient (proxy)',title='Grip demand; actual friction remains unknown')
    feeds=sorted([rows[2]]+rows[7:10],key=lambda r:r['inputs']['feed_speed'])
    axes[1,1].plot([r['inputs']['feed_speed'] for r in feeds],[r['width_m'] for r in feeds],'o-',color='#527e68');axes[1,1].set(xlabel='Line feed speed (m/s)',ylabel='Full sideways extent (m)',title='Shape changes with feed · payload / line = 0.2')
    for ax in axes.flat:ax.grid(alpha=.2)
    fig.suptitle('Single-loop steady screen — strength and grip are different constraints')
    for ext in ['png','svg']:fig.savefig(OUT/f'stress_and_grip.{ext}',dpi=180)
    plt.close(fig)
    # Refinement, conservation and limit checks independent of solver's convergence flag.
    refined,L=solve(base,tol=2e-8);fine,hfine=evaluate(base,refined,L,n=20001)
    original=rows[2];orig=histories['zylon_load_0.20']
    s=orig['s']; z=refined.sol(s)
    checks=dict(max_position_change_m=float(np.max(np.linalg.norm(z[:2]*base.radius_scale-orig['xy_m'],axis=0))),
        stress_relative_change=abs(fine['max_stress_GPa']/original['max_stress_GPa']-1),
        max_bvp_residual=max(r['bvp_residual'] for r in rows),
        max_boundary_residual=max(r['boundary_residual'] for r in rows),
        max_integrated_force_residual_scaled=max(r['integrated_force_residual_scaled'] for r in rows),
        unloaded_first_integral_range=rows[0]['unloaded_first_integral_range'],
        all_effective_tensions_positive=all(r['min_effective_tension_N']>0 for r in rows),
        unloaded_capstan_mu_abs=abs(rows[0]['capstan_mu_proxy']))
    assert checks['max_position_change_m']<.01
    assert checks['stress_relative_change']<1e-5
    assert checks['max_integrated_force_residual_scaled']<1e-5
    assert checks['unloaded_first_integral_range']<1e-6
    assert checks['all_effective_tensions_positive']
    assert checks['unloaded_capstan_mu_abs']<1e-6
    (OUT/'validation.json').write_text(json.dumps(checks,indent=2)+'\n')
    (OUT/'environment.json').write_text(json.dumps(dict(python=platform.python_version(),numpy=np.__version__,scipy=scipy.__version__,matplotlib=matplotlib.__version__),indent=2)+'\n')
    print(checks)
if __name__=='__main__':main()
