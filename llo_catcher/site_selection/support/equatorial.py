"""Equatorial prograde release-height survey, with exact piecewise-linear DEM cells.

No finite sling offset; release at periapsis and capture at 25 km apoapsis.
All post-miss trajectories stop at first impact or 1.5 payload periods.
"""
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor
import json, csv, hashlib
import numpy as np
from scipy.optimize import brentq
from llo_catcher.site_selection.support.terrain import Terrain, ROWS, RADIUS
from llo_catcher.site_selection.support.constants import MU, MOON_OMEGA

OUT=Path(__file__).resolve().parent
RC=RADIUS+25000.
STEP=2*np.pi/(360*512)
_GROUND=None

def initialize():
    global _GROUND
    band=Terrain()
    _GROUND=np.concatenate([.5*(a[ROWS-1].astype(float)+a[ROWS].astype(float))*1000 for a in band.tiles.values()])


def terrain(lon):
    u=np.asarray(lon)/STEP-.5;i=np.floor(u).astype(np.int64);w=u-i
    return (1-w)*_GROUND[i%len(_GROUND)]+w*_GROUND[(i+1)%len(_GROUND)]


def orbit(lon_deg,height):
    lon=np.radians(lon_deg);ground=float(terrain(lon));rp=RADIUS+ground+height
    assert 0<rp<RC
    a=(rp+RC)/2;e=(RC-rp)/(RC+rp);p=rp*(1+e);h=np.sqrt(MU*p);n=np.sqrt(MU/a**3)
    return dict(lon=lon,height=height,ground=ground,rp=rp,a=a,e=e,p=p,h=h,n=n,T=2*np.pi/n)


def motion(f,o):
    f=np.asarray(f);wrapped=f%(2*np.pi)
    E=np.arctan2(np.sqrt(1-o['e']**2)*np.sin(wrapped),o['e']+np.cos(wrapped))%(2*np.pi)
    t=(E-o['e']*np.sin(E)+2*np.pi*np.floor(f/(2*np.pi)))/o['n']
    r=o['p']/(1+o['e']*np.cos(f))
    return r,t


def at_longitude(x,o):
    """Invert monotonic body-fixed angular travel x=f-Omega*t(f)."""
    x=np.asarray(x);f=x/(1-MOON_OMEGA/o['n'])
    for _ in range(4):
        r,t=motion(f,o);f-=(f-MOON_OMEGA*t-x)/(1-MOON_OMEGA*r*r/o['h'])
    r,t=motion(f,o)
    rp=o['p']*o['e']*np.sin(f)/(1+o['e']*np.cos(f))**2
    slope=rp/(1-MOON_OMEGA*r*r/o['h'])
    return r,t,f,slope


def intervals(o,return_only=False):
    ceiling=RADIUS+float(_GROUND.max())+.01
    if o['rp']>=ceiling:return []
    fc=np.arccos(np.clip((o['p']/ceiling-1)/o['e'],-1,1))
    # This ensures radial height vs body longitude is strictly convex on all
    # possible-contact intervals; each linear DEM cell has at most one minimum.
    assert fc<np.pi/2
    fs=[(2*np.pi-fc,2*np.pi+fc)] if return_only else [(0.,fc)]
    return [(float(lo-MOON_OMEGA*motion(lo,o)[1]),float(hi-MOON_OMEGA*motion(hi,o)[1])) for lo,hi in fs]


def profile(o,lo,hi,refine=False):
    # Include every terrain interpolation knot; optionally every half-cell too.
    k0=int(np.ceil((o['lon']+lo)/STEP-.5));k1=int(np.floor((o['lon']+hi)/STEP-.5))
    xs=np.r_[lo,(np.arange(k0,k1+1)+.5)*STEP-o['lon'],hi]
    xs=np.unique(xs)
    if refine:xs=np.sort(np.r_[xs,(xs[:-1]+xs[1:])/2])
    r,t,f,slope=at_longitude(xs,o);heights=terrain(o['lon']+xs)
    gap=r-RADIUS-heights
    ground_slope=np.diff(heights)/np.diff(xs)
    # Convexity makes these all possible interior minima. Check them exactly,
    # including grazing dips whose cell endpoints are both above terrain.
    cells=np.flatnonzero((slope[:-1]<ground_slope)&(slope[1:]>ground_slope))
    roots=[]
    for i in cells:
        root=brentq(lambda x:float(at_longitude(x,o)[3])-ground_slope[i],xs[i],xs[i+1],xtol=1e-14)
        roots.append(root)
    if roots:
        xs=np.sort(np.r_[xs,roots]);r,t,_,_=at_longitude(xs,o);gap=r-RADIUS-terrain(o['lon']+xs)
    return xs,gap


def minimum_outbound(lon_deg,height,refine=False):
    o=orbit(lon_deg,height);bounds=intervals(o)
    if not bounds:return o['rp']-RADIUS-float(_GROUND.max())
    return min(float(profile(o,lo,hi,refine)[1].min()) for lo,hi in bounds)


def threshold(lon):
    ground=float(terrain(np.radians(lon)));high=max(1.,float(_GROUND.max())-ground+1)
    g0=minimum_outbound(lon,0.)
    h=0. if g0>=-1e-8 else brentq(lambda h:minimum_outbound(lon,h),0,high,xtol=.001)
    o=orbit(lon,h);bounds=intervals(o)
    critical={}
    if bounds:
        lo,hi=bounds[0];xs,gaps=profile(o,lo,hi);x=xs[int(np.argmin(gaps))]
        r,t,_,_=at_longitude(x,o)
        critical=dict(limiting_terrain_longitude_deg_east=float(np.degrees(o['lon']+x)%360),
            limiting_distance_from_release_km=float(x*RADIUS/1000),limiting_time_s=float(t),
            terrain_rise_to_limiting_point_m=float(terrain(o['lon']+x))-ground,
            payload_radial_rise_to_limiting_point_m=float(r-o['rp']))
    return dict(longitude_deg_east=lon,local_ground_height_m=ground,clearance_threshold_m=h,**critical)


def first_contact(o,return_only=False,refine=False):
    for lo,hi in intervals(o,return_only):
        xs,gap=profile(o,lo,hi,refine);hit=np.flatnonzero(gap<=0)
        if len(hit):
            i=int(hit[0]);x=xs[i]
            if i:
                x=brentq(lambda x:float(at_longitude(x,o)[0])-RADIUS-float(terrain(o['lon']+x)),xs[i-1],xs[i],xtol=1e-14)
            r,t,f,_=at_longitude(x,o)
            assert float(t)<=1.5*o['T']+1e-7
            return dict(impact_time_s=float(t),impact_longitude_deg_east=float(np.degrees(o['lon']+x)%360),impact_orbits=float(t/o['T']))
    return None


def classify(args):
    lon,height,refine=args;o=orbit(lon,height)
    impact=first_contact(o,refine=refine)
    if impact:status='outbound_collision'
    else:
        impact=first_contact(o,True,refine)
        status='return_impact' if impact else 'not_arrested'
    speed=o['h']/o['rp'];vapo=o['h']/RC;vc=np.sqrt(MU/RC)
    return dict(longitude_deg_east=lon,release_height_m=height,status=status,
        release_ground_elevation_m=o['ground'],release_radius_m=o['rp'],
        inertial_release_speed_m_s=speed,surface_relative_release_speed_m_s=speed-MOON_OMEGA*o['rp'],
        catch_relative_speed_m_s=vc-vapo,catch_time_s=o['T']/2,horizon_s=1.5*o['T'],
        period_s=o['T'],**(impact or dict(impact_time_s=None,impact_longitude_deg_east=None,impact_orbits=None)))


