# Corrected timed payout, return power and wheel ballast

> Historical baseline/review. The current speed-constrained spooling model and
> engineering status are in [CHECKPOINT.md](../CHECKPOINT.md) and the
> [scenario method](../results/speed_constrained/METHOD.md). Earlier independent
> track-radius and fixed-deployed-sling assumptions do not govern that branch.

The earlier mass-screen solar figures were **not spooling-machine figures**.
They used two moving payloads on fixed deployed cables and zero-mass returning
carriers. They omitted cable payout/retraction energy and should not be used
for a payout design. The previous pole masses also omitted the large ballast
loads now exposed. They are not retained as a candidate structure.

This replacement uses explicit one-dimensional cable inventory integrals and
rigid rotation. It includes cable mass during payout and return, simultaneous
wheel/spool power, a loading allowance, phase correction, rolling resistance
and the ballast required by the specified tangential traction model.

[Generated table](../results/spooling_cycle.md) ·
[Full numerical results](../results/spooling_cycle.json) ·
[Implementation](../spooling_cycle.py)

    .env/hub/bin/python -m sling_launcher.spooling_cycle
    .env/hub/bin/python -m unittest discover -s sling_launcher/tests -v

## Wheel speed and available time are different constraints

For required payload tip speed u, tip acceleration a_tip and track radius R:

    omega = a_tip / u
    wheel speed = omega R
    ground tangential force = required hub torque / R

At 300 g and u=1,684.52 m/s, omega=1.74649 rad/s. A 50 m wheel-path radius
requires 87.32 m/s; a 20 m radius requires 34.93 m/s. Taking two passes cannot
change either final speed. A smaller track solves this speed restriction but
requires more ground force for the same hub torque. The user's concern that
smaller radius makes acceleration harder is correct for traction. More time
helps reduce torque/traction demands. It does not cure an excessive required
release wheel speed.

The model keeps the rover angular speed constant during payout and retraction.
The payload still accelerates tangentially as it moves outward. This is one
explicit operating policy, not a conclusion that constant speed is optimal.
A small smooth speed excursion closes the rotation phase during the final
buffer, with the corresponding ballast inertia included.

## Time allocation

One site-relative catcher pass is 6,633.486 seconds (110.558 minutes).

| Segment | One-pass cycle | Two-pass cycle |
| --- | ---: | ---: |
| Load at moving apexes | 5.000 min | 5.000 min |
| Extend loaded cables; rest-to-rest radial motion | 50.279 min | 105.558 min |
| Release | Boundary event | Boundary event |
| Retract empty cables; rest-to-rest radial motion | 50.279 min | 105.558 min |
| Phase correction / operating buffer | 5.000 min | 5.000 min |
| Total | 110.558 min | 221.116 min |

The last five minutes actively restore rotation phase; they are not an
independent five-minute idle reserve. The assumed loading service takes five
minutes; its mechanism remains excluded, but bringing the loads up to the
apex's tangential speed is included as an idealized acquisition torque/energy
cost. Start-up from rest after lunar night is not a recurring cycle operation.

Travel uses a smooth quintic profile with zero radial velocity and acceleration
at both ends. Phase correction uses a smooth angular-speed bump whose integral
makes the machine turn an integer number of revolutions between releases. The
loaded payload's flight to the catcher proceeds while the empty cables retract.
Capture-targeting and countermass disposal are still separate constraints: the
symmetric mechanical example is not a certified orbital/disposal design.

## Cable mass, torque and power

Use 1,000 kg useful payload, 1,000 kg opposite load, density 1,450 kg/m³ and
provisional horizontal working stress 1 GPa, as in the previous material screen.
At 100 g and 50 m track radius the two cables total 36,980 kg. Each complete
cable remains aboard: part on the spool, part deployed. Stored cable is placed
at the apex radius in this first orbital-inertia approximation.

Let s run from the final cable root (0) to distal tip (L), and let q be deployed
length. Material from s=L-q to L is deployed, with radial position

    r(s,q) = R + s - (L-q).

The actual tapered linear density lambda(s) is integrated. For both sides:

    I(q) = 2 [m_stored R² + integral_deployed lambda(s) r(s,q)² ds
              + m_attached (R+q)²]
    I_q  = 4 [integral_deployed lambda(s) r(s,q) ds + m_attached (R+q)]
    M_radial(q) = 2 [m_deployed + m_attached]

The wheel torque is I*alpha + I_q*qdot*omega, plus the contribution of fixed
hardware and ballast when angular speed changes. No continuum solver is
needed to evaluate these integrals. In particular, tangential acceleration of
a moving mass is r*alpha + 2*omega*qdot, and the cable's own contribution is
integrated rather than replaced by a guessed tip mass.

The ideal radial-guide power follows conservation of energy:

    P_radial = [M_radial qddot + 0.5 M_radial_q qdot²
                - 0.5 I_q omega²] qdot.

Positive values require reel input; negative values are available braking power.
The changing radial kinetic energy of the moving cable is included. This is an
ideal reversible guide/inventory model: drum self-rotation, bend losses and
irreversible cable pickup/laydown losses remain additional hardware-dependent
terms. It is not a detailed spool mechanism simulation. Gravity/sag and elastic
energy changes are not included in this straight-cable power bound.

For each instant, sum positive wheel and radial power through 85% motor/drive
efficiency; subtract zero or 70% of simultaneous negative mechanical power,
then clip external solar demand at zero. Excess generation is not stored or
credited to a later time. Recovery on retraction can therefore supply the reel
from simultaneous wheel braking, without inventing a battery.

At 100 g, one pass, and the default traction assumptions:

| Quantity | Computed value |
| --- | ---: |
| Maximum wheel mechanical input, including rolling loss | 25.93 MW |
| Maximum outward radial braking available | 12.27 MW |
| Maximum inward radial mechanical input | 10.25 MW |
| Peak solar input, no recovery | 30.50 MW |
| Peak solar input, 70% instantaneous recovery | 21.91 MW |
| Peak solar input for two passes, no recovery / 70% recovery | 14.53 / 10.44 MW |

Thus retraction is now included explicitly and has a substantial positive reel
power requirement. The earlier 4.1 MW payload-only value is superseded for
spooling. Solar masses would be 305 / 219 tonnes for one pass if the installed
system really supplied 100 W/kg at that operating time; this remains an
unverified sizing assumption, not a hardware selection.

## Where peak spin-up demand occurs

For the 100 g example, the maximum tangential ground force occurs during payout
at **83.89% extension**, 2,116 seconds after payout starts. It is **890.7 kN**
for the complete machine, including rolling resistance. Peak force does not
occur at the fully extended state, because radial speed smoothly returns to
zero before release. The computation evaluates the entire time history.

The opposite radial payload tensions approximately balance through the main
tie, but the two angular-momentum demands add. Recovery changes electrical
supply requirements, not the torque that the road/wheel contacts must transmit.

## Local rock needed for tangential traction

The explicit reference assumptions are traction coefficient 0.5, 75% of total
normal load carried by powered wheels, and rolling-resistance coefficient 0.02.
These are sensitivity parameters, **not measured high-speed lunar-road values**.
NASA's wheel tests and terramechanics guidance show dependence on slip, wheel
load, speed and soil; they do not establish a single universal coefficient:
[NASA LRV wheel tests](https://ntrs.nasa.gov/search.jsp?R=19730004536),
[NASA LTV terramechanics guidance](https://ntrs.nasa.gov/citations/20220010732).

At each time solve

    |F_dynamic + F_rolling| <= mu * f_driven * g * M_supported.

Total cable weight (stored and deployed) and attached loads supply known normal
force in the small-sag approximation. Unsized hardware supplies no assumed
normal-load credit. One ballast mass is carried throughout the cycle; its
rolling drag and angular-acceleration demand during phase correction are included.
Both positive and braking traction inequalities are solved. This is a global
traction bound, not individual-wheel load sharing or an overturning solution.

| Case | Local ballast, BOTH frames total |
| --- | ---: |
| 100 g, 50 m track, one pass | 1,424.6 tonnes |
| 100 g, 50 m track, two passes | 658.1 tonnes |
| 300 g, 20 m track, one pass | 1,178.1 tonnes |
| 300 g, 20 m track, two passes | 540.9 tonnes |

For the 100 g one-pass case, changing friction from 0.5 to 0.3 raises ballast
to 2,495.5 t; increasing it to 0.7 lowers ballast to 989.9 t. Actual imported
hardware weight would reduce the rock requirement, while its inertia and
rolling load must also enter. Soil bearing capacity and finite wheel contact
area can invalidate any of these ballast amounts.

Ballast must also follow the circle. In the 100 g case its centripetal
acceleration is 16.95 m/s², far above lunar gravity. The model requires that
radial restraint to pass through the main tie/frames; tangential friction alone
does not provide it. Ballast adds about **12.07 MN of inward restraint per
frame**. The old main-tie and pole masses do not include that load.
If this force had to come entirely from lateral ground friction, the assumed
coefficient would be inadequate regardless of how much ballast were added.
A complete structural and contact closure is therefore still necessary before
claiming a feasible launcher mass ratio.

## Pole heights: old end-state estimate versus the cycle

The previous 7.49 m at 100 g, 54.56 m at 30 g and 471.21 m at 10 g were fully
extended, loaded clearance estimates. They did not cover deployment or unloaded
retraction and should not have been presented as the actual pole-height optimum.

The revised calculation scans intermediate deployed lengths on both loaded
and unloaded branches, includes the actual taper and a 3 m ground-clearance
margin, and finds a **9.31 m apex height at 100 g**. The controlling state is
unloaded retraction at about **41.7% extension**, rather than the fully loaded
end state. A vertical leg would be approximately that height and a 45-degree
trailing leg about 13.17 m, before wheel/hub/joint offsets.

At 300 g with 20 m track radius, the same approximation gives **3.69 m**.
These are quasi-static cable-clearance requirements, not proven transient
heights or structurally optimized pole masses. At 10 and 30 g the small-slope
approximation becomes invalid during some partially deployed states; the
screen outputs roughly 682 and 77 m respectively, but those two heights must
be replaced by a nonlinear cable-shape calculation before design use. The JSON
records the maximum slope and validity flag so these failures are visible.

## Checks and remaining limits

The suite has 21 passing tests, including cable deployment/retraction work-energy
balance, phase and time closure, interior traction peak, ballast inequalities,
spatial/time refinement, recovery consistency, and the distinction between
wheel-speed and two-pass torque limits. Numerical consistency does not qualify
the material, road, drum, powered-wheel load fraction or radial force path.

The remaining coupled tasks are nonlinear cable shape where necessary,
transient/elastic clearance, ballast-aware pole/tie/anchor sizing, wheel load
capacity, drum sizing and power-equipment mass. These are authorized ongoing
work; no new approval gate is inferred from this correction.
