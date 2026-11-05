"""Inspect terrain maps for representative screened footprints."""
import json,csv
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import TwoSlopeNorm
from . import survey as s

def main():
    s.initialize();p=s.ROOT/'results.json';r=json.loads(p.read_text());best=r['refined_best_per_corridor_side'][0]
    coarse=list(csv.DictReader((s.ROOT/'footprints.csv').open()))
    flattest=min(coarse,key=lambda x:float(x['total_relief_m']))
    flat=s.evaluate((float(flattest['release_longitude_deg_east']),1 if flattest['hub_side']=='north' else -1,True))
    r['least_relief_sample_refined']=flat;p.write_text(json.dumps(r,indent=2)+'\n')
    fig,axes=plt.subplots(1,2,figsize=(13,6.5),layout='constrained')
    for ax,row,label in zip(axes,[best,flat],['Least maximum rise found','Least total relief sampled']):
        axis=np.linspace(-5250,5250,351);x,y=np.meshgrid(axis,axis);distance=np.hypot(x,y)
        bearing=np.arctan2(x,y);theta=distance/(s.RADIUS+row['hub_ground_elevation_m'])
        lat,lon=s.destination(row['hub_latitude_deg'],row['hub_longitude_deg_east'],bearing,theta)
        z=s.T.height(lat,lon)-row['hub_ground_elevation_m'];z=np.ma.masked_where(distance>5000,z)
        vmin=min(float(z.min()),-1);vmax=max(float(z.max()),11)
        im=ax.pcolormesh(x/1000,y/1000,z,cmap='RdBu_r',norm=TwoSlopeNorm(vmin=vmin,vcenter=0,vmax=vmax),shading='auto',rasterized=True)
        ax.contour(x/1000,y/1000,z,levels=[10],colors='#222222',linewidths=.9)
        angle=np.linspace(0,2*np.pi,721);ax.plot(5*np.cos(angle),5*np.sin(angle),color='#333333',lw=1.2)
        ax.scatter([0],[0],marker='+',s=100,color='black',label='Hub')
        dy=-5 if row['hub_side']=='north' else 5
        ax.scatter([0],[dy],color='#df9a21',edgecolor='black',marker='D',s=65,zorder=5,label='Equatorial release')
        ax.set_aspect('equal');ax.set_xlim(-5.4,5.4);ax.set_ylim(-5.4,5.4);ax.set_xlabel('East from hub (km)');ax.set_ylabel('North from hub (km)')
        ax.set_title(f"{label}\nRelease {row['release_longitude_deg_east']:.5f}° E; hub {row['hub_side']}\nRise {row['maximum_rise_above_hub_m']:.1f} m; drop {row['maximum_drop_below_hub_m']:.1f} m",fontsize=10)
        fig.colorbar(im,ax=ax,label='Terrain elevation minus hub elevation (m)',shrink=.8);ax.legend(loc='lower left',fontsize=8)
    fig.suptitle('5 km hub footprints: no candidate found below the 10 m rise limit\nBlack terrain contour = 10 m above hub; each panel has its own color scale',fontsize=13)
    fig.savefig(s.ROOT/'footprint_maps.png',dpi=160,bbox_inches='tight');fig.savefig(s.ROOT/'footprint_maps.svg',bbox_inches='tight');plt.close(fig)

if __name__=='__main__':main()
