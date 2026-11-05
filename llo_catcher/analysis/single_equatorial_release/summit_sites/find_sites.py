"""Nominate hilltops in 7 km disks, screen shifted hubs, and list spaced sites."""
from pathlib import Path
import csv
import json
import numpy as np
from .extend import CACHE, ROWS
from ..hub_footprints.terrain import Terrain, RADIUS, PPD
from ..hub_footprints.survey import destination
from .. import calculate as orbit

ROOT = Path(__file__).resolve().parent
KM_PER_DEG = np.deg2rad(1)*RADIUS/1000
BANDS = json.loads((ROOT.parent/'local_corridors/results.json').read_text())['both_ranges']
terrain = None

def band_at(lon):
    return next((b for b in BANDS if b['start_deg_east'] < lon < b['end_deg_east']), None)

def vertex_extrema(lat, lon, radius):
    sector = int(lon//45)
    tile = terrain.tiles[sector]
    pad = np.degrees(radius/(RADIUS-10000))+.003
    y = np.arange(max(0,int(ROWS-.5-(lat+pad)*PPD)),min(2*ROWS,int(ROWS-.5-(lat-pad)*PPD)+2))
    x = np.arange(int((lon-sector*45-pad)*PPD)-1,int((lon-sector*45+pad)*PPD)+2)
    phi = (ROWS-.5-y)/PPD
    lam = sector*45+(x+.5)/PPD
    hav = (np.sin(np.radians((phi[:,None]-lat)/2))**2 +
           np.cos(np.radians(lat))*np.cos(np.radians(phi[:,None]))*np.sin(np.radians((lam-lon)/2))**2)
    h = tile[np.ix_(y,x)].astype(float)*1000
    inside = (RADIUS+h)*2*np.sqrt(hav*(1-hav)) <= radius
    i,j = np.unravel_index(np.argmax(np.where(inside,h,-np.inf)),h.shape)
    return float(phi[i]),float(lam[j]),float(h[i,j]),float(h[inside].min())

def rim(lat, lon, radius, count=7200):
    bearings = np.linspace(0,2*np.pi,count,endpoint=False)
    angle = np.full(count,np.arcsin(radius/(RADIUS+float(terrain.height(lat,lon)))))
    for _ in range(4):
        y,x = destination(lat,lon,bearings,angle)
        h = terrain.height(y,x)
        angle = np.arcsin(radius/(RADIUS+h))
    y,x = destination(lat,lon,bearings,angle)
    h = terrain.height(y,x)
    return h,(RADIUS+h)*np.cos(angle)

def nominal_lat(lon, side):
    r = RADIUS+float(terrain.height(0.,lon))+10
    return side*np.degrees(np.arcsin(5000/r))

def candidates():
    nominated = {}
    step = 1/2048
    checks=0
    for b in BANDS:
        lo,hi=b['start_deg_east'],b['end_deg_east']
        anchors=np.unique(np.r_[lo+1e-8,np.arange(np.ceil(lo/step)*step,hi,step),(lo+hi)/2,hi-1e-8])
        for side in [-1,1]:
            for lon in anchors:
                checks+=1
                lat=nominal_lat(lon,side)
                sy,sx,sh,_=vertex_extrema(lat,lon,7000)
                if abs(sy-nominal_lat(sx,side))*KM_PER_DEG>2 or sy*side<=0:
                    continue
                key=(sy,sx)
                nominated.setdefault(key,[]).append((float(lon),float(lat),sh))
    return nominated,checks

def dms(value, positive, negative):
    total=round(abs(value)*3600,1)
    degrees=int(total//3600)
    minutes=int(total%3600//60)
    return f'{degrees}° {minutes:02d}′ {total%60:04.1f}″ {positive if value>=0 else negative}'

def screen(sy,sx,nominations):
    side=1 if sy>0 else -1
    z=float(terrain.height(sy,sx))
    _,_,high,low=vertex_extrema(sy,sx,5000)
    boundary,_=rim(sy,sx,5000)
    rise=max(high,boundary.max())-z
    # Require a local grid summit and the previously requested 10 m rise limit.
    offsets=np.arange(-1,2)/PPD
    neighbors=terrain.height(sy+offsets[:,None],sx+offsets[None,:])
    if rise>10 or neighbors.max()>z+.001:
        return None
    # Verify a nomination against the interpolated rim of its 7 km search disk.
    witness=None
    for lon,lat,_ in sorted(nominations,key=lambda a:abs(a[0]-sx)):
        edge,_=rim(lat,lon,7000)
        if edge.max()<=z+.001:
            witness=(lat,lon)
            break
    if witness is None:
        return None
    result=orbit.classify((sx,10.,True))
    r=result['release_radius_m']
    radius=r*np.sin(np.radians(abs(sy)))
    htip,projection=rim(sy,sx,radius,count=14400)
    gap=float(r*np.cos(np.radians(sy))-projection.max())
    longitude=(sx+180)%360-180
    return dict(hub_lat_deg=sy,hub_lon_deg_east=sx,hub_lon_signed_deg=longitude,
                hub_side='north' if sy>0 else 'south',latitude_dms=dms(sy,'N','S'),
                longitude_dms=dms(longitude,'E','W'),hub_elevation_m=z,
                shift_from_nominal_latitude_km=float((sy-nominal_lat(sx,side))*KM_PER_DEG),
                release_lon_deg_east=sx,actual_radius_km=float(radius/1000),
                required_rpm=float(result['surface_relative_release_speed_m_s']/radius*60/(2*np.pi)),
                sampled_max_rise_m=float(max(0,rise)),sampled_max_drop_m=float(z-min(low,boundary.min())),
                actual_horizontal_tip_min_clearance_m=gap,aligned_release_status=result['status'],
                inside_previous_corridor=bool(band_at(sx)),
                first_impact_time_min=result['impact_time_s']/60 if result['impact_time_s'] is not None else None,
                search_center_lat_deg=witness[0],search_center_lon_deg_east=witness[1])

def separation(a,b):
    lat1,lat2=np.radians([a['hub_lat_deg'],b['hub_lat_deg']])
    dlon=np.radians(a['hub_lon_deg_east']-b['hub_lon_deg_east'])
    hav=np.sin((lat1-lat2)/2)**2+np.cos(lat1)*np.cos(lat2)*np.sin(dlon/2)**2
    return float(2*RADIUS*np.arcsin(np.sqrt(hav))/1000)

def spaced(sites):
    accepted=[]
    for site in sorted(sites,key=lambda r:(r['hub_lon_deg_east'],r['hub_side'])):
        if any((a['hub_side']==site['hub_side'] and
                abs(site['hub_lon_deg_east']-a['hub_lon_deg_east'])*KM_PER_DEG < 7) or
               separation(site,a)<7 for a in accepted):
            continue
        accepted.append(site)
    return accepted

def write_decimal_coordinates(sites):
    counts={'north':0,'south':0}
    with (ROOT/'hub_coordinates.csv').open('w') as stream:
        writer=csv.writer(stream)
        writer.writerow(['site','latitude_deg','longitude_deg'])
        for site in sites:
            side=site['hub_side']
            counts[side]+=1
            writer.writerow([side[0].upper()+str(counts[side]),site['hub_lat_deg'],site['hub_lon_signed_deg']])

def main():
    global terrain
    terrain=Terrain(CACHE,ROWS)
    orbit.initialize()
    nominations,checks=candidates()
    screened=[]
    for (y,x),anchors in nominations.items():
        site=screen(y,x,anchors)
        if site is not None:
            screened.append(site)
    # Eastward skip on each band; also enforce true hub-to-hub spacing across sides.
    accepted=spaced(screened)
    aligned=spaced([x for x in screened if x['aligned_release_status']=='return_impact'])
    result=dict(search_anchor_count=checks,unique_nominees=len(nominations),verified_before_spacing=screened,
                sites=accepted,aligned_sites=aligned,spacing_km=7)
    (ROOT/'results.json').write_text(json.dumps(result,indent=2)+'\n')
    write_decimal_coordinates(accepted)
    if accepted:
        with (ROOT/'sites.csv').open('w') as f:
            w=csv.DictWriter(f,fieldnames=list(accepted[0]));w.writeheader();w.writerows(accepted)
    print('Search anchors, nominees, verified, retained:',checks,len(nominations),len(screened),len(accepted))
    for a in accepted:
        print(a['hub_side'],a['hub_lat_deg'],a['hub_lon_deg_east'],a['actual_radius_km'],a['actual_horizontal_tip_min_clearance_m'])

if __name__=='__main__':
    main()
