# Launch-site blog: publication asset checklist

[Site-selection guide](../README.md).

**Accepted asset set.** The numbered files in [assets/](assets/) are local copies ready to move into a writing or publishing folder. PNG and SVG versions are included for every figure. Tables are supplied as short Markdown files and, where available, CSV files. The source figures remain in their analysis folders.

## Article order

| Order | Article item | Ready-to-copy file | Notes |
|---|---|---|---|
| 1 | Intro: elevation along the lunar equator | [PNG](assets/01_equatorial_elevation.png) · [SVG](assets/01_equatorial_elevation.svg) | Full 360° profile; markers belong to the original 10 m point-release survey. |
| 2 | The 144° E launch clearing a later mountain range | [PNG](assets/02_trajectory_144.png) · [SVG](assets/02_trajectory_144.svg) | Existing trajectory/terrain overlay covers 144–240° E. It shows 407.7 m clearance at the annotated mountain range, for release 10 m above local terrain. |
| 3 | Red/green launch-clearance scan | [PNG](assets/03_hub_scan_east_west.png) · [SVG](assets/03_hub_scan_east_west.svg) | Use the upper panel for the eastward discussion; the lower panel gives westward context. Each panel contains the same 695 selected hubs. |
| 4 | Scan counts and narrowing to featured hubs | [Tables](assets/04_hub_scan_tables.md) | 403,002 local peaks → 17,572 circle-clear candidates → 695 spaced hubs → 42 east-clear → 15 alignment-qualified → 6 clearance-qualified → 4 geographically diverse hubs. Also includes the four outcome categories summing to 695. |
| 5 | Four featured hilltops | [Table](assets/05_four_hills.md) · [CSV](assets/05_four_hills.csv) | Adjusted summit positions, elevation, release offset, tip clearance, and both westward checks. |
| 6 | Satellite photograph of one or two hills | Author-supplied | Reserved for the photographs selected for the article. |
| 7 | Terrain maps of the four hills | [P1](assets/07_P1_terrain.png) · [P2](assets/07_P2_terrain.png) · [P3](assets/07_P3_terrain.png) · [P4](assets/07_P4_terrain.png) | Accepted final terrain maps with ridge traces, named ridge, summit star and release triangle. SVG copies use the same stems. |
| 8 | Ridge-finding sample and segment counts | [Table](assets/08_ridge_scan_table.md) | 3,564 seeds → 3,354 qualifying downstream contacts; 3,335 samples form 84 named segments, with 19 samples left isolated or insufficiently traced. Four named segments contain the featured hubs. |
| 9 | Which ridge contains each featured hilltop | [Table](assets/09_hilltop_ridges.md) · [CSV](assets/09_hilltop_ridges.csv) | P1 → ER-006; P2 → ER-023; P3 → ER-058; P4 → ER-072. |
| 10 | Banded ridge map around the whole equator | [PNG](assets/10_equatorial_ridges.png) · [SVG](assets/10_equatorial_ridges.svg) | Accepted 12-band layout: muted terrain, stronger ridge lines, large type, 10° labels and 1° minor ticks. Seed-search windows are marked. |
| 11 | Maximum terrain height versus radius from a selected hub | [PNG](assets/11_selected_hill_terrain.png) · [SVG](assets/11_selected_hill_terrain.svg) · [CSV](assets/11_selected_hill_terrain.csv) | Completed terrain envelope; [method and four-hill comparison](../radial_terrain/README.md). |

## Closing example: lowering the release

[Ready-to-copy table](assets/12_lowered_release.md) · [CSV](assets/12_lowered_release.csv) · [Calculation and interpretation](../radial_terrain/LOWERED_RELEASE.md). P1 clears eastward in all tested cases: subtracting the 28.68 m reference apex height, then endpoint heights of −100, −200 and −300 m relative to the hub tangent plane.

## Optional sling-footprint figures

The accepted P1–P4 ridge maps are the primary terrain illustrations above. Earlier 15 × 15 km maps also show the **76.79 m rover track and full tip sweep circle**. Copies are included as `07_alternative_P1_sling_footprint` through `07_alternative_P4_sling_footprint`, each in PNG and SVG:

- [P1 footprint](assets/07_alternative_P1_sling_footprint.png)
- [P2 footprint](assets/07_alternative_P2_sling_footprint.png)
- [P3 footprint](assets/07_alternative_P3_sling_footprint.png)
- [P4 footprint](assets/07_alternative_P4_sling_footprint.png)

These offer a useful hardware-geometry illustration alongside a ridge map if space permits.

## Captions and interpretation

**Elevation and 144° example.** Both originate in the equatorial point-launch study. The 144° example retains its original 10 m local-ground release condition. The later summit-placement study uses hub-relative height and finite sling geometry.

**Hub scan.** Each panel plots 695 distinct hub candidates, with 42 green and 653 red for that direction. Across both directions, 39 clear east only, 39 west only, three both, and 614 encounter terrain before the catcher in both directions. Non-overlap selection prioritizes equatorial alignment. After choosing four representatives, the hubs were moved onto the nearby summits and departure checks repeated. The featured table reports those final positions.

**Ridge accounting.** Contact samples can rediscover the same feature from several starting locations. The progression changes units when contacts are grouped into named connected segments. The ridge table explicitly labels those units. This search uses four regional longitude windows and finite seed spacing; further sampling can reveal additional ridges and branches.

**Equatorial ridge map.** The figure displays the full longitude range, with regional discoveries superimposed. Blue bars identify the four seed-longitude windows. North–south distances are stretched for readability. The names identify segments in the study catalog.

## Sources and maintaining this packet

- [Global hill search](../global_hills/README.md): original population and directional counts.
- [Original four-site down-selection](../featured_four/README.md): alignment, clearance and diversity criteria.
- [Adjusted hilltop publication table](../featured_four/adjusted_hilltops/PUBLICATION.md): final coordinates and flight checks.
- [Expanded ridge search](../launch_ridges/expanded/README.md): accepted P1–P4 terrain maps.
- [Named ridge catalog](../launch_ridges/catalog/README.md): segment definitions, geographic scalar table, and the final banded map.
- [Asset manifest](manifest.json): source paths and SHA-256 hashes.

Asset packaging copies approved figures and reads saved result tables. The source analyses contain the numerical calculations and their validation. To refresh these copies after an approved source change:

```bash
.env/hub/bin/python -m llo_catcher.site_selection.publication.package
```

The [packaging script](package.py) updates this folder’s assets and manifest. Copy the entire `publication` folder to retain this checklist, tables, figures, and the plan together.
