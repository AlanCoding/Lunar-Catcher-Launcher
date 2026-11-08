"""Publication terrain maps from saved sites/impacts; no trajectory reruns."""
from pathlib import Path
import csv,json,hashlib,argparse
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import TwoSlopeNorm,LightSource
from matplotlib.patches import Circle
from ..extend import CACHE, ROWS
from ...hub_footprints.terrain import Terrain,RADIUS
from ...hub_footprints.survey import destination
from .fetch_regional import CACHE as REGIONAL
ROOT=Path(__file__).parent
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
    sites=read(ROOT.parent/'sites.csv')
    shots=[r for r in read(ROOT.parent/'missed_capture/shots.csv') if r['direction']=='east']+read(ROOT.parent/'missed_capture/opposite_tip.csv')
    summary=[]
    for sid,site in zip(ids,sites):
        lat0=float(site['hub_lat_deg']);lon0=float(site['hub_lon_deg_east']);r=float(site['actual_radius_km'])
        events=[]
        for q in [a for a in shots if a['site']==sid]:
            q=dict(q)
            if q['impact_lat_deg']:
                x,y=project(float(q['impact_lat_deg']),float(q['impact_lon_deg']),lat0,lon0)
                q.update(x_km=float(x),y_km=float(y),visible_local=bool(abs(x)<=7.5 and abs(y)<=7.5),visible_regional=bool(abs(x)<=40 and abs(y)<=40))
            events.append(q)
        large=any('x_km' in e and not e['visible_local'] and e['visible_regional'] for e in events)
        for side in ([15,80] if large else [15]):
            if args.regional_only and side==15:continue
            local=side==15;n=401 if local else 601
            axis,z=field(site,side,n,t.height if local else regional)
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
            notes=[]
            for q in events:
                direction='E' if q['direction']=='east' else 'W';color='#a83c32' if direction=='E' else '#7431a2'
                rx,ry=project(float(q['release_lat_deg']),float(q['release_lon_deg']),lat0,lon0)
                if max(abs(rx),abs(ry))<side/2:
                    ax.scatter(rx,ry,s=50,marker='^',facecolor='white',edgecolor=color,lw=1.3,zorder=6)
                if 'x_km' not in q:
                    notes.append(f'{direction}: starts below terrain (no valid impact)');continue
                dist=float(q['impact_distance_from_hub_km']);outcome='after missed catch' if q['status']=='return_impact' else 'outbound collision'
                visible=q['visible_local'] if local else q['visible_regional']
                notes.append(f'{direction}: {outcome}, {dist:,.2f} km from hub'+('' if visible else ' · outside map'))
                if visible:
                    x,y=q['x_km'],q['y_km'];ax.scatter(x,y,s=95,marker='X',c=color,edgecolor='white',lw=.8,zorder=9)
                    # Regional labels separate the two close-to-hub events.
                    offset=(14,18 if direction=='E' else -32) if not local else (-12 if x>side*.25 else 12,18 if y<0 else -28)
                    ax.annotate(f'{direction} impact',xy=(x,y),xytext=offset,textcoords='offset points',fontsize=9,color=color,ha='right' if offset[0]<0 else 'left',bbox=dict(fc='white',ec='none',alpha=.9,pad=2),arrowprops=dict(arrowstyle='-',color=color,lw=.7))
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
            fig.text(.1,.128,'▲ Release locations   × First impacts   |   E = useful payload; W = opposite-side counterpart',fontsize=9,va='top')
            fig.text(.1,.106,'\n'.join(notes),fontsize=9,linespacing=1.6,va='top')
            fig.text(.1,.038,('SLDEM2015 · ~59 m native grid' if local else 'LOLA LDEM64 · ~474 m native grid; context only')+'  |  Hillshade is synthetic illumination',fontsize=8,color='#5b6166')
            fig.text(.1,.019,'Footprint is a geometry overlay, not a demonstration of cable clearance. Impact coordinates reuse the saved model.',fontsize=8,color='#5b6166')
            stem=f'{sid}_{side}km';fig.savefig(ROOT/f'{stem}.png',dpi=180);fig.savefig(ROOT/f'{stem}.svg');plt.close(fig)
            p=ROOT/f'{stem}.svg';p.write_text('\n'.join(a.rstrip() for a in p.read_text().splitlines())+'\n')
            print(stem,flush=True)
        summary.append(dict(site=sid,track_radius_m=TRACK,tip_radius_km=r,regional_map=large,events=events))
    (ROOT/'map_index.json').write_text(json.dumps(summary,indent=2)+'\n')
    paths=[ROOT.parent/'sites.csv',ROOT.parent/'missed_capture/shots.csv',ROOT.parent/'missed_capture/opposite_tip.csv']
    (ROOT/'inputs.json').write_text(json.dumps({str(p.relative_to(ROOT.parent)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths},indent=2)+'\n')
if __name__=='__main__':main()
