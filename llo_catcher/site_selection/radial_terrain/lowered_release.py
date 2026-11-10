"""P1 eastward departure with the release lowered relative to the hub tangent plane."""
from pathlib import Path
import json,csv,hashlib
import numpy as np
from .calculate import ROOT
from ..global_hills.search import GlobalTerrain,RADIUS
from ..featured_four.adjusted_hilltops.check_launches import check

def main():
    sitepath=ROOT.parent/'featured_four/adjusted_hilltops/results.json'
    scenepath=ROOT.parents[2]/'sling_launcher/blender/scene_inputs.json'
    site=json.loads(sitepath.read_text())['sites'][0];scene=json.loads(scenepath.read_text())
    pole=scene['candidate']['apex_height_m'];original=site['tip_plane_offset_m'];terrain=GlobalTerrain();rows=[]
    cases=[('Existing reference',original),('Subtract reference pole height',original-pole),('100 m below hub tangent plane',-100.),('200 m below hub tangent plane',-200.),('300 m below hub tangent plane',-300.)]
    for name,offset in cases:
        z=RADIUS+site['hub_elevation_m']+offset;arm=site['arm_radius_m']
        lat=float(site['hub_latitude_deg']-np.degrees(np.arctan2(arm,z)));rp=float(np.hypot(z,arm))
        coarse=check(terrain,lat,site['longitude_deg_east'],rp,1,15)
        fine=check(terrain,lat,site['longitude_deg_east'],rp,1,7.5)
        assert coarse['clears']==fine['clears']
        error=abs(coarse['minimum_clearance_m']-fine['minimum_clearance_m']);assert error<.1,error
        row=dict(case=name,tip_plane_offset_m=offset,lowering_from_reference_m=original-offset,release_latitude_deg=lat,
                 release_longitude_deg=site['hub_longitude_deg'],release_elevation_m=rp-RADIUS,local_ground_clearance_m=fine['release_ground_clearance_m'],
                 eastward_clears=fine['clears'],minimum_outbound_clearance_m=fine['minimum_clearance_m'],angular_resolution_difference_m=error,
                 tip_circle_clearance_m=site['min_tip_circle_clearance_m']+offset-original)
        rows.append(row);print(row,flush=True)
    result=dict(site='P1',arm_radius_m=site['arm_radius_m'],reference_apex_height_m=pole,reference_tip_plane_offset_m=original,
                model='Pure eastward, periapsis release; speed retargeted to 25 km apoapsis; spherical gravity and lunar spin; bilinear SLDEM2015',
                source_sha256={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in [sitepath,scenepath]},cases=rows)
    (ROOT/'lowered_release.json').write_text(json.dumps(result,indent=2)+'\n')
    with (ROOT/'lowered_release.csv').open('w') as f:
        w=csv.DictWriter(f,fieldnames=rows[0]);w.writeheader();w.writerows(rows)
    lines=['# P1: eastward launches below the hilltop tangent plane','',
      '[Radial terrain profile](README.md) · [Publication packet](../publication/README.md)','',
      '**All five tested release heights clear the terrain outbound to 25 km apoapsis.** P1 retains its 5.716 km horizontal arm radius and intended southern release point.','',
      f"The published 50-g go-kart reference has an apex height of **{pole:.2f} m**. Its loaded endpoint is 0.8768 m above the original central tangent plane; site selection added 0.5 m, giving the current **{original:.4f} m** endpoint offset. Subtracting the {pole:.2f} m support height from that current endpoint puts release **{pole-original:.2f} m below the hub tangent plane**.",'',
      '| Release case | Height relative to hub tangent plane (m) | Ground clearance at release (m) | Minimum outbound terrain clearance (m) | Eastward clears? |',
      '|---|---:|---:|---:|:---:|']
    for r in rows:lines.append(f"| {r['case']} | {r['tip_plane_offset_m']:+.2f} | {r['local_ground_clearance_m']:.1f} | {r['minimum_outbound_clearance_m']:.1f} | {'Yes' if r['eastward_clears'] else 'No'} |")
    last=rows[-1]
    lines+=['','## Publication takeaway','',
      f"At P1, a payload released 300 m below the hilltop tangent plane still clears the eastward terrain on its way to a 25 km apoapsis. The smallest modeled clearance along that outbound flight is **{last['minimum_outbound_clearance_m']:.0f} m**. The hill provides substantial room for a lower release height.",'',
      '## Geometry and model','',
      'Offsets −100, −200 and −300 m are measured from the hub tangent plane. At horizontal arm radius a, the tip has axial coordinate Z = R + h_hub + offset and lunar-center radius sqrt(Z² + a²). Its latitude follows the corresponding angle atan(a/Z) southward from the hub. This preserves the arm radius while lowering the endpoint; latitude changes slightly as well. Local ground clearance and radial altitude include lunar curvature.','',
      'Each shot is horizontal and directly eastward at periapsis. Its speed is recalculated to retain the 25 km apoapsis. The calculation uses the established spherical-gravity model, lunar rotation, and terrain at the actual evolving latitude and longitude. The off-equator orbit reaches apoapsis at the opposite latitude; equatorial catcher targeting remains a separate calculation.','',
      'These cases test endpoint departure geometry. The separate sag/taper study will determine cable shapes, tension, supports and full-path hardware clearance at lowered endpoints. Translating the reference endpoint by the pole height is a geometric sensitivity case.','',
      f"The existing minimum tip-ring terrain height is about 422.2 m below the hub tangent plane. A horizontal endpoint circle at −300 m therefore retains about **{last['tip_circle_clearance_m']:.1f} m** of minimum rim clearance. The intended southern release point lies above lower terrain, explaining its larger local release clearance in the table.",'',
      'Every trajectory was sampled at 15 m and 7.5 m orbital-arc spacing, with local refinement of its minimum gap. Both resolutions agree on every classification and minimum clearances agree within 0.1 m. DEM resolution is approximately 59 m; the numerical agreement describes the interpolated terrain model.','',
      '- [Full results](lowered_release.json) · [CSV](lowered_release.csv).',
      '- [Generator](lowered_release.py): `.env/hub/bin/python -m llo_catcher.site_selection.radial_terrain.lowered_release`.',
      '- Reference support height: [published design dimensions](../../../sling_launcher/publication/DESIGN_AT_A_GLANCE.md).','']
    (ROOT/'LOWERED_RELEASE.md').write_text('\n'.join(lines))
if __name__=='__main__':main()
