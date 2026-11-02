"""Current reference: 50 mph, one pass, separate upper and lower radial paths."""
from pathlib import Path
import hashlib,json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from .scenario_study import Scenario,geometry,calculate
from .hardware_study import evaluate
from .component_sizing import variants
ROOT=Path(__file__).parent
OUT=ROOT/'results/split_tie';OUT.mkdir(exist_ok=True)
ACC=[4,6,6.2,6.3,8,10,15,20,25,30,35,40,45,50,55,60,65,70,75,80,90,100,125,150,220,300,600]

def produce():
    rows=[]
    for acc in ACC:
        c=Scenario(acceleration_g=acc,rover_mph=50,passes=1);geo=geometry(c);base=calculate(c,geo,history=True)
        for cfg in variants():rows.append(evaluate(base,geo,cfg,radial_policy='split'))
        print(acc,flush=True)
    (OUT/'all_estimates.json').write_text(json.dumps(rows,indent=2)+'\n')
    minima=[]
    for profile in ['lighter','reference','heavier']:
        candidates=[r for r in rows if r['assumptions']['name']==profile and r['converged']]
        minima.append(min(candidates,key=lambda r:r['imported_ratio']) if candidates else dict(profile=profile,converged=False))
    (OUT/'sampled_minima.json').write_text(json.dumps(minima,indent=2)+'\n')
    ref=[r for r in rows if r['assumptions']['name']=='reference']
    fig,ax=plt.subplots(figsize=(10,6));plt.rcParams['svg.hashsalt']='split-tie'
    for name,style in [('lighter','--'),('reference','-'),('heavier',':')]:
        rs=[r for r in rows if r['assumptions']['name']==name]
        ax.plot([r['acceleration_g'] for r in rs],[r.get('imported_ratio') if r.get('imported_ratio') is not None else np.nan for r in rs],style,marker='.',label=f'Imported: {name}')
    ax.plot([r['acceleration_g'] for r in ref],[r.get('physical_ratio') if r.get('physical_ratio') is not None else np.nan for r in ref],color='.5',label='Total including ballast: reference')
    best=min((r for r in ref if r['converged']),key=lambda r:r['imported_ratio'])
    ax.scatter([best['acceleration_g']],[best['imported_ratio']],marker='*',s=160,color='black',zorder=5,label=f"Reference sampled minimum: {best['acceleration_g']} g")
    ax.axvline(6.234,color='.6',ls=':',label='Approx. switch to low tether (~616 m track)')
    ax.set(xscale='log',yscale='log',xlabel='Payload release acceleration (Earth g)',ylabel='Permanent mass / useful payload mass',title='50 mph, one pass: upper payload tie + low rover tie as needed')
    ax.legend(fontsize=9);ax.grid(alpha=.2,which='both')
    fig.text(.5,.01,'Low tether carries rover/ballast turning load on small tracks; no banked track.\nGaps: mass iteration failed. Other fabrication/operation checks remain in the data.',ha='center',fontsize=9)
    fig.tight_layout(rect=(0,.07,1,1))
    for ext in ['png','svg']:
        p=OUT/f'mass_trade.{ext}';fig.savefig(p,dpi=150,bbox_inches='tight')
        if ext=='svg':p.write_text('\n'.join(l.rstrip() for l in p.read_text().splitlines())+'\n')
    plt.close(fig)
    lines=['# Reference scenarios: 50 mph, one pass','', '| Payload g | Track radius m | Apex height m | Four poles t | Low tie fiber t | Ballast t | Imported ratio | Physical ratio |','| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |']
    for r in ref:
        if r['converged']:
            lines.append(f"| {r['acceleration_g']} | {r['track_radius_m']:.2f} | {r['apex_height_m']:.2f} | {r['masses_kg']['poles']/1000:.2f} | {r['masses_kg']['low_tie']/1000:.3f} | {r['ballast_kg']/1000:.2f} | {r['imported_ratio']:.2f} | {r['physical_ratio']:.2f} |")
        else:lines.append(f"| {r['acceleration_g']} | {r.get('track_radius_m',float('nan')):.2f} | — | — | — | — | No closed mass iteration | — |")
    (OUT/'SCENARIOS.md').write_text('\n'.join(lines)+'\n')
    (OUT/'manifest.json').write_text(json.dumps(dict(source_sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in ROOT.glob('*.py')},policy='split',rover_mph=50,passes=1),indent=2)+'\n')
    print('MINIMA',[(r.get('assumptions',{}).get('name',r.get('profile')),r.get('acceleration_g'),r.get('imported_ratio')) for r in minima])
if __name__=='__main__':produce()
