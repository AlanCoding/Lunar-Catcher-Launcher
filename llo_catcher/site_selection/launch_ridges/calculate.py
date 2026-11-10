"""Regional eastward launch-height envelope and limiting-terrain ridge demo."""
from pathlib import Path
import json,csv,time
import numpy as np
from scipy.optimize import minimize_scalar
from ..global_hills.search import GlobalTerrain,RADIUS
from ..featured_four.adjusted_hilltops.check_launches import trajectory
ROOT=Path(__file__).resolve().parent
RA=RADIUS+25000

def solve(terrain,lat,lon,step=120):
    ground=float(terrain.height(lat,lon));rp=RADIUS+ground
    f=np.linspace(0,np.pi,int(np.ceil(np.pi*RA/step))+1)
    # At fixed anomaly the required periapsis radius is algebraic. Iterate
    # only because lunar rotation changes the terrain longitude with flight time.
    def required(ff,r):
        y,x,_,_=trajectory(lat,lon,r,1)(ff);q=RADIUS+terrain.height(y,x);c=np.cos(ff)
        return q*RA*(1+c)/(2*RA-q*(1-c))
    for it in range(20):
        needed=required(f,rp);j=int(np.argmax(needed));a=f[max(j-1,0)];b=f[min(j+1,len(f)-1)]
        opt=minimize_scalar(lambda v:-float(required(v,rp)),bounds=(a,b),method='bounded',options={'xatol':1e-12})
        new=max(RADIUS+ground,float(needed[j]),-float(opt.fun))
        if abs(new-rp)<.002:rp=new;break
        rp=new
    else:raise RuntimeError('Height-envelope iteration did not converge')
    # Dense verification of the entire outbound path, plus refine its worst gap.
    fine=np.linspace(0,np.pi,int(np.ceil(np.pi*RA/30))+1)
    def gap(ff):
        y,x,r,t=trajectory(lat,lon,rp,1)(ff);return r-RADIUS-terrain.height(y,x)
    g=gap(fine);k=int(np.argmin(g))
    opt=minimize_scalar(lambda v:float(gap(v)),bounds=(fine[max(0,k-1)],fine[min(k+1,len(fine)-1)]),method='bounded',options={'xatol':1e-12})
    ff=float(opt.x) if opt.fun<g[k] else float(fine[k]);minimum=min(float(opt.fun),float(g[k]))
    if minimum<-.1 and step>30:return solve(terrain,lat,lon,30)
    assert minimum>-.1,(lat,lon,minimum)
    y,x,r,t=trajectory(lat,lon,rp,1)(ff)
    return dict(start_latitude_deg=float(lat),start_longitude_deg=float(lon),ground_elevation_m=ground,
      required_release_elevation_m=float(rp-RADIUS),extra_release_height_m=float(rp-RADIUS-ground),
      contact_latitude_deg=float(y),contact_longitude_deg=float(x),contact_elevation_m=float(terrain.height(y,x)),
      contact_anomaly_deg=float(np.degrees(ff)),contact_time_min=float(t/60),minimum_gap_m=minimum,iterations=it+1)

def main():
    terrain=GlobalTerrain();rows=[];start=time.time()
    lons=np.arange(12,24.01,1.5);ys=np.arange(-2000,2001,125)
    for lon in lons:
        for y in ys:
            r=solve(terrain,np.degrees(y/RADIUS),lon)
            r['source_north_m']=float(y)
            # Fresh horizontal periapsis departure from the limiting terrain.
            v=solve(terrain,r['contact_latitude_deg'],r['contact_longitude_deg'])
            r['contact_fresh_launch_extra_height_m']=v['extra_release_height_m']
            rows.append(r)
        print('Longitude',lon,'complete; elapsed',round(time.time()-start),flush=True)
    d=dict(scope='Regional demo; 12–24 degrees east seed longitudes, +/-2 km latitude band; east only',seed_longitudes_deg=lons.tolist(),latitude_spacing_m=125,apoapsis_altitude_m=25000,rows=rows)
    (ROOT/'results.json').write_text(json.dumps(d,indent=2)+'\n')
    with (ROOT/'ridge_contacts.csv').open('w') as f:
        w=csv.DictWriter(f,fieldnames=rows[0]);w.writeheader();w.writerows(rows)
if __name__=='__main__':main()
