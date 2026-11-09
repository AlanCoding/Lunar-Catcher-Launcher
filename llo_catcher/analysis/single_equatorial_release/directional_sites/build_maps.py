"""Publication terrain maps of launcher geometry; no impact overlays."""
from pathlib import Path
import csv,json,hashlib,argparse
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import TwoSlopeNorm,LightSource
from matplotlib.patches import Circle
from ..summit_sites.extend import CACHE, ROWS
from ..hub_footprints.terrain import Terrain,RADIUS
from ..hub_footprints.survey import destination
from ..summit_sites.maps.fetch_regional import CACHE as REGIONAL
ROOT=Path(__file__).parent/'maps'
ROOT.mkdir(exist_ok=True)
plt.rcParams.update({'svg.fonttype':'none','font.family':'DejaVu Sans'})
TRACK=76.78937039996255
ids=['S1','S2','S3','N1','S4','N2']

def read(name):return list(csv.DictReader(name.open()))
def project(lat,lon,lat0,lon0):
    p,p0=np.radians(lat),np.radians(lat0);d=np.radians(lon-lon0)
    cosc=np.clip(np.sin(p0)*np.sin(p)+np.cos(p0)*np.cos(p)*np.cos(d),-1,1)
    c=np.arccos(cosc);k=np.divide(c,np.sin(c),out=np.ones_like(c),where=np.abs(c)>1e-12)
    return RADIUS/1000*k*np.cos(p)*np.sin(d),RADIUS/1000*k*(np.cos(p0)*np.sin(p)-np.sin(p0)*np.cos(p)*np.cos(d))

def regional(lat,lon):
    a=np.load(REGIONAL/'band.npy',mmap_mode='r')
    x=(np.asarray(lon)%360)*64-.5;y=(90-np.asarray(lat))*64-.5-5472
    xi=np.floor(x).astype(int);yi=np.floor(y).astype(int);wx=x-xi;wy=y-yi
    assert yi.min()>=0 and yi.max()+1<a.shape[0]
    return .5*((1-wx)*((1-wy)*a[yi,xi]+wy*a[yi+1,xi])+wx*((1-wy)*a[yi,(xi+1)%23040]+wy*a[yi+1,(xi+1)%23040]))

def field(site,side,n,height):
    axis=np.linspace(-side/2,side/2,n);x,y=np.meshgrid(axis,axis)
    lat,lon=destination(float(site['hub_lat_deg']),float(site['hub_lon_deg_east']),np.arctan2(x,y),np.hypot(x,y)*1000/RADIUS)
    return axis,height(lat,lon)-float(site['hub_elevation_m'])

def main():
    parser=argparse.ArgumentParser();parser.add_argument("--regional-only",action="store_true");args=parser.parse_args()
    t=Terrain(CACHE,ROWS)
    sites=json.loads((ROOT.parent/'catalog.json').read_text())['sites']
    summary=[]
    for site in sites:
        sid=site['id']
        lat0=float(site['hub_lat_deg']);lon0=float(site['hub_lon_deg_east']);r=float(site['actual_radius_km'])
        for side in [15]:
            if args.regional_only:continue
            local=True;n=401
            axis,z=field(site,side,n,t.height)
            norm=TwoSlopeNorm(vmin=min(-10,float(z.min())),vcenter=0,vmax=max(10,float(z.max())))
            rgba=plt.get_cmap('RdBu_r')(norm(z))
            rgb=LightSource(azdeg=315,altdeg=50).shade_rgb(rgba[:,:,:3],z,vert_exag=1.5,dx=side*1000/(n-1),dy=side*1000/(n-1),blend_mode='soft')
            fig,ax=plt.subplots(figsize=(10,10));fig.subplots_adjust(left=.1,right=.84,bottom=.18,top=.88)
            ax.imshow(rgb,extent=[-side/2,side/2,-side/2,side/2],origin='lower',interpolation='nearest')
            levels=np.arange(np.floor(z.min()/ (200 if local else 1000))*(200 if local else 1000),z.max(),200 if local else 1000)
            if len(levels):ax.contour(axis,axis,z,levels=levels,colors='#425462',linewidths=.4,alpha=.35)
            ring=RADIUS/1000*np.arcsin(r*1000/(RADIUS+float(site['hub_elevation_m'])))
            ax.add_patch(Circle((0,0),ring,fill=False,edgecolor='#246052',lw=2,linestyle='--',label=f'Tether tip sweep · {r:.3f} km radius'))
            ax.add_patch(Circle((0,0),TRACK/1000,fill=False,edgecolor='#f3a126',lw=1.5,label='Rover track · 76.79 m radius'))
            ax.scatter([0],[0],s=28,c='black',edgecolor='white',lw=.6,zorder=8,label='Hub / summit')
            notes=[f"Full-circle minimum clearance: {site['actual_horizontal_tip_min_clearance_m']:.1f} m (negative = terrain intersection)"]
            rx,ry=project(0.,lon0,lat0,lon0)
            if max(abs(rx),abs(ry))<side/2:
                ax.scatter(rx,ry,s=50,marker='^',facecolor='white',edgecolor='#283c46',lw=1.3,zorder=6)
            if local:
                ia=ax.inset_axes([.025,.715,.24,.24])
                iaxis,iz=field(site,.6,101,t.height)
                ia.imshow(iz,extent=[-300,300,-300,300],origin='lower',cmap='RdBu_r',norm=norm)
                ia.add_patch(Circle((0,0),TRACK,fill=False,edgecolor='#f3a126',lw=2));ia.scatter(0,0,s=16,color='black')
                ia.set_xticks([-200,0,200]);ia.set_yticks([-200,0,200]);ia.tick_params(labelsize=6)
                ia.set_title('Track inset · metres',fontsize=8,bbox=dict(fc='white',ec='none',alpha=.9));ia.set_aspect('equal')
            ax.set(xlim=(-side/2,side/2),ylim=(-side/2,side/2),xlabel='East from hub (km)',ylabel='North from hub (km)',aspect='equal')
            signed=(lon0+180)%360-180
            fig.suptitle(f'{sid} · Summit hub and launcher footprint',fontsize=18,y=.965)
            fig.text(.5,.924,f'{lat0:+.6f}°, {signed:+.6f}°  |  {side} × {side} km  |  Hub elevation {float(site["hub_elevation_m"]):+,.1f} m',ha='center',fontsize=10)
            cax=fig.add_axes([.87,.25,.025,.53]);cb=fig.colorbar(plt.cm.ScalarMappable(norm=norm,cmap='RdBu_r'),cax=cax,label='Terrain above / below hub (m)')
            cb.set_ticks(np.r_[np.linspace(norm.vmin,0,5),np.linspace(0,norm.vmax,3)[1:]])
            cb.ax.yaxis.set_major_formatter(matplotlib.ticker.StrMethodFormatter('{x:.0f}'))
            ax.legend(loc='upper right',fontsize=8,framealpha=.94)
            fig.text(.1,.128,'▲ Common equatorial release point for alternative eastward / westward launches',fontsize=9,va='top')
            fig.text(.1,.106,'\n'.join(notes),fontsize=9,linespacing=1.6,va='top')
            fig.text(.1,.038,('SLDEM2015 · ~59 m native grid' if local else 'LOLA LDEM64 · ~474 m native grid; context only')+'  |  Hillshade is synthetic illumination',fontsize=8,color='#5b6166')
            fig.text(.1,.019,'Footprint is a geometry overlay, not a demonstration of cable clearance.',fontsize=8,color='#5b6166')
            stem=f'{sid}_{side}km';fig.savefig(ROOT/f'{stem}.png',dpi=180);fig.savefig(ROOT/f'{stem}.svg');plt.close(fig)
            p=ROOT/f'{stem}.svg';p.write_text('\n'.join(a.rstrip() for a in p.read_text().splitlines())+'\n')
            print(stem,flush=True)
        summary.append(dict(site=sid,track_radius_m=TRACK,tip_radius_km=r,regional_map=False,impact_overlays=False))
    (ROOT/'map_index.json').write_text(json.dumps(summary,indent=2)+'\n')
    paths=[ROOT.parent/'catalog.json']
    (ROOT/'inputs.json').write_text(json.dumps({str(p.relative_to(ROOT.parent)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths},indent=2)+'\n')
if __name__=='__main__':main()
