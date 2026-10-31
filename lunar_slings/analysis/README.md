# Lunar Sling Analysis

## Initial assessment

The original notebook is a useful first model for launching material tangentially
from the lunar surface onto an ellipse whose apoapsis meets a circular orbital
catcher. It estimates launch speed, velocity mismatch at capture, launch errors,
rendezvous timing, downrange rise, and energy-based mass payoff.

It does not yet model a rotating sling. Treat the results below as a ballistic
catcher baseline, not a demonstration of tether feasibility.

## Reproducible baseline

Run `python3 lunar_slings/analysis/baseline.py` from the repository root.
The script uses the original notebook's radius (1,737 km) and lunar mass
(7.34767309 × 10²² kg), with G = 6.67430 × 10⁻¹¹ m³/(kg s²).
The 30 km case provides a comparison with the frozen-retreat topic, but is not an
exact reproduction of that study, which uses different lunar constants.

Assumptions: spherical Moon, two-body gravity, tangential impulsive launch,
circular catcher orbit, and no lunar rotation, terrain, or tether motion.

| Quantity | 30 km catcher | 100 km catcher |
| --- | ---: | ---: |
| Surface launch speed (m/s) | 1687.443 | 1703.610 |
| Tangential catch mismatch (m/s) | 7.147 | 23.020 |
| Launch-to-catch time (minutes) | 54.830 | 56.482 |
| Catcher lead at firing (km of orbital arc) | 70.536 | 234.009 |
| Apoapsis error from +1 m/s launch error (km) | 4.231 | 4.444 |
| Cross velocity from 0.1 degree error (m/s) | 2.895 | 2.811 |
| Direction error giving equal cross/mismatch speed (degrees) | 0.247 | 0.819 |
| Ideal launch kinetic energy (MJ/kg) | 1.424 | 1.451 |

The catcher lead is measured ahead of the launch site's radial line along the
catcher orbit at firing. Apoapsis error describes the perturbed orbit's maximum
radius; it is not a propagated miss distance at the scheduled capture time.
Cross velocity uses the local approximation that pointing error rotates the
arrival velocity vector; launch-direction errors require full trajectory
propagation to predict arrival position and time.

## What the calculations establish

- A higher catcher increases nominal capture mismatch: about 23.02 m/s at
  100 km versus 7.15 m/s at 30 km under these assumptions. Neither result
  establishes a required sling tip speed without specifying tether geometry.
- Launch-speed precision matters: a +1 m/s error shifts apoapsis by several
  kilometres in both cases. Capture tolerance must include timing and position,
  alongside velocity.
- Pointing error contributes transverse velocity. At 30 km, a 0.1 degree local
  velocity-direction error adds about 2.90 m/s, a substantial fraction of the
  nominal tangential mismatch. Capture needs a vector velocity budget.
- The launch kinetic energy is about 1.42–1.45 MJ/kg before driver losses.
  Energy cost alone does not determine throughput or system mass payoff.

## Findings in the original notebook

1. **Python compatibility:** Python 2 print syntax prevents execution as-is in
   Python 3. Preserve the original as a reference until a modernized notebook
   can be executed and compared with its saved outputs.
2. **Catch sign convention:** the notebook computes projectile minus catcher
   speed, yielding a negative tangential velocity. The table above reports
   catcher minus projectile, the positive mismatch magnitude for these cases.
3. **Shortcut trajectory:** the discussion of a more vertical launch is not
   followed by a propagated alternate trajectory. Its feasibility is unresolved.
4. **Energy/payoff scope:** the solar and battery calculations are energy-based
   estimates using historical selected values. They do not include a complete
   catcher/tether structure, capture loads, driver hardware, operational duty
   cycle, or momentum-restoration budget. Their payoff figures should not be
   interpreted as full-system performance predictions.
5. **Distinct design cases:** the original 100 km catcher and the frozen-retreat
   30 km catcher are separate assumptions, not interchangeable results.

## Rotating sling work to add here

Use this directory for subsequent derivations, scenarios, notebooks, and results.
Resolve the architecture first: a surface-mounted launcher sling, an orbital
rotating capture tether, or a combined catch-and-release system. The existing
notebook does not select one.

| Work item | Inputs and outputs needed |
| --- | --- |
| Geometry and kinematics | Orbit/site, tether length, spin rate, tip trajectory, surface clearance, capture/release phase, and vector tip-relative velocity. |
| Payload and capture | Payload mass, cadence, position/velocity tolerances, capture stroke and duration, peak force, and dissipated energy. |
| Structure | Material density and allowable stress, safety factor, taper, tether mass, payload ratio, and dynamic load cases. |
| Momentum and orbit | Changes in orbit and spin after each catch/release, plus restoration impulse, energy, and time per cycle. |
| Trajectory errors | Propagate launch speed, angle, timing, and spin-phase errors into miss distance and capture loads. |
| Operations and trade study | Terrain/clearance constraints, power and thermal budgets, cycle time, failure trajectories, and sensitivity to altitude, length, payload, and material. |

The baseline script verifies angular momentum, specific orbital energy,
agreement with the launch-speed formula, and recovery of the target apoapsis.
These are internal consistency checks of the ideal model, not validation of a
physical sling design.
