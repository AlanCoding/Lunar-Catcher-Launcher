"""Audit the old tip-relative height against a declared hub-relative plane."""
from pathlib import Path
import json,csv
import numpy as np
from ..analysis.single_equatorial_release.directional_sites import orbits
from ..analysis.single_equatorial_release.summit_sites import find_sites as hills
OUT=Path(__file__).parent
REFERENCE=OUT.parents[1]/'sling_launcher/blender/scene_inputs.json'
TIP_HEIGHT=float(json.loads(REFERENCE.read_text())['outward_points_m'][-1][2])
EXTRA_MARGIN=0.5
PLANE_OFFSET=TIP_HEIGHT+EXTRA_MARGIN

def main():
    orbits.initialize();hills.terrain=hills.Terrain(hills.CACHE,hills.ROWS)
    source=OUT.parent/'analysis/single_equatorial_release/directional_sites/catalog.json'
    rows=[];updated=[]
    for site in json.loads(source.read_text())['sites']:
        phi=np.radians(site['hub_lat_deg']);lon=site['hub_lon_deg_east'];z=site['hub_elevation_m'];R=hills.RADIUS
        ground=float(hills.terrain.height(0.,lon))
        old_r=R+ground+10
        plane=R+z+PLANE_OFFSET # Go-kart loaded tip height plus user-selected margin
        r=plane/np.cos(phi);arm=plane*abs(np.tan(phi))
        _,projection=hills.rim(site['hub_lat_deg'],lon,arm,36000)
        row=dict(id=site['id'],hub_latitude_deg=site['hub_lat_deg'],hub_longitude_deg=site['hub_lon_signed_deg'],hub_elevation_m=z,
                 equatorial_ground_elevation_m=ground,old_plane_above_hub_m=old_r*np.cos(phi)-(R+z),
                 old_min_circle_clearance_m=site['actual_horizontal_tip_min_clearance_m'],
                 assumed_plane_above_hub_m=PLANE_OFFSET,reference_tip_height_m=TIP_HEIGHT,extra_margin_m=EXTRA_MARGIN,
                 curvature_contribution_m=r-plane,hub_minus_release_ground_m=z-ground,new_release_height_above_local_ground_m=r-R-ground,
                 new_arm_radius_km=arm/1000,new_min_circle_clearance_m=float(plane-projection.max()))
        for direction,sign in [('east',1),('west',-1)]:
            m=orbits.MODELS[direction]
            shot=m.classify((sign*lon%360,row['new_release_height_above_local_ground_m'],True))
            row[direction+'_status']=shot['status']
            row[direction+'_impact_minutes']=shot['impact_time_s']/60 if shot['impact_time_s'] is not None else None
        rows.append(row)
        mapped=dict(site)
        mapped.update(actual_radius_km=row['new_arm_radius_km'],actual_horizontal_tip_min_clearance_m=row['new_min_circle_clearance_m'],height_reference=f'Tip plane {PLANE_OFFSET:.4f} m above hub tangent plane (go-kart + 0.5 m)')
        updated.append(mapped)
    (OUT/'catalog.json').write_text(json.dumps(dict(sites=updated,scope='Geometry-only hub-relative height diagnostic; use height_audit.json for corrected trajectories'),indent=2)+'\n')
    (OUT/'height_audit.json').write_text(json.dumps(rows,indent=2)+'\n')
    with (OUT/'height_audit.csv').open('w') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    for r in rows:print(r['id'],*[round(r[k],2) for k in ['old_plane_above_hub_m','new_release_height_above_local_ground_m','new_min_circle_clearance_m']],r['east_status'],r['west_status'])
if __name__=='__main__':main()
