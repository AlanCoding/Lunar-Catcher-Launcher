# Model, assumptions and buildability checks

This catalogue supersedes the fixed-track spooling screen for the current
question. It is a checkpoint of the calculation, **not a finished design or a
complete mass optimization**. All numerical inputs are recorded in each
`metrics.json`; `Scenario` in `scenario_study.py` is their single source of truth.

## Independent and dependent quantities

Independent scenario choices: release centripetal acceleration (Earth g), rover
operating speed (50 or 80 mph), useful payload (1,000 kg), cadence (one or two
catcher passes). Material/traction/power assumptions and control policies are
explicit inputs, not optimized silently.

For release speed u, rover speed v and release centripetal acceleration A:

    omega = A/u
    release radius b = u²/A
    track radius R = v/omega = vu/A

**Track radius is not a free variable.** Speed is exactly v during payout and
return, and at release. Small controlled slowdowns during loading and the final
buffer close rotational phase. The speed never exceeds v; interpreting v as
exactly constant at all times would generally make arbitrary acceleration and
integer-pass release timing incompatible.

Release speed is solved iteratively with the finite-offset, due-east,
equatorial-node intercept in `orbit.py`, including the actual release tip
height. This replaces the previous constant 1,684.52 m/s mechanical screen.
The two-body orbit is still an idealization; catcher sustainability, terrain,
Sun geometry and countermass disposal are not solved by this coupling.

Apex height is the minimum height clearing the quasi-static loaded AND empty
cable families, plus 3 m. It is a dependent clearance dimension, **not a
structural mass optimum**. Actual structure/transient design could require a
greater height. The reported acceleration label is centripetal acceleration at
release, not an imposed bound on the full applied-force vector; the vector peak
is separately calculated in every scenario.

## What happened to the old maximum acceleration?

For an independently fixed 50 m track, the old speed test was

    A_max = v u / 50 m.

That is approximately 123 Earth g at 80 mph, or 77 g at 50 mph. It was a
**fixed-radius kinematic limit**, not a universal material or traction limit.
It disappears when R is derived as above. More orbits lower torque/traction
needs but cannot change a required final wheel speed at a fixed R.

There is no demonstrated maximum *feasible machine* acceleration yet. Shrinking
R eventually makes the hardware fail to fit. A useful necessary check for the
reviewed 45° leg, with both feet on the same circular track, is

    horizontal leg span = H < 2 R.

A chord cannot exceed the track diameter; equality puts a trailing foot at the
opposing frame, so the bound is already too generous for real hardware. Since
H >= 3 m even before wheel/hardware allowances, this gives a loose upper bound
A < 2vu/(3 m), approximately 2,560 g at 50 mph and 4,100 g at 80 mph. Actual
calculated sag makes the bound slightly smaller. These are **geometric rejection
bounds, not plausible working accelerations**. Wheel/drum size, frame bending,
retention and contact moments are likely to constrain the design much earlier.
The catalogue therefore includes 4, 10, 30, 60, 100, 125, 300 g plus 1,000,
2,500, 4,000 and 4,200 g as explicitly labelled boundary diagnostics.

The 4-g end fails the same 45°-leg chord check in both speed cases because the
required poles are too tall. It also has a long release radius and much larger
catcher encounter speed than the high-acceleration cases.

## Finite-angle cable shape and taper

The old small-slope approximation is not used here. Let s be material arclength,
r distance from the hub axis, and d downward displacement from the apex. Tr and
Tv are positive inward/upward tension components; lambda is mass per material
length. In the rotating frame with constant local downward gravity g:

    Tr(s) = m_tip omega² r_tip + integral_s^tip lambda omega² r ds
    Tv(s) = g [m_tip + integral_s^tip lambda ds]
    dr/ds = Tr / hypot(Tr,Tv)
    dd/ds = Tv / hypot(Tr,Tv)

An iteration of these one-dimensional integrals solves each deployed shape.
For an empty tip, the 0/0 endpoint slope is replaced by its limiting direction
(omega² r_tip, g). The shape satisfies cable arclength, rather than treating
horizontal reach as cable length. Empty tips are not assigned a fictitious load.

At full loaded extension, lambda = rho * hypot(Tr,Tv) / sigma sizes a
constant-**total**-stress taper. Integrating inward in horizontal radius solves
that sizing problem and determines the required material length. Subsequently,
material at the distal end deploys first; stored fiber remains at the apex.
Every deployment fraction is checked against the same manufactured taper.
The small numerical excess above sigma in outputs is quadrature error, not a
chosen stress margin. Dynamic tension, bends, fatigue and cable construction
still need additional allowable/section treatment.

Terrain is a sphere: its height relative to the hub tangent plane is
sqrt(R_moon²-r²)-R_moon. The required apex height is

    H = 3 m + max_over_all_shapes_and_material [d(s) + terrain_height(r(s))].

Gravity is held constant and parallel to the hub local vertical. Its direction
and magnitude variation, elastic strain and dynamic lag are neglected; the
finite-angle shape does not claim a fully nonlinear dynamic cable simulation.
At 4 g, the tip offset is about 72 km; this local-gravity approximation is a
further small error rather than exact lunar geometry. Lunar curvature itself
is retained in clearance and the orbital release state.

## Cable inventory, motion and power integrals

Use f = deployed material length / total material length. Both sides are
included in these functions, with the appropriate tip load (loaded/empty):

    I(f) = 2 [m_stored R² + integral_deployed lambda r² ds + m_tip r_tip²]
    U(f) = -2g [integral_deployed lambda d ds + m_tip d_tip]
    K(f) = 2 [integral_deployed lambda (r_f² + d_f²) ds
              + m_tip (r_tip,f² + d_tip,f²)]

K is the meridional kinetic-energy coefficient, not a mass guessed at the tip.
Material derivatives hold **material coordinate s fixed**. Numerical derivatives
at fixed normalized deployed coordinate x are converted using

    derivative_at_fixed_s = derivative_at_fixed_f_grid + (1-x)/f * derivative_x.

The meridional kinetic energy is K fdot²/2. Wheel torque and ideal reel power
follow the generalized work-energy equations:

    tau_wheel = I alpha + I_f fdot omega
    P_reel = [K fddot + 0.5 K_f fdot² + U_f - 0.5 I_f omega²] fdot.

Thus gravity, cable kinetic energy, changing orbital inertia, and retraction
are included in this version. The signed reel channel distinguishes mechanical
input from outward braking. This replaces the straight-cable power model at
low accelerations as well as replacing its height calculation.

These are prescribed quasi-static shape families: they do not prove that the
flexible cable dynamically follows the chosen shape during travel. Tangential
lag and radial inertial perturbations remain additional checks. Tests verify
work-energy balance on each continuous branch and convergence under doubled
shape/time resolution, not dynamic controllability.

## Release is an unresolved transition, not free instantaneous settling

The loaded and empty equilibria at full material deployment are different.
Immediately after release the cable still occupies its old shape. The model
reports both the displacement between equilibrium tip positions and the
change in the **empty cable's** rotational-plus-gravitational energy between
these shapes, counting both sides. These are diagnostics, not a predicted
recoil trajectory, dissipation rate or additional solar load.

This discontinuity is **not included** in branch power totals or cycle time.
A real controller must handle it without striking the ground or needing more
time than available. No maximum recoil amplitude is established by the 3 m
clearance margin. The branch energy tests deliberately do not claim conservation
across an instantaneous change to the new equilibrium.

## Timing and phase

Site-relative catcher revisit: 110.5581 min. Both cadences use:

| Segment | One pass | Two passes |
| --- | ---: | ---: |
| Loading allowance | 5.000 min | 5.000 min |
| Loaded payout | 50.279 min | 105.558 min |
| Empty return | 50.279 min | 105.558 min |
| Final buffer / phase correction | 5.000 min | 5.000 min |
| Total | 110.558 min | 221.116 min |

Each travel branch uses f = 10x³-15x⁴+6x⁵ (reversed on return), giving zero
radial velocity and acceleration at the endpoints. The speed correction always
removes angle, split across loading and buffer, to land on an integer turn
without overspeed or stopping. Its inertia and traction are included. The
buffer is therefore not an independent idle allowance for recoil. Loading the
new masses includes an ideal angular-momentum acquisition torque; loading and
release mechanisms themselves remain excluded. This is a timing allocation,
not proof that five minutes is sufficient for real loading hardware.

## Traction, ballast and radial moment checks

Inputs: mu=0.5, powered normal-load fraction=0.75, rolling coefficient=0.02.
The calculation solves both signed traction inequalities throughout the cycle:

    |tau/R + rolling + ballast angular-acceleration force|
       <= mu * powered_fraction * g * supported_mass.

Ballast is one constant local rock mass carried through the whole cycle. Its
rolling loss and phase-acceleration inertia are included. Cable and payload
weight provide normal load; unsized hardware provides no credit. These are
aggregate equations, not individual wheel contact or load-sharing solutions.
The figures also report lunar **weight in N**, separately from mass in kg.
A contact footprint at 100 kPa is a transparent area conversion, not an adopted
soil bearing capacity or a wheel design.

The main tie carries the opposing payload forces, but each rotating frame and
its ballast also needs inward acceleration. The latter requires approximately
M_ballast omega² R / 2 per frame. The tie tensile subtotal includes that load,
stored cable inertia and its own distributed radial inertia. Its small sag is
estimated separately. The tie mass is not iterated back into the cycle: this
subtotal is not a closed hardware/inertia design.

For a compact frame with ballast near ground level and radial center near R,
transferring its inward force through an apex H above the road creates moment
approximately (M/2) omega² R H. Without a significant stabilizer reaction or
lateral ground force, a necessary normal-force support lever is

    b_required approximately H omega² R / g.

The plotted b_required/R is a **diagnostic of the compact-frame assumption**,
not an exact solution for a frame spanning a large fraction of the circle. It
exceeds unity in the current sweep: the assumed narrow A-frame cannot simply
be credited with an unlimited ballast mass and an elevated tie. A full 3D
frame/contact solution, strong stays, a different radial force application
height, or wider support would change this condition. None is silently adopted.
Tangentially fore/aft passive wheels are retained; individual contact engineering
was excluded by the user and remains beyond this aggregate calculation.

If the ballast's radial restraint is instead assigned entirely to lateral road
friction, a separate necessary bound is omega*v < mu*g. With the assumed mu=0.5
and u about 1,684 m/s, this means payload centripetal acceleration below about
6.2 Earth g at 50 mph or 3.9 Earth g at 80 mph. Equality leaves no friction
capacity for tangential acceleration; a combined contact-force solution would
be stricter. Ballast mass cancels from this bound. The main-tie/frame route
used in the reported cycle avoids that road-only constraint only if the
associated frame moment can actually be carried.

This explains why quoting the old axial-only pole masses would be misleading.
No pole or full imported mass is reported until that load path is resolved.
Low pole height reduces this problem but the 3 m minimum prevents it vanishing
as acceleration increases. Merely taking another orbit does not change the
centripetal acceleration or the moment-to-weight ratio.

## Power and mass assumptions

85% drive efficiency applies to positive mechanical input. Reversible wheel and
reel motor/generators are the proposed recovery mechanism; at most 70% of
simultaneous negative mechanical power is credited against contemporaneous
input. Excess generation is discarded; nothing is stored for a later phase.
No-recovery and recovery outputs are both supplied. Drives, bus, braking load
and heat rejection remain unsized equipment, so the recovery curve is an
engineering scenario, not a demonstrated hardware efficiency.

The installed array assumption is 100 W/kg at the operating illumination.
Solar mass is peak demand divided by this figure. To explore 50 or 200 W/kg,
double or halve only the array subtotal. No continuous lunar-night operation,
energy buffer or annual throughput is claimed. Near dawn/dusk available power
is lower; these numbers describe suitable illumination.

The cable density 1,450 kg/m³ is the Kevlar 49 value in the
[Toray–DuPont material table](https://www.td-net.co.jp/kevlar/data/), checked
2026-10-31. The 1 GPa working stress is a study assumption, not a qualified
finished-cable allowable. That supplier table does not establish finished-rope
bend life, vacuum/dust/UV life, terminations or this machine's duty cycle.
The [NASA terramechanics white paper](https://ntrs.nasa.gov/citations/20220010732)
describes wheel/soil and rolling-resistance modeling; it does not validate our
three aggregate traction assumptions at 50–80 mph.

Every case distinguishes accounted imported cable/tie/solar subtotals, local
ballast, 1,000 kg expendable rock and useful payload. Poles, wheels, motors,
drums, restraint hardware, thermal and electrical equipment remain **unsized,
not zero**. Total imported mass is null. The similar partial mass sums across
acceleration cannot establish an optimum for a complete machine.

## Reproduction and evidence

From repository root:

```bash
MPLCONFIGDIR=/tmp/lunar-sling-mpl-cache .env/hub/bin/python -m sling_launcher.scenario_study
.env/hub/bin/python -m unittest discover -s sling_launcher/tests -v
```

`manifest.json` records source hashes and installed numerical package versions.
Each case provides machine-readable metrics, a sampled time history (every
8th integration sample, including phase endpoints), branch shape figures and
power/speed plots. Derivatives use 241 deployment fractions and 501 spatial
nodes per shape; power histories use 1,601 samples per phase. Refinement tests
double these for the demanding 4-g case. SVGs are editable scientific plots;
PNGs are provided for convenient preview.
