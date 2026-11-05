# Local corridor survey: definitions and limits

This survey holds release height at **10 m above local terrain** and refines
longitude near eight previously successful samples. It replaces further work
on the abandoned global height-percentage survey. Its parent results and
full-equator graph are retained as context.

The inherited point-release model has one useful payload exactly on the equator,
prograde tangent launch at periapsis, a circular 25 km equatorial catcher at
apoapsis, and first terrain impact or **1.5 payload periods** as the cutoff.
Only the useful payload is followed. See the [parent method](../METHOD.md).

## Search domain

Search one degree west and east of each original seed: 144, 220, 264, 267,
283, 293, 294 and 295 degrees east. Merge overlapping windows. The resulting
six windows are **143–145, 219–221, 263–265, 266–268, 282–284 and 292–296° E**.
They cover 14 degrees, about 424.53 km of reference equatorial arc.

All window edges are checked and fail outbound clearance. Thus no reported
continuous interval is clipped at a search-window edge. Other disconnected
viable regions elsewhere on the equator may exist; this is not a complete
Moon-wide catalog. Nearby intervals not containing an original seed are also
retained, with the seed-connected subset reported separately.

## Criteria and lengths

- **Outbound-clear:** positive terrain clearance all the way to intended catch.
- **Both criteria:** outbound-clear, followed by a terrain impact after missed
  capture and before the 1.5-period cutoff.
- **Not arrested:** outbound-clear but no such contact by that cutoff. It does
  not mean permanent orbital survival.

First sample longitude at 512 points per degree, then 1,024, 2,048 and 4,096,
reusing prior samples. At each longitude the trajectory/DEM intersection is
resolved using every relevant terrain interpolation cell and its interior
clearance minimum; it is not sampled at the launch-longitude spacing.

At each detected transition, refine the longitude boundary by a bracketed root
solve on minimum clearance. For the combined criterion the signed score is
min(outbound clearance, minus minimum return clearance) once outbound is clear.
This separates departure boundaries from failed-capture-return boundaries.

The finest launch-longitude spacing is about **7.4 m**. That oversamples the
roughly 59 m DEM grid to locate transitions in the interpolated surface; it
adds no new terrain resolution. Refinement convergence is reported, but it
cannot prove that every still-narrower island or gap has been found.

Length is **horizontal reference-sphere arc length**:

```text
length_km = (end_longitude - start_longitude) * pi/180 * 1737.4
```

Intervals are summed without overlaps. This is not the distance measured over
the bumpy ground, land area, or a demonstrated construction footprint for the
full sling. Boundary equality is grazing; the mathematical interval endpoints
are not engineering clearance margins. Very narrow intervals may be inadequate
for a real installation even if their idealized release points qualify.

## 144° diagnostic

The full-equator elevation chart did not include the payload's rising orbital
path. The new diagnostic overlays both in the same reference datum, using
body-fixed longitude for each. The payload starts about 4.295 km above the
reference sphere, because the launch ground itself is elevated. It gains
altitude while traversing the long gap before the next major mountain range.
Independent Cartesian integration checks the clearance at a prominent later
ridge. This checks the explanation without changing the release model.

## Reproduction

From the repository root with the existing terrain cache:

```bash
MPLCONFIGDIR=/tmp/lunar-sling-mpl-cache .env/hub/bin/python -m llo_catcher.analysis.single_equatorial_release.local_corridors.survey
.env/hub/bin/python -m llo_catcher.analysis.single_equatorial_release.local_corridors.validate
```

These scripts write only this subfolder. The old elevation/height-scan results,
eight original classifications and accepted spherical optimum are preserved.
