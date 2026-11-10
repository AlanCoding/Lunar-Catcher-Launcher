"""Central-gravity, off-equator terrain checks to 25 km apoapsis."""
from pathlib import Path
import json,csv,hashlib
import numpy as np
from scipy.optimize import brentq, minimize_scalar
from ...global_hills.search import GlobalTerrain,RADIUS
from ....analysis.terrain.impact_demo import MU,MOON_OMEGA
ROOT=Path(__file__).resolve().parent

def trajectory(lat,lon,rp,direction):
    a=(rp+RADIUS+25000)/2;e=1-rp/a;n=np.sqrt(MU/a**3)
    phi,lam=np.radians([lat,lon])
    u=np.array([np.cos(phi)*np.cos(lam),np.cos(phi)*np.sin(lam),np.sin(phi)])
    v=direction*np.array([-np.sin(lam),np.cos(lam),0.])
    def at(f):
        f=np.asarray(f);E=2*np.arctan2(np.sqrt(1-e)*np.sin(f/2),np.sqrt(1+e)*np.cos(f/2))
        t=(E-e*np.sin(E))/n;r=a*(1-e*e)/(1+e*np.cos(f))
        q=np.cos(f)[...,None]*u+np.sin(f)[...,None]*v
        lat=np.degrees(np.arcsin(q[...,2]));lon=(np.degrees(np.arctan2(q[...,1],q[...,0])-MOON_OMEGA*t))%360
        return lat,lon,r,t
    return at

def check(terrain,lat,lon,rp,direction,step):
    at=trajectory(lat,lon,rp,direction)
    def gap(f):
        y,x,r,t=at(f);return r-RADIUS-terrain.height(y,x)
    f=np.linspace(0,np.pi,int(np.ceil(np.pi*(RADIUS+25000)/step))+1)
    g=gap(f);j=int(np.argmin(g));lo=f[max(0,j-1)];hi=f[min(len(f)-1,j+1)]
    opt=minimize_scalar(gap,bounds=(lo,hi),method='bounded',options={'xatol':1e-13})
    minimum=min(float(g[j]),float(opt.fun));bad=np.flatnonzero(g<=0)
    impact=None
    if len(bad):
        k=int(bad[0]);fc=0. if k==0 else brentq(gap,f[k-1],f[k],xtol=1e-13)
        y,x,r,t=at(fc)
        impact=dict(latitude_deg=float(y),longitude_deg=float((x+180)%360-180),time_min=float(t/60))
    return dict(clears=not len(bad),minimum_clearance_m=minimum,first_impact=impact,
                release_latitude_deg=lat,release_longitude_deg=(lon+180)%360-180,
                release_ground_clearance_m=float(g[0]),time_to_apoapsis_min=float(at(np.pi)[3]/60))

def main():
    source=ROOT/'results.json';sites=json.loads(source.read_text())['sites'];terrain=GlobalTerrain();results=[];pub=[]
    for i,s in enumerate(sites,1):
        z=RADIUS+s['hub_elevation_m']+s['tip_plane_offset_m'];arm=s['arm_radius_m'];rp=float(np.hypot(z,arm))
        delta=np.sign(s['hub_latitude_deg'])*np.degrees(np.arctan2(arm,z))
        near=s['hub_latitude_deg']-delta;far=s['hub_latitude_deg']+delta
        shots={}
        for name,lat,d in [('west_intended',near,-1),('west_opposite',far,-1),('east_intended',near,1)]:
            coarse=check(terrain,lat,s['longitude_deg_east'],rp,d,30)
            fine=check(terrain,lat,s['longitude_deg_east'],rp,d,15)
            assert coarse['clears']==fine['clears']
            fine['coarse_fine_minimum_difference_m']=abs(coarse['minimum_clearance_m']-fine['minimum_clearance_m'])
            assert fine['coarse_fine_minimum_difference_m']<.5
            shots[name]=fine
        results.append(dict(site=f'P{i}',source_id=s['id'],shots=shots))
        pub.append(dict(site=f'P{i}',hub_latitude_deg=s['hub_latitude_deg'],hub_longitude_deg=s['hub_longitude_deg'],
            hub_elevation_m=s['hub_elevation_m'],tip_offset_from_equator_m=s['near_equator_tip_offset_m'],
            minimum_tip_circle_clearance_m=s['min_tip_circle_clearance_m'],
            west_intended_clears=shots['west_intended']['clears'],west_opposite_clears=shots['west_opposite']['clears']))
        print(f'P{i}',shots,flush=True)
    (ROOT/'launch_checks.json').write_text(json.dumps(dict(source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),model='Central gravity; rotating Moon; periapsis release due east/west; 25 km apoapsis; no catcher targeting correction',mu_m3_s2=MU,moon_spin_rad_s=MOON_OMEGA,sites=results),indent=2)+'\n')
    with (ROOT/'publication_sites.csv').open('w') as f:
        w=csv.DictWriter(f,fieldnames=pub[0]);w.writeheader();w.writerows(pub)
    lines=['# Four hilltop launcher sites','',
      '[Terrain maps](maps/README.md) · [Machine-readable publication table](publication_sites.csv) · [Placement method and comparison](README.md)','',
      'Latitude and longitude are decimal degrees, north/east positive. Elevation is relative to the 1,737.4 km lunar reference sphere. Tip offset is signed north-positive, for the intended (equator-facing) north–south tip.','',
      '| Site | Hub latitude | Hub longitude | Elevation (m) | Tip equator offset (m) | Min. tip-circle clearance (m) | West: intended tip | West: opposite tip |',
      '|---|---:|---:|---:|---:|---:|:---:|:---:|']
    yes=lambda b:'Yes' if b else 'No'
    for r in pub:
        lines.append(f"| {r['site']} | {r['hub_latitude_deg']:+.8f} | {r['hub_longitude_deg']:+.8f} | {r['hub_elevation_m']:.1f} | {r['tip_offset_from_equator_m']:+.1f} | {r['minimum_tip_circle_clearance_m']:.1f} | {yes(r['west_intended_clears'])} | {yes(r['west_opposite_clears'])} |")
    lines+=['','**Yes means terrain clears from release through the first 25 km apoapsis.** It does not mean an equatorial catcher rendezvous has been solved. No means a terrain intersection occurs on that outbound leg. The opposite tip is diametrically across the hub, farther from the equator; it is not the same release point with velocity reversed.','',
      'The four sites use 5.72–5.86 km arm radii, a 76.79 m rover track, and a tip plane 1.3768 m above the hub tangent plane. Positive tip-circle clearance describes the minimum gap around the circular rim, not clearance of the entire drooping tether. P1–P4 correspond to the same labels on the existing terrain maps.','',
      '[Expanded ridge association](../../launch_ridges/expanded/README.md): all four adjusted summits match independently discovered eastward contact ridges within the DEM resolution. Includes a terrain overlay for each site.','', '## Flight checks','',
      '| Site | Release | Latitude | Local release clearance (m) | West clears | First west impact after release (min) |',
      '|---|---|---:|---:|:---:|---:|']
    for r in results:
        for key,label in [('west_intended','Intended tip'),('west_opposite','Opposite tip')]:
            a=r['shots'][key];impact=a['first_impact'];time='—' if impact is None else f"{impact['time_min']:.2f}"
            lines.append(f"| {r['site']} | {label} | {a['release_latitude_deg']:+.8f} | {a['release_ground_clearance_m']:.1f} | {yes(a['clears'])} | {time} |")
    lines+=['','As a consistency check we also reran eastward departure from the intended tip: '+', '.join(r['site']+' '+('clears' if r['shots']['east_intended']['clears'] else 'does not clear') for r in results)+'.','',
      '## Numerical approach','',
      'Each tip retains its actual three-dimensional radius sqrt((R + hub elevation + plane offset)² + arm²). Release velocity is horizontal and purely westward (eastward for the additional check), with speed chosen by vis-viva so release is periapsis and apoapsis is R + 25 km. Both tips have the same radial altitude but different underlying terrain. Adding the lunar surface rotation changes the required surface-relative speed, not this chosen inertial orbit.','',
      'The trajectory is an analytic inclined Kepler ellipse under spherical 1/r² gravity. Its position is rotated into Moon-fixed coordinates using lunar spin, and altitude is compared against the bilinearly interpolated SLDEM2015 terrain at its actual latitude and longitude. No equatorial terrain-profile substitution is used. A due-west shot from nonzero latitude reaches apoapsis at the opposite latitude, so reaching this altitude is only a terrain-screening proxy for reaching a catcher.','',
      'We sample true anomaly at a spacing corresponding to at most ~15 m of inertial orbital arc (well below the ~59 m native DEM spacing), compare against a ~30 m run, refine the sampled global minimum locally, and bracket the first intersection. All classifications agree between the two resolutions and minimum gaps agree within 0.5 m. This is a sampled terrain screen, not a rigorous bound on DEM errors or unresolved obstacles. Mascons, external gravity, targeting corrections, and release transients are excluded. Propagation stops at apoapsis; no post-miss orbit is needed for these yes/no questions.','',
      '- [Full checks, including impact coordinates and minimum gaps](launch_checks.json).',
      '- Reproduce with `.env/hub/bin/python -m llo_catcher.site_selection.featured_four.adjusted_hilltops.check_launches` after generating the hilltop catalog with `build.py`.','']
    (ROOT/'PUBLICATION.md').write_text('\n'.join(lines))
if __name__=='__main__':main()
