"""Explicit repeating jobs, integer common-release windows, support counts."""
from pathlib import Path
import json,math
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from .model import Model, Case
OUT=Path(__file__).parent/'results'

def metrics(h,s,dt):
    net=h+s
    return dict(net_input_utilization=float(net.mean()/net.max()),
      hub_net_utilization=float(h.mean()/np.max(abs(h))),
      hub_handling_utilization=float(np.mean(abs(h))/np.max(abs(h))),
      spool_handling_utilization=float(np.mean(abs(s))/np.max(abs(s))),
      net_min_MW=float((h+s).min()/1e6),net_max_MW=float((h+s).max()/1e6),
      spool_peak_to_peak_over_mean=float(np.ptp(s)/abs(s.mean())),hub_min_MW=float(h.min()/1e6),hub_max_MW=float(h.max()/1e6),hub_mean_MW=float(h.mean()/1e6),
      spool_min_MW=float(s.min()/1e6),spool_max_MW=float(s.max()/1e6),spool_mean_MW=float(s.mean()/1e6),
      net_mean_MW=float((h+s).mean()/1e6),net_peak_to_peak_MW=float(np.ptp(h+s)/1e6),
      hub_peak_to_peak_over_mean=float(np.ptp(h)/h.mean()),net_peak_to_peak_over_mean=float(np.ptp(h+s)/(h+s).mean()),
      hub_energy_J=float(h.sum()*dt),spool_energy_J=float(s.sum()*dt))


def calculate(N,B,plot=False,travel_fraction=None,delivered_kg=2000.,tag=None,in_transit_each=None,minimum_hold_s=300.):
    if in_transit_each is not None:
        assert isinstance(in_transit_each,int) and in_transit_each>0
        assert travel_fraction is None
        travel_fraction=in_transit_each/B
    elif travel_fraction is None:travel_fraction=.4
    tag=tag or f"bank_{N}_pairs"
    m=Model(Case(payload_kg=delivered_kg/B,counterweight_kg=delivered_kg/B,minimum_hold_s=minimum_hold_s));c=m.c;T=c.period_s;D=travel_fraction*T;loadtime=c.loading_s
    cadence=T/B;reuse=N*cadence;horizon=math.lcm(N,B)/B*T
    t=np.arange(24000)*horizon/24000;dt=t[1];h=np.zeros((N,len(t)));sp=h.copy()
    active=np.zeros((N,len(t)),bool);loaded_full=active.copy();jobs=[];releases=[];release_events=[]
    outbound=np.zeros(len(t),int);inbound=outbound.copy()
    for n in range(-2*N,math.ceil(horizon/cadence)+1):
        start=n*cadence;out=start+D+loadtime;end=out+D
        release=math.ceil((end+c.minimum_hold_s)/T-1e-10)*T
        assert release<=start+reuse+1e-7,'Insufficient installed spools to wait for release'
        j=n%N
        for begin,reverse,load in [(start,True,0.),(out,False,c.payload_kg)]:
            q,v,a=m.motion(t,begin,D,reverse);hh,ss,_=m.powers(q,v,a,load)
            h[j]+=hh;sp[j]+=ss
        inbound+=((t+1e-8>=start)&(t+1e-8<start+D)).astype(int)
        outbound+=((t+1e-8>=out)&(t+1e-8<end)).astype(int)
        if -1e-7<=release<=horizon+1e-7:
            release_events.append(dict(time_s=release,pair=j+1,ready_s=end,loaded_hold_s=release-end))
        active[j]|=(t>start)&(t<end)
        loaded_full[j]|=(t>=end)&(t<release)
        if 0<=release<horizon-1e-7:releases.append(round(release/T))
        if end>=0 and start<horizon:jobs.append(dict(pair=j+1,start_s=start,payout_s=out,end_s=end,release_s=release,next_start_s=start+reuse))
    fully=N-active.sum(0)
    assert fully.min()>=1
    assert all(releases.count(k)==B for k in range(round(horizon/T)))
    assert abs(B*c.payload_kg-delivered_kg)<1e-8
    # Event boundaries suffice to certify the minimum, independently of time sampling.
    edges=sorted(set([0.,horizon]+[e for j in jobs for e in [j['start_s'],j['end_s']] if 0<e<horizon]))
    probes=(np.array(edges[:-1])+edges[1:])/2
    certified=min(N-sum(j['start_s']<x<j['end_s'] for j in jobs) for x in probes)
    assert certified==fully.min()
    if in_transit_each is not None:
        # Mid-interval probes avoid floating-point ambiguity at exact handoffs.
        probes_motion=(np.arange(201)+.321)*horizon/201
        for offset in [0.,D+loadtime]:
            counts=sum(((probes_motion>=n*cadence+offset)&(probes_motion<n*cadence+offset+D)).astype(int) for n in range(-2*N,math.ceil(horizon/cadence)+1))
            assert np.all(counts==in_transit_each)
    r=dict(in_transit_each=in_transit_each,minimum_loaded_hold_s=minimum_hold_s,
        outbound_count_mean=float(outbound.mean()),inbound_count_mean=float(inbound.mean()),
        release_events=release_events,installed_pairs=N,tethers_per_side=N,total_tethers=2*N,releases_per_window=B,
        payload_per_tether_kg=c.payload_kg,delivered_kg_per_window=delivered_kg,maximum_payout_m_s=1.875*m.L/D,
        window_s=T,travel_s=D,reload_s=loadtime,cadence_s=cadence,physical_reuse_s=reuse,
        schedule_repeat_s=horizon,minimum_fully_extended_per_side=int(certified),
        maximum_fully_extended_per_side=int(fully.max()),minimum_loaded_fully_extended_per_side=int(loaded_full.sum(0).min()),
        tether_mass_kg=2*N*m.mass,useful_flow_kg_s=B*c.payload_kg/T,
        power=metrics(h.sum(0),sp.sum(0),dt))
    expected=B*horizon/T*(m.metadata()['released_energy_per_pair_J']-m.metadata()['loading_energy_per_pair_J'])
    err=abs((h+sp).sum()*dt/expected-1);assert err<2e-6;r['energy_relative_error']=err
    if plot:
        fig,axs=plt.subplots(4,1,figsize=(11,12 if N>=16 else 10),sharex=True,layout='constrained',gridspec_kw={'height_ratios':[2,2,1,2]})
        for ax,arr,color,label in [(axs[0],h,'#476d86','Hub (MW)'),(axs[1],sp,'#a2673d','Spools (MW)')]:
            for y in arr:ax.plot(t/60,y/1e6,color=color,alpha=.25)
            ax.plot(t/60,arr.sum(0)/1e6,color=color,lw=2,label='Total');ax.set_ylabel(label);ax.legend(fontsize=8);ax.axhline(0,color='.5',lw=.5)
        axs[2].step(t/60,fully,where='post',color='#527e68',label='Fully extended, loaded or empty');axs[2].axhline(1,color='.5',ls=':');axs[2].set_ylabel('Tethers / side');axs[2].legend(fontsize=8)
        for j in jobs:
            for a,b,col in [(j['start_s'],j['payout_s']-loadtime,'#a2673d'),(j['payout_s']-loadtime,j['payout_s'],'#aaa'),(j['payout_s'],j['end_s'],'#476d86'),(j['end_s'],j['release_s'],'#527e68'),(j['release_s'],j['next_start_s'],'#e4e4e4')]:
                left=max(a,0);right=min(b,horizon)
                if right>left:axs[3].broken_barh([(left/60,(right-left)/60)],(j['pair']-.8,.6),facecolors=col)
        for event in release_events:
            axs[3].scatter(event['time_s']/60,event['pair']-.5,marker='D',s=14,color='#8a3150',zorder=6,clip_on=False)
        for k in range(round(horizon/T)+1):
            axs[3].text(k*T/60,N+.1,f'{B} released',ha='center',va='bottom',fontsize=8)
        axs[3].set(ylabel='Pair / tether per side',xlabel='Time (minutes)',yticks=range(1,N+1,max(1,N//8)),ylim=(0,N+.2))
        for ax in axs:
            for k in range(round(horizon/T)+1):ax.axvline(k*T/60,color='.5',ls=':',lw=.8)
            ax.set_xlim(0,horizon/60);ax.grid(alpha=.12)
        fig.suptitle(f'{N} tethers per side · {B} payloads per common release · {certified}+ always extended{f' · transit {in_transit_each}+{in_transit_each}' if in_transit_each is not None else ''}\nBrown: retract · blue: extend · green: ready · pale: empty · diamonds: release',fontsize=12)
        for ext in ['png','svg']:fig.savefig(OUT/f'{tag}.{ext}',dpi=180)
        plt.close(fig)
        np.savez_compressed(OUT/f'{tag}.npz',time_s=t,hub_W=h,spool_W=sp,fully_extended_per_side=fully,outbound_count=outbound,inbound_count=inbound,loaded_ready_count=loaded_full.sum(0))
    return r

def single_pair(m):
    c=m.c;t=np.arange(30000)*c.period_s/30000;one=m.single(t)
    np.savez_compressed(OUT/'cycle_template.npz',time_s=t,**one)
    np.savez_compressed(OUT/'taper_profile.npz',material_coordinate_m=m.s,linear_density_kg_m=m.lam,fiber_area_m2=m.lam/c.density_kg_m3)
    fig,ax=plt.subplots(figsize=(11,5),layout='constrained')
    tt=np.r_[t,t+c.period_s,2*c.period_s]/60
    for key,col,label in [('hub_W','#476d86','Hub'),('spool_W','#a2673d','Spools')]:
        y=one[key];ax.plot(tt,np.r_[y,y,y[0]]/1e6,color=col,label=label)
    for k in range(2):
        for lo,hi,col,label in [(c.loading_s,c.loading_s+c.travel_s,'#dce9e1','Extend'),(c.loading_s+c.travel_s,c.loading_s+c.travel_s+c.minimum_hold_s,'#eee','Hold'),(c.loading_s+c.travel_s+c.minimum_hold_s,c.loading_s+2*c.travel_s+c.minimum_hold_s,'#f0e3d8','Retract')]:
            ax.axvspan((k*c.period_s+lo)/60,(k*c.period_s+hi)/60,color=col,alpha=.65)
            ax.text((k*c.period_s+(lo+hi)/2)/60,.98,label,ha='center',va='top',transform=ax.get_xaxis_transform(),fontsize=9)
    ax.axhline(0,color='.5',lw=.8);ax.set(xlabel='Time (minutes)',ylabel='Signed mechanical power (MW)',title='One payload–counterweight pair · two complete cycles',ylim=(-6,12));ax.legend();ax.grid(alpha=.15)
    for ext in ['png','svg']:fig.savefig(OUT/f'single_pair_power.{ext}',dpi=180)
    plt.close(fig)
    r=metrics(one['hub_W'],one['spool_W'],t[1])
    expected=m.metadata()['released_energy_per_pair_J']-m.metadata()['loading_energy_per_pair_J']
    error=abs((r['hub_energy_J']+r['spool_energy_J'])/expected-1);assert error<2e-6
    fine=Model(nodes=60001).single(t)
    diff=max(np.max(abs(fine[k]-one[k])) for k in ['hub_W','spool_W']);assert diff<2
    return dict(power=r,energy_relative_error=error,inventory_refinement_max_power_change_W=float(diff))

def main():
    OUT.mkdir(exist_ok=True)
    plt.rcParams.update({'font.size':10,'svg.fonttype':'none','axes.spines.top':False,'axes.spines.right':False})
    m=Model();single=single_pair(m)
    rows=[calculate(n,n//2,True,in_transit_each=n//4,minimum_hold_s=0.,tag=f'bank_{n}_reference') for n in [4,8,16,32]]
    reserve=calculate(32,28,True,travel_fraction=.04,tag='bank_32_release_28')
    assert all(abs(r['physical_reuse_s']/r['window_s']-2)<1e-10 for r in rows)
    assert all(abs(r['tether_mass_kg']/rows[0]['tether_mass_kg']-1)<1e-8 for r in rows)
    summary=dict(model=m.metadata(),single_pair=single,sequence=rows,
        reserve_case=reserve,
        schedule_rule='B=N/2; delivered mass=2000 kg/window; payload=2000/B; K_out=K_back=N/4; travel=0.5T; minimum hold=0; reload=300s; reuse=2T')
    (OUT/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    import csv
    with (OUT/'power_utilization.csv').open('w') as f:
        cols=['tethers_per_side','released_per_window','payload_kg','delivered_kg','reuse_windows','travel_min','net_input_utilization_percent','hub_handling_utilization_percent','spool_handling_utilization_percent','net_min_MW','net_max_MW','hub_peak_magnitude_MW','spool_peak_magnitude_MW']
        w=csv.DictWriter(f,fieldnames=cols);w.writeheader()
        for r in rows+[reserve]:
            p=r['power'];w.writerow(dict(tethers_per_side=r['tethers_per_side'],released_per_window=r['releases_per_window'],payload_kg=r['payload_per_tether_kg'],delivered_kg=r['delivered_kg_per_window'],reuse_windows=r['physical_reuse_s']/r['window_s'],travel_min=r['travel_s']/60,
                **{k+'_percent':100*p[k] for k in ['net_input_utilization','hub_handling_utilization','spool_handling_utilization']},
                **{k:p[k] for k in ['net_min_MW','net_max_MW']},
                **{k+'_peak_magnitude_MW':max(abs(p[k+'_min_MW']),abs(p[k+'_max_MW'])) for k in ['hub','spool']}))
    fig,axs=plt.subplots(4,1,figsize=(11,9),sharex=True,sharey=True,layout='constrained')
    for ax,r in zip(axs,rows):
        n=r['tethers_per_side'];d=np.load(OUT/f'bank_{n}_reference.npz');t=d['time_s'];mask=t<2*m.c.period_s
        for y,col,label in [(d['hub_W'].sum(0),'#476d86','Hub'),(d['spool_W'].sum(0),'#a2673d','Spools'),((d['hub_W']+d['spool_W']).sum(0),'#527e68','Net')]:
            ax.plot(t[mask]/60,y[mask]/1e6,color=col,label=label)
        ax.set_title(f"{n} tethers per side · release {r['releases_per_window']} × {r['payload_per_tether_kg']:g} kg · transit {r['in_transit_each']}+{r['in_transit_each']} · utilization {100*r['power']['net_input_utilization']:.1f}%",fontsize=11)
        ax.set_ylabel('MW');ax.grid(alpha=.15);ax.axhline(0,color='.5',lw=.5)
        ax.axvline(m.c.period_s/60,color='.5',ls=':');ax.legend(ncol=3,fontsize=8,loc='upper right')
    axs[-1].set_xlabel('Time (minutes) · identical throughput: 2,000 kg per window · each spool repeats every 2T')
    fig.suptitle('Modular payloads: larger batches and smoother power at fixed delivered mass')
    for ext in ['png','svg']:fig.savefig(OUT/f'bank_reference_sequence.{ext}',dpi=180)
    plt.close(fig)
    transit_study()
    print(json.dumps(rows,indent=2))
def transit_study():
    cases=[]
    for k,hold in [(1,300.),(4,300.),(7,300.),(8,0.)]:
        tag=f'bank_32_transit_{k}'
        row=calculate(32,16,True,in_transit_each=k,minimum_hold_s=hold,tag=tag)
        cases.append(row)
    (OUT/'transit_controls.json').write_text(json.dumps(dict(installed_per_side=32,batch_per_window=16,cases=cases),indent=2)+'\n')
    # Show the slow case in terms of counts and discrete cohort-release events.
    r=cases[3];d=np.load(OUT/'bank_32_transit_8.npz');T=r['window_s'];t=d['time_s']/60
    fig,axs=plt.subplots(3,1,figsize=(11,8),sharex=True,layout='constrained',gridspec_kw={'height_ratios':[1,1,2]})
    axs[0].step(t,d['outbound_count'],where='post',label='Extending',color='#476d86')
    axs[0].step(t,d['inbound_count'],where='post',label='Retracting',color='#a2673d',ls='--')
    axs[0].set(ylabel='In transit / side',ylim=(0,9),title='32 installed · 16 released together · 8 extending + 8 retracting');axs[0].legend()
    axs[1].step(t,d['loaded_ready_count'],where='post',color='#527e68',label='Loaded and ready')
    axs[1].set(ylabel='Ready for release',ylim=(0,18));axs[1].legend()
    # Group physical spool identities by their release cohort for readability.
    cohort={e['pair']:round(e['time_s']/T)%2 for e in r['release_events']}
    order=sorted(cohort,key=lambda j:(cohort[j],j));ypos={j:i+1 for i,j in enumerate(order)}
    for e in r['release_events']:
        x=e['time_s']/60;y=ypos[e['pair']]
        axs[2].plot([max(0,e['ready_s']/60),x],[y,y],color='#527e68',lw=2)
        axs[2].scatter(x,y,color='#8a3150',marker='D',s=23,clip_on=False,zorder=5)
    axs[2].set(ylabel='Physical tether, grouped by cohort',yticks=range(1,33),yticklabels=order,ylim=(0,35),xlabel='Time (minutes); diamonds are simultaneous payload releases')
    axs[2].tick_params(axis='y',labelsize=7)
    for k in range(3):
        x=k*T/60
        axs[2].text(x,33,'16 released',ha='center',color='#8a3150')
        for ax in axs:ax.axvline(x,color='.5',ls=':',lw=.8)
    for ax in axs:ax.set_xlim(0,2*T/60);ax.grid(alpha=.12)
    for ext in ['png','svg']:fig.savefig(OUT/f'cohort_release_16_reference.{ext}',dpi=180)
    plt.close(fig)

if __name__=='__main__':main()
