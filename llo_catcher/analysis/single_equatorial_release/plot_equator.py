"""Plot the cached equatorial elevation, marking saved 3 m / 10 m successes.
Does not recalculate trajectories or modify the height-survey results.
"""
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from . import calculate as c


def main():
    c.initialize()
    results=json.loads((c.OUT/'results.json').read_text())
    clear={h:[r for r in results['trajectories'] if r['release_height_m']==h and r['status']!='outbound_collision'] for h in [3.,10.]}
    lon=np.r_[0.,(np.arange(len(c._GROUND))+.5)/512,360.]
    elev=c.terrain(np.radians(lon))/1000
    three={r['longitude_deg_east'] for r in clear[3.]}
    extra=[r for r in clear[10.] if r['longitude_deg_east'] not in three]
    def draw(ax):
        ax.plot(lon,elev,color='#82745f',lw=.75,label='Equatorial terrain (SLDEM2015)',zorder=1)
        ax.axhline(0,color='#888888',lw=.6,ls='--')
        for rows,color,marker,label in [(clear[3.],'#24785b','o','Clears outbound at both 3 m and 10 m (7 sites)'),(extra,'#d57b27','D','Additional site clearing at 10 m (293° E)')]:
            ax.scatter([r['longitude_deg_east'] for r in rows],[r['release_ground_elevation_m']/1000 for r in rows],color=color,marker=marker,s=65,edgecolor='white',linewidth=.8,zorder=4,label=label)
        ax.grid(alpha=.15);ax.set_ylabel('Elevation above 1,737.4 km reference sphere (km)');ax.set_xlabel('Longitude east (degrees)')
    fig,ax=plt.subplots(figsize=(15,5.7),layout='constrained');draw(ax)
    ax.set_xlim(0,360);ax.set_ylim(-4.8,10.1);ax.set_xticks(np.arange(0,361,30))
    for label,x,y,tx,ty in [('144°',144,clear[3.][0]['release_ground_elevation_m']/1000,136,6.8),('220°',220,clear[3.][1]['release_ground_elevation_m']/1000,215,9.2),('264°, 267°',264,3.243,259,6.3),('283°',283,2.716,285,5.3),('293°–295°',294,-.554,310,-2.8)]:
        ax.annotate(label,xy=(x,y),xytext=(tx,ty),ha='center',fontsize=10,arrowprops=dict(arrowstyle='-',color='#555555',lw=.8))
    ax.annotate('Prograde launches travel east →',xy=(344,8.5),ha='right',color='#265e80',fontsize=10)
    ax.legend(loc='upper center',bbox_to_anchor=(.5,-.16),ncol=3,fontsize=9)
    fig.suptitle('Elevation along the entire lunar equator\nMarkers: sampled longitudes that clear the outbound path to the 25 km catcher',fontsize=14)
    fig.savefig(c.OUT/'equatorial_elevation.png',dpi=160,bbox_inches='tight');fig.savefig(c.OUT/'equatorial_elevation.svg',bbox_inches='tight');plt.close(fig)
    fig,ax=plt.subplots(figsize=(12,5),layout='constrained');draw(ax)
    ax.set_xlim(258,302);ax.set_ylim(-4.4,4.8);ax.set_xticks(np.arange(260,301,5))
    for rows in [clear[3.],extra]:
        for r in rows:
            x=r['longitude_deg_east']
            if 258<x<302:
                ax.annotate(f'{x}°',(x,r['release_ground_elevation_m']/1000),xytext=(7,10),textcoords='offset points',fontsize=10)
    ax.legend(loc='upper center',bbox_to_anchor=(.5,-.16),fontsize=9)
    fig.suptitle('Closer view: successful sites along an eastward descent\nAbsolute elevation alone does not determine departure clearance',fontsize=13)
    fig.savefig(c.OUT/'equatorial_elevation_detail.png',dpi=160,bbox_inches='tight');fig.savefig(c.OUT/'equatorial_elevation_detail.svg',bbox_inches='tight');plt.close(fig)
    print('Saved full-equator and detail figures. No trajectory outputs changed.')

if __name__=='__main__':main()
