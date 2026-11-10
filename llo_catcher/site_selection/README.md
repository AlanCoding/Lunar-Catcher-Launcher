# Lunar launcher site selection

[Broader LLO catcher topic](../README.md).

**[Current blog publication packet](publication/README.md):** ordered checklist, ready-to-copy figures and tables, and the final radial terrain-envelope graph.

The **[second-pass global hill-first search](global_hills/README.md)** is the current
candidate survey. It scans all equatorial longitudes for hub peaks and checks
terrain around each tip circle **before** testing eastward and westward launches.
It does not preselect neighborhoods using the old 10 m release-clearance test.

**Default population:** use the [non-overlapping selection](global_hills/README.md),
which excludes intersecting swept disks and prioritizes reference-arm equatorial
alignment. Raw peaks are archived, not the default plotting or analysis set.

**[Four adjusted hilltop locations](featured_four/adjusted_hilltops/README.md)** are the current terrain illustrations: the featured hubs moved onto the higher nearby summits. These accept off-equator release positions; [updated flight checks and a publication table](featured_four/adjusted_hilltops/PUBLICATION.md) give eastward and both westward outcomes. The [original four-site selection](featured_four/README.md) preserves the equatorial launch results and selection criteria.

## Terrain input for sling design

- **[Maximum terrain height versus radius](radial_terrain/README.md):** ring-by-ring terrain envelopes for all four adjusted summits and a publication graph for the selected hill. The separate [sag/taper plan](../../sling_launcher/sag_taper_trade/README.md) will use these profiles to study cable shape and support height.

## New investigation

- **[Eastward launch ridges](launch_ridges/README.md):** raise a fixed-apoapsis orbit to find its final terrain contacts, then test fresh launches from those points. The regional demonstration produces coherent contact lines; most sampled contacts need negligible extra release height, while some need up to 225.6 m. Includes terrain maps and orbit profiles. The [expanded four-region search](launch_ridges/expanded/README.md) compares the ridges with all four featured summit sites. The [named ridge catalog](launch_ridges/catalog/README.md) supplies publication tables and global-context maps.

## Blog reading order

1. **[Elevation against longitude](../analysis/single_equatorial_release/equatorial_elevation.png)**
   ([SVG](../analysis/single_equatorial_release/equatorial_elevation.svg)). The full
   equator establishes terrain context. Its markers are the original low-release
   seeds, not the full population found by the new hill-first search.
2. **[Global hill-first outcomes](global_hills/outcomes.png)**
   ([SVG](global_hills/outcomes.svg)). Red = blocked before capture; green = clears to the catcher.
   Only the non-overlapping hubs are plotted, with both launch directions checked.
3. **[Four hilltop sites: publication table](featured_four/adjusted_hilltops/PUBLICATION.md)** and
   **[numeric table](featured_four/adjusted_hilltops/publication_sites.csv)**: coordinates, summit elevations, off-equator offsets, tip clearance and westward outcomes.
   The [parent non-overlapping catalog](global_hills/README.md) retains the broader statistics.
4. **[Terrain-map gallery for the four selected hubs](featured_four/adjusted_hilltops/maps/README.md)**:
   hub, track, tip circle and release marker, with no impact overlays.

## Height and geometry

Use the go-kart loaded tip centerline **0.8768157 m above the hub tangent plane**,
plus the requested **0.5 m**, for a total of **1.3768157 m**. Local release
clearance adds lunar curvature and the hub-to-release terrain elevation difference.
Do not reset the release to 10 m above its local ground after selecting a summit.

[The height-reference explanation](HEIGHT_REFERENCE.md) documents the earlier
mistake, the sign conventions, equations, original nine-site audit and validation.
The global pass uses that corrected geometry. Positive tip-circle clearance
means the ideal circumference clears the sampled terrain; it does not certify
clearance of the entire drooping tether or a finite-sized payload.

## Earlier work and supporting analyses

- [First nine-site height audit](HEIGHT_REFERENCE.md#hub-relative-height-diagnostic):
  original corridor-selected hubs, recalculated using the go-kart endpoint height.
- [Original 10 m red/green/blue survey](search_outcomes.png): the initial equatorial
  point-launch screen, before hilltop placement. Mostly red; no blue cases at 10 m.
- [Eastward release corridors](../analysis/single_equatorial_release/local_corridors/README.md)
  and [separate westward search](../analysis/single_equatorial_release/directional_sites/README.md):
  historical corridor-first selection. Useful for comparison, not the latest candidate count.
- [Original height survey](../analysis/single_equatorial_release/README.md): the
  roughly 50% red / 25% green / 25% blue result required a **2,310.7 m** local
  release height; it is a different experiment.
- [Original hilltop-placement method](../analysis/single_equatorial_release/summit_sites/README.md)
  and [historical opposite-tip maps](../analysis/single_equatorial_release/summit_sites/maps/README.md).
- [Off-equator counterpart study](../analysis/single_equatorial_release/summit_sites/missed_capture/README.md):
  a separate geometry and catcher target, not the reverse-direction equatorial launch test.
