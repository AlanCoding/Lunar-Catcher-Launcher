"""Publish distinct east/west catalogs and explicitly separate all criteria."""
import json,csv
from pathlib import Path
import numpy as np
from . import orbits
OUT=Path(__file__).parent
LABEL={'outbound_collision':'Blocked outbound','return_impact':'Clears; impacts after miss','not_arrested':'Clears; no impact by cutoff'}
def main():
    data=json.loads((OUT/'catalog.json').read_text());west=json.loads((OUT/'west_corridors.json').read_text());survey=json.loads((OUT/'degree_survey.json').read_text())
    text='''# Eastward and westward equatorial launch-site searches

This corrects a gap in the original six-summit catalog: its northern hubs were
selected near **eastward** corridors, not westward ones. North/south describes
hub latitude; east/west describes release velocity. We now search westward
corridors independently and check **both directions from the same equatorial
release point** at each selected summit longitude.

**“Other direction” here means reverse the sling rotation and launch from the
same equatorial tip.** It does not mean firing a second payload simultaneously
from the opposite, off-equator tip. Those older opposite-tip results remain
[separately documented](../summit_sites/missed_capture/README.md).

Both directions use 10 m local release clearance, a periapsis release, a **25 km
circular equatorial catcher at apoapsis**, spherical inverse-square gravity,
SLDEM2015 terrain, lunar rotation, and first impact or a **1.5-period cutoff**.
The common 25 km target isolates direction; the older off-equator west study
used a different 35 km target. These are independently targeted launches, not
a demonstrated paired launch at a common RPM.

## Updated figures

- [Whole-equator elevation](../equatorial_elevation.png) and [direction-specific detail](../equatorial_elevation_detail.png): eastward and westward seeds, with refined corridors in the detail views.
- [Terrain map gallery](maps/README.md): all nine hub candidates with same-equatorial-tip E/W impacts.

## Search results

'''
    for direction in ['east','west']:
        rows=survey[direction];clear=[r for r in rows if r['status']!='outbound_collision'];arrest=sum(r['status']=='return_impact' for r in clear)
        text+=f'- **{direction.capitalize()}:** {len(clear)}/360 one-degree seeds clear outbound; {arrest} of those hit after missed capture. Clear seed longitudes: '+', '.join(f"{r['longitude_deg_east']:g}° E" for r in clear)+'.\n'
    text+=f'\nThe refined westward neighborhoods contain **{len(west["bands"])} outbound-clear intervals totaling {sum(b["length_km"] for b in west["bands"]):.3f} km**. The hilltop search nominated {data["west_search"]["nominees"]} distinct candidates from {data["west_search"]["anchors"]} trial placements; {data["west_search"]["verified_summits"]} passed the terrain screen before spacing and {data["west_search"]["spaced_summits"]} remain after spacing.\n'
    text+='''
**At the shifted summit longitudes, E-S4 clears eastward and W-S2 clears
westward; neither clears in reverse. All other listed candidates are blocked
in both equatorial directions. None of the listed candidates clears the full
horizontal tip circle at this release height.** These are useful directional
trajectory candidates, not construction-ready launcher sites.

A hilltop passing the terrain screen is **not** automatically a usable launcher.
We report the shifted equatorial release trajectory and the minimum clearance
around the whole horizontal tip circle separately. Negative circle clearance
means this exact 10 m-release-height horizontal geometry intersects terrain.
Raising the plane would require new trajectory/clearance calculations.

'''
    for direction in ['east','west']:
        rows=[r for r in data['sites'] if r['search_direction']==direction]
        text+=f'## {direction.capitalize()}-search summit candidates\n\n'
        if direction=='east':text+='E-S1 through E-N2 retain the original S1 through N2 identities; the prefix only labels the search direction.\n\n'
        text+='| Hub | Latitude (°) | Longitude (°) | Eastward equatorial shot | Westward equatorial shot | Both clear? | Full tip-circle minimum clearance |\n| --- | ---: | ---: | --- | --- | --- | ---: |\n'
        for r in rows:
            text+=f"| {r['id']} | {r['hub_lat_deg']:.6f} | {r['hub_lon_signed_deg']:.6f} | {LABEL[r['east_status']]} | {LABEL[r['west_status']]} | {'Yes' if r['both_equatorial_directions_clear'] else 'No'} | {r['actual_horizontal_tip_min_clearance_m']:.1f} m |\n"
        if not rows:text+='\nNo summit candidate passed this screen; the clear release intervals still exist.\n'
        text+=f'\n[Full {direction} table]({direction}_sites.csv) includes signed floating-point coordinates, arm radii, RPM for each direction, catch-relative speeds, impact coordinates/times and hub-to-impact distances.\n\n' if rows else '\n'
    text+='''
## Impact locations for both directions

All impacts below are on the equator; coordinates are body-fixed decimal degrees,
positive east. “Outbound” is a failed departure, not a successful arrest following
a missed catch. A no-impact result would mean only no contact within the cutoff.

| Hub | Direction | Event | Impact longitude (°) | Time (min) | Distance from hub (km) |
| --- | --- | --- | ---: | ---: | ---: |
'''
    for r in data['sites']:
        for d in ['east','west']:
            if r[d+'_impact_time_s'] is None:continue
            text+=f"| {r['id']} | {d} | {'Outbound' if r[d+'_status']=='outbound_collision' else 'After missed catch'} | {r[d+'_impact_longitude_deg']:.6f} | {r[d+'_impact_time_s']/60:.4f} | {r[d+'_impact_distance_from_hub_km']:.3f} |\n"
    text+='''
## Why reverse-direction clearance and failed-catch impact differ

A reversed launch tests the terrain **west of this release point during its
initial climb**, whereas an eastward missed shot returns toward periapsis after
an orbit. The Moon turns beneath that orbit, so its return ground track is
shifted. In a nonrotating spherical-gravity model, reversing a periapsis launch
would retrace the inbound half of the original orbital ellipse; even there,
the inbound terrain question is not the outbound terrain question. With the
rotating terrain used here, the trajectories do not retrace the same ground
profile. We therefore calculate the two outcomes independently rather than
use either one as a proxy for the other.

## Method and scope

1. Repeat the full 360-longitude survey at 10 m in **each** direction.
2. Around westward-clear seeds, scan merged ±1° neighborhoods at 512, 1024,
   2048 and 4096 samples/degree. Root-refine corridor boundaries using every
   piecewise-linear DEM cell and its possible interior minimum. Check window
   edges are blocked. These local windows are not an exhaustive all-longitude
   fine survey; narrow corridors between unsuccessful coarse seeds can be missed.
   Eastward corridors reuse the original four-level refinement.
3. Near westward intervals, place nominal hubs 5 km north and south. Use the
   original approximately 14.8 m longitude anchor spacing, find maxima in 7 km
   disks, allow ±2 km hub-latitude shift, and recheck the 5 km disk for at most
   10 m rise. Apply the original 7 km site spacing. Both north and south sides
   are searched for both launch directions.
4. Recheck east and west at **each actual summit longitude** after hill climbing.
   Compute missed-shot contacts only if the departure clears. Report original
   east candidates with these same-direction comparisons; do not relabel the
   older off-equator west shots as equivalent.
5. Check the entire horizontal tip-circle clearance. The radius follows from
   actual hub latitude and the equatorial release height; it is not fixed at 5 km.

The west calculation reflects longitude and the DEM and reverses the sign of
lunar rotation inside the existing eastward solver. Physical output longitudes
are transformed back. This retains the correct westward surface-relative speed
and the correct body-fixed return displacement. Independent Cartesian integration
checks the resulting contact coordinates against the original, unreflected DEM.

The DEM has roughly 59 m equatorial pixels; the finest search spacing is about
7.4 m. Interpolation and numerical convergence do not add physical terrain
resolution. Mascons, targeting error, structures and terrain preparation remain
outside this model. Full-circle clearance is a separate buildability constraint.

## Files and reproduction

- [One-degree results, both directions](degree_survey.json).
- [Westward intervals and convergence](west_corridors.json).
- [Catalog with all screened west summits](catalog.json), including a separately
  spaced outbound-qualified subset so blocked candidates cannot displace usable ones.
- [Validation](validation.json): reflected DEM and independent Cartesian contacts.
- [Original eastward intervals](../local_corridors/README.md) and
  [original terrain maps](../summit_sites/maps/README.md), preserved unchanged.

From the repository root, using the existing cached terrain:

```bash
export MPLCONFIGDIR=/tmp/lunar-sling-mpl-cache OPENBLAS_NUM_THREADS=1
.env/hub/bin/python -m llo_catcher.analysis.single_equatorial_release.directional_sites.search degree
.env/hub/bin/python -m llo_catcher.analysis.single_equatorial_release.directional_sites.search west
.env/hub/bin/python -m llo_catcher.analysis.single_equatorial_release.directional_sites.catalog
.env/hub/bin/python -m llo_catcher.analysis.single_equatorial_release.directional_sites.validate
.env/hub/bin/python -m llo_catcher.analysis.single_equatorial_release.directional_sites.report
```
'''
    (OUT/'README.md').write_text(text)
if __name__=='__main__':main()
