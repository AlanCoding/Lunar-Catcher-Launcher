"""Five-kilometre north/south hub terrain screening near accepted corridors."""
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor
import json,csv
import numpy as np
from scipy.optimize import minimize_scalar
from .terrain import Terrain,RADIUS,PPD
ROOT=Path(__file__).resolve().parent
L=5000.
T=None

def initialize():
    global T
    T=Terrain()

def destination(lat,lon,bearing,angle):
    phi=np.radians(lat);lam=np.radians(lon)
    p=np.arcsin(np.sin(phi)*np.cos(angle)+np.cos(phi)*np.sin(angle)*np.cos(bearing))
    q=lam+np.arctan2(np.sin(bearing)*np.sin(angle)*np.cos(phi),np.cos(angle)-np.sin(phi)*np.sin(p))
    return np.degrees(p),np.degrees(q)

def evaluate(args):
    lon,sign,refine=args
    release_h=float(T.height(0.,lon));rrelease=RADIUS+release_h+10.
    phi=sign*np.arcsin(L/rrelease);lat=np.degrees(phi);hub_h=float(T.height(lat,lon))
    plane=rrelease*np.cos(phi)
    # Sample all DEM vertices in a box enclosing the projected 5 km disk.
    # Fine mode includes half-grid interior samples and a tenfold finer rim.
    ppd=PPD
    ys=(np.arange(int(np.floor((lat-.18)*ppd)),int(np.ceil((lat+.18)*ppd))+1)+.5)/ppd
    xs=(np.arange(int(np.floor((lon-.18)*ppd)),int(np.ceil((lon+.18)*ppd))+1)+.5)/ppd
    if refine:
        ys=np.sort(np.r_[ys,(ys[:-1]+ys[1:])/2]);xs=np.sort(np.r_[xs,(xs[:-1]+xs[1:])/2])
    ys=ys[np.abs(ys)<=(176-.5)/PPD]
    yy,xx=np.meshgrid(ys,xs,indexing='ij');h=T.height(yy,xx)
    cosine=np.sin(phi)*np.sin(np.radians(yy))+np.cos(phi)*np.cos(np.radians(yy))*np.cos(np.radians(xx-lon))
    q=(RADIUS+h)*np.sqrt(np.maximum(0,1-cosine*cosine));mask=q<=L
    heights=h[mask];coords=np.c_[yy[mask],xx[mask]];projected=(RADIUS+heights)*cosine[mask]
    bearings=np.linspace(0,2*np.pi,7200 if refine else 720,endpoint=False)
    theta=np.full_like(bearings,np.arcsin(L/(RADIUS+hub_h)))
    for _ in range(4):
        ry,rx=destination(lat,lon,bearings,theta);rh=T.height(ry,rx);theta=np.arcsin(L/(RADIUS+rh))
    ry,rx=destination(lat,lon,bearings,theta);rh=T.height(ry,rx)
    allh=np.r_[heights,rh,hub_h];allxy=np.vstack([coords,np.c_[ry,rx],[[lat,lon]]]);i=int(np.argmax(allh))
    highest=float(allh[i]);lowest=float(allh.min());rim_proj=(RADIUS+rh)*np.cos(theta)
    return dict(release_longitude_deg_east=float(lon),hub_side='north' if sign>0 else 'south',hub_latitude_deg=float(lat),hub_longitude_deg_east=float(lon),
        release_ground_elevation_m=release_h,hub_ground_elevation_m=hub_h,
        maximum_rise_above_hub_m=highest-hub_h,maximum_drop_below_hub_m=hub_h-lowest,total_relief_m=highest-lowest,
        highest_terrain_latitude_deg=float(allxy[i,0]),highest_terrain_longitude_deg=float(allxy[i,1]),
        tip_ring_minimum_clearance_m=float(plane-rim_proj.max()),flat_disk_minimum_clearance_m=float(plane-max(projected.max(),rim_proj.max(),RADIUS+hub_h)),
        tip_plane_height_above_hub_ground_m=float(plane-(RADIUS+hub_h)),
        passes_10m_rise=bool(highest-hub_h<=10),refined_terrain=bool(refine))

def refine_candidate(args):
    lon,sign,lo,hi=args;step=1/1024
    left=max(lo+1e-7,lon-step);right=min(hi-1e-7,lon+step)
    objective=lambda x:evaluate((x,sign,False))['maximum_rise_above_hub_m']
    opt=minimize_scalar(objective,bounds=(left,right),method='bounded',options={'xatol':1e-9})
    candidates=[left,right,lon,float(opt.x)]
    best=min(candidates,key=objective)
    return evaluate((best,sign,True))


def run():
    initialize();corr=json.loads((ROOT.parent/'local_corridors/results.json').read_text())['both_ranges'];step=1/1024
    samples=[]
    for i,b in enumerate(corr):
        lo=b['start_deg_east'];hi=b['end_deg_east']
        lons=np.unique(np.r_[np.arange(np.ceil(lo/step)*step,hi,step),(lo+hi)/2,lo+1e-7,hi-1e-7])
        samples += [(float(lon),side,False) for lon in lons for side in [1,-1]]
    results=[]
    with ProcessPoolExecutor(max_workers=4,initializer=initialize) as pool:
        for i,row in enumerate(pool.map(evaluate,samples,chunksize=4)):
            results.append(row)
            if (i+1)%500==0:print(f'{i+1}/{len(samples)} footprints',flush=True)
        # Refine terrain and circle sampling at best representatives of each
        # corridor and side; these also cover every corridor with a coarse pass.
        best=[]
        for b in corr:
            for side in ['north','south']:
                group=[x for x in results if x['hub_side']==side and b['start_deg_east']<x['release_longitude_deg_east']<b['end_deg_east']]
                row=min(group,key=lambda x:x['maximum_rise_above_hub_m'])
                best.append((row['release_longitude_deg_east'],1 if side=='north' else -1,b['start_deg_east'],b['end_deg_east']))
        refined=list(pool.map(refine_candidate,best,chunksize=1))
    refined.sort(key=lambda x:(x['maximum_rise_above_hub_m'],x['total_relief_m']))
    output=dict(footprint_radius_m=L,maximum_allowed_rise_m=10.,release_height_m=10.,longitude_sample_spacing_deg=step,
        longitude_sample_spacing_m=step*np.pi/180*RADIUS,coarse_footprints=len(results),coarse_pass_count=sum(x['passes_10m_rise'] for x in results),
        refined_best_per_corridor_side=refined,refined_pass_count=sum(x['passes_10m_rise'] for x in refined))
    (ROOT/'results.json').write_text(json.dumps(output,indent=2)+'\n')
    with (ROOT/'footprints.csv').open('w') as f:
        w=csv.DictWriter(f,fieldnames=list(results[0]));w.writeheader();w.writerows(results)
    print('BEST',json.dumps(refined[:5]),flush=True)
    print('COUNTS',output['coarse_footprints'],output['coarse_pass_count'],output['refined_pass_count'],flush=True)

if __name__=='__main__':run()
