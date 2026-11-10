# Four east-launching locations for the post

[Site-selection guide](../README.md) · [Non-overlapping parent catalog](../global_hills/README.md)

These four are selected from the **695 non-overlapping hubs**, not the raw peak
population. All clear an eastward launch to the 25 km catcher under the inherited
model. “Best” means best under the explicit alignment, clearance and diversity
rules below, not a globally optimized installation design.

**Updated placements:** [Move these four hubs onto their nearby hilltops](adjusted_hilltops/README.md), with a new coordinate table and [regenerated maps](adjusted_hilltops/maps/README.md). The results below describe the original placements; their launch classifications do not carry over automatically.

## Selected locations

Coordinates are signed decimal degrees, positive north/east. The **reference-arm
miss** is how far the original 5,787.088 m go-kart arm would put the tip from the
equator. The **modeled arm** is individually adjusted so the actual simulated
release is exactly on the equator. We have not simulated an off-equator shot
using the unadjusted reference arm.

| Label | Catalog ID | Hub latitude (°) | Hub longitude (°) | Reference-arm equator miss (m) | Modeled arm (km) | Minimum tip-circle clearance (m) | Hub elevation (m) |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| P1 | H0333 | 0.188477 | 16.051758 | 70.6 | 5.7164 | 222.0 | +352.5 |
| P2 | H4765 | -0.192383 | 137.411133 | 67.9 | 5.8552 | 106.4 | +6396.3 |
| P3 | H6308 | 0.190430 | -111.510742 | 4.2 | 5.7913 | 246.9 | +5048.2 |
| P4 | H6941 | 0.192383 | -73.590820 | 54.0 | 5.8412 | 199.5 | +2217.7 |

[Full numeric table](selected_sites.csv) · [Selection results](results.json).
P1, P3 and P4 have northern hubs; P2 has a southern hub. P2 also clears westward;
the other three do not. Its historical lack of return impact did not affect
selection; that calculation is no longer a down-selection criterion.

## Interior terrain: these are not yet installation-qualified sites

Map review exposes terrain above the hub **inside** all four tip circles.
The highest sampled internal terrain rises above hub ground by:

- **P1: 256.3 m**.
- **P2: 86.2 m**.
- **P3: 34.8 m**.
- **P4: 45.6 m**.

These values are ground-height differences, not calculated rope clearances.
They demonstrate why a clear circumference does not certify a rotating rope
through the interior. In particular, P1's 256 m interior rise is a substantial
obstruction to investigate. Checking the full drooped rope profile, or changing
pole/guide geometry, is required before presenting these as four usable
installations. The selection fulfills the requested **tip-circle** ranking;
this limitation is explicitly not hidden by calling it a hilltop.

## How the four were chosen

1. Start with the 695 disjoint-sweep hubs; retain **42 eastward-clear** candidates.
2. Require **reference-arm equator miss ≤100 m**: **15** remain.
3. Require **minimum tip-circle clearance ≥100 m**: **6** remain.
4. Enumerate every four-site combination and require at least **30° longitude
   separation between every pair**, including wraparound: **2** combinations qualify.
5. Maximize the sum of tip-circle clearance over those combinations. Smaller
   total equator miss would break a tie. No tie occurred.

The 100 m alignment threshold is one tenth of the kilometre-scale misses the
user wants to avoid. The 100 m terrain threshold demands a substantial local
margin rather than simply a high absolute elevation. The 30° diversity threshold
corresponds to approximately 910 km along the equator. These are explicit
editorial selection choices; they are adjustable inputs, not physical limits.
All four remain mutually non-overlapping because they are a subset of the
validated parent selection.

The closest longitude pair is P3/P4, separated by about **37.92°**, or **1,150 km**
along the equator. P1 demonstrates why absolute elevation is not the ranking
metric: its summit is only about 353 m above the reference sphere, but the terrain
around its tip circle lies more than 221 m below the modeled tip plane.

## What tip-circle clearance means

At each bearing around the full rotating tip circle, compare the tip plane with
the terrain projected along the hub's vertical axis. **Tip-circle clearance is
the smallest of those gaps.** Positive means the modeled tip centerline remains
above terrain around the entire circle; negative means terrain intersects it.

It is not the payload's clearance at the release point alone, the maximum drop
from the hilltop, or the clearance of every segment along a drooping tether.
It also is not the colorbar value: map colors show **terrain elevation minus hub
elevation**, so negative/blue terrain values mean ground below the hub.
Clearance instead uses **tip-plane height minus projected terrain height**.

The tip plane remains **1.3768157 m above the hub tangent plane** (the saved
loaded go-kart tip height plus 0.5 m). Curvature and local terrain differences
then determine the much larger clearances around these selected hills. The
selected circles were rechecked at **144,000 bearings**; the rounded results
agree with the existing catalog. This does not add precision to the roughly
59 m DEM or establish clearance for a finite-sized payload or the full machine.

## Why east and west both had 42

The matching counts are coincidental for the current selected catalog. There
are no directional quotas in the selection algorithm: **39 sites clear only
east, 39 clear only west, and 3 clear both**, totaling 81 distinct launch-capable
sites. Equal totals do not mean the same points work in both directions or that
another selection must produce equal counts.

## Terrain maps for these four only

These are 15 × 15 km plots, with hub point, track inset, tether tip circle and
release marker. No impact points or labels are shown. PNG and SVG are provided.

- **P1 / H0333:** [PNG](maps/P1_H0333_15km.png) · [SVG](maps/P1_H0333_15km.svg)
- **P2 / H4765:** [PNG](maps/P2_H4765_15km.png) · [SVG](maps/P2_H4765_15km.svg)
- **P3 / H6308:** [PNG](maps/P3_H6308_15km.png) · [SVG](maps/P3_H6308_15km.svg)
- **P4 / H6941:** [PNG](maps/P4_H6941_15km.png) · [SVG](maps/P4_H6941_15km.svg)

[Four-map gallery](maps/README.md). Older nine-site maps remain historical assets;
only the four images here were regenerated for this down-selection.

## Reproduction

```bash
MPLCONFIGDIR=/tmp/lunar-sling-mpl-cache OPENBLAS_NUM_THREADS=1 .env/hub/bin/python -m llo_catcher.site_selection.featured_four.select
MPLCONFIGDIR=/tmp/lunar-sling-mpl-cache .env/hub/bin/python -m llo_catcher.site_selection.featured_four.build_maps
```
