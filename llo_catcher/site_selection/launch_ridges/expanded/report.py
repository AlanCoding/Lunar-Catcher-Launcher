"""Compare independent downstream ridge contacts to the four adjusted hubs."""
import json,csv
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from .calculate import ROOT
from ..calculate import GlobalTerrain,RADIUS
from llo_catcher.site_selection.support.maps import project
plt.rcParams.update({'svg.fonttype':'none'})

def save(fig,name):
    for ext in ['png','svg']:fig.savefig(ROOT/f'{name}.{ext}',dpi=180,bbox_inches='tight')
    plt.close(fig)

def main():
    d=json.loads((ROOT/'results.json').read_text());terrain=GlobalTerrain();comparison=[]
    name_path=ROOT.parent/'catalog/ridges.json'
    names={r['site']:r['ridge'] for r in json.loads(name_path.read_text())['featured_hubs']} if name_path.exists() else {}
    fig,axes=plt.subplots(4,1,figsize=(12,12),layout='constrained')
    for ax,region,s in zip(axes,d['regions'],d['sites']):
        label=region['label'];rows=[r for r in d['rows'] if r['region']==label]
        # Exclude seeds already on clear ground: those rediscover themselves,
        # which is not independent evidence of a downstream contact ridge.
        contacts=[r for r in rows if r['extra_release_height_m']>.1 and r['contact_anomaly_deg']>.05]
        def near(lat):
            x,y=project(np.array([r['contact_latitude_deg'] for r in contacts]),np.array([r['contact_longitude_deg'] for r in contacts]),lat,s['longitude_deg_east'])
            j=int(np.argmin(np.hypot(x,y)));return contacts[j],float(np.hypot(x,y)[j]*1000)
        best,distance=near(s['hub_latitude_deg']);tip,tipdist=near(s['near_equator_tip_latitude_deg'])
        result=dict(site=label,hub_latitude_deg=s['hub_latitude_deg'],hub_longitude_deg=s['hub_longitude_deg'],hub_elevation_m=s['hub_elevation_m'],
          nearest_hub_contact_distance_m=distance,nearest_hub_contact=best,nearest_release_contact_distance_m=tipdist,nearest_release_contact=tip,
          samples=len(rows),independent_downstream_contacts=len(contacts),matches_within_one_dem_cell=distance<59)
        comparison.append(result)
        x=np.array([r['contact_longitude_deg'] for r in contacts]);y=np.radians([r['contact_latitude_deg'] for r in contacts])*RADIUS/1000
        h=np.array([r['contact_fresh_launch_extra_height_m'] for r in contacts]);ax.scatter(x,y,c=np.where(h<=1,'#377e65','#b55342'),s=8)
        ax.scatter(s['longitude_deg_east'],np.radians(s['hub_latitude_deg'])*RADIUS/1000,marker='*',s=110,c='#e9ad27',edgecolor='black',zorder=6)
        ax.set(title=f'{label} · contact locations from expanded regional seeds',xlabel='Longitude east (degrees)',ylabel='North of equator (km)');ax.grid(alpha=.2)
        # Local terrain panel centered on the hub, 12 x 12 km.
        xaxis=np.linspace(-6,6,401);yaxis=np.linspace(-6,6,401);xx,yy=np.meshgrid(xaxis,yaxis)
        from llo_catcher.site_selection.support.geometry import destination
        lat,lon=destination(s['hub_latitude_deg'],s['longitude_deg_east'],np.arctan2(xx,yy),np.hypot(xx,yy)*1000/RADIUS)
        z=terrain.height(lat,lon)
        local,aa=plt.subplots(figsize=(9,9),layout='constrained');im=aa.pcolormesh(xx,yy,z,cmap='gist_earth',shading='auto',rasterized=True)
        cs=aa.contour(xx,yy,z,levels=10,colors='black',linewidths=.4,alpha=.4);aa.clabel(cs,fmt='%d',fontsize=7)
        for seed in region['longitudes']:
            rr=sorted([r for r in contacts if r['start_longitude_deg']==seed],key=lambda r:r['source_north_m'])
            for a,b in zip(rr,rr[1:]):
                px,py=project(np.array([a['contact_latitude_deg'],b['contact_latitude_deg']]),np.array([a['contact_longitude_deg'],b['contact_longitude_deg']]),s['hub_latitude_deg'],s['longitude_deg_east'])
                if np.hypot(px[1]-px[0],py[1]-py[0])<=1 and b['source_north_m']-a['source_north_m']<=126:
                    aa.plot(px,py,color='white',alpha=.6,lw=1)
        px,py=project(np.array([r['contact_latitude_deg'] for r in contacts]),x,s['hub_latitude_deg'],s['longitude_deg_east'])
        mask=(abs(px)<=6)&(abs(py)<=6)
        aa.scatter(px[mask],py[mask],c=np.where(h[mask]<=1,'#31cf98','#e66345'),s=12,edgecolors='black',linewidths=.2,zorder=4)
        aa.scatter(0,0,marker='*',s=230,c='#e9ad27',edgecolors='black',zorder=7)
        tx,ty=project(s['near_equator_tip_latitude_deg'],s['longitude_deg_east'],s['hub_latitude_deg'],s['longitude_deg_east'])
        aa.scatter(tx,ty,marker='^',s=80,facecolor='white',edgecolors='black',zorder=7)
        aa.set(xlim=(-6,6),ylim=(-6,6),aspect='equal',xlabel='East of hub (km)',ylabel='North of hub (km)',title=f"{label} · {names.get(label,'Eastward contact ridge')}\nAdjusted summit and mapped ridge traces")
        aa.legend(handles=[Line2D([],[],marker='*',ls='',mfc='#e9ad27',mec='black',markersize=12,label='Adjusted hub'),Line2D([],[],marker='^',ls='',mfc='white',mec='black',label='Intended release'),Line2D([],[],marker='o',ls='',color='#31cf98',label='Fresh launch needs ≤1 m'),Line2D([],[],marker='o',ls='',color='#e66345',label='Needs >1 m')],loc='lower left',fontsize=8)
        local.colorbar(im,ax=aa,label='Terrain elevation above reference sphere (m)');save(local,f'{label}_ridge_match')
    save(fig,'regional_contacts')
    (ROOT/'comparison.json').write_text(json.dumps(comparison,indent=2)+'\n')
    fields=['site','hub_latitude_deg','hub_longitude_deg','nearest_hub_contact_distance_m','nearest_release_contact_distance_m','matches_within_one_dem_cell']
    with (ROOT/'comparison.csv').open('w') as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows({k:r[k] for k in fields} for r in comparison)
    for r in comparison:print(r['site'],r['nearest_hub_contact_distance_m'],r['nearest_hub_contact']['contact_longitude_deg'],r['nearest_hub_contact']['start_longitude_deg'],flush=True)
if __name__=='__main__':main()
