# Tether sag, taper and support-height tradeoffs

**Status: initial steady P1 technical note completed.** This sling-design investigation asks how distributed tether weight, rotational tension and taper determine vertical drop—and how that shape fits above real terrain. It applies to the go-kart launcher and other tapered, spooled architectures.

- **[P1 publication note and figures](publication/README.md):** a fixed-speed Kevlar taper sweep from 100 g to terrain contact near 10.57 g, using the full-circle terrain envelope. Includes six panels, individual figures, numerical tables and reproducible source data.
- The stages below describe the broader remaining work, including material sensitivity, support optimization and operational states.

## Physical question

A rotating tether supports both its payload and its own distributed weight. The radial tension needed for rotation and the vertical tension needed to support weight set its slope. Changing the taper changes both distributed mass and tension. A downhill terrain envelope can accommodate a descending tether, potentially reducing the required support height.

Vertical sag is the steady shape in the radial/vertical plane. Tangential lag and release waves belong to the time-dependent dynamics described in [spooled tether in 2D](../spooled_tether_2d/README.md). The initial work here studies steady loaded configurations before adding operational cases.

The terrain input is the [maximum-around-ring profile](../../llo_catcher/site_selection/radial_terrain/README.md). Site selection supplies that reusable boundary; material, taper, stress and support sizing live in this sling-design work item.

## Inputs and dependencies

| Category | Parameters |
|---|---|
| Reference operating point | Payload mass, angular speed, support radius, release radius, useful release speed and payload acceleration |
| Material | Density, allowable working stress, elastic modulus and documented strength/durability assumptions |
| Taper | Cross-section profile A(s), endpoint area, maximum root area and allowed taper ratio |
| Geometry | Arc length, horizontal reach, support elevation, terminal height and terminal slope |
| Terrain and clearance | Tangent-plane terrain envelope, support-base terrain height, payload envelope and required clearance |
| Design outputs | Tether mass, peak stress, root and tip dimensions, vertical drop, required pole lengths and support loads |

Angular speed, release radius, speed and acceleration are linked by v = Ωr and a = Ω²r in the reference steady rotation. Choose an independent set for each sweep. Payload mass and allowable stress constrain the endpoint area. Taper ratio is explicitly **root area / tip area**; the diameter ratio for a circular line is its square root.

Import the published 50-g reference dimensions and existing material assumptions as the baseline, with provenance. The current geometry remains a comparison point while these tradeoffs are explored.

## Stage 1 — Explain and recover the existing sag model

Review [mass_screen.py](../mass_screen.py), [spooling_cycle.py](../spooling_cycle.py), and [cable_shape.py](../cable_shape.py). Document the assumptions behind their tension and vertical-drop estimates, then reproduce the reference values.

For a small-slope radial tether extending from a support radius to tip L, a useful first approximation is:

```
radial tension at r ≈ m_payload Ω² L + integral[r to L] ρ A(s) Ω² s ds
vertical tension at r ≈ m_payload g + integral[r to L] ρ A(s) g ds
dz/dr ≈ − vertical tension / radial tension
```

Here s is approximated by horizontal radius. The refined calculation uses true arc length and the vector gravity field consistently. The equations show how payload weight and distributed tether weight contribute separately. Any chosen terminal trajectory or vertical acceleration changes the endpoint boundary condition and must be specified.

## Stage 2 — Taper families and steady force balance

Compare constant area, a parameterized smooth taper, and a constant-working-stress taper. For each family, solve tension-only force balance in the rotating frame under lunar gravity, including actual cable orientation, changing cross-section and arc-length mass. Add elastic stretch after the inextensible baseline is verified.

Track these outputs together:

- Root/tip area and diameter ratios, material volume, tether-to-payload mass ratio.
- Maximum working stress and its position along the tether.
- Vertical drop and slope as functions of radius.
- Root radial/vertical loads and terminal tension direction.
- Support elevation required to satisfy clearance over every occupied radius.

Use adjustable allowable stress to expose the mass–sag tradeoff before selecting a material operating limit. Compare Kevlar with other material assumptions already present in the repository when their data sources and working-stress conventions are compatible.

## Stage 3 — Couple the shape to terrain and support mass

For a solved drop profile d(r) below a common support datum H and terrain envelope T(r), evaluate:

```
H_required = max over occupied cable radii [T(r) + d(r) + clearance(r)]
```

Convert this datum into pole lengths using terrain at the rover/support bases. Account for changing terminal height and physical cable arc length when varying H. Check the complete load path: opposing payload tension, the upper cross-tie, low cross-tie, poles and central stabilizers retain their separate roles.

Compare flat reference terrain with the selected hill profile, then the other three profiles. Quantify the resulting changes in support height and mass using the existing structural-sizing methods. Report the tradeoff between added tether mass, altered sag, and reduced support mass.

## Stage 4 — Sensitivity and design choices

Sweep allowable stress, taper ratio, endpoint sizing, Ω/release radius, payload loading and clearance margins. Keep release-speed and mass-flow requirements explicit when comparing designs. Produce Pareto curves for imported mass, support height, stress utilization and taper/spool dimensions. Check reel bending constraints against the existing reel assumptions as taper and diameter grow.

Then identify operational states worth carrying into a dynamic model: fully loaded hold, partial payout, payload release, and unloaded retraction. Their changing loads may set a different clearance requirement from the steady release state.

## Validation and deliverables

- Recover the massless-tether/payload limit and existing small-slope reference cases.
- Verify endpoint forces, integrated distributed loads, tension positivity and mesh convergence.
- Check equal-stress taper behavior and distinguish vertical drop from elastic elongation.
- Save steady shape/stress profiles, scalar scenario tables, material assumptions and comparison plots.
- Produce a short physical explanation, a taper/sag figure, and terrain-plus-cable overlays showing the controlling support-height location.

The first P1 steady-shape investigation is available in the publication note above. Support optimization, elastic response and operational dynamics remain follow-on work.
