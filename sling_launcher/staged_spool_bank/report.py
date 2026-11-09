"""Save reusable power histories, phase sums and a common-release schedule."""
from pathlib import Path
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from .model import Model
OUT=Path(__file__).parent/'results'

def metrics(h,s,dt):
    return dict(hub_min_MW=float(h.min()/1e6),hub_max_MW=float(h.max()/1e6),hub_mean_MW=float(h.mean()/1e6),
      spool_min_MW=float(s.min()/1e6),spool_max_MW=float(s.max()/1e6),spool_mean_MW=float(s.mean()/1e6),
      net_mean_MW=float((h+s).mean()/1e6),net_peak_to_peak_MW=float(np.ptp(h+s)/1e6),
      hub_peak_to_peak_over_mean=float(np.ptp(h)/h.mean()),net_peak_to_peak_over_mean=float(np.ptp(h+s)/(h+s).mean()),
      hub_energy_J=float(h.sum()*dt),spool_energy_J=float(s.sum()*dt))

def main():
    OUT.mkdir(exist_ok=True);m=Model();c=m.c;n=30000;t=np.arange(n)*c.period_s/n;dt=c.period_s/n
    one=m.single(t)
    shifted=[m.single(t-j*c.period_s/c.count) for j in range(c.count)]
    grouped=[m.synchronized(t,j) for j in range(c.count)]
    hs=np.array([r['hub_W'] for r in shifted]);ss=np.array([r['spool_W'] for r in shifted])
    hg=np.array([r['hub_W'] for r in grouped]);sg=np.array([r['spool_W'] for r in grouped])
    np.savez_compressed(OUT/'taper_profile.npz',material_coordinate_m=m.s,linear_density_kg_m=m.lam,fiber_area_m2=m.lam/c.density_kg_m3)
    np.savez_compressed(OUT/'cycle_template.npz',time_s=t,**one)
    np.savez_compressed(OUT/'bank_histories.npz',time_s=t,staggered_hub_W=hs,staggered_spool_W=ss,synchronized_hub_W=hg,synchronized_spool_W=sg,
                        synchronized_q_m=np.array([r['q_m'] for r in grouped]))
    summary=m.metadata();summary['single']=metrics(one['hub_W'],one['spool_W'],dt)
    summary['evenly_staggered']=metrics(hs.sum(0),ss.sum(0),dt);summary['synchronized_release']=metrics(hg.sum(0),sg.sum(0),dt)
    summary['stagger_s']=c.period_s/c.count
    summary['synchronized_schedule']=[{k:float(r[k]) for k in ['retract_start_s','payout_start_s','loaded_hold_s']} for r in grouped]
    # Closed-cycle kinetic-energy accounting, including loading/release events.
    expected=summary['released_energy_per_pair_J']-summary['loading_energy_per_pair_J']
    errors={}
    for key,number in [('single',1),('evenly_staggered',c.count),('synchronized_release',c.count)]:
        r=summary[key];err=abs((r['hub_energy_J']+r['spool_energy_J'])/(number*expected)-1)
        assert err<2e-6;errors[key]=err
    assert abs(m.mass/c.payload_kg-3)<1e-7
    refined=Model(nodes=60001).single(t)
    diff=max(np.max(abs(refined[k]-one[k])) for k in ['hub_W','spool_W'])
    assert diff<2.
    # All bank members are fully extended and stationary just before release.
    for j in range(c.count):
        x=m.synchronized(np.array([c.period_s-1e-5]),j)
        assert abs(x['q_m'][0]-m.L)<1e-6 and abs(x['qdot_m_s'][0])<1e-8
    summary['validation']=dict(cycle_energy_relative_errors=errors,inventory_refinement_max_power_change_W=float(diff),
                               common_release_all_fully_extended=True)
    (OUT/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    plt.rcParams.update({'font.size':11,'axes.spines.top':False,'axes.spines.right':False,'svg.fonttype':'none'})
    tt=np.r_[t,t+c.period_s,c.period_s*2]/60
    def twice(y):return np.r_[y,y,y[0]]
    def save(fig,name):
        for ext in ['png','svg']:fig.savefig(OUT/f'{name}.{ext}',dpi=200)
        plt.close(fig)
    fig,ax=plt.subplots(figsize=(11,5),layout='constrained')
    ax.plot(tt,twice(one['hub_W'])/1e6,color='#476d86',label='Hub: positive drives rotation')
    ax.plot(tt,twice(one['spool_W'])/1e6,color='#a2673d',label='Spools: negative regenerates')
    for cycle in [0,1]:
        offset=cycle*c.period_s
        for lo,hi,color,label in [(c.loading_s,c.loading_s+c.travel_s,'#dce9e1','Extend'),(c.loading_s+c.travel_s,c.loading_s+c.travel_s+c.minimum_hold_s,'#eeeeee','Hold'),(c.loading_s+c.travel_s+c.minimum_hold_s,c.loading_s+2*c.travel_s+c.minimum_hold_s,'#f0e3d8','Retract')]:
            ax.axvspan((offset+lo)/60,(offset+hi)/60,color=color,alpha=.65)
            ax.text((offset+(lo+hi)/2)/60,.98,label,va='top',transform=ax.get_xaxis_transform(),ha='center',fontsize=9)
    ax.set_ylim(-11.5,24);ax.axhline(0,color='.5',lw=.8);ax.set(xlabel='Time (minutes)',ylabel='Signed mechanical power (MW)',title='One payload–counterweight pair · two repeated cycles');ax.legend(loc='lower right');ax.grid(alpha=.15)
    save(fig,'single_pair_power')
    for name,hh,sss,title in [('staggered_bank_power',hs,ss,'15 identical cycles, shifted by exactly T/15 · releases also staggered'),('synchronized_bank_power',hg,sg,'15 pairs held for a common release · staggered empty return and loaded extension')]:
        fig,axes=plt.subplots(3,1,figsize=(11,8),sharex=True,layout='constrained')
        for ax,arr,color,label in [(axes[0],hh,'#476d86','Hub power'),(axes[1],sss,'#a2673d','Spool power')]:
            for y in arr:ax.plot(tt,twice(y)/1e6,color=color,alpha=.14,lw=.7)
            ax.plot(tt,twice(arr.sum(0))/1e6,color=color,lw=2,label='Sum of 15 pairs')
            ax.set_ylabel(label+' (MW)');ax.legend(loc='upper right',fontsize=8)
        axes[2].plot(tt,twice(hh.sum(0)+sss.sum(0))/1e6,color='#527e68',label='Hub + spool: ideal net shaft power')
        axes[2].set_ylabel('Net power (MW)');axes[2].legend(fontsize=8)
        for ax in axes:
            ax.axhline(0,color='.5',lw=.8);ax.grid(alpha=.15)
            for edge in [c.period_s/60,2*c.period_s/60]:ax.axvline(edge,color='.4',ls=':',lw=.8)
        axes[-1].set_xlabel('Time (minutes)');fig.suptitle(title,fontsize=12);save(fig,name)
    fig,ax=plt.subplots(figsize=(11,5),layout='constrained')
    for j,r in enumerate(grouped):
        start=r['retract_start_s'];out=r['payout_start_s'];end=out+c.travel_s
        for lo,hi,col in [(0,start,'#eeeeee'),(start,start+c.travel_s,'#a2673d'),(start+c.travel_s,out,'#b4b4b4'),(out,end,'#476d86'),(end,c.period_s,'#527e68')]:
            ax.broken_barh([(lo/60,(hi-lo)/60)],(j+.1,.8),facecolors=col)
    from matplotlib.patches import Patch
    ax.legend(handles=[Patch(color=x,label=y) for x,y in [('#eeeeee','Empty, extended wait'),('#a2673d','Retract'),('#b4b4b4','Reload'),('#476d86','Extend loaded'),('#527e68','Hold loaded')]],loc='upper center',ncol=5,fontsize=8,bbox_to_anchor=(.5,1.02))
    ax.axvline(c.period_s/60,color='#333333',ls='--');ax.set(xlabel='Time after previous common release (minutes)',ylabel='Payload–counterweight pair',yticks=np.arange(c.count)+.5,yticklabels=np.arange(1,c.count+1));fig.suptitle('All pairs ready at the next release boundary',fontsize=13);save(fig,'staged_schedule')
    print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
