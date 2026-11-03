# Reel bend ratio, dimensions and scope

The reference scenarios assume **D/d = 40:1**, where D is the bare reel/core
bending diameter and d is the largest outward-rope diameter, including the
assumed 65% fiber fill. This is a fixed input, not an optimized result. The
lighter and heavier sensitivity sets use **20:1 and 50:1**, respectively.
As the rope tapers toward the payload, the same core gives a larger D/d for
those thinner sections. The full storage-envelope diameter is not D in this rule.

Each detailed scenario JSON records `assumptions.bend_D_over_d`,
`reel.rope_outer_diameter_m`, `reel.core_radius_m`, `reel.outer_radius_m`, and
`reel.width_m`. Thus the ratio can also be checked as
`2 * core_radius_m / rope_outer_diameter_m`. These dimensions are derived
from the existing [scenario data](../results/split_tie/all_estimates.json);
no numerical estimates have been changed for this note.

## Reference scenario dimensions: 50 mph, one pass

| Payload g | Bend ratio D/d | Rope diameter mm | Core diameter m | Full storage diameter m | Width m | Reel-envelope check |
| ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 25 | 40:1 | 61.3 | 2.45 | 4.44 | 2.45 | Pass |
| 30 | 40:1 | 67.1 | 2.69 | 4.44 | 2.69 | Pass |
| 35 | 40:1 | 72.5 | 2.90 | 4.47 | 2.90 | Pass |
| 40 | 40:1 | 77.5 | 3.10 | 4.52 | 3.10 | Pass |
| 45 | 40:1 | 82.2 | 3.29 | 4.58 | 3.29 | Pass |
| 50 | 40:1 | 86.7 | 3.47 | 4.66 | 3.47 | Pass |
| 55 | 40:1 | 90.9 | 3.64 | 4.74 | 3.64 | Pass |
| 60 | 40:1 | 95.0 | 3.80 | 4.82 | 3.80 | Pass |
| 65 | 40:1 | 98.8 | 3.95 | 4.91 | 3.95 | Pass |
| 70 | 40:1 | 102.6 | 4.10 | 5.00 | 4.10 | Pass |
| 75 | 40:1 | 106.2 | 4.25 | 5.09 | 4.25 | Pass |
| 80 | 40:1 | 109.6 | 4.39 | 5.18 | 4.39 | Pass |
| 90 | 40:1 | 116.3 | 4.65 | 5.37 | 4.65 | Pass |
| 100 | 40:1 | 122.6 | 4.90 | 5.56 | 4.90 | Pass |
| 125 | 40:1 | 137.0 | 5.48 | 6.01 | 5.48 | Pass |
| 150 | 40:1 | 150.1 | 6.01 | 6.45 | 6.01 | Pass |
| 220 | 40:1 | 181.8 | 7.27 | 7.58 | 7.27 | Pass |
| 300 | 40:1 | 212.3 | 8.49 | 8.72 | 8.49 | Pass |

Only converged cases are listed. Nonconverged iterations are not usable designs.
The existing reel-envelope check only asks whether the full storage radius is
smaller than the track radius, screening overlap between opposing reels. It is
not a detailed layout, manufacturing or cable-handling qualification.

## What the assumption does—and does not—establish

At **50 g**, the maximum rope diameter is **86.7 mm**, the core diameter is
**3.47 m**, the full storage-envelope diameter is **4.66 m**, and the width is
**3.47 m**. This case passes the existing reel-envelope check. There is no
identified geometric contradiction in those spool dimensions, but this does
**not** establish that an 86.7 mm tapered Kevlar rope will survive the required
loaded bending cycles, or that a full-tension winding drum is adequately sized.

A constant D/d is not a guarantee of physical scalability. At extreme sizes,
rope construction, transverse compression, winding pressure, bend fatigue,
traction, guides, bearings and manufacturable machinery can invalidate the
simple scaling even if the arithmetic and envelope check pass. The model
contains no validated size-dependent cutoff for those effects. Treat such
outputs as conditional extrapolations, not buildable designs. The 50-g result
also remains conditional on this rope/reel engineering; it is not exempt merely
because it is the sampled mass minimum.

The [source register](../results/hardware_mass/SOURCES.md#reels-and-heat-rejection)
explains the 40:1 selection and 20/50 sensitivity. Those sources motivate the
assumption; they do not certify this rope, loading history or lunar application.

## Two outward reels; fixed cross-track connections

The intended illustration now contains **two reels total**, one at each apex
for its outward payload or countermass tether. The upper cross-track tether
terminates statically at the two pole tops. It has no spool or reel drive;
neither do the low cross-track connections. The extra pair of visible drums
has been removed to make this topology clear.

The **numerical allowance is deliberately unchanged**: it was calculated as
one tension-bearing capstan plus low-tension storage assembly per outward
line, with one major drive allowance per line. That is the provenance of the
235.30-tonne total for both reel systems, not a claim that the newly simplified
one-drum illustration is a fully engineered replacement. Combining storage
and full-tension handling into a single physical drum would require checking
winding pressure and resizing its structure; it cannot be validated by deleting
objects from Blender. No new mass saving is claimed.

At 50 g, each assembly retains 23.18 t of motor, 2.07 t of inverter,
76.89 t of gearing and 15.50 t of mechanical allowance. The mechanical estimate
uses a torsion-sized shaft, a rim-force estimate, a 6 mm storage shell and a
30% support allowance. Bearings, guides, level-winding and auxiliary storage
drives are not separately resolved. Payload-loading machinery is not separately
quantified. The motor rating combines peak torque and peak speed as an envelope,
which need not occur simultaneously. These are preliminary sizing allowances,
not a complete production-machine bill of materials.

See also [why the mass minimum exists](WHY_THE_MASS_MINIMUM_EXISTS.md) and
[the illustrated 50-g dimensions](DESIGN_AT_A_GLANCE.md).
