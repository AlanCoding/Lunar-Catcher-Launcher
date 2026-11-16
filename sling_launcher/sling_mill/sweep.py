"""One-variable screens and a sampled mass/length/heat/drive Pareto set.
All rows retain feasibility flags. No conditional optimum is certified buildable.
"""
import json,csv
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from run import compute,ROOT,save

def main():
    base=json.loads((ROOT/'config.json').read_text());base['integration_steps_per_pitch']=8
    groups={'radius':np.geomspace(.05,1,8),'acceleration':np.geomspace(100,3000,8)*9.80665,
            'hub_ratio':np.linspace(.1,.65,8),'payload_depth':np.linspace(.02,.12,8)}
    rows=[]
    for variable,values in groups.items():
        for value in values:
            c=base.copy();c[variable]=float(value)
            # Radius family explicitly keeps L=10R, pitch=2.2R; W,D independent.
            if variable=='radius':c.update(pitch=2.2*value,payload_length=10*value)
            r,st,mass=compute(c)
            rows.append(dict(family=variable,input_value=float(value),material=c['material'],
                             mass_kg=r['conditional_installed_mass_kg'],length_m=r['installed_length_m'],
                             heat_W=r['slip_heat_W'],installed_drive_W=r['peak_installed_motor_power_W'],
                             entry_occupancy=r['entry_occupancy'],max_belt_thickness_m=r['maximum_belt_thickness_m'],
                             radius_m=c['radius'],finite_mass=bool(np.isfinite(r['conditional_installed_mass_kg'])),
                             basic_screens_pass=bool(r['entry_occupancy']<=1 and c['pitch']>2*c['radius'] and r['maximum_belt_thickness_m']<=.05*c['radius']),
                             feasible_demonstrated=False))
    for material in ['Kevlar 49','Zylon AS','Zylon HM']:
        c=base.copy();c['material']=material;r,_,_=compute(c)
        rows.append(dict(family='material',input_value=0,material=material,mass_kg=r['conditional_installed_mass_kg'],length_m=r['installed_length_m'],heat_W=r['slip_heat_W'],installed_drive_W=r['peak_installed_motor_power_W'],entry_occupancy=r['entry_occupancy'],max_belt_thickness_m=r['maximum_belt_thickness_m'],radius_m=c['radius'],finite_mass=bool(np.isfinite(r['conditional_installed_mass_kg'])),basic_screens_pass=False,feasible_demonstrated=False))
    # Conditional Pareto set over sampled designs, excluding non-finite entries.
    metrics=np.array([[r[k] for k in ['mass_kg','length_m','heat_W','installed_drive_W']] for r in rows])
    for i,r in enumerate(rows):
        r['conditional_pareto']=bool(np.isfinite(metrics[i]).all() and not np.any(np.all(metrics<=metrics[i],axis=1)&np.any(metrics<metrics[i],axis=1)))
    with (ROOT/'results'/'sweep.csv').open('w') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    fig,axs=plt.subplots(2,2,figsize=(12,8))
    for ax,(var,values) in zip(axs.flat,groups.items()):
        rr=[r for r in rows if r['family']==var]
        ax.plot([r['input_value'] for r in rr],[r['mass_kg']/1000 for r in rr],'o-',color='#49677e')
        ax.set(xlabel=var+' (SI)',ylabel='Conditional inventory (tonnes)',yscale='log');ax.grid(alpha=.2)
    fig.suptitle('Design screens · baseline contact geometry remains unresolved');fig.tight_layout();save(fig,'parameter_sweeps')
    fig,ax=plt.subplots(figsize=(8,5))
    valid=[r for r in rows if r['finite_mass']]
    sc=ax.scatter([r['length_m'] for r in valid],[r['mass_kg']/1000 for r in valid],c=[r['heat_W']/1e6 for r in valid],cmap='viridis')
    pareto=[r for r in valid if r['conditional_pareto']]
    ax.scatter([r['length_m'] for r in pareto],[r['mass_kg']/1000 for r in pareto],facecolors='none',edgecolors='brown',s=120,label='Sampled Pareto candidates')
    ax.set(xlabel='Installed length (m)',ylabel='Conditional inventory (tonnes)',yscale='log',title='Trade space · no demonstrated feasible optimum');ax.legend();fig.colorbar(sc,label='Sliding heat (MW)');save(fig,'pareto')
    print(f'{len(rows)} samples; {sum(r["basic_screens_pass"] for r in rows)} pass basic screens; feasibility remains open.')
if __name__=='__main__':main()
