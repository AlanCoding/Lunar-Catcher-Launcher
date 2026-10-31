# First mass numbers and the single-pass operating sequence

> Historical baseline/review. The current speed-constrained spooling model and
> engineering status are in [CHECKPOINT.md](../CHECKPOINT.md) and the
> [scenario method](../results/speed_constrained/METHOD.md). Earlier independent
> track-radius and fixed-deployed-sling assumptions do not govern that branch.

**Superseded for spooling:** see [corrected cable-mass payout, return power and ballast](spooling_cycle_review.md). The solar and pole subtotals here are not payout-machine sizing results.

This is a quantitative screening calculation, not a closed launcher BOM or a
feasible optimized machine. It retains the deployed-sling branch to obtain a
checkable reference before introducing the moving cable mass of payout. The
user has now authorized payout comparisons, recovery scenarios and optimization;
no additional phase approval is needed for that work.

[Generated composition table](../results/mass_screen.md) and
[full inputs/outputs](../results/mass_screen.json) are produced by:

    .env/hub/bin/python -m lunar_slings.hub_study.mass_screen

## Inputs and provenance

Useful payload and opposite load: 1,000 kg each. Examples: 10, 30, 100 and 300
Earth-g. Release speed is held at 1,684.52 m/s for this mechanical screen;
trajectory targeting is not re-solved for each large-radius geometry. Track
radius is 50 m; wheel speed limit 35.76 m/s. Constant spin, no climber mass and
no cable motion are comparison assumptions, not a selected operational design.

Kevlar density is 1,450 kg/m³, consistent with the manufacturer’s Kevlar 49 data:
[Toray–DuPont properties](https://www.td-net.co.jp/kevlar/data/).
The **1 GPa working stress is a provisional assumption**, roughly one-third of
nominal yarn tensile strength, not a qualified finished-cable allowable. Rope
construction, sheath, terminations, fatigue, creep and spool-bend derating can
increase the result. In particular, repeated spooling is not qualified by yarn
strength data.

Aluminum density 2,710 kg/m³, modulus 68.3 GPa and a preliminary 124 MPa allowable
(half the cited 248 MPa sheet yield) are based on the
[NASA 6061-T6 data compilation](https://ntrs.nasa.gov/api/citations/20120014854/downloads/20120014854.pdf).
These sheet values are screening inputs, not certified tube/joint allowables.
Tube wall is at least 2 mm and at least diameter/100; pinned Euler buckling uses
a factor of two. Diameter is searched from 0.01 to 5 m.

Solar subsystem specific power **100 W/kg at the operating condition** is an
assumption, including the intended support allowance, not a selected lunar
product. [NASA's power survey](https://www.nasa.gov/smallsat-institute/sst-soa/power-subsystems/)
illustrates the wide spread of array performance; it does not validate this
installed lunar value. At 50 W/kg, double the solar column; at 200 W/kg, halve
it. Low Sun, dust, temperature and support mass must eventually be explicit.
Motor efficiency is 0.85. Recovery cases use zero or 0.70 net conversion from
outbound radial braking to the concurrent electrical bus; no storage is used.

## What is calculated

For constant spin omega, tip radius b and apex radius a, the horizontal,
constant-stress rotating sling solution including its own mass is

    T(r) = m_payload * omega² * b * exp[rho * omega² * (b²-r²)/(2 sigma)]
    A(r) = T(r) / sigma
    m_sling = integral rho A(r) dr

Vertical tension is the weight of material and payload outward of the section.
Integrating vertical/horizontal tension gives a small-slope sag estimate. Height
is the largest ground-relative sag plus 3 m, including spherical curvature.
This is a steady loaded-state approximation; cable elasticity, transient sag,
unloaded shape, crosswind-free but nonzero gravity curvature effects, retained
hardware depth and alignment still require the full shape solver.

The main tie is estimated separately from sling-root tension. Its distributed
radial loading is approximated; exact tie/stabilizer/frame balance is not yet
solved. Its displayed mass is not an approved cable design.

The two-leg ideal truss resolves tangential apex load using a 45-degree trailing
leg. Axial load magnitude sizes each tube for strength/buckling. This omits pole
self-weight feedback, joints, bending, transverse stability and wheel ballast.
**Consequently the pole column is an axial-only lower estimate, particularly
unreliable for the extremely tall 10 g case.** A negative leading-leg axial
force implies a tension load path requiring wheel/ballast restraint; it is not
accepted as a demonstrated ground contact solution.

Height is searched over [clearance height, twice clearance height] with 41
samples; each tube diameter is searched over 10,000 values. The least axial
material occurs at the minimum permitted height in all tested cases. This is a
**conditional boundary minimum**, not a demonstrated full structural optimum.
The 100 g case gives about 7.49 m and 200 kg for four axial-only tubes; 30 g
requires about 54.56 m and 20.8 t under the same approximation. The 10 g result
is an indication to reject/revisit the slender-column architecture, not a
credible fabrication specification.

## One site-relative pass: 6,633.49 seconds

The orbital catcher repeats the site-relative geometry every 110.558 minutes.
The illustrative sequence budgets:

1. 120 s for loading near the continuously moving apexes.
2. 3,196.74 s outward rest-to-rest travel. The radial speed is solved to fit
   the allocated time; both loads reach the tips at zero radial speed.
3. Release at the specified phase; flight to interception proceeds independently
   while the surface machine continues its cycle.
4. 3,196.74 s return travel of the unloaded carriers.
5. 120 s reserved for restoration/settling and synchronization.

This fills the entire interval. The 120 s reservation is not a demonstrated
transient recovery time. Synchronization must meet the integral of angular
speed as well as the release speed; finite acceleration ramps may force a
shorter travel allocation or a skipped pass. Actual return energy depends on
carrier mass; the present zero-mass comparison is a lower bound.

In a payout branch, steps 2 and 4 become cable deployment and cable retraction.
The entire cable inventory remains permanent imported mass even when wound.
Its radius-dependent inertia, radial kinetic energy, stored versus deployed
mass, spool torque and bend limits must be added to the same time and energy
ledger. It is incorrect to use the current payload-only power column as the
power requirement of a spooling machine: the large tether mass makes that
omission material.

## Rover speed and acceleration constraints

At 50 m track radius, the 300 g example needs about 87.3 m/s and fails the
35.76 m/s speed limit. This does not rule out 300 g on a smaller track. At fixed
tip speed, increasing payload acceleration raises angular speed and shrinks the
allowable track radius. Track radius must therefore join the optimization.

Spin-up time is a separate condition. The torque requirement is

    tau(t) = I(t) * alpha(t) + I_dot(t) * omega(t).

Wheel torque, traction and electrical power must support this history within
the pass window. A speed limit alone cannot determine spin-up time. Selecting
a motor torque or treating arbitrary ballast as free unlimited traction would
hide this constraint. The present calculation includes the constant-spin
transport torque of the payloads, but has not demonstrated a variable-spin
machine cycle or any particular spin-up duration.

## Energy recovery scenarios

The recovery scenario requires a reversible radial drive/inverter supplying the
wheel bus while the wheel motors draw power. At every instant the credited
power is 0.70 times the available radial braking power, subtracted from the
concurrent wheel electrical demand. No credit is carried forward in time.
A real machine must include conversion/transfer hardware and its mass.

The 100 g reference gives these **incomplete subtotals per useful payload kg**:

- Poles, axial-only: 0.200.
- Two outward slings: 36.980.
- Main tie approximation: 1.112.
- Solar at assumed 100 W/kg: 41.055 without recovery, 28.841 with recovery.
- Subtotal: **79.347 without recovery; 67.133 with 70% recovery**.

These are useful composition numbers, but are not the requested final objective.
The missing imported mass is not zero. Motors, wheels, passive steering wheels,
spools, climbers or payout load attachments, stabilizers, joints, braces,
anchors, controls, protection, power conversion and ballast retention remain
unsized. Local ballast and expendable rock must also be carried in the dynamics.
The full ratio is the subtotal plus all remaining imported kg / payload kg.

This screen identifies the next numerical priorities: qualified cable stress
and mass, loaded/unloaded cable shape, wheel/contact and pole self-weight
closure, a physically timed payout or carrier cycle, and installed power
hardware. It does not support claiming a finite global mass optimum yet.
