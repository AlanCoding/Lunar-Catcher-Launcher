# Planned figure: maximum terrain height versus distance from the hub

**Status: terrain figure completed.** See the [results and publication graph](../radial_terrain/README.md). The design-dependent sag, taper and support-height calculations are planned separately under [sling design](../../../sling_launcher/sag_taper_trade/README.md). The original plan below records the motivation and engineering handoff.

## Question and plotted quantity

At each radius from a candidate hub, what is the highest terrain that a rotating tether could pass over?

The main plot will use:

- **Horizontal axis:** horizontal radius from the hub, in kilometres; initially 0–6.5 km to include the four existing tip radii and some context.
- **Vertical axis:** maximum terrain height around the entire ring, in metres relative to the hub tangent plane.
- A horizontal zero line marking the hub tangent plane.
- Markers for the 76.79 m rover track and the selected site’s actual release radius.

Each value is the maximum around the ring **at that radius**. This preserves the radial shape of the hill. A cumulative maximum over the entire interior disk can be stored separately for engineering checks.

The tangent-plane reference includes lunar curvature. For reference radius R, terrain elevation h, hub elevation h₀, and central angular distance θ:

```
r = (R + h) sin θ
z = (R + h) cos θ − (R + h₀)
T(r) = maximum z around the ring
```

Use the same terrain source and reference sphere as the existing analyses. Solve the ring geometry consistently with horizontal radius. The difference in radial elevations, h − h₀, can be retained as an auxiliary series to explain the curvature correction.

## Choosing the featured hill

**P1 is the provisional illustration candidate.** Its existing minimum tip-circle clearance is 423.6 m, compared with roughly 264–275 m for the others. That result concerns one radius; the terrain closer to the hub could still determine the support height.

Before selecting the final hill:

1. Compute the same radial terrain envelope for all four adjusted hubs.
2. Compare the profiles over the radii occupied by the reference sling.
3. Where the saved go-kart tether geometry supports a consistent comparison, add its vertical drop profile and evaluate the required support height for each hill under the same clearance convention.
4. Use the lowest resulting support-height requirement to select the featured profile. Retain all four numerical profiles and a compact comparison as supporting data.

“Best slope” thus means favorable terrain over the full occupied radius, including any intermediate high points. Maximum rim clearance alone serves as a provisional indicator.

## How this becomes a tower-height requirement

The terrain envelope supplies the lower boundary for the tether. If the cable centerline lies a distance d(r) below an adjustable support datum H, then a simplified vertical-clearance condition is:

```
H ≥ maximum over occupied radii [T(r) + d(r) + clearance margin(r)]
```

Apply this only over the cable’s actual occupied radii, using the saved design geometry. The terrain curve and tether drop must share the hub tangent-plane reference. Account for the ground elevation at the rover/pole bases when converting the common support datum into actual pole lengths. The go-kart support points lie on the track, displaced from the hub center.

The existing design’s endpoint height, sag profile and clearance convention should be carried forward explicitly. Payload size and terrain uncertainty enter the chosen clearance margin. If a different sling geometry changes d(r), the same terrain envelope can be reused.

The first publication figure can show the terrain envelope by itself. A second panel or supporting overlay can show how adding tether sag and clearance sets the support height, once those inputs have been reconciled.

## Sampling and checks

- Use the existing native-resolution SLDEM2015 cache and bilinear interpolation.
- Start with radial spacing around 25–30 m and enough angular samples that ring-point separation is below the ~59 m DEM spacing; refine near controlling peaks.
- Explicitly include the track and actual tip radii in the sampled array.
- Verify the r = 0 reference, spherical-curvature sign, and consistency with the previously calculated tip-circle clearance.
- Repeat with finer radial/angular spacing around the controlling maxima. Report numerical sensitivity separately from DEM uncertainty.
- Keep the controlling azimuth at each radius in the data so a high point can be located on the terrain map.

## Deliverables when this work begins

- Publication PNG and SVG of the selected hill’s radial terrain envelope.
- CSV of radius, maximum tangent-plane terrain height, controlling azimuth, and optional radial-elevation difference.
- Saved profiles and selection metrics for all four hubs.
- A short method paragraph and design-input interpretation linked from the publication checklist.

The terrain-envelope result completes the publication figure. The support-height and taper tradeoff continues as a separate sling-design work item.
