"""Select four east-launching sites by explicit alignment/clearance/diversity criteria."""
from pathlib import Path
from itertools import combinations
import csv,json,hashlib
from ..global_hills.search import GlobalTerrain,rim,RADIUS
from llo_catcher.site_selection.support import summits as terrain_screen
OUT=Path(__file__).parent

def angular_separation(a,b):
    return abs((a['longitude_deg_east']-b['longitude_deg_east']+180)%360-180)

def main():
    source=OUT.parent/'global_hills/nonoverlap_results.json'
    original=json.loads(source.read_text());rows=original['candidates']
    east=[r for r in rows if r['east_status']!='outbound_collision']
    aligned=[r for r in east if r['reference_arm_equator_miss_m']<=100]
    eligible=[r for r in aligned if r['min_tip_circle_clearance_m']>=100]
    options=[g for g in combinations(eligible,4) if all(angular_separation(a,b)>=30 for a,b in combinations(g,2))]
    assert options
    best=max(options,key=lambda g:(sum(r['min_tip_circle_clearance_m'] for r in g),-sum(r['reference_arm_equator_miss_m'] for r in g)))
    selected=sorted(best,key=lambda r:r['longitude_deg_east']);terrain=GlobalTerrain();mapped=[]
    for rank,r in enumerate(selected,1):
        r['feature_label']=f'P{rank}'
        fine=RADIUS+r['hub_elevation_m']+r['tip_plane_offset_m']-rim(terrain,r['hub_latitude_deg'],r['longitude_deg_east'],r['arm_radius_km']*1000,144000)
        assert abs(fine-r['min_tip_circle_clearance_m'])<.1
        r['refined_tip_circle_clearance_m']=fine
        terrain_screen.terrain=terrain
        _,_,interior_high,_=terrain_screen.vertex_extrema(r['hub_latitude_deg'],r['longitude_deg_east'],r['arm_radius_km']*1000)
        r['highest_sampled_interior_terrain_above_hub_m']=float(interior_high-r['hub_elevation_m'])
        mapped.append(dict(id=f"P{rank}_{r['id']}",hub_lat_deg=r['hub_latitude_deg'],hub_lon_deg_east=r['longitude_deg_east'],hub_elevation_m=r['hub_elevation_m'],actual_radius_km=r['arm_radius_km'],actual_horizontal_tip_min_clearance_m=fine,height_reference=f"Tip plane {r['tip_plane_offset_m']:.4f} m above hub tangent plane; eastward launch clears"))
    result=dict(criteria=dict(max_reference_arm_equator_miss_m=100,min_tip_circle_clearance_m=100,min_pairwise_longitude_separation_deg=30,objective='Maximize summed tip-circle clearance among every feasible four-site combination; tie-break by smaller total reference-arm equator miss.'),counts=dict(nonoverlap=len(rows),east_clear=len(east),aligned=len(aligned),clearance_qualified=len(eligible),feasible_quartets=len(options)),reference_arm_m=original['reference_arm_m'],selected=selected,source_sha256=hashlib.sha256(source.read_bytes()).hexdigest())
    (OUT/'results.json').write_text(json.dumps(result,indent=2)+'\n')
    (OUT/'catalog.json').write_text(json.dumps(dict(sites=mapped),indent=2)+'\n')
    with (OUT/'selected_sites.csv').open('w') as f:
        w=csv.DictWriter(f,fieldnames=list(selected[0]));w.writeheader();w.writerows(selected)
    print(result['counts'])
    for r in selected:print(r['feature_label'],r['id'],r['hub_latitude_deg'],r['hub_longitude_deg'],r['reference_arm_equator_miss_m'],r['refined_tip_circle_clearance_m'])
if __name__=='__main__':main()
