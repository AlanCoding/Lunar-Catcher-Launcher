# Stage 1: time-stepped launcher operations

Status: **Next launcher work item; planned, not started**. Captured 2026-11-03.
[Work-item index](../../WORK_ITEMS.md) · [Frozen reference](../publication/candidate_50g.json)

## Objective and boundary

Describe the daily work of the 50-g launcher: prepare payloads, carry a batch,
spin up, launch repeatedly, spin down, stop and refill. Turn the design study's
parameters into constraints for a forward, time-stepped operations simulation.
Do not prescribe a successful cycle and infer whatever power/force it needs
without checking against installed hardware.

Use an explicit simulated duration and sunlight schedule: distinguish Earth
hours, a lunar daylight operating period and individual catcher revisits.
Start with a reduced-order/quasi-static tether model and state where it ceases
to be valid; [Stage 2](02_DYNAMIC_TETHERS.md) adds segmented 3D dynamics.

## Freeze the design; identify controls and states

Create a versioned input snapshot from the reference candidate and documented
assumptions. Classify every item as fixed hardware, actuator/control input,
environment/mission input, simulated state, or derived output.

| Category | Required quantities / treatment |
| --- | --- |
| Fixed design | Track radius, pole geometry, wheels, installed motor/gearbox/inverter allowances, rope length/taper, reel dimensions, ballast, solar and heat-rejection equipment. No resizing during a run. |
| Limits needing interpretation | Motor torque-speed/power envelopes, reel speed and braking limits, traction, stress, clearances and thermal rejection. A sizing allowance or peak rating is not automatically a validated operating curve. Flag missing data. |
| Wheel control | Drive/brake torque commands, or a speed controller commanding torque; speed is an evolving state. Do not independently prescribe incompatible torque and speed histories. |
| Reel control | Separate payout/retraction/braking control per outward line; line-speed or tension targets implemented through bounded actuator torque. Do not independently prescribe position, speed and tension. |
| Events / supervisory control | Cargo and countermass loading/transfer, release authorization and phase, missed-window response, batching, refill stops, shutdown and restart. |
| States | Rotation angle/rate, deployed cable length/rate, payload positions, spool rotation/inertia, inventories, carried mass and its location, accumulated electrical/thermal energy. |
| External inputs | Catcher windows/state, lunar environment, sunlight and terrain/clearance constraints; use a declared provisional interface until the LLO survey is available. |

Preserve force paths: the upper static tie closes opposing payload radial loads;
the low connection turns the rover assemblies; wheel-ground traction supplies
tangential drive. Account explicitly for asymmetry and residual support loads.
The two outward reel systems are the only payout devices; cross-ties stay fixed.
The illustrated single-reel layout and numerical capstan/storage allowance still
need reconciliation, per [reel assumptions](../publication/REEL_ASSUMPTIONS.md).

## Operational sequence to implement

1. **Stopped preparation/refill:** stage ready-to-launch cargo and rock batches,
   load both frames, establish balanced inventory and a stowed/retracted state.
2. **Spinup:** accelerate within wheel traction, torque and electrical limits;
   coordinate cable deployment and tension as speed rises. Determine which
   deployment sequence preserves clearance instead of assuming it does.
3. **Repeated launches:** transfer the next cargo/countermass pair to its line,
   deploy, meet the catcher window, release, retract and reset. Simulate changes
   in inventory, inertia and balance after every pair. Determine how slowly
   rotation must run for each transfer and whether a stop is needed.
4. **Spindown:** coordinate retraction and braking, including recovery or dump
   loads. Demonstrate that dropping rotation does not leave unsupported extended
   cables sweeping the ground. Do not extend a steady-spin droop solution to rest.
5. **Full stop and refill:** make the periodic batch-reload stop explicit,
   quantify its time and throughput cost, then simulate restart.
6. **Exceptions:** define missed catch windows, interrupted loading, inadequate
   sunlight/power, and controlled stop/abort behavior as distinct outcomes.

The existing 110.56-minute revisit, five-minute loading allowance, five-minute
buffer and roughly 50.28-minute payout/return are comparison targets, not timings
that the new simulator must force. Separate per-shot transfer from full-batch
refill; the earlier loading allowance does not establish either mechanism.

## Inventory, power and energy accounting

- Quantify batch capacity in payload pairs and tonnes, both staged on the ground
  and carried on the rotating frames. Locate every carried mass. Determine
  whether stock replaces ballast or adds load; do not count it twice or assume
  capacity without container/transfer geometry and load limits.
- Report cargo, consumable rock, empty containers/fixtures, ballast and handling
  equipment separately. Unspecified loading/transfer machinery needs an explicit
  assumption and sensitivity; it cannot be treated as a proven zero-mass device.
- Plot signed instantaneous **power** versus time with distinct colors for
  wheels, reels and auxiliary/handling consumers; show recovered power separately,
  plus solar supply, bus balance, any unmet demand and braking/dump heat.
- Also plot cumulative **energy** per consumer and total cycle/day energy. Keep
  mechanical work, electrical draw/recovery and heat separate, with losses
  counted once. Recovery offsets demand only when it can actually be used.
- Retain the reference's no-nighttime-storage assumption unless a new scenario
  explicitly adds storage capacity, mass and charge/discharge constraints.
- Integrate rotation and reel states through start/stop, accounting for deployed
  and wound cable mass/inertia. Resolve power/torque/speed peaks, traction and
  ground clearance throughout, not just at release.

## Deliverables and acceptance criteria

- A control/state/constraint dictionary and forward simulator with event logs,
  time-step convergence checks, mass/inventory conservation, and energy balance.
- A complete operations map covering multiple launches and at least one full
  batch exhaustion, stop, refill and restart; quantify delivered mass per cycle
  and operating day, waiting time, refill cadence and capacity bottlenecks.
- Colored full-cycle and multi-cycle power plots; cumulative energy, speed,
  deployment, tension, inventory and constraint-margin histories.
- Specific pictures or short animations of stopped, spinup, deployment, release,
  retraction and spindown states, including spool/rope routing and clearance.
- A feasibility report distinguishing demonstrated operating sequences from
  missing machinery data and violations of the frozen design. Propose any
  needed redesign separately rather than silently relaxing limits.

The [LLO terrain/failed-shot work](../../llo_catcher/work_items/EQUATOR_TERRAIN_AND_FAILED_SHOTS.md)
provides targeting and exclusion constraints. Implementation can start with a
clearly labeled provisional spherical environment without claiming terrain safety.
