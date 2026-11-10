"""Audit full-longitude coverage, interpolation, rim refinement and trajectories."""
from pathlib import Path
import json,hashlib
import numpy as np
from scipy.integrate import solve_ivp
from .search import GlobalTerrain,coarse_batch,rim,separation,CACHE,ROWS,RADIUS,PLANE_OFFSET,orbits
OUT=Path(__file__).parent

def main():
    result=json.loads((OUT/'results.json').read_text());rows=result['candidates']
    assert [s['sector_west_deg'] for s in result['sectors']]==list(range(0,360,45))
    t=GlobalTerrain();orbits.initialize();e=orbits.MODELS['east']
    # Check all tile seams in the global interpolator against the independent slice.
    lon=np.r_[np.arange(0,360,45)+.0001,np.arange(0,360,45)-.0001,np.linspace(0,360,997)]
    err=float(np.max(abs(t.height(0,lon)-e.terrain(np.radians(lon)))))
    assert err<1e-5
    for r in rows:
        assert 3<=r['arm_radius_km']<=7 and r['min_tip_circle_clearance_m']>=0
        for d in ['east','west']:
            assert r[d+'_status'] in ['outbound_collision','return_impact','not_arrested']
    old=json.loads((OUT.parent/'height_audit.json').read_text())
    recovered=[]
    for previous in old:
        if previous['new_min_circle_clearance_m']<=0:continue
        matches=[r for r in rows if abs(r['hub_latitude_deg']-previous['hub_latitude_deg'])<1e-9 and abs(r['hub_longitude_deg']-previous['hub_longitude_deg'])<1e-9]
        assert len(matches)==1, ('Previous circle-clear hill missing',previous['id'])
        match=matches[0]
        assert abs(match['min_tip_circle_clearance_m']-previous['new_min_circle_clearance_m'])<.01
        assert all(match[d+'_status']==previous[d+'_status'] for d in ['east','west'])
        recovered.append(previous['id'])
    # Deterministic representative checks plus up to 32 lowest-clearance cases.
    ix=np.unique(np.r_[np.linspace(0,len(rows)-1,min(24,len(rows))).astype(int),np.argsort([r['min_tip_circle_clearance_m'] for r in rows])[:32]])
    checks=[]
    for i in ix:
        r=rows[int(i)];lat=r['hub_latitude_deg'];lon=r['longitude_deg_east'];z=r['hub_elevation_m'];arm=r['arm_radius_km']*1000
        scalar=RADIUS+z+PLANE_OFFSET-rim(t,lat,lon,arm,360)
        batched=float(coarse_batch(t,[(lat,lon,z,arm)])[0]);assert abs(scalar-batched)<1e-7
        fine=RADIUS+z+PLANE_OFFSET-rim(t,lat,lon,arm,144000)
        assert fine>=0 # No audited terrain intersections accepted.
        for direction,sign in [('east',1),('west',-1)]:
            m=orbits.MODELS[direction];shot=m.classify((sign*lon%360,r['release_height_m'],False))
            assert shot['status']==r[direction+'_status']
            if shot['impact_time_s'] is None:continue
            tm=shot['impact_time_s'];rp=shot['release_radius_m'];v=shot['inertial_release_speed_m_s']
            assert abs(tm/60-r[direction+'_impact_time_min'])<1e-5
            def rhs(t,y):return np.r_[y[3:],-e.MU*y[:3]/np.linalg.norm(y[:3])**3]
            sol=solve_ivp(rhs,(0,tm),[rp,0,0,0,sign*v,0],method='DOP853',rtol=1e-12,atol=1e-8,max_step=20)
            assert sol.success
            pos=sol.y[:3,-1];angle=np.radians(lon)+np.arctan2(pos[1],pos[0])-e.MOON_OMEGA*tm
            gap=float(np.linalg.norm(pos)-RADIUS-e.terrain(angle));assert abs(gap)<.001
            checks.append(dict(id=r['id'],direction=direction,contact_residual_m=gap,rim_144000_clearance_m=fine,rim_clearance_change_m=fine-r['min_tip_circle_clearance_m']))
    spaced=[r for r in rows if r['selected_7km_subset']]
    from scipy.spatial import cKDTree
    if len(spaced)>1:
        lat=np.radians([r['hub_latitude_deg'] for r in spaced]);lon=np.radians([r['hub_longitude_deg'] for r in spaced])
        xyz=np.column_stack([np.cos(lat)*np.cos(lon),np.cos(lat)*np.sin(lon),np.sin(lat)])
        chord=cKDTree(xyz).query(xyz,k=2)[0][:,1].min()
        mindist=float(2*RADIUS*np.arcsin(chord/2))
    else:mindist=None
    assert mindist is None or mindist>=7000
    validation=dict(all_eight_sectors_checked=True,previous_circle_clear_hills_recovered=recovered,equatorial_interpolation_error_m=err,candidate_count=len(rows),representative_and_marginal_checks=checks,minimum_spaced_subset_separation_m=mindist)
    (OUT/'validation.json').write_text(json.dumps(validation,indent=2)+'\n')
    manifest=dict(terrain_sources=[json.loads((CACHE/f'{w:03d}.json').read_text()) for w in range(0,360,45)],terrain_array_sha256={f'{w:03d}':hashlib.sha256((CACHE/f'{w:03d}.npy').read_bytes()).hexdigest() for w in range(0,360,45)},source_sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in OUT.glob('*.py')})
    (OUT/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print('Validated',len(rows),'candidates,',len(checks),'Cartesian contacts; minimum selected spacing',mindist,flush=True)
if __name__=='__main__':main()
