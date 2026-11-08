# Stage 2: 2D moving-loop stress and dynamics

**Resumed after acceptance of the [point-mass prerequisite](../payout_control/README.md).**
The [first steady results](steady/README.md) are available; time-domain elasticity,
discrete payload/release dynamics and contact/slip simulation remain future work.

Status: **Single-loop steady solver implemented; dynamic model outlined.**
See the [one-arm stack and output plan](03_SIMULATION_STACK.md). A steady solve
is optional; direct dynamics is allowed after specifying the model inputs.
[Concept](README.md) · [Stage 1 inputs](01_SCALAR_ANALYSIS.md)

## Objective and dimensional scope

Test the moving-loop geometry and stresses using discrete cable segments in the
**plane of sling rotation**. Resolve radial transport and tangential deflection,
including the outgoing and returning strands. This is a new conveyor model,
separate from the paused spool-based 3D plan.

Declare an inertial or rotating frame and apply its equations consistently.
A horizontal planar model cannot validate vertical lunar-gravity droop, ground
clearance or out-of-plane stability. Track those as separate static checks or
explicitly excluded questions. Do not project full lunar gravity into the plane
and imply that vertical support has been solved.

## Implementation stages

1. **Uniform unloaded loop:** closed material path, wheel-free outer turn,
   driven inner wheel, tension-only cable law and resolved curved wheel paths.
   Specify wheel constraints, traction/slip assumption, bending idealization,
   elasticity and damping. Start with steady Ω and u to verify force balances.
2. **Loaded single loop:** attach discrete payloads/fixtures, transport them,
   release at defined phase, and return reusable fixtures. Resolve differing
   outgoing/returning tensions and deflections. Separate prescribed-drive tests
   from actuator-limited runs with feedback to main-drive torque and feed brake.
3. **Two-stage variant:** add the intermediate assembly as a moving mass, not a
   pinned radial point in the stability test. Model each loop separately and
   transfer payload support over a finite interval. Matched feed speed does not
   by itself demonstrate a smooth force transfer. Test position stability and
   tension continuity under repeated transfers.
4. **Events on the symmetric one-arm model:** initially assume the opposite arm
   is mirrored and coordinate payload/countermass release and
   examine loading pulses, feed changes and
   controlled slowdown. Preserve the static cross-tie force paths. A symmetric
   one-arm test cannot establish balance after an asymmetric event; explicit
   two-arm timing/load mismatches are a deferred extension.

Advect actual material around the closed path or use a demonstrably conservative
moving-mesh equivalent. Prevent artificial creation of cable mass, momentum or
energy at wheels, transfer stations and segment remeshing. Assign material mass
from each loop's constant area; discontinuity between stages belongs to two
separate loops, not a taper circulating through one wheel.

## Slippage model

No-slip wheel contact is an initial comparison case, not the default feasibility
conclusion. Compare demanded tension difference/brake torque with finite contact
traction; model onset of sliding and relative line/rim speed when the limit is
exceeded. Track accumulated slip distance, frictional heat, lost recovery and
payload timing errors. Examine loading, handoff and release transients as well
as steady feed. Treat friction coefficients as uncertain inputs until supported
by appropriate material/contact data. Compare added wraps or a separate traction
mechanism with their mass, routing and attachment-passage constraints.

## Outputs and checks

- 2D animations and strand trajectories; tension/stress histories, peak locations,
  slack events, wheel reactions, intermediate displacement and payload paths.
- Grip margin, slip onset, relative slip speed/distance and contact heating,
  alongside breaking, bending, attachment and slack limits.
- Drive/brake torque and power, energy recovery, losses and energy balance;
  comparison with Stage 1 mass flow and ideal energy relations.
- Sensitivity to feed speed, inventory, stage ratio, assembly mass and controller
  limits. Distinguish absence of observed instability from proven stability.
- Segment/time-step convergence and limiting cases: stationary feed, unloaded
  steady rotation, prescribed motion and isolated conservation tests. Include
  momentum flux and release/attachment bookkeeping in open-system checks.
- A result summary identifying feasible simulated regimes, broken scalar
  assumptions and the unresolved 3D/clearance and mechanical-transfer questions.

Begin with numerical trajectories and scientific plots; detailed Blender assets
or a new publication draft are later tasks. No 3D simulator is required to finish
this stage, and a successful planar run is not full launcher validation.

## Updated concept inputs (2026-11-05)

Use reusable attachments returning on the inward strand and loaded again near
the feed wheel. Both conveyors circulate in the hub's rotational sense. The
current concept has a **wheel-free outer turn**, while the two-stage shared intermediate
pulley remains. Revise the earlier turnaround-mass assumptions accordingly;
check whether line curvature, transport and tension permit that free turn.
Do not silently reintroduce a tip pulley to make the model work.

Add a controlled unloading stroke between attachment and payload before release,
with approximately 10 m as an initial sensitivity input. Determine required
travel and time, force/acceleration ramp, device energy/mass, reset cycle and
release-state changes. Compare instantaneous release against progressive
unloading and track waves after reflection and repeated launches. A smooth
command or simultaneous paired release alone does not establish safe stresses.
The [illustration notes](figures/README.md) link the motivating external simulation;
its results do not size this mechanism.

## Shared intermediate pulley: selected concept

The two-stage design uses **one shared intermediate pulley/common shaft**, with
both loop contact surfaces locked to the same angular velocity. This is the
mechanical torque/power connection between the outer and inner loops, not two
independent wheels on a bracket. Use matched effective groove radii for matched
feed speeds in the initial no-slip model. Calculate the torque balance and
traction capacity at both contacts; do not assume shaft coupling guarantees grip.
Detailed out-of-plane shaft/groove bending is outside the initial 2D scope.
The payload handoff still needs its own load-transfer mechanism.
