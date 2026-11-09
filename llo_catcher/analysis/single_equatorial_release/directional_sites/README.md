# Eastward and westward equatorial launch-site searches

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

- **East:** 8/360 one-degree seeds clear outbound; 8 of those hit after missed capture. Clear seed longitudes: 144° E, 220° E, 264° E, 267° E, 283° E, 293° E, 294° E, 295° E.
- **West:** 2/360 one-degree seeds clear outbound; 2 of those hit after missed capture. Clear seed longitudes: 177° E, 194° E.

The refined westward neighborhoods contain **12 outbound-clear intervals totaling 24.211 km**. The hilltop search nominated 233 distinct candidates from 3346 trial placements; 4 passed the terrain screen before spacing and 3 remain after spacing.

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

## East-search summit candidates

E-S1 through E-N2 retain the original S1 through N2 identities; the prefix only labels the search direction.

| Hub | Latitude (°) | Longitude (°) | Eastward equatorial shot | Westward equatorial shot | Both clear? | Full tip-circle minimum clearance |
| --- | ---: | ---: | --- | --- | --- | ---: |
| E-S1 | -0.196289 | 144.176758 | Blocked outbound | Blocked outbound | No | -264.7 m |
| E-S2 | -0.176758 | -92.922852 | Blocked outbound | Blocked outbound | No | -435.3 m |
| E-S3 | -0.194336 | -77.116211 | Blocked outbound | Blocked outbound | No | -105.2 m |
| E-N1 | 0.217773 | -66.249023 | Blocked outbound | Blocked outbound | No | -734.9 m |
| E-S4 | -0.155273 | -65.852539 | Clears; impacts after miss | Blocked outbound | No | -119.2 m |
| E-N2 | 0.129883 | -64.047852 | Blocked outbound | Blocked outbound | No | -221.2 m |

[Full east table](east_sites.csv) includes signed floating-point coordinates, arm radii, RPM for each direction, catch-relative speeds, impact coordinates/times and hub-to-impact distances.

## West-search summit candidates

| Hub | Latitude (°) | Longitude (°) | Eastward equatorial shot | Westward equatorial shot | Both clear? | Full tip-circle minimum clearance |
| --- | ---: | ---: | --- | --- | --- | ---: |
| W-S1 | -0.208008 | -166.678711 | Blocked outbound | Blocked outbound | No | -1838.2 m |
| W-N1 | 0.141602 | -166.571289 | Blocked outbound | Blocked outbound | No | -1186.9 m |
| W-S2 | -0.186523 | -165.692383 | Blocked outbound | Clears; impacts after miss | No | -106.4 m |

[Full west table](west_sites.csv) includes signed floating-point coordinates, arm radii, RPM for each direction, catch-relative speeds, impact coordinates/times and hub-to-impact distances.


## Impact locations for both directions

All impacts below are on the equator; coordinates are body-fixed decimal degrees,
positive east. “Outbound” is a failed departure, not a successful arrest following
a missed catch. A no-impact result would mean only no contact within the cutoff.

| Hub | Direction | Event | Impact longitude (°) | Time (min) | Distance from hub (km) |
| --- | --- | --- | ---: | ---: | ---: |
| E-S1 | east | Outbound | 144.260016 | 0.0251 | 6.465 |
| E-S1 | west | Outbound | 144.174627 | 0.0006 | 5.952 |
| E-S2 | east | Outbound | -92.710585 | 0.0640 | 8.376 |
| E-S2 | west | Outbound | -92.927026 | 0.0013 | 5.361 |
| E-S3 | east | Outbound | -77.113179 | 0.0009 | 5.894 |
| E-S3 | west | Outbound | -93.047358 | 4.7760 | 483.121 |
| E-N1 | east | Outbound | -66.097181 | 0.0456 | 8.050 |
| E-N1 | west | Outbound | -66.276594 | 0.0082 | 6.656 |
| E-S4 | east | After missed catch | -140.240590 | 87.3199 | 2255.697 |
| E-S4 | west | Outbound | -65.865253 | 0.0038 | 4.724 |
| E-N2 | east | Outbound | -63.965616 | 0.0247 | 4.662 |
| E-N2 | west | Outbound | -64.129882 | 0.0245 | 4.658 |
| W-S1 | east | Outbound | -166.675629 | 0.0009 | 6.308 |
| W-S1 | west | Outbound | -166.708267 | 0.0089 | 6.371 |
| W-N1 | east | Outbound | -166.570589 | 0.0002 | 4.294 |
| W-N1 | west | Outbound | -166.806828 | 0.0709 | 8.334 |
| W-S2 | east | Outbound | -165.665466 | 0.0082 | 5.715 |
| W-S2 | west | After missed catch | -140.085512 | 101.8071 | 776.505 |

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
