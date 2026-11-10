# Adjusted four: hubs on the hilltops

These replace the nearby original hub placements for the four featured terrain illustrations. Each hub now sits on the highest SLDEM2015 grid vertex inside its original sweep disk. Repeating that search around the new hub returns the same summit in every case. The original four locations remain available [for comparison](../README.md).

We retain each original tether radius (5.72–5.86 km), the 76.79 m track radius, and the tip plane 1.3768 m above the hub tangent plane. Moving the hub therefore moves the release point away from the equator; we do not silently resize the launcher to recover an equatorial release.

## Placement comparison (not the publication table)

Latitude is signed north-positive; longitude is signed east-positive. The CSV also includes 0–360° east longitude. All distances below are metres.

| Site | Latitude | Longitude | Hub move | Elevation gain | Tip offset from equator | Minimum tip-circle clearance |
|---|---:|---:|---:|---:|---:|---:|
| P1_H0333_hilltop | +0.11425781 | +16.15722656 | 3910.7 | 256.3 | -2249.7 | 423.6 |
| P2_H4765_hilltop | -0.15917969 | +137.34082031 | 2357.9 | 86.2 | +1006.5 | 264.4 |
| P3_H6308_hilltop | +0.16503906 | -111.47949219 | 1221.0 | 34.8 | -769.8 | 274.8 |
| P4_H6941_hilltop | +0.17089844 | -73.57128906 | 880.4 | 45.6 | -651.3 | 274.2 |

Tip offset is signed north-positive. A northern hub can now have its equator-facing meridional tip **south** of the equator (and vice versa).

**[Publication table and updated flight checks](PUBLICATION.md):** all four adjusted intended tips clear eastward to 25 km apoapsis. P2 clears westward from both its intended and opposite tips; P1, P3 and P4 do not clear westward from either tip. These are off-equator terrain checks, not a completed equatorial-catcher targeting solution. The separate comparison table below retains the placement history.

## Method and limits

The hilltop search uses native ~59 m grid vertices, not the lower-resolution rendered image. Each selected point is also checked against its eight neighboring vertices. In all four recentered sweep disks, the highest native terrain vertex is the hub itself (0 m maximum rise). The tip-circle clearance is the minimum vertical gap between the fixed tip plane and terrain projected onto the hub vertical, sampled at 144,000 bearings; comparison with 72,000 bearings agrees within 0.05 m. This convergence is numerical, not a claim of centimetre DEM accuracy.

This resolves the visible taller-hill-inside-the-circle issue. It does not establish rover track grade, small unresolved obstacles, or the clearance of a dynamically drooping tether. Coordinates identify DEM summits, not surveyed construction pads.

The equator-facing meridional tip uses angular offset atan(arm / (Moon radius + summit elevation + plane offset)); its local ground clearance is calculated separately in the CSV. Hub displacement is great-circle distance using the 1,737.4 km reference radius.

## Files and reproduction

- [Numeric table](hilltop_sites.csv) and [full results](results.json).
- [Terrain maps](maps/README.md): four 15 × 15 km views, PNG and SVG, without impact markers.
- [Generator](build.py): run `MPLCONFIGDIR=/tmp/lunar-sling-mpl-cache OPENBLAS_NUM_THREADS=1 .env/hub/bin/python -m llo_catcher.site_selection.featured_four.adjusted_hilltops.build` from the repository root. Uses the existing cached SLDEM2015 bands.
