"""Move the featured hubs to nearby native-grid summits; preserve arm lengths."""
from pathlib import Path
import csv,json,hashlib
import numpy as np
from ...global_hills.search import GlobalTerrain, RADIUS, rim
from ....analysis.single_equatorial_release.summit_sites import find_sites as screen
from ....analysis.single_equatorial_release.directional_sites import build_maps as renderer
ROOT=Path(__file__).resolve().parent

def main():
    source=ROOT.parent/'results.json'
    terrain=GlobalTerrain();screen.terrain=terrain
    rows=[];catalog=[]
    for old in json.loads(source.read_text())['selected']:
        y0,x0=old['hub_latitude_deg'],old['longitude_deg_east']
        arm=1000*old['arm_radius_km']
        y,x,h,_=screen.vertex_extrema(y0,x0,arm)
        yy,xx,high,_=screen.vertex_extrema(y,x,arm)
        assert (yy,xx)==(y,x), 'Recentered disk contains a higher summit'
        neighbors=terrain.height(y+np.arange(-1,2)[:,None]/512,x+np.arange(-1,2)[None,:]/512)
        assert neighbors.max() <= h+.001
        z=RADIUS+h+old['tip_plane_offset_m']
        tip_lat=y-np.sign(y)*np.degrees(np.arctan2(arm,z))
        gap=z-rim(terrain,y,x,arm,72000)
        gap_fine=z-rim(terrain,y,x,arm,144000)
        assert abs(gap-gap_fine)<.05
        dx,dy=renderer.project(y,x,y0,x0)
        row=dict(id=old['feature_label']+'_'+old['id']+'_hilltop',original_id=old['id'],
          original_latitude_deg=y0,original_longitude_deg=(x0+180)%360-180,
          hub_latitude_deg=y,hub_longitude_deg=(x+180)%360-180,longitude_deg_east=x,
          hub_elevation_m=h,elevation_gain_m=h-old['hub_elevation_m'],
          hub_move_m=float(np.hypot(dx,dy)*1000),arm_radius_m=arm,
          tip_plane_offset_m=old['tip_plane_offset_m'],
          near_equator_tip_latitude_deg=float(tip_lat),
          near_equator_tip_offset_m=float(RADIUS*np.radians(tip_lat)),
          near_equator_tip_ground_clearance_m=float(np.hypot(z,arm)-RADIUS-terrain.height(tip_lat,x)),
          min_tip_circle_clearance_m=float(gap_fine),
          highest_native_vertex_above_hub_in_disk_m=high-h,
          launch_status='Not recalculated for shifted, off-equator release')
        rows.append(row)
        catalog.append(dict(id=row['id'],hub_lat_deg=y,hub_lon_deg_east=x,hub_elevation_m=h,
          actual_radius_km=arm/1000,actual_horizontal_tip_min_clearance_m=float(gap_fine),
          release_lat_deg=float(tip_lat),release_lon_deg_east=x,
          release_caption='▲ Equator-facing meridional tip · flight terrain checks in publication table',
          height_reference=f"Tip plane {old['tip_plane_offset_m']:.4f} m above hub tangent plane; highest sampled point in disk"))
    (ROOT/'results.json').write_text(json.dumps(dict(source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),sites=rows),indent=2)+'\n')
    with (ROOT/'hilltop_sites.csv').open('w') as f:
        w=csv.DictWriter(f,fieldnames=rows[0]);w.writeheader();w.writerows(rows)
    (ROOT/'catalog.json').write_text(json.dumps(dict(sites=catalog),indent=2)+'\n')
    lines=['# Adjusted four: hubs on the hilltops','',
      'These replace the nearby original hub placements for the four featured terrain illustrations. Each hub now sits on the highest SLDEM2015 grid vertex inside its original sweep disk. Repeating that search around the new hub returns the same summit in every case. The original four locations remain available [for comparison](../README.md).','',
      'We retain each original tether radius (5.72–5.86 km), the 76.79 m track radius, and the tip plane 1.3768 m above the hub tangent plane. Moving the hub therefore moves the release point away from the equator; we do not silently resize the launcher to recover an equatorial release.','',
      '## Placement comparison (not the publication table)','',
      'Latitude is signed north-positive; longitude is signed east-positive. The CSV also includes 0–360° east longitude. All distances below are metres.','',
      '| Site | Latitude | Longitude | Hub move | Elevation gain | Tip offset from equator | Minimum tip-circle clearance |',
      '|---|---:|---:|---:|---:|---:|---:|']
    for r in rows:
        lines.append(f"| {r['id']} | {r['hub_latitude_deg']:+.8f} | {r['hub_longitude_deg']:+.8f} | {r['hub_move_m']:.1f} | {r['elevation_gain_m']:.1f} | {r['near_equator_tip_offset_m']:+.1f} | {r['min_tip_circle_clearance_m']:.1f} |")
    lines+=['','Tip offset is signed north-positive. A northern hub can now have its equator-facing meridional tip **south** of the equator (and vice versa).','',
      '**[Publication table and updated flight checks](PUBLICATION.md):** all four adjusted intended tips clear eastward to 25 km apoapsis. P2 clears westward from both its intended and opposite tips; P1, P3 and P4 do not clear westward from either tip. These are off-equator terrain checks, not a completed equatorial-catcher targeting solution. The separate comparison table below retains the placement history.','',
      '## Method and limits','',
      'The hilltop search uses native ~59 m grid vertices, not the lower-resolution rendered image. Each selected point is also checked against its eight neighboring vertices. In all four recentered sweep disks, the highest native terrain vertex is the hub itself (0 m maximum rise). The tip-circle clearance is the minimum vertical gap between the fixed tip plane and terrain projected onto the hub vertical, sampled at 144,000 bearings; comparison with 72,000 bearings agrees within 0.05 m. This convergence is numerical, not a claim of centimetre DEM accuracy.','',
      'This resolves the visible taller-hill-inside-the-circle issue. It does not establish rover track grade, small unresolved obstacles, or the clearance of a dynamically drooping tether. Coordinates identify DEM summits, not surveyed construction pads.','',
      'The equator-facing meridional tip uses angular offset atan(arm / (Moon radius + summit elevation + plane offset)); its local ground clearance is calculated separately in the CSV. Hub displacement is great-circle distance using the 1,737.4 km reference radius.','',
      '## Files and reproduction','',
      '- [Numeric table](hilltop_sites.csv) and [full results](results.json).',
      '- [Terrain maps](maps/README.md): four 15 × 15 km views, PNG and SVG, without impact markers.',
      '- [Generator](build.py): run `MPLCONFIGDIR=/tmp/lunar-sling-mpl-cache OPENBLAS_NUM_THREADS=1 .env/hub/bin/python -m llo_catcher.site_selection.featured_four.adjusted_hilltops.build` from the repository root. Uses the existing cached SLDEM2015 bands.','']
    (ROOT/'README.md').write_text('\n'.join(lines))
    renderer.ROOT=ROOT/'maps';renderer.ROOT.mkdir(exist_ok=True)
    renderer.Terrain=lambda *args,**kwargs:terrain
    renderer.main()
    links=['# Adjusted hilltop terrain maps','','[Publication table and flight checks](../PUBLICATION.md) · [Coordinates and method](../README.md). Black dot: hilltop hub; orange circle: rover track; dashed green circle: tip sweep; white triangle: equator-facing meridional tip. Terrain colors are relative to the new summit elevation.','']
    for r in rows:
        stem=r['id']+'_15km'
        links += [f"## {r['id']}",'',f'![Hilltop terrain]({stem}.png)','',f'[SVG]({stem}.svg) · [PNG]({stem}.png)','']
    (ROOT/'maps/README.md').write_text('\n'.join(links))

if __name__=='__main__':main()
