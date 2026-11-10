# Eastward launch-ridge catalog

[Ridge investigation](../README.md) · [Expanded search](../expanded/README.md)

**ER-001, ER-002, … are study names for mapped contact-ridge segments.** This first catalog contains 84 traced segments from the four regional searches. Names refer to this version of the catalog and should be retained through a crosswalk if future sampling splits or joins segments.

The algorithm samples four regional longitude windows at 1.5° intervals and the ±6 km equatorial band at 125 m intervals. This finite coverage and spacing can miss qualifying ridges and narrow branches. The catalog therefore describes the features found in this search; further sampling can extend it.

## Featured ridges

Coordinates are a representative sampled point on each segment, in signed decimal degrees (north/east positive). Elevations use the lunar reference sphere. The north–south span measures the extent of the mapped samples.

| Ridge | Associated hub | Representative latitude | Representative longitude | North–south span (km) | Elevation range (m) |
|---|---|---:|---:|---:|---:|
| ER-006 | P1 | +0.102783 | +16.157227 | 5.87 | -187–609 |
| ER-023 | P2 | -0.168278 | +137.325195 | 1.77 | 6366–6483 |
| ER-058 | P3 | +0.176820 | -111.489258 | 1.39 | 5015–5083 |
| ER-072 | P4 | -0.004117 | -73.493164 | 12.00 | 1972–2263 |

## Hilltops and their ridges

| Hilltop | Hub latitude | Hub longitude | Ridge |
|---|---:|---:|---|
| P1 | +0.11425781 | +16.15722656 | ER-006 |
| P2 | -0.15917969 | +137.34082031 | ER-023 |
| P3 | +0.16503906 | -111.47949219 | ER-058 |
| P4 | +0.17089844 | -73.57128906 | ER-072 |

## Equatorial ridge map

- **[Twelve stacked equatorial strips](equator_strips.png)** ([SVG](equator_strips.svg)): 30° longitude per row, with all named traces and labels for the four featured ridges.
- [Detailed terrain maps of the four featured ridges](../expanded/README.md#terrain-maps).

The map covers all longitudes. Blue bars locate the four seed-longitude windows, sampled every 1.5°. Terrain contacts can lie beyond those windows because trajectories are followed to apoapsis. Empty areas show where these searches contributed no cataloged traces. The north–south scale is stretched for visibility. The muted terrain background uses coarser sampling; ridge coordinates retain the original native-grid calculations.

Dark lines show the mapped contact-ridge segments. Orange lines and labels highlight the four segments associated with P1–P4. The expanded analysis provides the required fresh-launch heights along these traces.

## How a segment is defined

We keep downstream contacts only (release-height raising >0.1 m and contact anomaly >0.05°). Consecutive samples from a common seed meridian are linked when their seed northing differs by at most 126 m and their contact separation is at most 1 km. Contacts from different seed paths within 80 m are merged to remove repeated discoveries. Connected components with at least three distinct contact latitudes (rounded to 0.00001°) receive names, sorted by median east longitude and then latitude. These thresholds define reproducible connected segments. Nearby branches can remain separate and disconnected portions of one physical ridge can have different names.

Scalar ranges use the component’s actual contact samples. Representative coordinates are the sample nearest the median coordinates after collapsing repeated samples into approximately 59 m cells. Lines between samples are visual interpolation. We avoid total line length because overlap, branching and incomplete sampling would make it misleading.

The catalog excludes 19 isolated or insufficiently traced contact samples from naming. They remain in the source results. The original six geographic groups used broader longitude-based grouping; this catalog separates connected traces within the expanded search.

The hub latitudes were selected previously to favor a roughly 5.8 km sling reaching near the equator. Their hubs lie about 3.5–5.2 km north or south of the equator. The expanded ridge search covers ±6 km, which itself limits the mapped segment spans.

## Data and reproduction

- [Full ridge table](ALL_RIDGES.md), [CSV](ridges.csv), [JSON with source hash](ridges.json).
- [Publication hilltop–ridge table CSV](featured_hubs.csv).
- [Generator](build.py): `.env/hub/bin/python -m llo_catcher.site_selection.launch_ridges.catalog.build` using the existing environment and DEM cache. This groups existing results; it performs no new orbit search.
