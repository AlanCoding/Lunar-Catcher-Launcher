"""Hill-first full-longitude search: local DEM peaks, tip rim, then two shots."""
from pathlib import Path
import csv,json
from concurrent.futures import ProcessPoolExecutor
import numpy as np
from scipy.ndimage import maximum_filter,minimum_filter
from llo_catcher.site_selection.support.terrain import CACHE,ROWS
from llo_catcher.site_selection.support.terrain import Terrain,RADIUS,PPD,COLS
from llo_catcher.site_selection.support.geometry import destination
from llo_catcher.site_selection.support import orbits
from ..support.constants import PLANE_OFFSET
OUT=Path(__file__).parent
class GlobalTerrain(Terrain):
    def __init__(self):
        self.rows=ROWS
        self.tiles={k:np.load(CACHE/f'{45*k:03d}.npy',mmap_mode='r') for k in range(8)}

def rim(terrain,lat,lon,arm,count):
    bearing=np.linspace(0,2*np.pi,count,endpoint=False)
    angle=np.full(count,np.arcsin(arm/(RADIUS+float(terrain.height(lat,lon)))))
    for _ in range(4):
        y,x=destination(lat,lon,bearing,angle)
        angle=np.arcsin(arm/(RADIUS+terrain.height(y,x)))
    y,x=destination(lat,lon,bearing,angle);h=terrain.height(y,x)
    return float(np.max((RADIUS+h)*np.cos(angle)))

def coarse_batch(terrain,items):
    values=np.asarray(items);lat,lon,z,arm=values.T
    bearing=np.linspace(0,2*np.pi,360,endpoint=False)[None,:]
    angle=np.broadcast_to(np.arcsin(arm/(RADIUS+z))[:,None],(len(items),360)).copy()
    for _ in range(4):
        y,x=destination(lat[:,None],lon[:,None],bearing,angle)
        angle=np.arcsin(arm[:,None]/(RADIUS+terrain.height(y,x)))
    y,x=destination(lat[:,None],lon[:,None],bearing,angle)
    return RADIUS+z+PLANE_OFFSET-np.max((RADIUS+terrain.height(y,x))*np.cos(angle),axis=1)

def peaks(terrain):
    # Native (~59m) grid, one-column halo gives longitude-seam continuity.
    for sector in range(8):
        a=np.concatenate([terrain.tiles[(sector-1)%8][:,-1:],terrain.tiles[sector],terrain.tiles[(sector+1)%8][:,:1]],axis=1)
        maxa=maximum_filter(a,size=3,mode='nearest');mina=minimum_filter(a,size=3,mode='nearest')
        good=(a==maxa)&(a>mina)
        # Deterministic tie suppression for adjacent equal-height maxima.
        for dy,dx in [(-1,-1),(-1,0),(-1,1),(0,-1)]:
            good &= a!=np.roll(np.roll(a,-dy,axis=0),-dx,axis=1)
        good[:1]=False;good[-1:]=False;good[:,0]=False;good[:,-1]=False
        yy,xx=np.where(good);lat=(ROWS-.5-yy)/PPD;lon=sector*45+(xx-1+.5)/PPD
        height=a[yy,xx].astype(float)*1000
        arm=(RADIUS+height+PLANE_OFFSET)*abs(np.tan(np.radians(lat)))
        valid=(arm>=3000)&(arm<=7000)
        yield sector,list(zip(lat[valid],lon[valid],height[valid],arm[valid]))

def shot(lon,height,direction):
    m=orbits.MODELS[direction];sign=1 if direction=='east' else -1
    r=m.classify((sign*lon%360,height,True))
    impact=r['impact_longitude_deg_east']
    return dict(status=r['status'],impact_time_min=None if r['impact_time_s'] is None else r['impact_time_s']/60,
        impact_longitude_deg=None if impact is None else (sign*impact+180)%360-180,
        catch_relative_speed_m_s=r['catch_relative_speed_m_s'])

def separation(a,b):
    p,q=np.radians([a['hub_latitude_deg'],b['hub_latitude_deg']]);dl=np.radians(a['hub_longitude_deg']-b['hub_longitude_deg'])
    return float(2*RADIUS*np.arcsin(np.sqrt(np.sin((p-q)/2)**2+np.cos(p)*np.cos(q)*np.sin(dl/2)**2)))

_WORK_TERRAIN=None
def worker_initialize():
    global _WORK_TERRAIN
    _WORK_TERRAIN=GlobalTerrain();orbits.initialize()
def evaluate_item(item):
    terrain=_WORK_TERRAIN
    lat,lon,z,arm=item
    plane=RADIUS+z+PLANE_OFFSET
    gap=plane-rim(terrain,lat,lon,arm,36000)
    if gap<0:return None
    if gap<1:
        gap=min(gap,plane-rim(terrain,lat,lon,arm,72000))
        if gap<0:return None
    if gap<.1:gap=min(gap,plane-rim(terrain,lat,lon,arm,144000))
    if gap<.01:return None # 1 cm numerical guard against a grazing sampled rim
    ground=float(terrain.height(0,lon));r=plane/np.cos(np.radians(lat));height=r-RADIUS-ground
    if height<=0:raise RuntimeError('Circle passed but release is underground')
    row=dict(hub_latitude_deg=float(lat),hub_longitude_deg=float((lon+180)%360-180),longitude_deg_east=float(lon),hub_elevation_m=float(z),arm_radius_km=float(arm/1000),tip_plane_offset_m=PLANE_OFFSET,min_tip_circle_clearance_m=float(gap),release_height_m=float(height))
    for d in ['east','west']:
        for key,value in shot(lon,height,d).items():row[d+'_'+key]=value
    return row

def main():
    terrain=GlobalTerrain();orbits.initialize();candidates=[];counts=[]
    for sector,items in peaks(terrain):
        survivors=[];coarse_items=[]
        print('Sector',sector,'native peaks',len(items),flush=True)
        for start in range(0,len(items),256):
            batch=items[start:start+256];gaps=coarse_batch(terrain,batch)
            coarse_items.extend(row for row,gap in zip(batch,gaps) if gap>=0)
        coarse=len(coarse_items)
        print('Sector',sector,'coarse rim passes',coarse,flush=True)
        with ProcessPoolExecutor(max_workers=4,initializer=worker_initialize) as pool:
            for i,row in enumerate(pool.map(evaluate_item,coarse_items,chunksize=8)):
                if row is not None:survivors.append(row)
                if i%200==0:print('Sector',sector,'fine',i,'/',coarse,'passed',len(survivors),flush=True)
        counts.append(dict(sector_west_deg=sector*45,native_local_peaks=len(items),coarse_circle_pass=coarse,fine_circle_pass=len(survivors)))
        candidates+=survivors
        (OUT/'progress.json').write_text(json.dumps(dict(sectors=counts,candidates=candidates),indent=2)+'\n')
        print(counts[-1],flush=True)
    finalize(candidates,counts)

def finalize(candidates,counts):
    # Keep ALL passing peaks in the table. Flag a reproducible spaced subset,
    # ranked by tip-circle clearance, independent of trajectory outcomes.
    chosen=[];chosen_xyz=[]
    chord=2*np.sin(7000/(2*RADIUS))
    for row in sorted(candidates,key=lambda r:(-r['min_tip_circle_clearance_m'],r['longitude_deg_east'],r['hub_latitude_deg'])):
        lat,lon=np.radians([row['hub_latitude_deg'],row['hub_longitude_deg']]);xyz=np.array([np.cos(lat)*np.cos(lon),np.cos(lat)*np.sin(lon),np.sin(lat)])
        row['selected_7km_subset']=bool(not chosen_xyz or np.all(np.linalg.norm(np.asarray(chosen_xyz)-xyz,axis=1)>=chord))
        if row['selected_7km_subset']:chosen.append(row);chosen_xyz.append(xyz)
    candidates.sort(key=lambda r:(r['longitude_deg_east'],r['hub_latitude_deg']))
    for i,row in enumerate(candidates,1):row['id']=f'H{i:04d}'
    def stats(rows):
        out=dict(count=len(rows),east_clear=sum(r['east_status']!='outbound_collision' for r in rows),west_clear=sum(r['west_status']!='outbound_collision' for r in rows),both_clear=sum(all(r[d+'_status']!='outbound_collision' for d in ['east','west']) for r in rows),neither_clear=sum(all(r[d+'_status']=='outbound_collision' for d in ['east','west']) for r in rows))
        for d in ['east','west']:
            for status in ['outbound_collision','return_impact','not_arrested']:out[d+'_'+status]=sum(r[d+'_status']==status for r in rows)
        return out
    result=dict(scope='All 360 degrees longitude; native-grid local maxima with 3-7 km arms to equatorial release; no prior launch-corridor filter',sectors=counts,all_peaks_stats=stats(candidates),spaced_subset_stats=stats(chosen),candidates=candidates)
    (OUT/'results.json').write_text(json.dumps(result,indent=2)+'\n')
    for name,rows in [('all_candidate_hills.csv',candidates),('spaced_candidate_hills.csv',[r for r in candidates if r['selected_7km_subset']])]:
        if rows:
            with (OUT/name).open('w') as f:
                w=csv.DictWriter(f,fieldnames=['id']+[k for k in rows[0] if k!='id']);w.writeheader();w.writerows(rows)
    (OUT/'progress.json').unlink(missing_ok=True)
    print(json.dumps(result['all_peaks_stats']),json.dumps(result['spaced_subset_stats']),flush=True)
if __name__=='__main__':main()
