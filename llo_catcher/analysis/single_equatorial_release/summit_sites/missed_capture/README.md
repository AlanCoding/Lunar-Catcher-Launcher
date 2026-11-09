# Six summit hubs: eastward and opposite-tip westward first impacts

**[Separate eastward/westward site tables](../../directional_sites/README.md).** These westward shots start at the opposite, off-equator tip. For westward equatorial launch and separate westward-selected hubs, use the new direction-specific catalogs.

Only **S4 east** and **S3 west** reach their intended catch points in the same-plane comparison. After missed capture they hit terrain 2,255.70 km and 601.17 km from their respective hubs. S3 west crosses back inside the projected tether footprint. The modeled payload remains above the tip plane throughout that crossing.

## Release geometry

The east shot starts exactly on the equator, 10 m above the local ground, tangent to the sphere and heading due east. Its apoapsis coincides with a 25 km circular equatorial catcher. For the primary west shot, reflect the east tip across the hub's vertical axis, keeping the same horizontal plane and arm radius. Its starting latitude is twice the hub latitude and its initial height above ground follows from the terrain there. Offsets from the equator range from about 7.9 to 13.2 km.

The west velocity is due west and perpendicular to the lunar radius. The payload first crosses the equator 90 degrees into its orbital path. Set its semilatus rectum to the 35 km circular catcher's radius so that crossing occurs at the catch altitude. Assume station phasing and independently target each direction's release speed. Stop every trajectory at first terrain contact or 1.5 payload periods.

## First terrain contacts

All angles use body-fixed signed decimal degrees, positive north and east. Distances are great-circle distances from the hub on the 1,737.4 km reference sphere. “After miss” means the terrain was clear through the scheduled catch. “Outbound” means terrain prevented the intended catch.

| Hub | Shot | Release latitude | Release clearance (m) | Outcome | Impact latitude | Impact longitude | Hub to impact (km) | Time since release (min) | Sweep re-entry |
| --- | --- | ---: | ---: | --- | ---: | ---: | ---: | ---: | --- |
| S1 | east | 0.000000 | 10.0 | Outbound | 0.000000 | 144.260016 | 6.465 | 0.02513 | No |
| S1 | west | -0.392578 | 366.8 | Outbound | -0.392572 | 143.858213 | 11.346 | 0.09505 | No |
| S2 | east | 0.000000 | 10.0 | Outbound | 0.000000 | -92.710585 | 8.376 | 0.06396 | No |
| S2 | west | -0.353516 | 62.2 | Outbound | -0.353501 | -93.449954 | 16.858 | 0.15701 | No |
| S3 | east | 0.000000 | 10.0 | Outbound | 0.000000 | -77.113179 | 5.894 | 0.00091 | No |
| S3 | west | -0.388672 | 1588.2 | After miss | -0.368042 | -96.940997 | 601.169 | 117.25999 | Yes, above plane |
| N1 | east | 0.000000 | 10.0 | Outbound | 0.000000 | -66.097181 | 8.050 | 0.04562 | No |
| N1 | west | 0.435547 | -404.9 | Starts below terrain | — | — | — | — | — |
| S4 | east | 0.000000 | 10.0 | After miss | 0.000000 | -140.240590 | 2255.697 | 87.31989 | No |
| S4 | west | -0.310547 | 27.9 | Outbound | -0.310546 | -65.970174 | 5.907 | 0.03492 | No |
| N2 | east | 0.000000 | 10.0 | Outbound | 0.000000 | -63.965616 | 4.662 | 0.02468 | No |
| N2 | west | 0.259766 | -16.4 | Starts below terrain | — | — | — | — | — |

The east and west tips of N1 and N2 cannot both occupy the specified plane at release. Their west endpoints are respectively 404.9 m and 16.4 m below the interpolated surface. A first-impact location is undefined for these starting states.

## Does the payload cross the tether sweep?

Each shot begins on its own tether's outer edge. Re-entry means that, after departure, the payload passes inside the actual site-specific radius about the hub axis on the near side of the Moon. The calculation rotates the hub with the Moon and measures the payload's transverse distance from that axis, then evaluates its height above the plane. Ground distance in the table uses the reference sphere, so it can be slightly shorter than the elevated tether radius even at an impact just outside the physical disk.

S3 west reaches its equatorial catch point at about 27 minutes. Following a miss, it re-enters the projected disk **111.34837 minutes** after launch, exits at **111.35126 minutes**, and lands at **117.25999 minutes**. During those **0.174 seconds**, its maximum penetration is **1.849 m** inside the 5.902 km radius. Its height is **4.982–5.078 m above the tip plane**. It clears the ideal horizontal disk. An actual tether contact assessment would require its height, motion, dimensions and rotation phase at that instant.

Every other launched shot stays outside its own disk after release. All first impacts lie outside the swept disk. Some modeled edge margins are sub-metre. Terrain resolution and hardware dimensions matter when interpreting such small separations.

## Alternative westward assumption: give that tip 10 m local clearance too

This alternative holds horizontal arm radius fixed, shifts the west release latitude slightly to meet local 10 m clearance, and independently targets the 35 km catcher. The two tips generally require different plane heights. All six west shots strike terrain outbound and stay outside the disk after departure.

| Hub | West release latitude | Impact latitude | Impact longitude | Hub to impact (km) | Time (s) |
| --- | ---: | ---: | ---: | ---: | ---: |
| S1 | -0.392618 | -0.392618 | 144.174902 | 5.954 | 0.033 |
| S2 | -0.353521 | -0.353507 | -93.437230 | 16.493 | 9.193 |
| S3 | -0.388848 | -0.388848 | -77.118546 | 5.899 | 0.042 |
| N1 | 0.435495 | 0.435495 | -66.250703 | 6.602 | 0.030 |
| S4 | -0.310548 | -0.310548 | -65.922044 | 5.159 | 1.238 |
| N2 | 0.259764 | 0.259764 | -64.048662 | 3.938 | 0.014 |

This explains why the two westward answers differ for S3. At the mirrored tip the terrain falls far enough to give 1,588 m of clearance. Resetting the west tip to 10 m removes almost all of that height.

## Common RPM and what the ballistic results establish

Equal arm radii at a common RPM give both payloads the same speed relative to the rotating surface. For a same-plane mirror, use the east shot's surface-relative speed and subtract lunar rotation at the west release latitude to obtain west inertial speed. Its node radius is then `r_release² v_inertial² / mu`. In these six cases the resulting node altitudes range from **−7.52 to −4.84 km** relative to the reference sphere. None reaches the specified 35 km catcher under that constraint. The independently targeted trajectories above answer the requested miss and impact question. Simultaneous operation at one RPM would require different arm geometry or a changed catch target.

## Data, verification and reproduction

- [Signed hub coordinates](../hub_coordinates.csv) and [summit catalog](../README.md).
- [East and local-10-m west CSV](shots.csv) and [same-plane west CSV](opposite_tip.csv). Impact coordinates and distances are numeric. Empty impact fields denote an unavailable physical release or impact.
- [Trajectory results](results.json) and [mirrored results with sweep events](mirrored_west.json).
- [Model code](calculate.py), [independent checks](verify.py), and [validation results](validation.json).

East contacts reuse the equatorial DEM-cell intersection solver. West contacts are refined with 0.5 m and 0.25 m trajectory steps and bracketed first-contact roots. The westward release and return latitude corridor uses the wider summit terrain cache, with an extra public SLDEM2015 strip in the 315–360° E sector. Independent Cartesian integration reproduces the 16 computed contacts within 0.1 mm in this DEM model and confirms the S3 sweep entry and exit within 1 mm. Numerical tolerances describe model agreement. The underlying DEM has approximately 59 m equatorial pixel spacing and metre-scale elevation uncertainty.

From the repository root, with the parent terrain caches installed:

```bash
.env/hub/bin/python -m llo_catcher.analysis.single_equatorial_release.summit_sites.missed_capture.extend
.env/hub/bin/python -m llo_catcher.analysis.single_equatorial_release.summit_sites.missed_capture.calculate
.env/hub/bin/python -m llo_catcher.analysis.single_equatorial_release.summit_sites.missed_capture.verify
```
