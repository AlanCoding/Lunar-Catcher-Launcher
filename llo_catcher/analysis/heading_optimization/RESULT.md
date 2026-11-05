# Accepted result: minimum-speed capture by a 25 km equatorial catcher

**Status: completed and accepted, 2026-11-04.** This is the endpoint of this
spherical-Moon heading study. Start here; [README.md](README.md) contains the
tradeoff graph, derivation, assumptions and reproduction instructions.

## Problem and solution

A sling centered on the lunar equator releases payloads several kilometres north
or south of it. A due-east release from the southern tip crosses the equator
90 degrees later. Targeting a 25 km equatorial catcher there produces an unwanted
50.7 km apoapsis. The objective here is to minimize the **vector relative speed
at capture**, allowing a north/south component at release while keeping the
catcher in its circular equatorial orbit.

The accepted solution releases the southern payload **0.240709 degrees before
its southernmost position**, initially moving slightly south of east. This
delays the equator crossing to **141.557022 degrees**, lowers apoapsis to
**28.087805 km**, and yields **13.282500 m/s** relative catch speed.
Capture occurs **42.930505 minutes** after release. No new impulse at release
is required in the ideal circular tip kinematics.

## Selected optimum: fixed reference RPM, radius and phase solved

The table reports extra digits so the numerical case is reproducible; it does
not imply that the physical hardware or lunar environment is known this precisely.

| Parameter | Numerical optimum | Units |
| --- | ---: | --- |
| Sling rotation rate | 2.779627912 | RPM |
| Horizontal sling radius | 5778.274529942 | m |
| Centripetal acceleration | 49.923848891 | Earth g |
| Signed release phase | -0.240708970 | degrees |
| East offset from hub | -24.275407935 | m |
| North offset from hub | -5778.223537381 | m |
| Orbital angle to first equator crossing | 141.557021538 | degrees |
| Orbital inclination | 0.306487547 | degrees |
| Relative catch speed | 13.282500444 | m/s |
| Radial catch component | 8.340425593 | m/s |
| Northward catch component | 8.893855776 | m/s |
| Along-track catch component | -5.268913398 | m/s |
| Apoapsis altitude | 28087.805372482 | m |
| Flight time to capture | 2575.830275551 | s |
| Uncaught orbital period | 6577.376162202 | s |
| Inertial release speed | 1686.575819755 | m/s |
| Minimum spherical clearance | 3.000000000 | m |

Negative release phase means before the southernmost position; negative east
and north offsets mean west and south. The angle to capture is orbital angle,
not Moon-fixed longitude. The southward inertial release component is about
7.066133 m/s. The 3 m clearance is an illustrative held constraint above a
perfect sphere, not a validated clearance over real terrain.

The first exploratory sweep instead held the release position fixed and let
speed change. It found **141.491983 degrees / 13.301436 m/s / 28.099113 km
apoapsis**. Those values label the existing graph. The table above is the
**selected reference-RPM result**, with a slightly adjusted 5,778.275 m radius;
the two optima should not be mixed in a single numerical design description.

## Scope and dependencies

Constants: lunar radius 1,737,400 m; mu = 4.902800118e12 m³/s²;
uniform rotation period 655.720 hours. Catcher altitude is 25,000 m above that
sphere. Release remains locally horizontal and at periapsis. The phase and arm
radius are free; release speed, inclination, catch angle and flight time follow.
The 50-g acceleration is approximately recovered, not separately imposed.

The optimum balances decreasing outward radial catch speed against increasing
northward crossing speed. It applies to the prograde first-node horizontal
branch and the stated clearance. Neither a joint prograde/retrograde schedule
nor real-terrain siting is claimed. The published launcher mass optimization
and its hardware snapshot are unchanged. Tower sizing still needs the chosen
tether drop. No further revisions to this accepted orbital case are pending.

## Files and reading order

| File | Purpose |
| --- | --- |
| [RESULT.md](RESULT.md) | This concise accepted problem–solution checkpoint. |
| [README.md](README.md) | Explanation, comparison cases, equations and run command. |
| [heading_tradeoff.png](heading_tradeoff.png), [SVG](heading_tradeoff.svg) | Fixed-position sweep: capture components, apoapsis and flight time. |
| [results.json](results.json) | Both optima, Cartesian states, exact values and validation residuals. Use `reference_rpm_phase_optimization` for the accepted case. |
| [sweep.csv](sweep.csv) | 6,001 fixed-position trial angles and outcomes. |
| [calculate.py](calculate.py) | Reproducible sweep, optimization, figures and independent propagation checks. |

The implementation uses constants and the old reference offset from
[../spherical_release/calculate.py](../spherical_release/calculate.py); it does
not load terrain data. It requires NumPy, SciPy and Matplotlib in the repository
Python environment. Independent Cartesian integration verifies the selected
phase-shifted state reaches the equator at 25 km with the stated relative speed.

[Parent analysis guide](../README.md) · [LLO study guide](../../README.md) ·
[Why earlier terrain trajectories hit the ground](../terrain/results/release_audit/README.md)
