"""Fixed-throughput mass/stress frontier and cadence-independent crossover map."""
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.interpolate import PchipInterpolator
from .compare import OUT,MDOT,PERIOD
from .stress_frontier import taper_ratio

def interpolation(curve):
    r=curve['rows'];x=[p['specific_stress_J_kg'] for p in r]
    q=PchipInterpolator(x,[p['q'] for p in r])
    c=PchipInterpolator(x,[p['mass_per_flow_s']*p['q'] if p['q'] else r[1]['mass_per_flow_s']*r[1]['q'] for p in r])
    return lambda k:c(k)/q(k)

def main():
    d=json.loads((OUT/'stress_frontier.json').read_text());assert len(d['curves'])==3
    plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False,'svg.fonttype':'none'})
    panels=[plt.subplots(figsize=(8.5,6.5),layout='constrained') for _ in range(2)]
    figures=[p[0] for p in panels];axs=[p[1] for p in panels]
    k=np.linspace(.8,3.5,300)*1e6
    axs[0].plot(k/1e6,[MDOT*PERIOD*taper_ratio(v)/1000 for v in k],color='#343434',lw=2,label='Tapered spool · 110.6 min cycle')
    table=[]
    for c,color in zip(d['curves'],['#a2673d','#527e68','#476d86']):
        floor=c['rows'][0]['specific_stress_J_kg'];f=interpolation(c)
        kk=np.geomspace(floor+1000,min(3.5e6,c['rows'][-1]['specific_stress_J_kg']),250)
        mass=f(kk)*MDOT
        axs[0].plot(kk/1e6,mass/1000,color=color,label=f'Conveyor · {c["feed_m_s"]:g} m/s')
        axs[1].plot(kk/1e6,[float(f(v))/taper_ratio(v)/60 for v in kk],color=color,label=f'Conveyor · {c["feed_m_s"]:g} m/s')
        for stress in [1.,1.4,1.5,1.6,1.8,2.,2.5,3.]:
            value=None if stress*1e6<=floor else float(f(stress*1e6))*MDOT
            table.append(dict(specific_stress_MJ_kg=stress,feed_m_s=c['feed_m_s'],spool_mass_kg=MDOT*PERIOD*taper_ratio(stress*1e6),conveyor_mass_kg=value))
    low=min(c['rows'][0]['specific_stress_J_kg'] for c in d['curves'])/1e6
    for ax in axs:
        ax.axvspan(.8,low,color='#ebded6',alpha=.65)
        ax.axvline(low,ls=':',color='#a2673d')
        ax.set_xlim(.8,3.5);ax.set_yscale('log');ax.grid(alpha=.18)
        ax.set_xlabel('Allowed specific stress σ / ρ (MJ/kg)')
    axs[0].set(ylabel='Working tether mass per useful arm (tonnes)',ylim=(.1,200))
    axs[0].text(1.12,45,'Conveyor below\nself-stress floor',ha='center',fontsize=9)
    axs[0].legend(fontsize=8,loc='upper right')
    for minutes in [30,60,PERIOD/60]:
        axs[1].axhline(minutes,color='.6',ls=':',lw=1)
        axs[1].text(3.48,minutes*1.04,f'{minutes:.1f} min',ha='right',fontsize=8)
    axs[1].set(ylabel='Equal-mass spool cycle (minutes)',ylim=(10,3000))
    axs[1].text(2.05,1500,'Longer cycles than the curve: conveyor lighter\nShorter cycles than the curve: tapered spool lighter',fontsize=9)
    axs[1].legend(fontsize=8,loc='lower left')
    figures[0].suptitle('Fixed mass flow: 0.1507503 kg/s\nRelease speed 1,684.517 m/s · steady/quasi-static tether material only',fontsize=13)
    figures[1].suptitle('Spool cycle at which both architectures need equal tether mass\nFixed mass flow and release speed · mechanical cycle sensitivity',fontsize=12)
    for fig,name in zip(figures,['fixed_mass_flow','cycle_crossover']):
        for ext in ['png','svg']:fig.savefig(OUT/f'{name}.{ext}',dpi=240)
        plt.close(fig)
    (OUT/'frontier_matrix.json').write_text(json.dumps(table,indent=2)+'\n')
    for v in table:
        if v['feed_m_s']==5:print(v)
if __name__=='__main__':main()
