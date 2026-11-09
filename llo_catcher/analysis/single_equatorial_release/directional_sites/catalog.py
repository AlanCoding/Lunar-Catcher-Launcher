"""Repeat hilltop nomination for west corridors and check both release directions."""
from pathlib import Path
import json,csv
from types import SimpleNamespace
import numpy as np
from . import orbits
from ..summit_sites import find_sites as old
OUT=Path(__file__).parent

def decorate(site,identifier,origin):
    result=dict(site);result['id']=identifier;result['search_direction']=origin
    for direction in ['east','west']:
        r=orbits.classify(site['hub_lon_deg_east'],direction,True)
        for key in ['status','impact_time_s','impact_longitude_deg_east','catch_time_s','catch_relative_speed_m_s','surface_relative_release_speed_m_s']:
            result[direction+'_'+key]=r[key]
        result[direction+'_rpm']=r['surface_relative_release_speed_m_s']/(site['actual_radius_km']*1000)*60/(2*np.pi)
        if r['impact_longitude_deg_east'] is not None:
            lon=r['impact_longitude_deg_east'];result[direction+'_impact_longitude_deg']=(lon+180)%360-180
            result[direction+'_impact_latitude_deg']=0.
            result[direction+'_impact_distance_from_hub_km']=old.separation(site,dict(hub_lat_deg=0.,hub_lon_deg_east=lon))
        else:
            for key in ['impact_longitude_deg','impact_latitude_deg','impact_distance_from_hub_km']:result[direction+'_'+key]=None
    result['both_equatorial_directions_clear']=all(result[d+'_status']!='outbound_collision' for d in ['east','west'])
    result['full_tip_circle_clear']=site['actual_horizontal_tip_min_clearance_m']>=0
    return result

def main():
    orbits.initialize();old.terrain=old.Terrain(old.CACHE,old.ROWS)
    old.BANDS=json.loads((OUT/'west_corridors.json').read_text())['bands']
    old.orbit=SimpleNamespace(classify=lambda args:orbits.classify(args[0],'west',args[2]))
    nominees,count=old.candidates();print('West anchors/nominees',count,len(nominees),flush=True)
    screened=[]
    for k,((y,x),anchors) in enumerate(nominees.items()):
        site=old.screen(y,x,anchors)
        if site is not None:screened.append(site)
        if k%25==0:print('Screened',k,'passed',len(screened),flush=True)
    accepted=old.spaced(screened)
    original=json.loads((old.ROOT/'results.json').read_text())['sites']
    rows=[]
    for origin,sites,prefix in [('east',original,'E'),('west',accepted,'W')]:
        counts={'north':0,'south':0}
        for s in sites:
            side=s['hub_side'];counts[side]+=1
            rows.append(decorate(s,f'{prefix}-{side[0].upper()}{counts[side]}',origin))
    qualified=old.spaced([s for s in screened if s['aligned_release_status']!='outbound_collision'])
    # Retain a separate qualified list: a rejected trajectory cannot exclude a
    # usable neighbor just by winning the terrain-only spacing pass.
    out=dict(assumptions=dict(height_m=10,catcher_altitude_m=25000,max_orbits=1.5,opposite_direction='Reverse rotation; same equatorial release point, not opposite tip'),west_search=dict(anchors=count,nominees=len(nominees),verified_summits=len(screened),spaced_summits=len(accepted)),sites=rows,west_all_verified=screened,west_outbound_qualified_spaced=qualified)
    (OUT/'catalog.json').write_text(json.dumps(out,indent=2)+'\n')
    for direction in ['east','west']:
        selected=[r for r in rows if r['search_direction']==direction]
        if selected:
            with (OUT/f'{direction}_sites.csv').open('w') as f:
                writer=csv.DictWriter(f,fieldnames=list(selected[0]));writer.writeheader();writer.writerows(selected)
    print(json.dumps(out['west_search']),flush=True)
    for r in rows:print(r['id'],r['hub_lat_deg'],r['hub_lon_signed_deg'],r['east_status'],r['west_status'],r['actual_horizontal_tip_min_clearance_m'],flush=True)
if __name__=='__main__':main()
