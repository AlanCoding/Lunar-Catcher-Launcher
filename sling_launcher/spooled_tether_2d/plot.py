"""Static snapshots and angular/stress histories from saved dynamic runs."""
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from matplotlib.patches import Circle
from .run import OUT

def save(fig,name):
    for ext in ['png','svg']:fig.savefig(OUT/f'{name}.{ext}',dpi=190)
    plt.close(fig)

def snapshots(d,meta,stem,part):
    phases=d['phase'];t=d['time_s'];xy=d['xy_m']/1000;stress=d['stress_Pa']/1e9
    if part=='extension':
        mask=phases=='extend';tt=t[mask];targets=list(np.linspace(tt[0],tt[-1],5))
        hold=t[phases=='loaded_hold'];targets.append(hold[-1] if len(hold) else tt[-1])
    else:
        mask=phases=='retract'
        if not mask.any():return
        tt=t[mask];targets=list(np.linspace(tt[0],tt[-1],5));hold=t[phases=='final_hold'];targets.append(hold[-1]) if len(hold) else None
        if not len(hold):targets=list(np.linspace(tt[0],tt[-1],6))
    ids=[int(np.argmin(abs(t-v))) for v in targets]
    points=xy[ids].reshape(-1,2);xmin=min(-.6,points[:,0].min()-.3);xmax=max(.6,points[:,0].max()+.3)
    ymin=min(-.6,points[:,1].min()-.3);ymax=max(.6,points[:,1].max()+.3)
    fig,axes=plt.subplots(2,3,figsize=(13,8),layout='constrained')
    norm=plt.Normalize(0,3)
    for ax,i in zip(axes.flat,ids):
        line=LineCollection(np.stack([xy[i,:-1],xy[i,1:]],axis=1),cmap='viridis',norm=norm,linewidth=3)
        line.set_array(stress[i]);ax.add_collection(line)
        ax.plot(*xy[i,-1],'o',color='#a2673d',ms=5);ax.plot(meta['station_radius_m']/1000,0,'o',color='black',ms=4)
        ax.add_patch(Circle((0,0),.5,facecolor='none',edgecolor='.75',ls=':'))
        ax.axhline(0,color='.85',lw=.7);ax.axvline(0,color='.85',lw=.7)
        ax.set(xlim=(xmin,xmax),ylim=(ymin,ymax));ax.set_aspect('equal');ax.grid(alpha=.12)
        span = f'angular span {d["angle_min_deg"][i]:.1f}° to {d["angle_max_deg"][i]:.1f}°' if np.isfinite(d["angle_min_deg"][i]) else 'entire cable within 500 m'
        ax.set_title(f'{str(phases[i]).replace("_"," ")} · t = {t[i]:.0f} s\npeak {stress[i].max():.2f} GPa · {span}',fontsize=9)
        ax.set_xlabel('Outward x (km)');ax.set_ylabel('Sideways y (km)')
    fig.colorbar(line,ax=axes,label='Axial stress (GPa)',shrink=.8,extend='max')
    ratio=meta['tether_mass_kg']/meta['config']['payload']
    fig.suptitle(f'{part.capitalize()} shapes · Kevlar 49 · {ratio:.2f}:1 tether / payload mass\nHub-rotating frame; equal x/y scale. Angular span excludes radius < 500 m.' + ('\nLate return is provisional: slack/retension and mesh sensitivity.' if part=='retraction' else ''),fontsize=12)
    save(fig,f'{stem}_{part}')

def main():
    plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False,'svg.fonttype':'none'})
    names=['kevlar_1p5GPa_n64','kevlar_ratio3_n32']
    fig,axes=plt.subplots(2,1,figsize=(12,7),sharex=True,layout='constrained')
    for stem,color in zip(names,['#527e68','#a2673d']):
        d=np.load(OUT/f'{stem}.npz');meta=json.loads((OUT/f'{stem}.json').read_text())
        snapshots(d,meta,stem,'extension');snapshots(d,meta,stem,'retraction')
        ratio=meta['tether_mass_kg']/meta['config']['payload'];label=f'{ratio:.2f}:1 tether/payload'
        axes[0].plot(d['time_s']/60,d['stress_Pa'].max(axis=1)/1e9,color=color,label=label)
        axes[1].fill_between(d['time_s']/60,d['angle_min_deg'],d['angle_max_deg'],alpha=.25,color=color,label=label+' occupied span')
        axes[1].plot(d['time_s']/60,d['tip_angle_deg'],color=color,lw=.9)
        # Save per-case angular envelope with tip history for multi-spool assessment.
        ef,ea=plt.subplots(figsize=(11,4.5),layout='constrained')
        ea.fill_between(d['time_s']/60,d['angle_min_deg'],d['angle_max_deg'],alpha=.3,color=color,label='Cable span outside 500 m')
        ea.plot(d['time_s']/60,d['tip_angle_deg'],color=color,label='Tip angle')
        for val in [-6,6]:ea.axhline(val,color='.5',ls=':',lw=.8)
        ea.set(xlabel='Time (minutes)',ylabel='Angle relative to feed-station radial line (degrees)',title=f'{label} · angular occupancy, not a collision-clearance certificate')
        ea.legend(fontsize=9);ea.grid(alpha=.2);save(ef,f'{stem}_angles')
    for ax in axes:
        ax.grid(alpha=.2);ax.legend(fontsize=9)
    axes[0].axhline(3,color='#9e4545',ls='--',label='Nominal fiber strength');axes[0].set_ylabel('Maximum sampled axial stress (GPa)');axes[0].legend(fontsize=9)
    axes[1].set(xlabel='Time (minutes)',ylabel='Angular envelope / tip (degrees)')
    fig.suptitle('Elastic spooled tether: extension, hold, abrupt release, empty retraction',fontsize=13)
    save(fig,'stress_and_angles')
if __name__=='__main__':main()
