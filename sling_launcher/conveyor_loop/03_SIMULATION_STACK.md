# One-arm conveyor simulation: stack and first implementation plan

**Resumed after acceptance of the [point-mass prerequisite](../payout_control/README.md).**
The [first steady results](steady/README.md) are available; time-domain elasticity,
discrete payload/release dynamics and contact/slip simulation remain future work.

Outlined 2026-11-07; **steady boundary-value solver implemented separately**.
[Concept](README.md) · [Scalar screen](01_SCALAR_ANALYSIS.md) · [2D dynamics scope](02_PLANAR_DYNAMICS.md)

## What the first simulator should answer

For adjustable machine rotation, conveyor feed and outgoing payload density,
what shape does the loop take, what tensile stress occurs along it, and where
is the available strength exceeded? Produce a 2D view colored by stress margin,
plus stress along the cable and its evolution over time. Keep pulley slip as a
separate failure criterion.

**Simulate one entire outward arm**, including both moving strands, the feed
pulley, reusable attachments and outgoing payloads. Assume the opposite arm is
an exactly mirrored counterweight arm with synchronized loading and release.
This eliminates the need to simulate a second arm initially; it does not remove
the return strand from the first arm. Prescribe the hub motion and record its
required torque/reactions. Doubling symmetric arm contributions estimates both
arms' demand; hub/rover/support mass and losses must be accounted separately.
This boundary cannot diagnose asymmetric hub or frame motion.

Start with a single uniform loop, then add the two-stage variant with **one
shared intermediate pulley**, a common shaft and finite inertia. The current
outer end is a **free turn with no tip pulley**. Do not fix it to a distant
anchor or enforce the illustrated oval. Failure to find a sustainable free turn
is a model result, not justification for adding an unrequested support.

## Proposed stack

Use the existing `.env/hub` Python environment. Inspected versions are NumPy
2.5.4, SciPy 1.18.1 and Matplotlib 3.11.2; save exact versions with each run.
No new language, game engine or finite-element package is needed for the first
implementation. Notebooks should call the same model functions as command-line
runs, rather than containing a separate solver.

| Layer | Proposed implementation |
| --- | --- |
| Inputs and units | Python dataclasses plus JSON scenario files; SI internally. Store material assumptions, geometry, controls, initial conditions and solver settings separately. |
| Model state | NumPy arrays for 2D node position/velocity, immutable material labels, segment rest lengths/areas, attachment states, payload masses and pulley states. |
| Steady screen | SciPy `least_squares`, scaled residuals and sparse Jacobian structure, for stationary shape with **moving** line; optional initialization shortcut. |
| Time integration | SciPy `solve_ivp` with `Radau` as the first stiff-elastic candidate; sparse Jacobian. Compare a smaller verification case with an explicit method and refine tolerances/time steps. Choose on measured accuracy/cost, not assumed speed. |
| Contact and events | Explicit feed-wheel geometry, finite traction law, attachment/load/unload events, gentle-release states and shared-shaft torque balance. Restart integration at discrete events; resolve release duration. |
| Data | JSON metadata and summaries plus compressed NumPy `.npz` histories initially. Save material-indexed stress and geometry, not just screenshots. Add chunked storage only if measured history size requires it. |
| Figures | Matplotlib `LineCollection` for stress-colored 2D cable, stress profiles, space/time heatmaps and peak-utilization histories; SVG/PNG figures and optional animation. |
| Exploration | A notebook with scenario controls first. Optional `ipywidgets` sliders for Ω, feed speed and payload spacing can rerun/inspect precomputed cases; avoid making a UI a prerequisite for mechanics. |

SciPy's [bounded least-squares solver](https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.least_squares.html)
supports sparse Jacobians. [Radau](https://docs.scipy.org/doc/scipy/reference/generated/scipy.integrate.Radau.html)
also accepts sparse Jacobians or a sparsity pattern; this makes it a candidate
for the coupled elastic chain, not proof that it will be the best solver here.

## Controls and independent inputs

- **Machine rotation Ω** in rad/s or displayed RPM, with an optional time ramp.
  The initial study holds it fixed and measures required drive torque.
- **Conveyor circulation:** choose feed-line speed `u` (m/s) or commanded feed
  pulley RPM plus effective radius, not both independently. In no-slip operation
  they are linked. In traction-limited runs, wheel speed is controlled and actual
  line speed/slip is an output; a desired line-speed controller must obey torque
  and grip limits. Keep Ω distinct from pulley spin relative to its carrier.
- **Outgoing payload density:** specify payload mass and spacing along the
  material line; derive mean added mass per line metre and nominal cadence.
  For steady screening, use a continuous added density only on the outgoing
  strand. For dynamics, use discrete masses with controllable spacing/phase.
  Return fixtures have their own mass and spacing; they are never massless.
- **Line/geometry:** unstretched loop length, constant area per loop, feed-wheel
  radius/location, material density, axial modulus, working strength, ultimate
  strength and damping assumptions. Loop length and shape determine the achieved
  outer radius; do not fix every radius, tension and length independently.
- **Two-stage additions:** inner/outer line properties and lengths, common
  shaft inertia, effective groove radii, free intermediate position and transfer
  schedule. Equal effective radii enforce equal nominal feed speed under no slip.
- **Loading and release:** load pickup/acceleration law at the inner wheel,
  phase/position trigger, controlled unloading law and available stroke. Test
  approximately 10 m as an input, not a proven adequate release length.

Do not optimize payload density and claim a throughput result without checking
catcher windows. The first mechanical test can use an idealized release cadence,
explicitly separated from actual captured delivery rate.

## Mechanics and steady versus dynamic solution

Use a hub-centered frame rotating at Ω: model centrifugal, Coriolis and, for
variable Ω, Euler terms consistently. Keep the feed-wheel center at its stated
rover radius. A horizontal planar calculation excludes vertical lunar gravity
and droop; bending, ground clearance and out-of-plane support remain separate.
In-plane gravity gradients may be omitted in the first declared idealization,
then checked as a correction. Frame forces do not replace physical tension or
hub work in energy accounting.

For dynamics, use a closed chain of material nodes with axial elastic,
tension-only links: mass from density × area × rest length, axial stiffness from
modulus × area / rest length. Nodes circulate around the wheel rather than being
created/destroyed at a spool. Resolve the free end's curvature through dynamics.
Use an explicit, documented unilateral contact/traction treatment and test its
stiffness/regularization sensitivity; `solve_ivp` by itself does not solve rigid
contact constraints. If exact constraint enforcement becomes necessary, select
a constrained integrator rather than burying constraints inside an unconstrained
ODE with arbitrary penalties. Keep physical damping distinct from temporary
initialization damping and numerical dissipation.

A steady shape in the rotating frame still has material velocity, convective
acceleration and mass transport. A static spring equilibrium with every material
node at rest would solve the wrong problem. Attempt a moving-line steady solve
with continuous payload density, wheel contact, loop closure and tension bounds.
Check the *force residual*, not merely the optimizer's success flag. If this is
hard or no admissible steady solution emerges, proceed directly to dynamics.
Relaxation can initialize a run, but remove artificial damping before judging
stability. Discrete payloads may produce a repeatable cycle instead of a strictly
steady shape; report that distinction.

Carry attachment masses around the loop. Model pickup and unloading forces over
finite intervals, including the momentum and energy entering/leaving with cargo.
For two stages, couple both contacts through one shaft torque balance and model
support transfer; do not prescribe incompatible independent pulley speeds.

## Stress and closeness to failure

For each segment, record axial tensile stress `σ = T/A` using an explicitly
consistent area convention. Show both:

- **Working utilization** `U = σ / σ_allowable`: unity reaches the selected
  working limit, which already includes the stated derating/safety factor.
- **Ultimate utilization** `σ / σ_ultimate`: unity reaches the assumed material
  ultimate strength. Crossing the working limit is not automatically fracture.

Report peak U, its position/material label and time; report the working margin
`1 − U`. A displayed factor `σ_allowable/σ` is undefined at zero stress and should
be masked there. Initially flag crossings without deleting links so that a
numerical fracture event does not conceal the preceding load history.

Use five complementary outputs:

1. 2D cable geometry colored by U, with a fixed comparison color scale and a
   clearly marked U=1 threshold; include payloads, wheel and velocity arrows.
2. Stress versus material arc length around the **whole loop**, with outgoing
   and return portions identified, plus allowable and ultimate lines.
3. Stress/utilization heatmap against **material coordinate and time**, allowing
   waves to be followed without confusing cable motion with a spatial index.
4. Peak utilization and grip margin versus time, including pickup, transfer,
   release and repeated wave reflections.
5. Torque, electrical/mechanical power, slip speed/distance and heat histories.

Keep separate failure checks for axial strength, traction loss, slack/contact
loss, attachment capacity and drive/thermal limits. A 2D axial chain does not
resolve local bend stress, groove crushing or fatigue; carry their allowances
and unknowns explicitly rather than claiming a complete failure envelope.

[Rüdiger's tether-dynamics study](https://blog.klaehn.org/blog/lunar-sling-launcher-tether-dynamics/)
is a useful presentation reference for stress profiles and release-wave tests.
Our model adds a closed circulating line, wheel traction and a distributed stream
of payloads; his numerical release settings are not transferred as validated
values for this design.

## First implementation milestones

1. Freeze the input schema and axial constitutive/contact assumptions. Add
   material-source provenance before treating a result as a material comparison.
2. Verify unloaded and simple analytic cases, then one loaded loop at chosen Ω/u.
   Try a moving-line steady solution briefly; do not make it a prerequisite.
3. Produce the 2D stress map and time histories. Sweep feed speed and outgoing
   density at fixed declared hardware. Keep the counterweight arm symmetric.
4. Add finite pickup and gentle release; compare repeated events, grip and
   waves after reflection. Demonstrate spatial/time-step convergence, mass and
   energy balance and actuator work accounting. Recheck any stability conclusion
   without initialization damping.
5. Add the shared-pulley two-stage arm and handoff, retaining the same outputs.
   Asymmetric two-arm dynamics and 3D behavior remain later extensions.

Suggested module boundaries: `config`, `materials`, `loop_state`, `forces`,
`pulley_contact`, `events`, `steady`, `integrate`, `diagnostics`, `plots`, plus
scenario files and result manifests. This is an outline, not a new dependency
installation or an implementation claim. The prior spool-based operations and
3D simulation tasks remain on hold.
