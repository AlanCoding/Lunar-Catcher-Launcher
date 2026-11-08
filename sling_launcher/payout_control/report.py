"""Reproduce four payout experiments, plots and animated GIFs."""
from pathlib import Path
from dataclasses import asdict
import json,csv
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation,PillowWriter
from matplotlib.patches import Circle
from .model import Config,scenarios,run,sample,COLUMNS,anchor
ROOT=Path(__file__).parent;OUT=ROOT/'results'
IX={k:i for i,k in enumerate(COLUMNS)}
NAMES=dict(constant='Constant 5 m/s',slow_then_fast='Slow → fast (2 → 8 m/s)',fast_then_slow='Fast → slow (8 → 2 m/s)',too_fast='Too fast: 40 m/s')
COLORS=dict(constant='#466e84',slow_then_fast='#557c6a',fast_then_slow='#9a683d',too_fast='#ad4538')
plt.rcParams.update({'svg.fonttype':'none','font.family':'DejaVu Sans','axes.spines.top':False,'axes.spines.right':False})

def metric(r,a,name):
    c=r['config'];p=r['profile'];finish=sample(r,[p.duration])[0]
    k=a[:,IX['kinetic_j']];balance=k-k[0]-a[:,18]-a[:,19]-a[:,21]+a[:,20]
    H=a[:,16];hbal=H-H[0]-a[:,23]-a[:,22]
    slack_time=sum(s['end']-s['start'] for s in r['segments'] if s['mode']=='slack')
    return dict(name=name,config=asdict(c),omega_rad_s=c.omega,profile=p.metadata(),end_time_s=r['end'],
        payout_end_radius_m=finish[10],payout_end_speed_m_s=float(np.hypot(finish[3],finish[4])),
        payout_end_angular_speed_ratio=finish[13]/c.omega,payout_end_lag_deg=float(np.degrees(finish[28])),
        payout_end_radial_speed_m_s=finish[12],payout_end_slack_m=finish[25],
        after_hold_speed_m_s=float(np.hypot(a[-1,3],a[-1,4])),peak_regular_tension_n=float(a[:,14].max()),
        peak_abs_regular_torque_nm=float(np.abs(a[:,15]).max()),slack_time_s=slack_time,
        sampled_max_slack_m=float(a[:,25].max()),energy_relative_residual=float(abs(balance).max()/max(k.max(),1)),
        angular_momentum_relative_residual=float(abs(hbal).max()/max(abs(H).max(),1)),events=r['events'])

def animate(r,name):
    c=r['config'];duration=r['end'];times=np.linspace(0,duration,180);a=sample(r,times)
    fine=sample(r,np.linspace(0,duration,4801))
    fig=plt.figure(figsize=(11,6.5),facecolor='white');gs=fig.add_gridspec(2,2,width_ratios=[1.25,1],left=.07,right=.97,top=.84,bottom=.22,hspace=.35,wspace=.3)
    ax=fig.add_subplot(gs[:,0]);ax.set_aspect('equal');ax.set_xlabel('East / x (km)');ax.set_ylabel('North / y (km)')
    ax.set_title('Inertial view · auto zoom',fontsize=11)
    ax.add_patch(Circle((0,0),c.anchor_radius_m/1000,fill=False,ec='#c3c8c0',lw=1.5))
    ax.scatter([0],[0],s=16,c='black',zorder=5)
    tether,=ax.plot([],[],lw=1.8,color=COLORS[name]);trail,=ax.plot([],[],lw=.8,color='#b1bdc0')
    mass,=ax.plot([],[],'o',ms=8,color=COLORS[name]);pin,=ax.plot([],[],'s',ms=5,color='#303c3c')
    detail=ax.inset_axes([.64,.025,.34,.34]);detail.set_aspect('equal')
    detail.set_xlim(-120,160);detail.set_ylim(-140,140)
    detail.add_patch(Circle((0,0),c.anchor_radius_m,fill=False,ec='#c3c8c0',lw=1))
    detail.scatter([0],[0],s=10,c='black');detail.scatter([c.anchor_radius_m],[0],s=14,c='#303c3c',marker='s')
    detail.axhline(0,c='#d5d5d5',lw=.6);detail.set_xticks([]);detail.set_yticks([])
    detail.set_title('Hub-frame detail',fontsize=7)
    local_line,=detail.plot([],[],color=COLORS[name],lw=1.3)
    state=ax.text(.02,.97,'',transform=ax.transAxes,va='top',fontsize=10,bbox=dict(fc='white',alpha=.85,ec='none'))
    axr=fig.add_subplot(gs[0,1]);axw=fig.add_subplot(gs[1,1])
    axr.plot(fine[:,0],fine[:,10]/1000,color=COLORS[name],label='Payload radius')
    axr.plot(fine[:,0],fine[:,7]/1000,'--',color='#80877f',label='Paid length (from attachment)')
    axr.set_ylabel('Distance (km)');axr.legend(fontsize=7,loc='upper left');axr.set_xlim(0,duration)
    axw.plot(fine[:,0],fine[:,13]/c.omega,color=COLORS[name]);axw.axhline(1,color='#777',ls=':',lw=1)
    axw.set(xlim=(0,duration),ylabel='Payload Ω / attachment Ω',xlabel='Physical time (s)')
    cursors=[axr.axvline(0,c='black',lw=1),axw.axvline(0,c='black',lw=1)]
    for seg in r['segments']:
        if seg['mode']=='slack':
            for axi in [axr,axw]:axi.axvspan(seg['start'],seg['end'],color='#e9c482',alpha=.25)
    fig.suptitle(NAMES[name],fontsize=17,y=.97)
    fig.text(.5,.90,'Ideal point mass · 76.79 m moving attachment · 50 mph track speed · no cable mass or elasticity',ha='center',fontsize=9)
    info=fig.text(.07,.105,'',fontsize=10)
    fig.text(.07,.055,'Solid = taut   ·   dotted = slack separation (not cable shape)   ·   shading = zero-tension flight',fontsize=9)
    fig.text(.07,.025,f'Time compressed: {duration:.1f} s in {180/12:.0f} s. Playback is not real-time; displayed clock is physical time.',fontsize=9,color='#666')
    def frame(i):
        row=a[i];t=row[0];x,y=row[1:3]/1000;px,py=row[5:7]/1000
        window=max(.3,1.15*row[10]/1000);ax.set_xlim(-window,window);ax.set_ylim(-window,window)
        mask=(fine[:,0]<=t)&(fine[:,0]>=t-2*np.pi/c.omega)
        trail.set_data(fine[mask,1]/1000,fine[mask,2]/1000)
        tether.set_data([px,x],[py,y]);tether.set_linestyle('-' if row[24] else ':')
        mass.set_data([x],[y]);pin.set_data([px],[py])
        angle=c.omega*t;co,si=np.cos(angle),np.sin(angle)
        local_line.set_data([c.anchor_radius_m,1000*(co*x+si*y)],[0,1000*(-si*x+co*y)])
        local_line.set_linestyle('-' if row[24] else ':')
        state.set_text(f't = {t:7.1f} s\n'+('TAUT' if row[24] else 'SLACK · T = 0')+f'\nView ±{window:.2f} km')
        for cursor in cursors:cursor.set_xdata([t,t])
        info.set_text(f'Payout {row[8]:5.1f} m/s    T = {row[14]/1000:7.1f} kN    torque = {row[15]/1e6:+6.2f} MN m    slack = {row[25]:6.1f} m')
        return tether,trail,mass,pin,state,info,*cursors
    frame(0);ani=FuncAnimation(fig,frame,frames=len(times),interval=1000/12,blit=False)
    ani.save(OUT/f'{name}.gif',writer=PillowWriter(fps=12),dpi=85);frame(113);fig.savefig(OUT/f'{name}_preview.png',dpi=150);plt.close(fig)


def compare(histories):
    fig,axs=plt.subplots(2,3,figsize=(15,8),layout='constrained')
    for name,a in histories.items():
        t=a[:,0];kw=dict(color=COLORS[name],label=NAMES[name])
        axs[0,0].plot(t,a[:,8],**kw);axs[0,1].plot(t,a[:,10]/1000,**kw);axs[0,2].plot(t,a[:,13]/Config().omega,**kw)
        axs[1,0].plot(t,a[:,14]/1000,**kw);axs[1,1].plot(t,a[:,25],**kw);axs[1,2].plot(a[:,10]/1000,a[:,15]/1e6,**kw)
    for ax,title,ylabel in zip(axs.flat,['Payout controls','Payload radius','Angular speed tracking','Tension (impulses excluded)','Slack length','Torque versus radius'],['m/s','km','Ω payload / Ω attachment','kN','m','MN m']):
        ax.set_title(title);ax.set_ylabel(ylabel);ax.set_xlabel('Time (s)' if ax!=axs[1,2] else 'Payload radius (km)');ax.grid(alpha=.18)
    axs[0,2].axhline(1,c='gray',ls=':',lw=1);axs[0,0].legend(fontsize=8)
    fig.suptitle('Point-mass payout: same cable length, different controls\nThree equal-duration strategies; deliberately fast payout is a shorter failure demonstration',fontsize=15)
    fig.savefig(OUT/'comparison.png',dpi=160);fig.savefig(OUT/'comparison.svg');plt.close(fig)
    p=OUT/'comparison.svg';p.write_text('\n'.join(s.rstrip() for s in p.read_text().splitlines())+'\n')

def main():
    OUT.mkdir(exist_ok=True);c=Config();hist={};records=[]
    for name,p in scenarios(c).items():
        r=run(c,p);a=sample(r,np.unique(np.r_[np.arange(0,r['end'],.5),p.duration,r['end']]))
        hist[name]=a;record=metric(r,a,name);records.append(record)
        np.savez_compressed(OUT/f'{name}.npz',columns=COLUMNS,history=a)
        print(name,record['payout_end_speed_m_s'],record['payout_end_angular_speed_ratio'],record['slack_time_s'],flush=True)
        animate(r,name)
    compare(hist)
    (OUT/'summary.json').write_text(json.dumps(records,indent=2)+'\n')
    keys=['name','payout_end_radius_m','payout_end_speed_m_s','payout_end_angular_speed_ratio','payout_end_lag_deg','payout_end_slack_m','peak_regular_tension_n','slack_time_s']
    with (OUT/'summary.csv').open('w') as f:
        w=csv.DictWriter(f,fieldnames=keys,extrasaction='ignore');w.writeheader();w.writerows(records)
if __name__=='__main__':main()
