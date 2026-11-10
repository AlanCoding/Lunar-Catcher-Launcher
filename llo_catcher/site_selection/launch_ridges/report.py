"""Plot limiting terrain curves, fresh-launch height and orbit profiles."""
from pathlib import Path
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from ..global_hills.search import GlobalTerrain,RADIUS
from ..featured_four.adjusted_hilltops.check_launches import trajectory
ROOT=Path(__file__).resolve().parent
plt.rcParams.update({'svg.fonttype':'none'})

def save(fig,name):
    for ext in ['png','svg']:fig.savefig(ROOT/f'{name}.{ext}',dpi=180,bbox_inches='tight')
    plt.close(fig)

def main():
    d=json.loads((ROOT/'results.json').read_text());rows=d['rows'];terrain=GlobalTerrain()
    x=np.array([r['contact_longitude_deg'] for r in rows]);y=np.array([r['contact_latitude_deg'] for r in rows])*np.pi/180*RADIUS/1000
    colors=plt.get_cmap('tab10')(np.arange(len(d['seed_longitudes_deg'])))
    # Show separated panels for each ridge group: regional aspect otherwise hides 4 km band.
    groups=[]
    for lon in d['seed_longitudes_deg']:
        rr=[r for r in rows if r['start_longitude_deg']==lon]
        # Join adjacent latitude samples only when both are downstream contacts
        # and less than 1 km apart. Never bridge a jump between mountains.
        current=[]
        for r in rr:
            if r['extra_release_height_m']<.1:
                if len(current)>1:groups.append(current)
                current=[];continue
            if current:
                prev=current[-1];dx=np.radians(r['contact_longitude_deg']-prev['contact_longitude_deg'])*RADIUS
                dy=np.radians(r['contact_latitude_deg']-prev['contact_latitude_deg'])*RADIUS
                if np.hypot(dx,dy)>1000:
                    if len(current)>1:groups.append(current)
                    current=[]
            current.append(r)
        if len(current)>1:groups.append(current)
    fig,ax=plt.subplots(figsize=(13,5))
    for i,lon in enumerate(d['seed_longitudes_deg']):
        rr=[r for r in rows if r['start_longitude_deg']==lon]
        ax.scatter([r['contact_longitude_deg'] for r in rr],np.array([r['contact_latitude_deg'] for r in rr])*np.pi/180*RADIUS/1000,s=12,color=colors[i],label=f'Seed {lon:g}° E')
    for g in groups:ax.plot([r['contact_longitude_deg'] for r in g],np.array([r['contact_latitude_deg'] for r in g])*np.pi/180*RADIUS/1000,color='#555555',lw=.6,zorder=0)
    ax.set(xlabel='Limiting terrain longitude east (degrees)',ylabel='North of equator (km)',title='Where the minimum-height eastward orbits touch terrain\nDifferent seed meridians can identify the same ridge');ax.grid(alpha=.2);ax.legend(ncol=3,fontsize=8)
    save(fig,'contact_overview')
    # Cluster contact longitudes by geographic gaps for detailed terrain strips.
    order=np.sort(x);cuts=np.flatnonzero(np.diff(order)>0.25)+1;clusters=np.split(order,cuts)
    clusters=[a for a in clusters if len(a)>=3]
    fig,axes=plt.subplots(len(clusters),1,figsize=(12,3.5*len(clusters)),squeeze=False,layout='constrained')
    for ax,cluster in zip(axes[:,0],clusters):
        lo,hi=cluster.min()-.035,cluster.max()+.035
        lons=np.linspace(lo,hi,max(201,min(1800,int((hi-lo)*512*2))));north=np.linspace(-2.15,2.15,180)
        xx,yy=np.meshgrid(lons,north);z=terrain.height(np.degrees(yy*1000/RADIUS),xx)
        ax.pcolormesh(xx,yy,z,cmap='gist_earth',shading='auto',rasterized=True)
        cs=ax.contour(xx,yy,z,levels=6,colors='black',alpha=.3,linewidths=.4)
        ax.clabel(cs,fontsize=6,fmt='%d m')
        for g in groups:
            gx=np.array([r['contact_longitude_deg'] for r in g]);gy=np.array([r['contact_latitude_deg'] for r in g])*np.pi/180*RADIUS/1000
            if np.any((gx>=lo)&(gx<=hi)):ax.plot(gx,gy,color='white',lw=2,alpha=.8)
        mask=(x>=lo)&(x<=hi);h=np.array([r['contact_fresh_launch_extra_height_m'] for r in rows])
        sc=ax.scatter(x[mask],y[mask],c=h[mask],cmap='plasma',s=22,vmin=0,vmax=max(1,h.max()),edgecolors=np.where(h[mask]<=1,'#00cc85','#e8372e'),lw=1.2)
        ax.set(xlim=(lo,hi),ylim=(-2.15,2.15),xlabel='Longitude east (degrees)',ylabel='North of equator (km)',title=f'Terrain and contact lines · {cluster.min():.2f}–{cluster.max():.2f}° E')
        fig.colorbar(sc,ax=ax,label='Extra height for fresh launch (m)')
        ax.legend(handles=[Line2D([],[],marker='o',ls='',mfc='none',mec='#00cc85',label='Fresh launch needs ≤1 m'),Line2D([],[],marker='o',ls='',mfc='none',mec='#e8372e',label='Needs >1 m')],fontsize=7,loc='lower left')
    save(fig,'ridge_terrain')
    fig,axes=plt.subplots(2,1,figsize=(12,7),layout='constrained')
    for i,lon in enumerate(d['seed_longitudes_deg']):
        r=min((r for r in rows if r['start_longitude_deg']==lon),key=lambda r:abs(r['source_north_m']))
        # Local profile up to the active contact, with enough downrange context.
        end=min(np.pi,max(.02,np.radians(r['contact_anomaly_deg'])*1.2))
        f=np.linspace(0,end,10000);lat,lontrack,rad,t=trajectory(r['start_latitude_deg'],lon,RADIUS+r['required_release_elevation_m'],1)(f)
        dist=f*RADIUS/1000
        if i in [0,4]:
            ax=axes[0 if i==0 else 1];ax.plot(dist,terrain.height(lat,lontrack),color='#79664c',label='Terrain along orbit ground track');ax.plot(dist,rad-RADIUS,color='#226e94',label='Minimum-height orbit');ax.scatter(np.radians(r['contact_anomaly_deg'])*RADIUS/1000,r['contact_elevation_m'],color='#bd483b',label='Limiting contact',zorder=5)
            ax.set(xlabel='Inertial angular travel × Moon radius (km)',ylabel='Elevation above reference sphere (m)',title=f'Equatorial seed at {lon:g}° E · required release height {r["extra_release_height_m"]:.1f} m above local ground');ax.legend();ax.grid(alpha=.2)
    save(fig,'orbit_profiles')
    summary=dict(seed_count=len(rows),seed_meridians=len(d['seed_longitudes_deg']),contact_lon_min=float(x.min()),contact_lon_max=float(x.max()),self_limited_count=sum(r['extra_release_height_m']<.1 for r in rows),traced_segments_before_deduplication=len(groups),fresh_height_max_m=max(r['contact_fresh_launch_extra_height_m'] for r in rows),fresh_height_median_m=float(np.median([r['contact_fresh_launch_extra_height_m'] for r in rows])),contact_segments=groups)
    (ROOT/'segments.json').write_text(json.dumps(summary,indent=2)+'\n')
    print({k:v for k,v in summary.items() if k!='contact_segments'})
if __name__=='__main__':main()
