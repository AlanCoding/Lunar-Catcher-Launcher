# Conveyor-loop lunar sling: concept and work plan

Status: **New concept; planning stubs only.** Recorded 2026-11-04.
[Launcher guide](../README.md) · [Work queue](../../WORK_ITEMS.md)

## Proposal

Replace the outward payload/countermass spools with circulating tether loops.
Each loop has constant cross-section along its own length, an outward-moving
strand, an inward return strand, a drive/brake wheel near its inner end, and an
outer turnaround. Payloads attach near the inner end, travel outward with the
line, and detach at a controlled release phase. Several payloads may be in
transit simultaneously. The empty line returns without retracting the whole arm.
Reusable attachment hardware and its return route remain to be specified.

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

## Stages and deliverables

1. **[Scalar screening, mass flow and payback](01_SCALAR_ANALYSIS.md).** Define free
   and dependent variables; audit the preliminary strength/energy equations;
   estimate loaded-line stresses, total mass, throughput, power and mass-payback
   time. Identify candidates and failure boundaries for simulation.
2. **[2D tether stresses and dynamics](02_PLANAR_DYNAMICS.md).** Model both moving
   strands, discrete payloads and turnaround assemblies. Test steady transport,
   loading, transfer and paired release, with explicit planar limitations.

[Initial SVG concept illustrations](figures/README.md) are available for review.
They describe the mechanism, not calculated geometry. No numerical analysis,
material selection, optimization or simulation has been performed yet. The older spool-based
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
and dynamic loads. Neither the material values nor the claimed two-stage
optimum has been independently checked here. Source material properties before
using them in results. The handoff's concept-post and four illustration ideas
are retained as later communication options; this task creates research plans.
