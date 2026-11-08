"""Plot the saved outbound-only 1:3 cases without rerunning the solver."""
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from matplotlib.patches import Circle
from .report import OUT


def main():
    rows=json.loads((OUT/'ratio_cases.json').read_text())
    plt.rcParams.update({'font.size':11,'axes.spines.top':False,'axes.spines.right':False,'svg.fonttype':'none'})
    fig,axes=plt.subplots(2,1,figsize=(13,7),layout='constrained')
    titles=['1:3 payload / tether per outbound meter', '1:3 payload / tether across the whole loop']
    for ax,row,title in zip(axes,rows,titles):
        with np.load(OUT/f'{row["name"]}.npz') as h:
            xy=h['xy_m'].T/1000; s=h['s']; stress=h['stress_Pa']/1e9
        lc=LineCollection(np.stack([xy[:-1],xy[1:]],axis=1),cmap='viridis',norm=plt.Normalize(0,4.5),linewidth=3)
        lc.set_array(stress[:-1]);ax.add_collection(lc)
        c=row['inputs'];ax.add_patch(Circle((c['station_radius']/1000,0),c['wheel_radius']/1000,facecolor='#a58b68',edgecolor='#54442d'))
        ax.plot(0,0,'o',color='#222222',ms=5)
        # Symbols identify the loaded region, not simulated discrete payloads.
        inds=np.searchsorted(s,np.linspace(.06,.45,12))
        ax.scatter(xy[inds,0],xy[inds,1],s=25,marker='s',color='#a2673d',zorder=4)
        for frac,label,offset in [(.25,'Loaded outbound →',(0,-.36)),(.75,'← Unloaded return',(0,.28))]:
            i=np.searchsorted(s,frac)
            ax.annotate(label,xy=xy[i],xytext=xy[i]+offset,ha='center',va='center',color='#573c26' if frac<.5 else '#333333',arrowprops=dict(arrowstyle='-',color='.5'))
        j=np.searchsorted(s,c['release_center'])
        ax.plot(*xy[j],marker='o',mfc='white',mec='#a2673d',ms=6,zorder=5)
        ax.annotate('Unload before free turn',xy=xy[j],xytext=(4.5,-1.5),ha='center',fontsize=10,arrowprops=dict(arrowstyle='-',color='.5'))
        ax.set(xlim=(-.16,6.05),ylim=(-1.7,.6),ylabel='Sideways (km)')
        ax.set_aspect('equal');ax.grid(alpha=.15)
        ax.set_title(f'{title}  ·  payload {row["payload_inventory_kg"]/1000:.2f} t / tether {row["bare_loop_mass_kg"]/1000:.2f} t  ·  peak {row["max_stress_GPa"]:.2f} GPa',loc='left',fontsize=11)
    axes[-1].set_xlabel('Outward from hub (km) — equal horizontal and vertical scale')
    fig.colorbar(lc,ax=axes,label='Tensile stress (GPa)',shrink=.85)
    fig.suptitle('Payload on the outbound strand only · calculated steady conveyor shapes\n5 m/s feed · squares mark the continuously loaded region, not discrete simulated packages',fontsize=13)
    for ext in ['png','svg']:fig.savefig(OUT/f'ratio_shapes.{ext}',dpi=180)
    plt.close(fig)

if __name__=='__main__':main()
