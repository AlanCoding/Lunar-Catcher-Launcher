# Lunar Slider Straw: work plan

[Concept](README.md) · [Shared spooled-tether dynamics](../spooled_tether_2d/README.md)

## 1. Scalar load and power model

Specify the architecture before solving: which stream contacts the guide, which
contacts the other stream, contact-side geometry, and where residual transverse
loads terminate. Record whether “20 sets” counts useful payloads only or balanced
payload/countermass pairs. Choose fixed delivered mass flow, radius, RPM, taper,
payload cadence, retained end-device mass and extension/retraction schedules.
Keep full-extension dwell and catch phasing separate from power smoothing.

Compute distributed mass and transverse acceleration along each path. In a
co-rotating radial approximation the Coriolis term has magnitude `2 Ω v_radial`;
the force density therefore depends on local mass density as well as velocity.
Match the signed load distributions locally, not merely total tonnes per cycle.
Include payload point loads and the guide's own centrifugal loading. Integrate
unmatched loads and torques and identify their mechanical reaction paths.

For declared contacts, calculate `P_friction = integral(mu * N_per_length *
v_relative) ds`, slip criteria and drive/braking power. Sweep friction,
phase spacing, mass-flow mismatch and spool rates; do not invent a qualified
Kevlar friction/wear coefficient. Report total energy per delivered kilogram,
peak/mean heat, hub/spool power and required guide mass bounds. Use both
ideal-recovery and stated-efficiency cases and close the energy balance so
internal force exchange is not counted as free energy.

## 2. Guide and contact model

Determine whether a purely tensile guide can support the proposed contact
geometry. Bound taper, prestress, anchors, local normal pressure, friction,
abrasion, fatigue, bending radii, handling of changing tether thickness and
attachments, and thermal paths in vacuum. Distinguish normal contact from
adhesion: contact may separate, and a rope cannot push. Estimate interface and
radiator mass as well as guide fiber mass. Compare to the same-throughput tapered
spool and conveyor cases before calculating a system payback.

## 3. Time-domain dynamics

Extend the existing 2D distributed-inertia spool model with two moving material
streams and a massive tensile guide. Start with a small contact patch, checking
momentum/energy exchange and frictional dissipation, before a full-length system.
Then simulate approximately 20 phased sets with transient mass-flow mismatch,
payload release, startup/shutdown and a missed/late spool command. Measure
stress histories, angular envelopes, contact loss, local load spikes, dissipated
energy and guide motion. Assess convergence and sensitivity to damping and
contact compliance. Optimal control and 3D packaging follow only after this
basic feasibility investigation.
