# Terrain maps: separate eastward / westward site checks

[Direction-specific results and assumptions](../README.md).

All maps show a **15 × 15 km** region with the hub, 76.79 m track inset,
actual-radius tether sweep, common equatorial release point, and both directions’
first impacts where visible. East and west are alternative launches after
reversing rotation, **not opposite-tip simultaneous launches**. Notes distinguish
outbound collisions from impacts after missed capture and flag full-circle
terrain intersections. Each PNG has a matching SVG.

## Equatorial elevation and corridor plots

- [Entire equator, 0–360°](../../equatorial_elevation.png) · [SVG](../../equatorial_elevation.svg): eight eastward and two westward clear one-degree seeds at 10 m.
- [Direction-specific detail and corridor overlays](../../equatorial_elevation_detail.png) · [SVG](../../equatorial_elevation_detail.svg).

## Local terrain maps

| Search | Candidate | Terrain map | SVG |
| --- | --- | --- | --- |
| east | E-S1 | [PNG](E-S1_15km.png) | [SVG](E-S1_15km.svg) |
| east | E-S2 | [PNG](E-S2_15km.png) | [SVG](E-S2_15km.svg) |
| east | E-S3 | [PNG](E-S3_15km.png) | [SVG](E-S3_15km.svg) |
| east | E-N1 | [PNG](E-N1_15km.png) | [SVG](E-N1_15km.svg) |
| east | E-S4 | [PNG](E-S4_15km.png) | [SVG](E-S4_15km.svg) |
| east | E-N2 | [PNG](E-N2_15km.png) | [SVG](E-N2_15km.svg) |
| west | W-S1 | [PNG](W-S1_15km.png) | [SVG](W-S1_15km.svg) |
| west | W-N1 | [PNG](W-N1_15km.png) | [SVG](W-N1_15km.svg) |
| west | W-S2 | [PNG](W-S2_15km.png) | [SVG](W-S2_15km.svg) |

No additional 80 km context map is needed for these same-equatorial-tip shots:
all impacts outside a local map are also outside ±40 km bounds. The older 80 km
maps remain valid for their **different opposite-tip geometry**, and are preserved
in the [historical map set](../../summit_sites/maps/README.md).

The terrain colors are elevation relative to the hub; illumination is synthetic.
The circumference overlay does not assert that a horizontal tether clears terrain.
[Map index](map_index.json) records projected impact locations and visibility;
[input hashes](inputs.json) tie these overlays to the saved catalog. Terrain data
and trajectories are reused, not recalculated by the plotting script.

Reproduce from the repository root:

```bash
MPLCONFIGDIR=/tmp/lunar-sling-mpl-cache .env/hub/bin/python -m llo_catcher.analysis.single_equatorial_release.plot_equator
MPLCONFIGDIR=/tmp/lunar-sling-mpl-cache .env/hub/bin/python -m llo_catcher.analysis.single_equatorial_release.directional_sites.build_maps
```
