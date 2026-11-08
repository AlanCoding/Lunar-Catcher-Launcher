# Conveyor-loop lunar sling: concept and work plan

Status: **Concept and illustrations published; first steady conveyor results available.**
Publication recorded 2026-11-06.

[Conveyor Belt Lunar Mass Sling](https://alanse.medium.com/conveyor-belt-lunar-mass-sling-7abc7bac7a05) ·
[Lunar Mass Launchers collection](https://alanse.medium.com/list/lunar-mass-launchers-9a765f4e596a)

This folder contains the concept notes and [four supporting illustrations](figures/README.md)
for the published post. Start with the [steady shape, strength and grip results](steady/README.md).
The scalar and 2D dynamics documents describe the broader unfinished program. The original handoff is preserved as historical
context; subsequent clarifications are recorded here and in the figure guide.
[Launcher guide](../README.md) · [Work queue](../../WORK_ITEMS.md)

The [matched-throughput comparison with tapered spooling](../architecture_comparison/README.md)
now uses these steady results to compare tether material and peak stress on equal terms.

## Proposal

Replace the outward payload/countermass spools with circulating tether loops.
Each loop has constant cross-section along its own length, an outward-moving
strand, an inward return strand, a drive/brake wheel near its inner end, and a
free outer turn (no tip pulley in the current illustration). Payloads attach near the inner end, travel outward with the
line, and detach at a controlled release phase. Several payloads may be in
transit simultaneously. The line returns with its small reusable attachment devices, which receive new
payloads on their next loading pass. It does not retract the whole arm. Both
conveyors circulate in the same rotational sense as the hub in this iteration.
The free outer-turn shape and attachment passage need dynamic/mechanical checks.

Two motions coexist: the entire sling rotates about the lunar hub at angular
speed **Ω**, while line circulates through its wheels at linear feed speed **u**.
The intended regime is u much smaller than ΩR at release radius R. These have
different units; wheel spin rates also depend on wheel radii. Feeding outward
increases payload angular momentum and requires main-drive torque. The outward
motion can drive a regenerative feed brake while the main drive consumes power.

Retain the original force-path distinction: opposing radial payload loads close
through the tensioned structure; ground traction supplies tangential drive and
any explicitly assigned rover turning load. Feeding wheels are on the rotating
structure, not assumed stationary on the lunar surface. “Near the hub” does not
yet fix their position or the loading interface. Static cross-ties are not conveyors.

## Two architectures to investigate

| Concept | Arrangement | Main unresolved issues |
| --- | --- | --- |
| **Zyling: single loop per outward arm** | One uniform loop from the rotating feed station to the release turnaround; the name combines Zylon and sling, but material choice is open. | Uniform-line self-stress, payload inventory, turnaround mass, bending, routing and coupled strand dynamics. |
| **Two-loop Kevlar variant** | A thicker inner loop and thinner outer loop meet at an intermediate wheel/transfer assembly: one discrete step in cross-section. | Intermediate support and stability, transfer of payload load, matched feed velocities, wheel mass and bending. Kevlar feasibility is unproven. |

“Two-loop” counts successive stages on an arm, not simply the two opposing arms.
A mirrored two-stage machine would have four circulating loops before any
additional loading mechanism. Neither variant assumes a rigid arm supporting
the distant turnaround or intermediate assembly. Their masses and required
force balance must be included. Coordinate useful-payload and countermass
release; a permanently retained counterweight does not balance a released load.
Simultaneous release alone does not remove transient stress waves.

The handoff anticipates opposite lateral deflection of outgoing and returning
strands from Coriolis effects. Treat their exact shapes and stability as outputs,
not prescribed geometry. Continuous feeding also does not guarantee continuous
capture: launch phase and catcher windows can limit actual delivery rate.

## Wheel grip is a key design criterion

The line must transmit regenerative braking loads without slipping on its
wheel. Both stages will report grip limits alongside breaking limits, and
consider increased wrap or a separate tension-holding mechanism. Friction,
contact pressure, bending, wear, attachment passage and transient slip remain
to be quantified; regenerative energy is recovered from the coupled main-drive
work, not created independently by the feed mechanism.

## Accepted prerequisite and first conveyor results

The [point-mass payout experiment](../payout_control/README.md) now precedes
conveyor simulation. It isolates rotating-attachment geometry, payout controls,
slack and torque using an ideal massless cable, with four initial strategy GIFs.
The point-mass study is accepted; optimal control is deferred. The
[first conveyor calculation](steady/README.md) now solves a free-turn moving
loop, with adjustable feed and payload loading, stress and grip estimates.
This does not resume the earlier full-machine spool operations plan.

## Simulation implementation outline

The [one-arm simulation stack](03_SIMULATION_STACK.md) proposes Python/NumPy/SciPy
and stress-colored 2D plots, with adjustable machine rotation, conveyor speed
and outgoing payload density. Model both strands on one side and assume a
symmetric counterweight arm. Attempt a moving-line steady solution if useful,
otherwise proceed directly to dynamics. A [steady solver](steady/model.py) is now
implemented; time dynamics and the shared-pulley two-stage model remain future work.

## Stages and deliverables

1. **[Scalar screening, mass flow and payback](01_SCALAR_ANALYSIS.md).** Define free
   and dependent variables; audit the preliminary strength/energy equations;
   estimate loaded-line stresses, total mass, throughput, power and mass-payback
   time. Identify candidates and failure boundaries for simulation.
2. **[2D tether stresses and dynamics](02_PLANAR_DYNAMICS.md).** Model both moving
   strands, discrete payloads and turnaround assemblies. Test steady transport,
   loading, transfer and paired release, with explicit planar limitations.

[SVG concept illustrations](figures/README.md) are available for review, including
a separate [Coriolis / tangential-force diagram](figures/README.md#4-coriolis--tangential-force-picture).
They describe the mechanism, not calculated geometry. New calculated geometry
and material screening are in the [steady report](steady/README.md); no complete
machine optimization or dynamic-stability demonstration has been performed. The older spool-based
[operations](../work_items/01_OPERATIONS_SIMULATION.md) and
[3D dynamics](../work_items/02_DYNAMIC_TETHERS.md) plans are **on hold**, not
prerequisites. The [published 50-g spool design](../publication/README.md) stays
as the comparison baseline; its optimum and hardware masses do not transfer
automatically to this architecture.

## Handoff and provisional numbers

[Original handoff](HANDOFF.md) is preserved verbatim as supplied context, not a
validated report or an instruction to update the published post immediately.
It proposes these **self-loading-only estimates, to reproduce in Stage 1**:

- At 1.67 km/s, a straight uniform radial strand has approximately
  σ/ρ = v²/2 = **1.394 MJ/kg**, neglecting inner radius and end load.
- A two-stage example claims **0.761 MJ/kg** peak working specific strength
  at inner/outer area ratio **6:1** and intermediate radius **0.674R**.
- Its illustrative Kevlar allowance is **1.04 MJ/kg** at safety factor two.

These exclude payloads, wheel/attachment masses, bending, environmental losses
and dynamic loads. The [steady screen](steady/README.md) now sources Zylon HM and Kevlar 49 fiber
properties. The claimed two-stage optimum has not yet been independently checked. The handoff's concept-post and four illustration ideas
are retained as later communication options; the concept and four illustrations are now published; the first single-loop numerical results are now separate from that publication.

## Revision: reusable devices and gentle release

The [revised concept figures](figures/README.md) remove tip pulleys, retain the
shared intermediate stage pulley, and show returning reusable attachment devices.
Release should progressively unload the line through a controlled extension
before detachment. Approximately 10 m of travel is a suggested starting input,
not a validated requirement. Include device mass, stroke reset, dissipation or
recovery, and release-vector/timing changes in the scalar and dynamic studies.
See the figure guide for the motivating Rüdiger simulation reference.

## Shared intermediate pulley: selected concept

The two-stage design uses **one shared intermediate pulley/common shaft**, with
both loop contact surfaces locked to the same angular velocity. This is the
mechanical torque/power connection between the outer and inner loops, not two
independent wheels on a bracket. Use matched effective groove radii for matched
feed speeds in the initial no-slip model. Calculate the torque balance and
traction capacity at both contacts; do not assume shaft coupling guarantees grip.
Detailed out-of-plane shaft/groove bending is outside the initial 2D scope.
The payload handoff still needs its own load-transfer mechanism.
