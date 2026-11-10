# Lunar Slider Straw

**Concept record: November 8, 2026.** Also described as the *Lunar Sling Super
Tube*. This is a new architecture investigation, not a demonstrated machine.

Combine independently spooled, tapered Kevlar tethers with a shared rotating,
flexible tensile guide—a “straw made of tether.” About **20 tether-and-payload
sets** operate at staggered phases. Outgoing loaded assemblies and returning
empty tethers slide along neighboring paths, potentially transferring opposing
transverse loads through normal contact and smoothing the hub/spool power demand.
The guide may itself be tapered; it is not assumed to support itself by bending
stiffness like a rigid tube.

The hypothesis is that opposite radial motions generate opposite Coriolis terms
in the rotating frame. Appropriate routing might let those streams push together
and exchange transverse force and angular momentum, capturing part of the
[double-conveyor](../conveyor_loop/README.md) benefit while retaining
[tapered-spool material efficiency](../architecture_comparison/README.md).
Cancellation is a question to calculate, not an assumption: outgoing payloads,
returning tether, taper and deployment phase generally produce unequal loads.
A tensile guide can change direction under tension, but sustained normal contact
still needs suitable routing, constraint geometry and a path for residual loads.

The [current Kevlar shape study](../spooled_tether_2d/README.md) has a lower-stress
example near **7.31:1 tether/payload mass**. This is the motivating reference,
not a universal material requirement or a new mass estimate for the straw.
The [staged spool bank](../staged_spool_bank/README.md) supplies related phased
power accounting, but a group of 20 sets and its release schedule remain inputs.

## Why the speed distinction matters

The tip's roughly 1,600 m/s inertial speed is not the relative sliding speed of
co-rotating contact surfaces. Radial payout might be about 5 m/s or less.
Frictional heating depends on **normal force times friction coefficient times
relative slip speed**. A stream moving outward at 5 m/s against one returning
at 5 m/s has about **10 m/s** relative slip, while each slips about 5 m/s against
a guide fixed in the rotating frame. Which surfaces actually contact must be
specified before claiming small losses. The required transverse loads can still
be large even at low slip speed.

## Planned stages

- **[Scalar loads, power and mass](PLAN.md#1-scalar-load-and-power-model):** derive
  local transverse loads, contact force, unmatched load and friction/heating for
  stated mass flows. Compare at equal delivered mass flow with existing designs.
- **[Guide/contact sizing](PLAN.md#2-guide-and-contact-model):** bound tensile-guide
  mass, normal pressures, wear, heat rejection and handling of taper/splices.
- **[2D dynamics](PLAN.md#3-time-domain-dynamics):** couple outgoing/incoming elastic
  tethers and the guide, retaining inertia, tension-only behavior and intermittent
  contact. Test stability, release waves and synchronization.

No simulation, material qualification or mass-payback result exists for this
concept yet. Its potential benefits—tapered mass efficiency, transverse force
coupling and steady operation—are the hypotheses these stages will test.
