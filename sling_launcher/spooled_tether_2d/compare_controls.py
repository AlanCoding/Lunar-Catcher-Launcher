"""Compare time-domain responses to three prescribed payout histories."""
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from .model import Config,Tether
from .run import OUT
from .plot import snapshots,save

CASES=[('kevlar_1p5GPa_n32','quintic','Gradual quintic','#527e68'),
       ('kevlar_early_cruise_n32','early_cruise','Early cruise','#a2673d'),
       ('kevlar_front_loaded_n32','front_loaded','Front-loaded','#566a9b')]

def main():
    plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False,'svg.fonttype':'none'})
    fig,axs=plt.subplots(4,1,figsize=(11,12),sharex=True,layout='constrained')
    rows=[]
    for stem,profile,label,color in CASES:
        d=np.load(OUT/f'{stem}.npz');meta=json.loads((OUT/f'{stem}.json').read_text())
        m=Tether(Config(**meta['config']));mask=np.isin(d['phase'],['extend','loaded_hold']);t=d['time_s'][mask]
        speed=np.array([m.motion(v,'extend')[1] if p=='extend' else 0 for v,p in zip(t,d['phase'][mask])])
        xy=d['xy_m'][mask,-1];v=d['material_velocity_m_s'][mask,-1]
        # material_velocity is relative to the rotating frame. Add hub omega.
        omega=(xy[:,0]*v[:,1]-xy[:,1]*v[:,0])/np.sum(xy**2,axis=1)+m.w
        angle=d['tip_angle_deg'][mask];stress=d['stress_Pa'][mask].max(axis=1)/1e9
        axs[0].plot(t/60,speed,color=color,label=label)
        axs[1].plot(t/60,angle,color=color,label=label)
        axs[1].fill_between(t/60,d['angle_min_deg'][mask],d['angle_max_deg'][mask],color=color,alpha=.14)
        axs[2].plot(t/60,omega/m.w,color=color,label=label)
        axs[3].plot(t/60,stress,color=color,label=label)
        e=d['phase'][mask]=='extend';k=np.argmin(angle[e]);te=t[e]
        solver=meta['solver'][0]
        rows.append(dict(profile=profile,minimum_tip_angle_deg=float(angle[e][k]),minimum_time_s=float(te[k]),minimum_is_interior=bool(0<k<len(te)-1),peak_payout_m_s=float(speed.max()),payout_at_60_s_m_s=float(m.motion(60,'extend')[1]),peak_extension_stress_GPa=solver['accepted_step_peak_stress_Pa']/1e9,extension_completed=solver['completed'],end_extension_tip_angle_deg=float(angle[e][-1]),min_tip_omega_over_hub=float(omega[e].min()/m.w),max_tip_omega_over_hub=float(omega[e].max()/m.w)))
        if profile!='quintic':snapshots(d,meta,stem,'extension')
    for ax in axs:
        ax.grid(alpha=.2);ax.axvline(m.c.travel_s/60,color='.6',ls=':',lw=1)
    axs[0].legend(ncol=3);axs[0].set_ylabel('Payout speed (m/s)')
    axs[1].set_ylabel('Tip angle / cable span (°)')
    axs[2].set_ylabel('Tip angular speed / hub speed');axs[2].axhline(1,color='.6',lw=.8)
    axs[3].set(ylabel='Peak axial stress (GPa)',xlabel='Time (minutes); dotted line starts loaded hold')
    fig.suptitle('Time-domain payout comparison · 1 t payload + 7.31 t tapered Kevlar\nDistributed cable inertia and tip inertia retained; same duration and final length')
    save(fig,'payout_control_comparison')
    (OUT/'payout_control_comparison.json').write_text(json.dumps(rows,indent=2)+'\n')
    print(json.dumps(rows,indent=2))
if __name__=='__main__':main()
