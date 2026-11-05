# Breakout: spherical-Moon release geometry and no-impact criterion

**Heading optimization update:** [Varying launch phase/heading reduces catch speed to about 13.3 m/s and apoapsis to 28.1 km](../analysis/heading_optimization/README.md). The 90-degree case remains a comparison baseline.

Status: **Closed at user-accepted scope, 2026-11-04.** [Final result and file map](../analysis/heading_optimization/RESULT.md). Historical framing and possible extensions below are retained for context; they are not pending requirements.

[Worked explanation, diagram and height-margin results](../analysis/spherical_release/README.md).
The user clarified that the concern is reaching circular equatorial catchers
from north/south-offset releases. The recommended correction is first-node
capture with the node radius set to catcher altitude; no inward velocity is
required. Catch at apoapsis is incompatible with this particular horizontal
release geometry and an equatorial catcher. This establishes the orbital
branch; tether drop remains an explicit parameter for tower-height sizing.
The terrain/longitude survey is **paused by user request**. Preserve its reports,
graphs and data. This work uses a perfectly spherical Moon and central gravity;
no DEM, site search or topographic corrections enter the calculations.

## Questions to answer

1. Given a circular equatorial catcher target (start with **25 km**), and either
   payload centripetal acceleration or sling RPM, what minimum tower height
   permits a nominal payload trajectory that does not hit the sphere? What is
   the payload's clearance above the sphere at the release point?
2. Starting from that limiting geometry, how much does minimum orbital clearance
   increase when the tower is raised by 1 m? Distinguish release clearance from
   minimum clearance later in the orbit. Specify what remains fixed when height
   is changed, and repeat with target/RPM constraints re-solved if necessary.

Assume a single tower at one point. Structural reactions during a small release
angle adjustment are outside scope. Derive the geometry/orbits algebraically
where convenient and use numerical roots/propagation as cross-checks. Do not
import the old pole mass, droop optimization or 3 m DEM initial conditions as
constraints on this blank-slate study. Use the old geometry only as a labeled
comparison, not as an answer imposed on the new calculation.

## Geometry distinction and clarification

The clarification distinguishes two possible meanings of **“payload pointing slightly inward”**:

- The tether can slope downward from tower to payload while the release velocity
  remains east/west and locally horizontal.
- The payload velocity can instead have a component toward the lunar center,
  making release precede the orbit's closest approach.

These are different initial states. The clarified concern is equatorial
interception, resolved in the linked baseline using horizontal node capture.
A finite north/south arm offset by itself does **not** create an inward radial
velocity for an exactly east/west release. Also distinguish the tether's inward
centripetal acceleration before release from the velocity it has after release.
An arbitrary velocity tilt is not automatically realizable by the same rigid
rotation geometry; declare the required change of release plane/phase, without
turning this study into a structural-reaction calculation.

## Variables and dependencies

| Symbol / role | Meaning |
| --- | --- |
| R, mu | Spherical lunar radius and gravity parameter; keep consistent and explicitly declared. |
| h_c | Circular equatorial catcher altitude above that sphere; initial target 25 km. |
| H | Tower apex height above the sphere at the tower foot. |
| d | Horizontal payload offset from the tower's radial axis at release. |
| delta | Payload drop below the apex along the tower's local vertical; alternatively specify tether length/angle to determine it. |
| gamma | Flight-path angle relative to the payload's own local horizontal; inward/downward is negative. Not the tether's downward angle. |
| omega_s OR a_s | Independent sling rate OR specified payload centripetal acceleration; derive the other and the arm radius from compatible geometry/target conditions. |
| Moon spin / direction | Add surface rotation to obtain inertial release velocity; start prograde, then compare retrograde. |
| Release phase / catcher phase | Choose a physically explicit intercept geometry and solve station timing. Do not assume an offset launch meets an equatorial catcher at apoapsis. |

Tower height cannot be inferred uniquely from RPM/acceleration and target altitude
without the tether drop/release geometry and velocity direction. The report should
make those extra assumptions visible, or give results as functions of them.
Keep the instantaneous launch-state model separate from a future cable-shape model.

## Baseline algebra: height above the sphere

At an equatorial tower, take X radial through the tower, Y east, Z north.
For a north/south-offset release,

```text
r_release = (R + H - delta, 0, +/-d)
r0        = sqrt((R + H - delta)^2 + d^2)
c_release = r0 - R
```

For a prescribed release clearance c, at fixed d and delta,

```text
H = delta + sqrt((R + c)^2 - d^2) - R
```

An algebraically negative H is not a requirement for underground construction;
it means that release clearance alone places no positive-height requirement on
that particular geometry. Tower/payload/cable physical clearance must still be
consistent, and a real tower has H >= 0.

At fixed d and delta, adding height changes release clearance according to

```text
d(c_release)/dH = (R + H - delta) / r0
```

Thus the geometric gain is nearly, but not exactly, 1 m per added tower metre
when d is small relative to R. This does not by itself establish the gain in
minimum orbital clearance for an inward-aimed release or a retargeted trajectory.

For comparison only, R = 1,738,100 m and d = 5,787.088 m give approximately
9.634 m of spherical clearance even when the tip lies in the tower-foot tangent
plane. The old release point was about 0.877 m above that plane, giving about
10.511 m radial clearance. A 3 m radial-clearance point at the same offset would
instead lie about 6.634 m **below** that tangent plane. These are different
release geometries. At the old geometry, fixed-drop/fixed-offset height gain is
approximately 0.999994 m of release clearance per tower metre.

## Baseline algebra: no impact over a bound orbit

Given inertial release position r and velocity v,

```text
specific energy E = |v|^2/2 - mu/|r|
specific angular momentum h = |r cross v|
p = h^2 / mu
e = sqrt(1 + 2 E h^2 / mu^2)
r_peri = p / (1 + e)
minimum spherical clearance = r_peri - R
```

For the bound nonradial trajectories of interest, the all-orbit criterion is
**r_peri > R**; equality is grazing contact. Find the limiting tower height by
solving r_peri(H) = R under the explicitly chosen targeting and release geometry,
then evaluate margin at H+1 m and other height increments. No repeated-orbit
terrain scan or 1.5-orbit cutoff is needed to establish this spherical criterion.

For an east/west release with zero radial velocity and speed above local circular
speed, release itself is periapsis. In that special case, any strictly positive
release clearance clears a perfect sphere for the entire ideal two-body orbit.
Therefore the previous terrain crashes do not by themselves demonstrate an
orbital-mechanics conflict between 3 m clearance and a 5.8 km lateral offset.

If gamma is inward, release is before periapsis and release clearance alone is
insufficient. Calculate the subsequent dip explicitly. Do not equate a velocity
angle to d/R without deriving it from the chosen release geometry.

For a finite offset, a trajectory in the plane spanned by the release radial
vector and east/west direction reaches its first equator node after 90 degrees
of orbital angle measured from release. With radial and transverse inertial
release speeds v_r and v_t, h = r0 v_t, its radius there is

```text
r_node = p / (1 - h v_r / mu)
```

Set r_node = R+h_c for this particular targeting branch. With v_r = 0 this
reduces to p = R+h_c, not apoapsis radius = R+h_c. A different release-plane
choice needs its own node/interception condition. Report relative capture speed
as a full vector difference, not just a difference of speed magnitudes.

## Deliverables and completion criteria

- Explicit diagram of the single tower, tangent plane, sphere, arm/drop, local
  horizontal, release velocity and orbital periapsis; angles must be unambiguous.
- Constraint/dependency table and reproducible algebra or Python calculations
  solving H_min, release clearance, periapsis clearance and catch-relative speed.
- Horizontal release is the calculated baseline. Add inward-velocity cases only
  if a specific alternative targeting requirement calls for them. Include RPM-driven and acceleration-driven parameterizations
  without treating their dependent arm radius as an independent fixed input.
- A height-margin table/curve: H_min plus selected added metres, showing both
  release and minimum orbital clearance. State whether geometry/velocity are
  held fixed or re-solved to retain the catcher target and chosen RPM/acceleration.
- Check algebra against independent Cartesian two-body propagation near the
  limiting orbit; verify the zero-radial-velocity periapsis limit.
- Explain which conclusions, if any, should later change the paused terrain
  model. Do not rerun or overwrite the terrain sweep during this breakout.

[Work-item index](../../WORK_ITEMS.md) · [Paused terrain study](EQUATOR_TERRAIN_AND_FAILED_SHOTS.md)
