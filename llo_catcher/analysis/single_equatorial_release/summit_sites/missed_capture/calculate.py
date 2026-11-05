"""Paired due-east/west ballistic shots for six summit hubs."""
import csv
import json
from pathlib import Path
import numpy as np
from scipy.optimize import brentq, minimize_scalar
from ....terrain.impact_demo import MU, MOON_OMEGA, RADIUS, state, ground_coordinates
from ....terrain.sweep_equator import first_impact_bounded
from ....terrain.terrain_band import TerrainBand
from ... import calculate as equator
from ...hub_footprints.terrain import Terrain
from ..extend import CACHE, ROWS

ROOT = Path(__file__).resolve().parent
IDS = ('S1','S2','S3','N1','S4','N2')

def signed(lon):
    return float((lon+180)%360-180)

class Heights:
    def __init__(self):
        self.wide = Terrain(CACHE,ROWS)
        self.wide.tiles[7]=np.load(CACHE/'315.npy',mmap_mode='r')
        self.global_strip = TerrainBand()
        self.max_height_m = 20000.  # Conservative broad-phase search ceiling.

    def height_m(self, lat, lon):
        lat,lon=np.broadcast_arrays(lat,lon)
        shape=lat.shape
        lat,lon=lat.ravel(),lon.ravel()%360
        wide=(lon>=135.002)&(lon<359.998)
        z=np.empty(len(lat))
        if np.any(wide):
            z[wide]=self.wide.height(lat[wide],lon[wide])
        if np.any(~wide):
            z[~wide]=self.global_strip.height_m(lat[~wide],lon[~wide])
        return z.reshape(shape)

def release(site, direction, dem, mirrored=False):
    lon=site['hub_lon_deg_east']
    phi=np.radians(site['hub_lat_deg'])
    arm=site['actual_radius_km']*1000
    if direction=='east':
        lat=0.
    elif mirrored:
        lat=2*phi
    else:
        side=np.sign(phi)
        def tip_radius(delta):
            tip=phi+side*delta
            r=RADIUS+10+float(dem.height_m(np.degrees(tip),lon))
            return r*np.sin(delta)-arm
        lat=phi+side*brentq(tip_radius,.98*abs(phi),1.02*abs(phi),xtol=1e-15)
    height_lat=0. if mirrored else np.degrees(lat)
    rp=RADIUS+10+float(dem.height_m(height_lat,lon))
    if direction=='east':
        ra=RADIUS+25000
        e=(ra-rp)/(ra+rp)
    else:
        # Set the semilatus rectum to the equatorial catcher radius.
        e=(RADIUS+35000)/rp-1
    assert 0<e<1
    a=rp/(1-e)
    T=2*np.pi*np.sqrt(a**3/MU)
    node_E=np.arccos(e)
    catch=T/2 if direction=='east' else (node_E-e*np.sin(node_E))*T/(2*np.pi)
    return dict(longitude_deg_east=lon,release_latitude_deg=float(np.degrees(lat)),site=direction,
        rhat=[np.cos(lat),0.,np.sin(lat)],q=[0.,1. if direction=='east' else -1.,0.],
        periapsis_radius_m=rp,apoapsis_radius_m=a*(1+e),semimajor_axis_m=a,eccentricity=e,
        ideal_catch_time_s=catch,inertial_release_speed_m_s=np.sqrt(MU*(1+e)/rp),
        period_s=T,max_orbits=1.5)

def hub_ground_distance(lat,lon,site):
    p,q=np.radians([lat,site['hub_lat_deg']])
    dlon=np.radians(lon-site['hub_lon_deg_east'])
    hav=np.sin((p-q)/2)**2+np.cos(p)*np.cos(q)*np.sin(dlon/2)**2
    return float(2*RADIUS*np.arcsin(np.sqrt(hav))/1000)

def relative_position(sol, site, times):
    pos,_=state(sol,times)
    angle=MOON_OMEGA*np.asarray(times)
    radial=pos[...,0]*np.cos(angle)+pos[...,1]*np.sin(angle)
    east=-pos[...,0]*np.sin(angle)+pos[...,1]*np.cos(angle)
    phi=np.radians(site['hub_lat_deg'])
    north=pos[...,2]*np.cos(phi)-radial*np.sin(phi)
    axial=radial*np.cos(phi)+pos[...,2]*np.sin(phi)
    return np.hypot(east,north),axial

def sweep(sol,site,end):
    # Closest approach in the hub's transverse plane. Include sub-sample
    # minima on any later near pass, even when a narrow entry is between samples.
    arm=site['actual_radius_km']*1000
    times=np.linspace(0,end,max(5,int(np.ceil(end))+1))
    q,z=relative_position(sol,site,times)
    assert abs(float(q[0])-arm)<1e-5
    candidates=[]
    minima=np.flatnonzero((q[1:-1]<=q[:-2])&(q[1:-1]<=q[2:]))+1
    for i in minima:
        if z[i]>0 and q[i]<arm+5000:
            best=minimize_scalar(lambda t:relative_position(sol,site,t)[0],bounds=(times[i-1],times[i+1]),method='bounded')
            candidates.append((float(best.x),float(best.fun)))
    # The trajectory is symmetric in time about release (apart from longitude
    # wrap). Check departure curvature, the endpoint, and later local minima.
    q_near,_=relative_position(sol,site,min(end,.01))
    assert q_near>arm
    reentered=bool((z[-1]>0 and q[-1]<arm-1e-5) or any(d<arm-1e-5 for t,d in candidates))
    events=[]
    plane=float(relative_position(sol,site,0.)[1])
    for t,d in candidates:
        if d>=arm-1e-5:
            continue
        gap=lambda u:float(relative_position(sol,site,u)[0])-arm
        lo=brentq(gap,max(.001,t-15),t)
        hi=brentq(gap,t,min(end,t+15)) if gap(min(end,t+15))>=0 else end
        height=lambda u:float(relative_position(sol,site,u)[1])-plane
        minimum=min(height(lo),height(hi),minimize_scalar(height,bounds=(lo,hi),method='bounded').fun)
        maximum=max(height(lo),height(hi),-minimize_scalar(lambda u:-height(u),bounds=(lo,hi),method='bounded').fun)
        events.append(dict(entry_min=lo/60,exit_min=hi/60,duration_s=hi-lo,
            penetration_m=arm-d,min_height_above_tip_plane_m=minimum,max_height_above_tip_plane_m=maximum,
            crosses_ideal_tip_plane=bool(minimum<=0<=maximum)))
    assert bool(events)==reentered
    return dict(sweep_radius_km=arm/1000,post_release_disk_entry=reentered,
        final_projected_radius_km=float(q[-1]/1000),
        impact_edge_margin_m=float(q[-1]-arm) if z[-1]>0 else None,
        inside_disk_at_end=bool(z[-1]>0 and q[-1]<=arm),
        later_near_pass_minima=candidates,sweep_events=events)

def calculate(site_id,site,direction,dem,mirrored=False):
    sol=release(site,direction,dem,mirrored)
    release_gap=float(sol['periapsis_radius_m']-RADIUS-dem.height_m(sol['release_latitude_deg'],site['hub_lon_deg_east']))
    if release_gap<=0:
        return dict(site=site_id,direction=direction,release_geometry='equal_plane',release_clearance_m=release_gap,
            release_lat_deg=sol['release_latitude_deg'],release_lon_deg=signed(site['hub_lon_deg_east']),status='no_clear_release',
            reaches_catcher=False,impact_time_min=None,impact_lat_deg=None,impact_lon_deg=None,impact_distance_from_hub_km=None,post_release_disk_entry=None)
    if direction=='east':
        answer=equator.classify((site['hub_lon_deg_east'],10.,True))
        status=answer['status'];t=answer['impact_time_s']
    else:
        hit=first_impact_bounded(sol,dem,.5)
        fine=first_impact_bounded(sol,dem,.25)
        assert hit['status']==fine['status']
        t=fine['impact_time_s']
        if t is not None:assert abs(hit['impact_time_s']-t)<.001
        status={'arrested_after_missed_capture':'return_impact','outbound_collision':'outbound_collision','not_arrested':'not_arrested'}[fine['status']]
    end=t if t is not None else 1.5*sol['period_s']
    lat,lon,r=ground_coordinates(sol,end)
    if t is not None:
        assert abs(float(r)-RADIUS-float(dem.height_m(lat,lon)))<.001
    catch_lat,_,catch_r=ground_coordinates(sol,sol['ideal_catch_time_s'])
    assert abs(float(catch_lat))<1e-9 and abs(float(catch_r)-RADIUS-(25000 if direction=='east' else 35000))<1e-5
    row=dict(site=site_id,direction=direction,hub_lat_deg=site['hub_lat_deg'],hub_lon_deg=signed(site['hub_lon_deg_east']),
        release_lat_deg=sol['release_latitude_deg'],release_lon_deg=signed(site['hub_lon_deg_east']),
        release_geometry='equal_plane' if mirrored else 'local_10m',release_clearance_m=release_gap,
        status=status,reaches_catcher=status!='outbound_collision',catch_time_min=sol['ideal_catch_time_s']/60,
        impact_time_min=None if t is None else float(t/60),impact_lat_deg=None if t is None else float(lat),
        impact_lon_deg=None if t is None else signed(lon),impact_distance_from_hub_km=None if t is None else hub_ground_distance(lat,lon,site),
        cutoff_min=1.5*sol['period_s']/60,**sweep(sol,site,end))
    row['target_surface_speed_m_s']=float(sol['inertial_release_speed_m_s'] +
        (-1 if direction=='east' else 1)*MOON_OMEGA*sol['periapsis_radius_m']*np.cos(np.radians(sol['release_latitude_deg'])))
    row['target_rpm']=row['target_surface_speed_m_s']/(row['sweep_radius_km']*1000)*60/(2*np.pi)
    return row

def main():
    equator.initialize()
    dem=Heights()
    sites=json.loads((ROOT.parent/'results.json').read_text())['sites']
    rows=[]
    for name,site in zip(IDS,sites,strict=True):
        for direction in ['east','west']:
            row=calculate(name,site,direction,dem)
            rows.append(row)
            print(name,direction,row['status'],row['impact_lat_deg'],row['impact_lon_deg'],row['impact_distance_from_hub_km'],row['post_release_disk_entry'],flush=True)
    mirrors=[]
    for name,site in zip(IDS,sites,strict=True):
        row=calculate(name,site,'west',dem,mirrored=True)
        mirrors.append(row)
        print('mirror',name,row['status'],row['impact_distance_from_hub_km'],flush=True)
    for name,site,row in zip(IDS,sites,mirrors,strict=True):
        phi=np.radians(site['hub_lat_deg'])
        east=release(site,'east',dem)
        radius=east['periapsis_radius_m']
        u=east['inertial_release_speed_m_s']-MOON_OMEGA*radius
        vi=u-MOON_OMEGA*radius*np.cos(2*phi)
        row['node_altitude_equal_east_rpm_m']=float((radius*vi)**2/MU-RADIUS)
    (ROOT/'mirrored_west.json').write_text(json.dumps(mirrors,indent=2)+'\n')
    (ROOT/'results.json').write_text(json.dumps(rows,indent=2)+'\n')
    with (ROOT/'shots.csv').open('w') as f:
        cols=[key for key in rows[0] if key not in ('later_near_pass_minima','sweep_events')]
        writer=csv.DictWriter(f,fieldnames=cols,extrasaction='ignore');writer.writeheader();writer.writerows(rows)
    with (ROOT/'opposite_tip.csv').open('w') as f:
        writer=csv.DictWriter(f,fieldnames=cols+['node_altitude_equal_east_rpm_m'],extrasaction='ignore')
        writer.writeheader();writer.writerows(mirrors)

if __name__=='__main__':
    main()
