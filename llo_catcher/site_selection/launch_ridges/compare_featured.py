"""Compare the four adjusted sites with the regional contact groups; extend P1."""
import json,csv,hashlib
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from .calculate import ROOT,GlobalTerrain,RADIUS,solve
from ..featured_four.adjusted_hilltops.check_launches import trajectory
from llo_catcher.site_selection.support.maps import project

def main():
    source=ROOT.parent/'featured_four/adjusted_hilltops/results.json'
    sites=json.loads(source.read_text())['sites'];old=json.loads((ROOT/'results.json').read_text())['rows'];terrain=GlobalTerrain()
    s=sites[0];extension=[]
    for north in np.r_[np.arange(2000,3751,125),np.radians(s['hub_latitude_deg'])*RADIUS]:
        r=solve(terrain,np.degrees(north/RADIUS),15.)
        dx,dy=project(r['contact_latitude_deg'],r['contact_longitude_deg'],s['hub_latitude_deg'],s['longitude_deg_east'])
        r['distance_to_P1_hub_m']=float(np.hypot(dx,dy)*1000);extension.append(r)
    best=min(extension,key=lambda r:r['distance_to_P1_hub_m'])
    out=dict(adjusted_sites_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),seed_longitude_deg=15,extension=extension,closest_contact_to_P1=best)
    (ROOT/'featured_comparison.json').write_text(json.dumps(out,indent=2)+'\n')
    with (ROOT/'P1_ridge_extension.csv').open('w') as f:
        w=csv.DictWriter(f,fieldnames=extension[0]);w.writeheader();w.writerows(extension)
    # Regional terrain map; no claim of geological naming or global coverage.
    lon=np.linspace(16.09,16.23,320);north=np.linspace(-2.6,4.2,400)
    xx,yy=np.meshgrid(lon,north);z=terrain.height(np.degrees(yy*1000/RADIUS),xx)
    fig,ax=plt.subplots(figsize=(8,9),layout='constrained')
    im=ax.pcolormesh(xx,yy,z,cmap='gist_earth',shading='auto',rasterized=True)
    cs=ax.contour(xx,yy,z,levels=12,colors='black',linewidths=.4,alpha=.4);ax.clabel(cs,fmt='%d',fontsize=7)
    rr=sorted([r for r in old if r['start_longitude_deg']==15 and 16.09<r['contact_longitude_deg']<16.23],key=lambda r:r['contact_latitude_deg'])
    for rows,color,label in [(rr,'#80e4ff','Original mapped contact line'),(sorted(extension,key=lambda r:r['contact_latitude_deg']),'#f9b74b','Targeted northern extension')]:
        ax.plot([r['contact_longitude_deg'] for r in rows],np.radians([r['contact_latitude_deg'] for r in rows])*RADIUS/1000,'.-',color=color,lw=2,label=label)
    ax.scatter(s['longitude_deg_east'],np.radians(s['hub_latitude_deg'])*RADIUS/1000,marker='*',s=220,color='#d63146',edgecolor='white',zorder=6,label='P1 adjusted hub / summit')
    ax.scatter(s['longitude_deg_east'],s['near_equator_tip_offset_m']/1000,marker='^',s=90,color='white',edgecolor='black',zorder=6,label='P1 intended release point')
    ax.axhline(2,ls='--',color='white',lw=1);ax.axhline(-2,ls='--',color='white',lw=1)
    ax.set(xlabel='Longitude east (degrees)',ylabel='North of lunar equator (km)',title='P1 hilltop lies on the northern continuation\nof the contact ridge near 16.15° E')
    ax.legend(loc='lower left',fontsize=8);fig.colorbar(im,ax=ax,label='Terrain elevation above reference sphere (m)')
    for ext in ['png','svg']:fig.savefig(ROOT/f'P1_ridge_match.{ext}',dpi=180)
    plt.close(fig)
    print('P1 nearest contact separation (m):',best['distance_to_P1_hub_m'])
if __name__=='__main__':main()
