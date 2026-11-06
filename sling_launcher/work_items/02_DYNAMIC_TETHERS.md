# Stage 2: 3D segmented tether dynamics in the operations simulator

Status: **On hold at the user's request, 2026-11-04; not started.**
The new [conveyor-loop work plan](../conveyor_loop/README.md) takes priority.
This preserved plan applies to the spool-based reference. Originally captured 2026-11-03.
Dependency: [time-stepped operations simulator](01_OPERATIONS_SIMULATION.md).
[Work-item index](../../WORK_ITEMS.md).

## Objective

Replace prescribed/quasi-static outward tether shapes with a three-dimensional
model of incremental cable segments, retaining the same operation sequence,
actuator controls, inventory, hardware limits and energy accounting. Resolve
transient droop, lag, tension and motion during spinup, payout, release,
retraction and spindown. This is a discrete-segment model, not a requirement
for a continuum finite-element analysis.

## Required model design

- Read taper and linear density along the original material coordinate. Assign
  segment masses from integrals over that coordinate, so total cable mass and
  changing deployed/wound mass match the frozen design.
- Evolve 3D node positions and velocities. Choose and document either
  tension-only elastic segments or an inextensible constraint formulation;
  include a declared treatment of slack. Do not let rope carry compression.
- Couple apex motion to the A-frame rotation and payload motion to the end node.
  Feed cable forces and torques back into the Stage 1 wheel/reel equations rather
  than prescribing both an unresponsive drive trajectory and its required torque.
- Model payout/retraction as material transfer through a moving boundary. Track
  spool storage, cable mass, momentum and energy consistently when segments enter
  or leave the deployed domain; prevent numerical creation/loss of these quantities.
- Preserve the existing static cross-tie force paths. Declare whether upper/low
  ties and pivot stays initially remain ideal constraints or are discretized too.
  State the residual reactions and the limits of the chosen support treatment.
- Use compatible inertial or rotating-frame equations with lunar gravity and
  orientation. Include terrain-contact detection and minimum cable clearance.
- Handle payload release as a boundary/mass event; account for recoil and the
  transition to the unloaded tether. Treat rock release separately where needed.
- Declare elasticity, damping and contact assumptions. Do not choose damping just
  to hide oscillations. Track dissipated energy separately from numerical error.

## Progression and validation

1. Begin with a fixed-length, steady-spin, tensioned cable and compare the solved
   shape, root tension and distributed mass with the existing quasi-static model.
2. Add prescribed boundary motion for verification, then coupled actuator motion,
   rest-to-spin transitions and controlled slowdown with slack/clearance checks.
3. Add payout and retraction, checking material transport at the reel boundary
   and continuity of forces/energy across segment insertion and removal.
4. Add release transients and the full repeated-launch/refill sequence from
   Stage 1. Compare peak loads and feasible controls with the earlier approximation.
5. Refine segment count and time step independently; show convergence and energy/
   momentum behavior in appropriate isolated test cases. Distinguish real wave
   or oscillation behavior from numerical instability.

## Deliverables and completion criteria

- A reusable tether-dynamics component plugged into the Stage 1 simulator, with
  documented units, frame conventions, material coordinates and boundary events.
- 3D renderable position histories and animations through the critical operating
  phases, plus tension/stress, strain if modeled, clearance and actuator-load plots.
- Checks that integrated segment mass reproduces the tapered cable and that
  spooling/release transfers preserve the declared mass and energy accounting.
- Mesh/time-step convergence results, static-equilibrium comparisons, and a
  quantitative comparison with the Stage 1 power/torque/clearance estimates.
- A list of operating constraints that change when dynamics are included and any
  reference-design violations. Keep resulting redesign proposals separate from
  the published 50-g snapshot.

This stage tests dynamic plausibility; creating this work item does not establish
cable fatigue life, certified reel construction or successful orbital capture.
