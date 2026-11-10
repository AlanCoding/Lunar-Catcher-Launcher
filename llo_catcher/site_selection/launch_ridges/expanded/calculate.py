"""Expand ridge seeds around all four featured regions and to +/-6 km latitude."""
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor
import json,time,csv,hashlib
import numpy as np
from ..calculate import solve,GlobalTerrain,RADIUS
ROOT=Path(__file__).resolve().parent
T=None

def initialize():
    global T
    T=GlobalTerrain()

def task(args):
    label,lon,ys=args;rows=[]
    for y in ys:
        r=solve(T,float(np.degrees(y/RADIUS)),lon)
        r['region']=label;r['source_north_m']=float(y)
        v=solve(T,r['contact_latitude_deg'],r['contact_longitude_deg'])
        r['contact_fresh_launch_extra_height_m']=v['extra_release_height_m'];rows.append(r)
    return rows

def main():
    source=ROOT.parent.parent/'featured_four/adjusted_hilltops/results.json'
    sites=json.loads(source.read_text())['sites'];tasks=[];regions=[]
    for i,s in enumerate(sites,1):
        center=1.5*round(s['longitude_deg_east']/1.5)
        lons=np.arange(center-6,center+6.01,1.5)
        ys=np.unique(np.r_[np.arange(-6000,6001,125),np.radians(s['hub_latitude_deg'])*RADIUS,s['near_equator_tip_offset_m']])
        regions.append(dict(label=f'P{i}',longitudes=lons.tolist(),north_positions_m=ys.tolist()))
        for lon in lons:tasks.append((f'P{i}',float(lon),ys.tolist()))
    rows=[];start=time.time()
    with ProcessPoolExecutor(max_workers=3,initializer=initialize) as pool:
        for result in pool.map(task,tasks):
            rows.extend(result);print(result[0]['region'],result[0]['start_longitude_deg'],len(rows),'samples;',round(time.time()-start),'s',flush=True)
            (ROOT/'progress.json').write_text(json.dumps(dict(completed_samples=len(rows),total_samples=sum(len(t[2]) for t in tasks))))
    d=dict(scope='Four regional longitude windows, each 12 degrees wide; +/-6 km seed latitude; eastward 25 km apoapsis',regions=regions,sites=sites,source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),rows=rows)
    (ROOT/'results.json').write_text(json.dumps(d,indent=2)+'\n')
    with (ROOT/'ridge_contacts.csv').open('w') as f:
        w=csv.DictWriter(f,fieldnames=rows[0]);w.writeheader();w.writerows(rows)
    (ROOT/'progress.json').unlink(missing_ok=True)
if __name__=='__main__':main()
