"""Generate blended-model diagnostics and smooth parameter comparisons."""
import json,csv
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from model import solve
ROOT=Path(__file__).parent

def writecsv(name,rows):
    with (ROOT/'results'/name).open('w') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

def save(fig,name):
    for ext in ['svg','png']:fig.savefig(ROOT/'results'/f'{name}.{ext}',dpi=160,bbox_inches='tight')
    plt.close(fig)

def main():
    c=json.loads((ROOT/'config.json').read_text());r,a,m=solve(c)
    (ROOT/'results/summary.json').write_text(json.dumps(r,indent=2)+'\n')
    (ROOT/'results/mass.json').write_text(json.dumps(m,indent=2)+'\n')
    writecsv('profile.csv',[dict(zip(a,vals)) for vals in zip(*a.values())])
    fig,axs=plt.subplots(2,2,figsize=(11,7))
    x=a['x_m']/1000
    axs[0,0].plot(x,a['acceleration_m_s2']/9.80665);axs[0,0].set_ylabel('Derived acceleration (Earth g)')
    axs[0,1].plot(x,a['coating_indentation_m']*1e6,label='Layer compression')
    axs[0,1].plot(x,a['belt_deflection_m']*1e6,label='Belt deflection');axs[0,1].set_ylabel('Mean per-surface squeeze (µm)');axs[0,1].legend()
    axs[1,0].plot(x,a['belt_stress_Pa']/1e9);axs[1,0].axhline(c['working_stress_Pa']/1e9,ls='--',color='brown',label='Working ceiling');axs[1,0].legend();axs[1,0].set_ylabel('Structural belt stress (GPa)')
    axs[1,1].plot(x,a['roller_temperature_K']);axs[1,1].axhline(c['coating_temperature_limit_K'],ls='--',color='brown');axs[1,1].set_ylabel('Steady roller temperature (K)')
    for ax in axs.flat:ax.set_xlabel('Distance (km)');ax.grid(alpha=.2)
    fig.suptitle('Blended tightness-driven example · fixed 0.40 mm total squeeze')
    fig.tight_layout();save(fig,'coupled_profile')
    rows=[]
    for squeeze in [.0001,.0002,.0003,.0004,.0006,.0008,.001,.002]:
        cc=dict(c,total_squeeze_m=squeeze)
        row=dict(squeeze_mm=squeeze*1000,status='',length_km=None,slip_heat_MW=None,max_stress_GPa=None,max_roller_K=None,mass_t=None,payback_h=None,failed_screens='')
        try:
            rr,_,_=solve(cc)
            row.update(status='solved',length_km=rr['corridor_length_m']/1000,slip_heat_MW=rr['slip_heat_W']/1e6,max_stress_GPa=rr['maximum_belt_stress_Pa']/1e9,max_roller_K=rr['maximum_average_roller_temperature_K'],mass_t=rr['conditional_machine_mass_kg']/1000,payback_h=rr['gross_operating_payback_hours'],failed_screens='; '.join(k for k,val in rr['constraint_residuals'].items() if val>1e-8))
        except ValueError as error:row['status']=str(error)
        rows.append(row)
    writecsv('tightness_sweep.csv',rows)
    fig,axs=plt.subplots(1,3,figsize=(13,4))
    good=[row for row in rows if row['status']=='solved']
    for ax,key,label in zip(axs,['length_km','slip_heat_MW','payback_h'],['Required corridor (km)','Sliding heat (MW)','Conditional mass payoff (h)']):
        ax.plot([rr['squeeze_mm'] for rr in good],[rr[key] for rr in good],color='#49677e')
        for rr in good:ax.scatter(rr['squeeze_mm'],rr[key],color='#a25c43' if rr['failed_screens'] else '#426e60',zorder=3)
        ax.set(xlabel='Total squeeze (mm)',ylabel=label);ax.grid(alpha=.2)
    fig.suptitle('Tightness tradeoff · green passes current screens; brown fails one or more')
    fig.tight_layout();save(fig,'tightness_tradeoff')
    # Fixed geometry: show mass and feasibility at alternative stress ceilings.
    strength=[]
    for ceiling in [1e9,1.25e9,1.5e9,1.856e9]:
        rr,_,_=solve(dict(c,working_stress_Pa=ceiling))
        strength.append(dict(working_ceiling_GPa=ceiling/1e9,required_belt_stress_GPa=rr['maximum_belt_stress_Pa']/1e9,utilization=rr['working_stress_utilization'],conditional_mass_t=rr['conditional_machine_mass_kg']/1000,belt_pass=rr['constraint_residuals']['belt_stress']<=1e-8))
    writecsv('strength_ceilings.csv',strength)
    print(json.dumps(r,indent=2));print(rows)
if __name__=='__main__':main()
