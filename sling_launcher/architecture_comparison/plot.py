"""Figures from saved comparison results; no engineering model rerun."""
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from .compare import OUT

def main():
    d=json.loads((OUT/'comparison.json').read_text());rows=d['rows'];ref=rows[2]
    plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False,'svg.fonttype':'none'})
    fig,axs=plt.subplots(2,2,figsize=(12,8),layout='constrained')
    blue='#476d86';green='#547f66';red='#a15b47'
    ax=axs[0,0];ax.plot([r['feed_m_s'] for r in rows[:5]],[r['conveyor']['material_mass_kg']/1000 for r in rows[:5]],'o-',color=green,label='Uniform conveyor, both strands')
    ax.axhline(ref['spool']['material_mass_kg']/1000,color=blue,label='Tapered spool, one outgoing cable')
    ax.set(xlabel='Conveyor feed (m/s)',ylabel='Tether material per arm (tonnes)',title='Matched mean flow and release speed',xscale='log');ax.set_xticks([1,2,5,10,20],['1','2','5','10','20']);ax.legend(fontsize=8)
    ax=axs[0,1];rr=[rows[5],ref,rows[6]];x=[r['allowance_Pa']/1e9 for r in rr]
    for kind,col,label in [('conveyor',green,'Conveyor · 5 m/s'),('spool',blue,'Tapered spool')]:ax.plot(x,[r[kind]['material_mass_kg']/1000 for r in rr],'o-',color=col,label=label)
    ax.axvline(ref['conveyor']['unloaded_stress_Pa']/1e9,ls=':',color=red,label='Conveyor self-stress floor')
    ax.set(xlabel='Chosen working stress (GPa)',ylabel='Tether material per arm (tonnes)',title='Same Zylon material in both');ax.legend(fontsize=8)
    ax=axs[1,0];t=np.linspace(1200,14000,100);flow=d['matched_mean_flow_kg_s'];k=ref['spool']['tether_to_batch_mass_ratio'];mc=ref['conveyor']['material_mass_kg']
    ax.plot(t/60,k*flow*t/1000,color=blue,label='Spool: batch grows with cycle time');ax.axhline(mc/1000,color=green,label='Conveyor · 5 m/s')
    ax.axvline(ref['crossover_spool_cycle_s']/60,ls=':',color=red,label=f'Equal mass: {ref["crossover_spool_cycle_s"]/60:.1f} min')
    ax.axvline(d['spool_cycle_s']/60,ls='--',color='.5',label='Inherited 110.6 min cycle')
    ax.set(xlabel='Assumed spool cycle (minutes)',ylabel='Tether material per arm (tonnes)',title='Cadence sensitivity · not a validated schedule');ax.legend(fontsize=8)
    ax=axs[1,1];duty=np.linspace(.15,1,100)
    ax.plot(duty,mc/duty/1000,color=green,label='Conveyor: same average useful flow')
    ax.axhline(ref['spool']['material_mass_kg']/1000,color=blue,label='Reference spool')
    ax.axvline(ref['conveyor_over_spool_mass'],ls=':',color=red,label=f'Equal mass: {ref["conveyor_over_spool_mass"]:.1%}')
    ax.set(xlabel='Conveyor productive fraction (assumed)',ylabel='Tether material per arm (tonnes)',title='Window / duty sensitivity · transitions excluded');ax.legend(fontsize=8)
    for ax in axs.flat:ax.grid(alpha=.18)
    fig.suptitle(f'Tether material comparison · {flow:.5f} kg/s per useful arm · {d["matched_release_speed_m_s"]:.2f} m/s release\nBaseline: Zylon, 2.9 GPa allowance; machinery and transient stress excluded',fontsize=12)
    for ext in ['png','svg']:fig.savefig(OUT/f'comparison.{ext}',dpi=180)
    plt.close(fig)
if __name__=='__main__':main()
