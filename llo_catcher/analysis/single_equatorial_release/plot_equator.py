"""Equatorial terrain with separately calculated east/west 10 m launch markers."""
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from . import calculate as c

def main():
    c.initialize();root=c.OUT/'directional_sites'
    survey=json.loads((root/'degree_survey.json').read_text())
    bands={'east':json.loads((c.OUT/'local_corridors/results.json').read_text())['outbound_ranges'],
           'west':json.loads((root/'west_corridors.json').read_text())['bands']}
    lon=np.r_[0.,(np.arange(len(c._GROUND))+.5)/512,360.];elev=c.terrain(np.radians(lon))/1000
    colors={'east':'#24785b','west':'#985631'};markers={'east':'>','west':'<'}
    def draw(ax,overlays=False):
        ax.plot(lon,elev,color='#82745f',lw=.7,label='Equatorial terrain',zorder=1)
        ax.axhline(0,color='.6',lw=.6,ls='--')
        for d in ['east','west']:
            rows=[r for r in survey[d] if r['status']!='outbound_collision']
            xs=[r['longitude_deg_east'] for r in rows]
            ax.scatter(xs,[r['release_ground_elevation_m']/1000 for r in rows],color=colors[d],marker=markers[d],s=80,edgecolor='white',lw=.7,zorder=4,label=f'{d.capitalize()}ward clear seeds ({len(rows)})')
            if overlays:
                for b in bands[d]:ax.axvspan(b['start_deg_east'],b['end_deg_east'],color=colors[d],alpha=.2,lw=0)
        ax.grid(alpha=.15);ax.set_ylabel('Elevation above reference sphere (km)');ax.set_xlabel('Longitude east (degrees)')
    plt.rcParams['svg.fonttype']='none'
    fig,ax=plt.subplots(figsize=(15,6),layout='constrained');draw(ax)
    ax.set(xlim=(0,360),ylim=(-4.8,10.5),xticks=np.arange(0,361,30))
    for x,tx,ty,d in [(144,135,6.5,'east'),(220,231,9.5,'east'),(177,165,9.6,'west'),(194,200,10,'west'),(264,255,6,'east'),(267,275,6,'east'),(283,292,4.5,'east'),(294,320,-2.5,'east')]:
        ax.annotate('293°–295° E' if x==294 else f'{x}° E',xy=(x,float(c.terrain(np.radians(x)))/1000),xytext=(tx,ty),ha='center',fontsize=9,color=colors[d],arrowprops=dict(arrowstyle='-',color=colors[d],lw=.7))
    ax.legend(loc='upper center',bbox_to_anchor=(.5,-.16),ncol=3,fontsize=9)
    fig.suptitle('Elevation along the lunar equator · eastward and westward launch clearance\n10 m above local terrain; 25 km catcher; all 10 clear one-degree seeds impact after missed capture',fontsize=13)
    for ext in ['png','svg']:fig.savefig(c.OUT/f'equatorial_elevation.{ext}',dpi=170)
    plt.close(fig)
    fig,axes=plt.subplots(2,1,figsize=(13,9),layout='constrained')
    for ax,lo,hi,title in [(axes[0],174,197,'Westward seed neighborhoods'),(axes[1],258,302,'Eastern group of eastward seeds')]:
        draw(ax,True);ax.set_xlim(lo,hi)
        z=elev[(lon>=lo)&(lon<=hi)];ax.set_ylim(z.min()-.7,z.max()+.9)
        ax.set_title(title+' · shading = refined clear corridors',loc='left',fontsize=11)
        for d in ['east','west']:
            for r in survey[d]:
                x=r['longitude_deg_east']
                if lo<x<hi and r['status']!='outbound_collision':ax.annotate(f'{x:g}°',xy=(x,r['release_ground_elevation_m']/1000),xytext=(6,12),textcoords='offset points',fontsize=9)
    axes[0].legend(loc='lower left',fontsize=8)
    fig.suptitle('Terrain profiles and direction-specific release corridors\nMarkers are equatorial release seeds, not shifted hilltop hubs',fontsize=13)
    for ext in ['png','svg']:fig.savefig(c.OUT/f'equatorial_elevation_detail.{ext}',dpi=170)
    plt.close(fig)
    for path in c.OUT.glob('equatorial_elevation*.svg'):
        path.write_text('\n'.join(line.rstrip() for line in path.read_text().splitlines())+'\n')
if __name__=='__main__':main()
