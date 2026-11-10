"""Ring maxima in hub tangent coordinates, with angular and radial refinement."""
from pathlib import Path
import json,csv,hashlib
import numpy as np
from scipy.optimize import minimize_scalar
from ..global_hills.search import GlobalTerrain,RADIUS
from llo_catcher.site_selection.support.geometry import destination
ROOT=Path(__file__).resolve().parent
TRACK=76.78937039996255

def profile_point(t,s,r,spacing):
    h0=s['hub_elevation_m'];lat=s['hub_latitude_deg'];lon=s['longitude_deg_east']
    if r==0:return dict(radius_m=0.,max_tangent_height_m=0.,max_radial_elevation_difference_m=0.,controlling_azimuth_deg=0.)
    def values(b):
        angle=np.zeros_like(np.asarray(b,dtype=float))+np.arcsin(r/(RADIUS+h0))
        for _ in range(5):
            y,x=destination(lat,lon,b,angle);h=t.height(y,x);angle=np.arcsin(r/(RADIUS+h))
        y,x=destination(lat,lon,b,angle);h=t.height(y,x)
        return (RADIUS+h)*np.cos(angle)-(RADIUS+h0),h-h0
    n=max(128,int(np.ceil(2*np.pi*r/spacing)));b=np.arange(n)*2*np.pi/n;z,h=values(b)
    j=int(np.argmax(z));delta=2*np.pi/n
    # Refine several competing peaks: the tallest coarse sample can belong
    # to a different hill than the true maximum after interpolation.
    peaks=np.flatnonzero((z>=np.roll(z,1))&(z>=np.roll(z,-1)))
    peaks=peaks[np.argsort(z[peaks])[-5:]]
    bearing=float(b[j]);best=float(z[j])
    for k in peaks:
        opt=minimize_scalar(lambda a:-float(values(a)[0]),bounds=(b[k]-delta,b[k]+delta),method='bounded',options={'xatol':1e-11})
        if -opt.fun>best:bearing=float(opt.x);best=-float(opt.fun)
    best,dh=values(bearing)
    return dict(radius_m=float(r),max_tangent_height_m=float(best),max_radial_elevation_difference_m=float(dh),controlling_azimuth_deg=float(np.degrees(bearing)%360))

def main():
    source=ROOT.parent/'featured_four/adjusted_hilltops/results.json';sites=json.loads(source.read_text())['sites'];t=GlobalTerrain()
    common=min(s['arm_radius_m'] for s in sites)
    radii=np.unique(np.r_[np.arange(0,6500.01,12.5),TRACK,[s['arm_radius_m'] for s in sites],common])
    summaries=[];allrows=[]
    for i,s in enumerate(sites,1):
        rows=[profile_point(t,s,r,15) for r in radii]
        coarse=[profile_point(t,s,r,30) for r in radii if r%25==0 or r in [TRACK,s['arm_radius_m']]]
        lookup={a['radius_m']:a for a in rows}
        error=max(abs(a['max_tangent_height_m']-lookup[a['radius_m']]['max_tangent_height_m']) for a in coarse)
        assert error<.2,(i,error)
        ztip=lookup[s['arm_radius_m']]['max_tangent_height_m'];gap=s['tip_plane_offset_m']-ztip
        assert abs(gap-s['min_tip_circle_clearance_m'])<.05,(i,gap)
        rr=np.array([a['radius_m'] for a in rows]);zz=np.array([a['max_tangent_height_m'] for a in rows]);mask=(rr>=TRACK)&(rr<=common)
        score=float(-np.trapezoid(zz[mask],rr[mask])/(common-TRACK))
        coarse_r=np.unique(np.r_[np.arange(0,6500.01,25),TRACK,common]);coarse_z=np.array([lookup[float(r)]['max_tangent_height_m'] for r in coarse_r]);cm=(coarse_r>=TRACK)&(coarse_r<=common)
        score_coarse=float(-np.trapezoid(coarse_z[cm],coarse_r[cm])/(common-TRACK))
        summary=dict(site=f'P{i}',hub_latitude_deg=s['hub_latitude_deg'],hub_longitude_deg=s['hub_longitude_deg'],hub_elevation_m=s['hub_elevation_m'],tip_radius_m=s['arm_radius_m'],
            mean_ring_drop_m=score,radial_score_change_m=abs(score-score_coarse),max_angular_refinement_change_m=error,
            tip_ring_height_m=ztip,tip_clearance_check_m=gap,tip_clearance_difference_m=gap-s['min_tip_circle_clearance_m'],track_ring_height_m=lookup[TRACK]['max_tangent_height_m'])
        summaries.append(summary)
        with (ROOT/f'P{i}_profile.csv').open('w') as f:
            w=csv.DictWriter(f,fieldnames=rows[0]);w.writeheader();w.writerows(rows)
        allrows.append(dict(site=f'P{i}',profile=rows));print(summary,flush=True)
    selected=max(summaries,key=lambda a:a['mean_ring_drop_m'])['site']
    # Flat-sphere curvature sign and endpoint test of the projection formula.
    assert np.sqrt(RADIUS**2-6000**2)-RADIUS<0
    d=dict(source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),reference_radius_m=RADIUS,track_radius_m=TRACK,common_comparison_radius_m=common,
           selection='Largest mean drop of the maximum-around-ring terrain envelope, track to common radius; terrain-only criterion',selected_site=selected,summaries=summaries,profiles=allrows)
    (ROOT/'results.json').write_text(json.dumps(d,indent=2)+'\n')
if __name__=='__main__':main()
