"""Check direction reflection and contacts against inertial Cartesian dynamics."""
from pathlib import Path
import json
import numpy as np
from scipy.integrate import solve_ivp
from . import orbits
OUT=Path(__file__).parent

def main():
    orbits.initialize();east=orbits.MODELS['east'];west=orbits.MODELS['west']
    lon=np.linspace(-720,720,1003)
    reflection=float(np.max(abs(east.terrain(np.radians(lon))-west.terrain(np.radians(-lon)))))
    assert reflection<1e-5
    records=[]
    cat=json.loads((OUT/'catalog.json').read_text()) if (OUT/'catalog.json').exists() else {'sites':[]}
    longitudes=sorted(set([177.,194.,144.,294.]+[s['hub_lon_deg_east'] for s in cat['sites']]))
    for lon in longitudes:
        for direction,sign in [('east',1),('west',-1)]:
            r=orbits.classify(lon,direction);fine=orbits.classify(lon,direction,True)
            assert r['status']==fine['status']
            if r['impact_time_s'] is None:continue
            assert abs(r['impact_time_s']-fine['impact_time_s'])<1e-5
            t=r['impact_time_s'];rp=r['release_radius_m'];v=r['inertial_release_speed_m_s']
            def rhs(t,y):return np.r_[y[3:],-east.MU*y[:3]/np.linalg.norm(y[:3])**3]
            sol=solve_ivp(rhs,(0,t),[rp,0,0,0,sign*v,0],method='DOP853',rtol=1e-12,atol=1e-8,max_step=20)
            assert sol.success
            pos=sol.y[:3,-1];angle=np.radians(lon)+np.arctan2(pos[1],pos[0])-east.MOON_OMEGA*t
            gap=float(np.linalg.norm(pos)-east.RADIUS-east.terrain(angle))
            err=float(abs((np.degrees(angle)-r['impact_longitude_deg_east']+180)%360-180))
            assert abs(gap)<.001 and err<1e-7
            records.append(dict(longitude=lon,direction=direction,contact_gap_m=gap,longitude_error_deg=err))
    from ..summit_sites import find_sites as hills
    hills.terrain=hills.Terrain(hills.CACHE,hills.ROWS)
    terrain_checks=[]
    for site in cat.get('west_all_verified',[]):
        y,x,z=site['hub_lat_deg'],site['hub_lon_deg_east'],site['hub_elevation_m']
        for cy,cx,radius in [(y,x,5000),(site['search_center_lat_deg'],site['search_center_lon_deg_east'],7000)]:
            edge,_=hills.rim(cy,cx,radius,36000)
            _,_,inside,_=hills.vertex_extrema(cy,cx,radius)
            rise=float(max(edge.max(),inside)-z)
            assert rise <= (10. if radius==5000 else .001)
            terrain_checks.append(rise)
        _,projection=hills.rim(y,x,site['actual_radius_km']*1000,36000)
        r=east.RADIUS+float(hills.terrain.height(0,x))+10
        gap=float(r*np.cos(np.radians(y))-projection.max())
        assert abs(gap-site['actual_horizontal_tip_min_clearance_m'])<1
    west_sites=[s for s in cat['sites'] if s['search_direction']=='west']
    from itertools import combinations
    assert all(hills.separation(a,b)>=7 for a,b in combinations(west_sites,2))
    out=dict(reflected_terrain_max_error_m=reflection,independent_cartesian_contacts=records,
        west_terrain_finer_rim_bearings=36000,west_max_rise_checks_m=terrain_checks,west_spacing_verified=True)
    (OUT/'validation.json').write_text(json.dumps(out,indent=2)+'\n')
    print('Validated',len(records),'Cartesian contacts; max gap',max(abs(r['contact_gap_m']) for r in records))
if __name__=='__main__':main()
