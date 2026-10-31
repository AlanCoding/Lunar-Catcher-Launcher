# Free variables, dependent outputs, and constraints

> Historical baseline/review. The current speed-constrained spooling model and
> engineering status are in [CHECKPOINT.md](../CHECKPOINT.md) and the
> [scenario method](../results/speed_constrained/METHOD.md). Earlier independent
> track-radius and fixed-deployed-sling assumptions do not govern that branch.

No numerical bounds below are approved unless stated in the mission requirements.
Choose independent parameterizations for each branch; avoid overdetermined inputs.

| Role | Quantities | Treatment |
| --- | --- | --- |
| Fixed architecture | Two opposing A-frames, four drive wheels, two climbers, Kevlar slings, equator, single useful payload, direct solar | `MissionRequirements`; 20 km catcher and 35.76 m/s wheel limit are initial targets to validate |
| Environment | Moon reference radius, mu, spin, gravity, terrain, sunlight history | Sourced environment; derive gravity/spin speed consistently; latitude alone does not specify terrain or horizon |
| Design variables | Track/apex radius, trailing-leg angle, wheel radius/width, support sections/material | Geometry and catalog/discrete choices; wheel and apex radii need not coincide; central pivot is fixed at ground level |
| Dependent geometry | Apex/pole height | Solve sling shape/droop and terrain clearance across cycle states; use the required height with 3 m clearance margin, not an independent height optimization |
| Separate load paths | Main apex-to-apex tether and two small ground-pivot stabilizers | Main tie carries opposing radial loads directly; calculate stabilizer forces and tie sag/clearance, including asymmetric loads |
| Scale variable | Successfully captured payload kg | Sweep absolute sizes; fixed/minimum hardware sizes prevent guaranteed linear scaling |
| Payload constraint | Maximum permitted payload acceleration / Earth g | Outer trade-study variable, not necessarily the achieved acceleration; constrain full acceleration vector throughout the cycle |
| Sling parameterization | Outward length and spin-rate history, OR spin-rate history with length solved from release conditions | Release speed/heading, apex radius, length, and spin cannot all be independent |
| Control variables | Climber radial position histories, wheel torque/speed history, release phase | Slings stay extended; no cyclic full-length payout/retraction. Constrained by dynamics, peak power, traction, phase, and return readiness |
| Balance variable | Countermass/useful-payload ratio, possibly unequal sling geometry | Equal mass is an initial comparison, not a constraint; unequal loads produce residual pivot reactions and transients |
| Tether sizing policy | Grade, construction, working-stress policy, safety factor, taper family | Safety factor minimum is an engineering constraint; do not optimize it to an unsafe value; stress-limited area follows loads |
| Operating choices | Skipped catcher passes, allowed sun-elevation window, daylight launch interval | Bounded by orbital/site geometry, complete cycle time, available solar power, and permitted annual duty |
| Uncertain parameters | Cable efficiency/end fittings, creep/life derating, friction, rolling resistance, motor efficiency, solar degradation/specific power | Sourced ranges and sensitivity variables, not knobs chosen just to reduce objective |
| Dependent outputs | Required release state, length or spin, tip speed/acceleration, tensions, lag/strain, wheel loads, ballast, torque, structure/cable/motor mass | Derived from selected geometry and control; reject impossible solutions |
| Dependent outputs | Cycle duration, power history, panel area/installed mass, delivered mass ratio, annual throughput | Include peak simultaneous demand, darkness and failed cadence; no energy-average panel sizing |

For the **ideal planar, straight, fixed-length, steady-spin limit only**, if apex
radius is R and outward length L, tip radius is R+L, tip speed relative to the
site is omega(R+L), and centripetal acceleration is omega²(R+L). For a wheel
contact on radius R_w, wheel ground speed is omega R_w. These are dependency
illustrations, not the dynamic model. Sag, lag, elasticity, site rotation,
curvature, and climber motion require vector equations and change these relations.
Lunar-inertial release velocity includes the local Moon-rotation contribution.

An unlimited acceleration tolerance does not force the machine to use unlimited
acceleration. The feasible set may expand as the tolerance rises, allowing the
best achievable objective to fall or plateau. We must distinguish an optimum in
actual operating acceleration from an optimum in an externally imposed tolerance.

Mass objective is per single captured payload, not amortized over lifetime.
Throughput, lifetime, and minimum useful cadence must be reported separately;
without an agreed throughput requirement the optimizer might favor long cycles.
