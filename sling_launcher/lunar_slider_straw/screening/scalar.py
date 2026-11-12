"""Straight radial, constant line-speed scalar screen; no elastic shape solution."""
from pathlib import Path
import json,csv
import numpy as np
from scipy.integrate import quad
from scipy.optimize import brentq
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from ...staged_spool_bank.model import Model,Case
OUT=Path(__file__).parent/'results'
N=16

def states(m,B,K,t):
    T=m.c.period_s;delta=T/B;D=K*delta;reuse=N*delta;u=m.L/D
    phases=(np.asarray(t)[None,:]-np.arange(N)[:,None]*delta)%reuse
    # Release assignment changes when reuse is a fractional window. Use absolute jobs.
    out=np.zeros(phases.shape,bool);back=out.copy();full=out.copy();loadedfull=out.copy();q=np.zeros(phases.shape)
    for n in range(-2*N,int(np.ceil(np.max(t)/delta))+1):
        start=n*delta;begin=start+D+300;end=begin+D;release=np.ceil(end/T-1e-10)*T
        assert release<=start+reuse+1e-7
        j=n%N;sel=(t>=start)&(t<start+reuse)
        qb=np.clip(m.L-u*(t-start),0,m.L);qo=np.clip(u*(t-begin),0,m.L)
        q[j,sel]=np.where(t[sel]<begin,qb[sel],qo[sel])
        back[j]|=(t>=start)&(t<start+D)
        out[j]|=(t>=begin)&(t<end)
        full[j]|=(t>=end)&(t<start+reuse)
        loadedfull[j]|=(t>=end)&(t<release)
    return q,out,back,full,loadedfull,u

def run(B,K,ratio=3.,name=None):
    name=name or f'b{B}_k{K}'
    m=Model(Case(payload_kg=250,counterweight_kg=250,tether_to_payload_mass=ratio,minimum_hold_s=0))
    T=m.c.period_s;delta=T/B;D=K*delta;t=(np.arange(12000)+.314159)*T/12000
    q,out,back,full,loadedfull,u=states(m,B,K,t)
    assert np.all(out.sum(0)==K) and np.all(back.sum(0)==K)
    deployed=m.mass-np.interp(m.L-q,m.s,m.mom[0])
    Fout=2*m.w*u*np.sum((deployed+250)*out,axis=0)
    Fin=2*m.w*u*np.sum(deployed*back,axis=0)
    h=np.zeros(len(t));s=h.copy();gen=h.copy();ret=h.copy();gencable=h.copy()
    for j in range(N):
        for active,v,load in [(out[j],u,250),(back[j],-u,0)]:
            hh,ss,_=m.powers(q[j],v*np.ones(len(t)),np.zeros(len(t)),load)
            h+=np.where(active,hh,0);s+=np.where(active,ss,0)
            if load:
                gen+=np.where(active,-ss,0)
                _,sc,_=m.powers(q[j],v*np.ones(len(t)),np.zeros(len(t)),0)
                gencable+=np.where(active,-sc,0)
            else:ret+=np.where(active,ss,0)
    mean=lambda x:float(np.mean(x));maxi=lambda x:float(np.max(x))
    # Both sides: sums of normal magnitudes; μ multiplies this coefficient.
    friction_coeff=2*u*(Fout+Fin)
    mdot=B*250/T;expected=mdot*((m.w*m.R)**2-(m.w*m.a)**2)
    assert abs(mean(h+s)/expected-1)<3e-4
    residual_expected=2*m.w*250*m.L*B/T
    assert abs(mean(Fout-Fin)/residual_expected-1)<3e-4
    assert abs(mean(gencable)/mean(ret)-1)<3e-4
    # Straw duplicates one moving taper per side, but has no endpoint payload.
    x=m.s;r=m.a+x;guideT=m.w**2*(m.a*(m.mom[0][-1]-m.mom[0])+m.mom[1][-1]-m.mom[1])
    area=m.lam/m.c.density_kg_m3;guide_stress=guideT/area
    rootQ=Fout-Fin;rootstress=np.hypot(guideT[0],rootQ)/area[0]
    summary=dict(validation=dict(net_energy_relative_error=abs(mean(h+s)/expected-1),cable_cycle_work_relative_error=abs(mean(gencable)/mean(ret)-1),mean_residual_force_relative_error=abs(mean(Fout-Fin)/residual_expected-1),constant_transit_counts=True),name=name,installed_per_side=N,batch=B,transit_each=K,payload_kg=250,
        period_s=T,travel_s=D,line_speed_m_s=u,opposing_slip_m_s=2*u,delivered_kg_per_window=B*250,
        delivered_kg_s=mdot,tether_per_arm_kg=m.mass,straw_per_side_kg=m.mass,
        moving_tethers_kg=2*N*m.mass,straws_kg=2*m.mass,total_fiber_kg=2*(N+1)*m.mass,
        fiber_mass_over_delivered_rate_s=2*(N+1)*m.mass/mdot,working_stress_GPa=m.kappa*m.c.density_kg_m3/1e9,
        outward_reaction_mean_N=mean(Fout),outward_reaction_max_N=maxi(Fout),inward_reaction_mean_N=mean(Fin),inward_reaction_max_N=maxi(Fin),
        residual_against_spin_mean_N=mean(rootQ),residual_against_spin_abs_max_N=maxi(abs(rootQ)),payload_contact_each_N=2*m.w*u*250,
        friction_both_sides_W_per_mu=mean(friction_coeff),friction_peak_W_per_mu=maxi(friction_coeff),
        friction_at_mu_0p1_fraction_of_ideal_net=mean(friction_coeff)*.1/expected,
        hub_mean_W=mean(h),spool_mean_W=mean(s),net_mean_W=mean(h+s),
        payout_generated_mean_W=mean(gen),return_demand_mean_W=mean(ret),
        cable_only_generated_mean_W=mean(gencable),
        direct_return_coverage_fraction=mean(np.minimum(gen,ret))/mean(ret),
        cable_only_direct_coverage_fraction=mean(np.minimum(gencable,ret))/mean(ret),
        direct_transfer_mean_W=mean(np.minimum(gen,ret)),
        guide_root_self_tension_N=float(guideT[0]),guide_max_self_stress_GPa=float(guide_stress.max()/1e9),
        guide_root_resultant_stress_max_GPa=maxi(rootstress)/1e9,
        guide_root_equivalent_solid_fiber_diameter_mm=float(np.sqrt(4*area[0]/np.pi)*1000),
        minimum_fully_extended_per_side=int(full.sum(0).min()),
        endpoint_radial_kinetic_energy_stop_per_pair_J=(m.mass+250)*u*u,
        ideal_net_energy_per_pair_J=250*((m.w*m.R)**2-(m.w*m.a)**2))
    np.savez_compressed(OUT/f'{name}.npz',time_s=t,hub_W=h,spool_W=s,payout_generated_W=gen,return_demand_W=ret,cable_generated_W=gencable,
        normal_out_per_side_N=Fout,normal_in_per_side_N=Fin,friction_W_per_mu=friction_coeff,radius_m=r,guide_axial_tension_N=guideT,guide_self_stress_Pa=guide_stress)
    if B==8 and K==4 and ratio==3: profiles(m,B,K,summary)
    return summary

def profiles(m,B,K,summary):
    T=m.c.period_s;delta=T/B;u=m.L/(K*delta);times=np.array([.05*delta,300-1/u,T-1e-3,T+1e-3])
    q,out,back,full,loaded,u=states(m,B,K,times)
    edges=np.linspace(m.a,m.R,1001);r=(edges[1:]+edges[:-1])/2;dr=edges[1]-edges[0]
    plots=[];records=[]
    for it,t in enumerate(times):
        fout=np.zeros(len(r));fin=fout.copy();payload_positions=[]
        for j in range(N):
            if not(out[j,it] or back[j,it]):continue
            length=q[j,it];material=m.L-length+r-m.a
            density=np.where(r<m.a+length,np.interp(material,m.s,m.lam),0.)
            if out[j,it]:
                fout+=2*m.w*u*density
                idx=min(len(r)-1,max(0,int(length/dr)));fout[idx]+=2*m.w*u*250/dr
                payload_positions.append(float(m.a+length))
            else:fin+=2*m.w*u*density
        residual=fin-fout # force ON the straw; positive is with spin.
        Q=np.cumsum(residual[::-1])[::-1]*dr
        x=r-m.a
        axial=m.w**2*(m.a*(m.mom[0][-1]-np.interp(x,m.s,m.mom[0]))+m.mom[1][-1]-np.interp(x,m.s,m.mom[1]))
        # Optimistic parallel sharing by fully extended tethers only.
        supported=(1+full[:,it].sum())*axial+loaded[:,it].sum()*250*m.w**2*m.R
        nearest=max(payload_positions);xx=nearest-m.a
        tipT=m.w**2*(m.a*(m.mom[0][-1]-np.interp(xx,m.s,m.mom[0]))+m.mom[1][-1]-np.interp(xx,m.s,m.mom[1]))
        records.append(dict(nearest_payload_distance_from_tip_m=m.R-nearest,
            guide_axial_tension_at_nearest_payload_N=float(tipT),
            payload_normal_over_local_guide_tension=float(2*m.w*u*250/tipT),
            phase_label=["Early in window","Payload one metre from tip","Just before common release","Just after release / return start"][it],time_s=float(t),fully_extended=int(full[:,it].sum()),loaded_fully_extended=int(loaded[:,it].sum()),
            payload_radii_m=payload_positions,root_residual_N=float(Q[0]),
            guide_Q_over_T_at_90pct=float(np.interp(m.a+.9*m.L,r,abs(Q)/axial)),
            shared_Q_over_T_at_90pct=float(np.interp(m.a+.9*m.L,r,abs(Q)/supported))))
        plots.append((fout,fin,Q,axial,supported))
    (OUT/'force_snapshots.json').write_text(json.dumps(records,indent=2)+'\n')
    fig,axs=plt.subplots(2,2,figsize=(12,7),layout='constrained')
    for ax,record,(fo,fi,Q,axial,shared) in zip(axs.flat,records,plots):
        ax.plot(r/1000,fo,label='Outbound on straw: against spin',color='#a2673d')
        ax.plot(r/1000,-fi,label='Return on straw: with spin',color='#476d86')
        ax.axhline(0,color='.5',lw=.7);ax.set(xlabel='Radius (km)',ylabel='Normal load density (N/m)',title=f"{record['phase_label']} · {record['loaded_fully_extended']} held loads")
        ax.grid(alpha=.15)
    axs[0,0].legend(fontsize=8);fig.suptitle('Local contact demand · positive plotted against spin; payloads spread over one 5.7 m bin')
    save(fig,'contact_profiles')
    fig,axs=plt.subplots(1,2,figsize=(12,4),layout='constrained')
    for rec,(_,_,Q,axial,shared) in zip(records,plots):
        label=f"t={rec['time_s']/60:.2f} min; {rec['loaded_fully_extended']} held loads"
        axs[0].plot(r/1000,abs(Q)/axial,label=label)
        axs[1].plot(r/1000,abs(Q)/shared,label=label)
    for ax,title in zip(axs,['Guide alone','Optimistic sharing with fully extended cables']):
        ax.set(xlabel='Radius (km)',ylabel='Distal transverse demand / axial tension',yscale='log',title=title);ax.grid(alpha=.2);ax.legend(fontsize=7)
    fig.suptitle('Force-direction screen · load ratios for the future shape solution')
    save(fig,'guide_force_ratio')
    # Minimal hand-drawn vector diagrams; guide shape intentionally straight.
    fig,axs=plt.subplots(2,2,figsize=(12,7),layout='constrained')
    for ax,rec,(fo,fi,Q,_,_) in zip(axs.flat,records,plots):
        ax.plot([0,1],[0,0],color='#607765',lw=7,alpha=.5)
        for xpos in [.18,.43,.68,.9]:
            idx=int(xpos*(len(r)-1));down=fo[idx]*dr;up=fi[idx]*dr
            if down>1e-9:ax.annotate('',xy=(xpos,-.25),xytext=(xpos,0),arrowprops=dict(arrowstyle='->',color='#a2673d',lw=1.5))
            if up>1e-9:ax.annotate('',xy=(xpos,.25),xytext=(xpos,0),arrowprops=dict(arrowstyle='->',color='#476d86',lw=1.5))
        for radius in rec['payload_radii_m']:
            xpos=(radius-m.a)/m.L;ax.scatter(xpos,0,color='#a2673d',s=35,zorder=5)
            ax.annotate('',xy=(xpos,-.5),xytext=(xpos,-.03),arrowprops=dict(arrowstyle='->',color='#a2673d',lw=2))
        ax.text(0,.45,'↑ with spin',fontsize=9);ax.text(0,-.65,'↓ against spin',fontsize=9)
        ax.text(0,.05,'Hub',ha='right');ax.text(1,.05,'Tip',ha='left')
        ax.text(.5,.72,f"{rec['phase_label']} · {rec['fully_extended']} extended / {rec['loaded_fully_extended']} loaded",ha='center',fontsize=10)
        ax.text(.5,-.85,f"Residual on straw: {abs(rec['root_residual_N'])/1000:.2f} kN "+('against spin' if rec['root_residual_N']<0 else 'with spin'),ha='center',fontsize=9)
        ax.set(xlim=(-.08,1.08),ylim=(-1,1));ax.axis('off')
    fig.suptitle('Forces on the straw · blue: inward-moving cable; brown: outward cable and payloads\nArrows indicate direction; positions schematic and arrow lengths unscaled',fontsize=12)
    save(fig,'force_diagrams')

def save(fig,name):
    for ext in ['png','svg']:fig.savefig(OUT/f'{name}.{ext}',dpi=180)
    plt.close(fig)

def main():
    OUT.mkdir(exist_ok=True);plt.rcParams.update({'font.size':10,'svg.fonttype':'none','axes.spines.top':False,'axes.spines.right':False})
    rows=[run(8,k) for k in [1,2,3,4]]
    throughput=[rows[-1],run(12,2),run(14,1)]
    # Re-size moving taper at 1.5 GPa while keeping geometry, payload and timing.
    m=Model(Case(payload_kg=250,counterweight_kg=250));k=1.5e9/1450
    ratio=m.w**2*m.R/k*quad(lambda r:np.exp(m.w**2*(m.R*m.R-r*r)/(2*k)),m.a,m.R)[0]
    conservative=run(8,4,ratio=ratio,name='b8_k4_1p5GPa')
    data=dict(fixed_delivery=rows,throughput_trade=throughput,lower_stress=conservative,
        friction_coefficients=[.02,.05,.1,.2],scope='two sides; one 750 kg guide per side in 3:1 reference; prescribed straight radial cruise')
    (OUT/'summary.json').write_text(json.dumps(data,indent=2)+'\n')
    with (OUT/'cases.csv').open('w') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows+throughput[1:]+[conservative])
    ref=np.load(OUT/'b8_k4.npz');t=ref['time_s']/60
    fig,axs=plt.subplots(3,1,figsize=(11,9),sharex=True,layout='constrained')
    axs[0].plot(t,ref['normal_out_per_side_N']/1000,label='Outbound reaction magnitude',color='#a2673d')
    axs[0].plot(t,ref['normal_in_per_side_N']/1000,label='Return reaction magnitude',color='#476d86')
    axs[0].plot(t,(ref['normal_out_per_side_N']-ref['normal_in_per_side_N'])/1000,label='Residual against spin',color='#527e68');axs[0].set_ylabel('Normal load / side (kN)')
    for key,col,label in [('payout_generated_W','#a2673d','Payout generation'),('return_demand_W','#476d86','Return demand')]:axs[1].plot(t,ref[key]/1e6,color=col,label=label)
    axs[1].set_ylabel('Common-shaft powers (MW)')
    for mu in [.02,.1,.2]:axs[2].plot(t,mu*ref['friction_W_per_mu']/1000,label=f'μ={mu:g}')
    axs[2].set(ylabel='Sliding heat, both sides (kW)',xlabel='Time after common release (minutes)')
    for ax in axs:ax.legend(fontsize=8);ax.grid(alpha=.15)
    fig.suptitle('16 tethers per side · release 8 × 250 kg · 4 out + 4 back · constant line speed')
    save(fig,'loads_recovery_friction')
    fig,axs=plt.subplots(1,2,figsize=(11,4),layout='constrained')
    for mu in [.02,.05,.1,.2]:axs[0].plot([r['line_speed_m_s'] for r in rows],[mu*r['friction_both_sides_W_per_mu']/1000 for r in rows],'-o',label=f'μ={mu:g}')
    axs[0].set(xlabel='Constant line speed (m/s)',ylabel='Mean sliding heat, both sides (kW)',title='Fixed delivery: faster travel raises sliding losses');axs[0].legend()
    axs[1].plot([r['line_speed_m_s'] for r in throughput],[r['fiber_mass_over_delivered_rate_s']/3600 for r in throughput],'-o',color='#527e68')
    for r in throughput:axs[1].annotate(f"B={r['batch']}, K={r['transit_each']}",(r['line_speed_m_s'],r['fiber_mass_over_delivered_rate_s']/3600),xytext=(0,8),textcoords='offset points',fontsize=8)
    axs[1].set(xlabel='Constant line speed (m/s)',ylabel='Fiber mass / delivered rate (hours)',title='Larger batches improve material productivity')
    for ax in axs:ax.grid(alpha=.15)
    save(fig,'speed_trade')
    print(json.dumps(data,indent=2))
if __name__=='__main__':main()
