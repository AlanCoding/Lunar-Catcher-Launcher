"""Select disjoint projected swept disks; no new trajectory integrations."""
from pathlib import Path
import csv,json
import numpy as np
from .search import GlobalTerrain,RADIUS
OUT=Path(__file__).parent

def main():
    data=json.loads((OUT/'results.json').read_text());rows=data['candidates']
    scene=json.loads((Path(__file__).resolve().parents[3]/'sling_launcher/blender/scene_inputs.json').read_text())
    reference_arm=scene['outward_points_m'][-1][0]
    terrain=GlobalTerrain();floor=min(float(a.min())*1000 for a in terrain.tiles.values())
    for r in rows:
        phi=np.radians(r['hub_latitude_deg']);Z=RADIUS+r['hub_elevation_m']+r['tip_plane_offset_m']
        r['reference_arm_equator_miss_m']=float(RADIUS*abs(abs(phi)-np.arctan(reference_arm/Z)))
        # Conservative cap enclosing ground projection at any cached terrain elevation.
        r['sweep_cap_angle_rad']=float(np.arcsin(r['arm_radius_km']*1000/(RADIUS+floor)))
    ordered=sorted(rows,key=lambda r:(r['reference_arm_equator_miss_m'],-r['min_tip_circle_clearance_m'],r['longitude_deg_east'],r['hub_latitude_deg']))
    selected=[];xyzs=[];angles=[]
    for r in ordered:
        lat,lon=np.radians([r['hub_latitude_deg'],r['longitude_deg_east']]);xyz=np.array([np.cos(lat)*np.cos(lon),np.cos(lat)*np.sin(lon),np.sin(lat)])
        ok=not xyzs or np.all(np.linalg.norm(np.asarray(xyzs)-xyz,axis=1)>=2*np.sin((np.asarray(angles)+r['sweep_cap_angle_rad'])/2))
        if ok:selected.append(r);xyzs.append(xyz);angles.append(r['sweep_cap_angle_rad'])
    # Independent angular-distance pair check (lat/lon, not the selection chord test).
    minimum=float('inf')
    for i,a in enumerate(selected):
        for b in selected[i+1:]:
            p,q=np.radians([a['hub_latitude_deg'],b['hub_latitude_deg']]);dl=np.radians(a['hub_longitude_deg']-b['hub_longitude_deg'])
            sep=2*np.arcsin(np.sqrt(np.sin((p-q)/2)**2+np.cos(p)*np.cos(q)*np.sin(dl/2)**2))
            gap=RADIUS*(sep-a['sweep_cap_angle_rad']-b['sweep_cap_angle_rad']);minimum=min(minimum,float(gap))
    assert minimum>=-1e-6
    selected.sort(key=lambda r:(r['longitude_deg_east'],r['hub_latitude_deg']))
    stats=dict(count=len(selected),east_clear=sum(r['east_status']!='outbound_collision' for r in selected),west_clear=sum(r['west_status']!='outbound_collision' for r in selected),both_clear=sum(all(r[d+'_status']!='outbound_collision' for d in ['east','west']) for r in selected),either_clear=sum(any(r[d+'_status']!='outbound_collision' for d in ['east','west']) for r in selected))
    for d in ['east','west']:
        for status in ['outbound_collision','return_impact','not_arrested']:stats[d+'_'+status]=sum(r[d+'_status']==status for r in selected)
    result=dict(selection='Disjoint conservative ground-projected swept disks; favor reference-arm equatorial alignment, then terrain clearance. No launch-outcome preference.',reference_arm_m=reference_arm,cached_terrain_floor_m=floor,minimum_sweep_separation_m=minimum,stats=stats,candidates=selected)
    (OUT/'nonoverlap_results.json').write_text(json.dumps(result,indent=2)+'\n')
    with (OUT/'nonoverlap_candidates.csv').open('w') as f:
        keys=[k for k in selected[0] if k!='selected_7km_subset'];w=csv.DictWriter(f,fieldnames=keys,extrasaction='ignore');w.writeheader();w.writerows(selected)
    print(json.dumps(stats), 'minimum gap m',minimum)
if __name__=='__main__':main()
