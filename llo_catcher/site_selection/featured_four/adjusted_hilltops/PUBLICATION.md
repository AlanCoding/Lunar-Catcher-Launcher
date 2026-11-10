# Four hilltop launcher sites

[Terrain maps](maps/README.md) · [Machine-readable publication table](publication_sites.csv) · [Placement method and comparison](README.md)

Latitude and longitude are decimal degrees, north/east positive. Elevation is relative to the 1,737.4 km lunar reference sphere. Tip offset is signed north-positive, for the intended (equator-facing) north–south tip.

| Site | Hub latitude | Hub longitude | Elevation (m) | Tip equator offset (m) | Min. tip-circle clearance (m) | West: intended tip | West: opposite tip |
|---|---:|---:|---:|---:|---:|:---:|:---:|
| P1 | +0.11425781 | +16.15722656 | 608.8 | -2249.7 | 423.6 | No | No |
| P2 | -0.15917969 | +137.34082031 | 6482.6 | +1006.5 | 264.4 | Yes | Yes |
| P3 | +0.16503906 | -111.47949219 | 5083.0 | -769.8 | 274.8 | No | No |
| P4 | +0.17089844 | -73.57128906 | 2263.4 | -651.3 | 274.2 | No | No |

**Yes means terrain clears from release through the first 25 km apoapsis.** It does not mean an equatorial catcher rendezvous has been solved. No means a terrain intersection occurs on that outbound leg. The opposite tip is diametrically across the hub, farther from the equator; it is not the same release point with velocity reversed.

The four sites use 5.72–5.86 km arm radii, a 76.79 m rover track, and a tip plane 1.3768 m above the hub tangent plane. Positive tip-circle clearance describes the minimum gap around the circular rim, not clearance of the entire drooping tether. P1–P4 correspond to the same labels on the existing terrain maps.

[Expanded ridge association](../../launch_ridges/expanded/README.md): all four adjusted summits match independently discovered eastward contact ridges within the DEM resolution. Includes a terrain overlay for each site.

## Flight checks

| Site | Release | Latitude | Local release clearance (m) | West clears | First west impact after release (min) |
|---|---|---:|---:|:---:|---:|
| P1 | Intended tip | -0.07419095 | 1514.7 | No | 0.46 |
| P1 | Opposite tip | +0.30270658 | 1027.3 | No | 1.66 |
| P2 | Intended tip | +0.03319361 | 1388.4 | Yes | — |
| P2 | Opposite tip | -0.35155299 | 1177.1 | Yes | — |
| P3 | Intended tip | -0.02538683 | 1052.1 | No | 0.83 |
| P3 | Opposite tip | +0.35546495 | 954.4 | No | 1.50 |
| P4 | Intended tip | -0.02147933 | 499.1 | No | 0.92 |
| P4 | Opposite tip | +0.36327620 | 1511.0 | No | 1.09 |

As a consistency check we also reran eastward departure from the intended tip: P1 clears, P2 clears, P3 clears, P4 clears.

## Numerical approach

Each tip retains its actual three-dimensional radius sqrt((R + hub elevation + plane offset)² + arm²). Release velocity is horizontal and purely westward (eastward for the additional check), with speed chosen by vis-viva so release is periapsis and apoapsis is R + 25 km. Both tips have the same radial altitude but different underlying terrain. Adding the lunar surface rotation changes the required surface-relative speed, not this chosen inertial orbit.

The trajectory is an analytic inclined Kepler ellipse under spherical 1/r² gravity. Its position is rotated into Moon-fixed coordinates using lunar spin, and altitude is compared against the bilinearly interpolated SLDEM2015 terrain at its actual latitude and longitude. No equatorial terrain-profile substitution is used. A due-west shot from nonzero latitude reaches apoapsis at the opposite latitude, so reaching this altitude is only a terrain-screening proxy for reaching a catcher.

We sample true anomaly at a spacing corresponding to at most ~15 m of inertial orbital arc (well below the ~59 m native DEM spacing), compare against a ~30 m run, refine the sampled global minimum locally, and bracket the first intersection. All classifications agree between the two resolutions and minimum gaps agree within 0.5 m. This is a sampled terrain screen, not a rigorous bound on DEM errors or unresolved obstacles. Mascons, external gravity, targeting corrections, and release transients are excluded. Propagation stops at apoapsis; no post-miss orbit is needed for these yes/no questions.

- [Full checks, including impact coordinates and minimum gaps](launch_checks.json).
- Reproduce with `.env/hub/bin/python -m llo_catcher.site_selection.featured_four.adjusted_hilltops.check_launches` after generating the hilltop catalog with `build.py`.
