# Stage 1: scalar conveyor-loop screening

Status: **Next proposed analysis; not started.**
[Concept and stage map](README.md) · [Next: planar dynamics](02_PLANAR_DYNAMICS.md)

## Objective

Get preliminary mass flows and payback periods for the single-loop and staged
loop concepts before investing in dynamics. Use scalar balances and radial
integrals where needed; no continuum simulation is required. Distinguish a
self-loading material screen from a loaded machine estimate.

## Inputs versus derived quantities

Build an explicit variable dictionary with units and provenance before scanning.

| Independent inputs or scenario choices | Dependent quantities / constraints |
| --- | --- |
| Target release speed and either Ω or target centrifugal acceleration a | R = v/Ω; a = Ω²R. Do not vary v, Ω, R and a independently. Specify inertial versus surface-relative speed; catcher geometry supplies the actual required release vector. |
| Rover operating speed, initially 50 mph as the comparison case | Track radius = rover speed / Ω; retain the prior dependent-track-radius convention. |
| Loading radius r₀, stage split, loop areas, material and working-strength deratings | Strand tensions/stresses, line mass and strength margin; areas may be solved or scanned, with the choice stated. |
| Feed speed u, payload mass m and spacing s, or equivalent attachment cadence f | f = u/s; mass flow = mf; transit time ≈ (R−r₀)/u; mean in-flight count ≈ f(R−r₀)/u under straight steady feed. Discrete counts vary during loading/release. |
| Countermass schedule and masses | Opposing radial loads, carried inventories and torque balance; unequal radii require explicit balance, not equal masses by default. |
| Wheel sizes, assemblies and handling allowances; drive efficiency and recovery fraction | Imported mass, local rock demand, wheel torque/speed, bending requirements, electrical power and heat. |
| Catcher windows, loading capacity, availability and capture success scenario | Accepted delivery rate and calendar payoff; nominal conveyor capacity is only an upper bound. |

For two loops, state each loop's feed speed and wheel radius. Equal line speeds
do not imply equal wheel RPM. Specify transfer timing and whether intermediate
buffer inventory is permitted. Do not assume both loops are driven by one rigid
coaxial wheel without checking speed compatibility.

## Calculation sequence

1. **Audit the handoff.** Derive the uniform-strand self-stress and two-stage
   tension balance, counting both strands and end assemblies explicitly.
   Reproduce or correct 1.394/0.761 MJ/kg, 6:1 and 0.674R; record assumptions.
   Source realistic material data and working allowances, including bend effects.
2. **Add loads.** Include discrete payloads, returned fixtures, turnaround and
   intermediate masses. Enforce nonnegative tension and force balance at each
   assembly. Determine which strand supports each load; equal sharing is an
   assumption to test. Include line-curvature/transport terms where the straight
   approximation omits them. Do not apply the isolated-strand formula to the
   full loop without a free-body balance.
3. **Inventory and throughput.** Sweep u, spacing/cadence, payload mass and stage
   split. At fixed cadence, slower feed raises carried inventory and radial
   loading. At fixed spacing, slowing feed instead lowers throughput; distinguish
   these experiments. Check release phase and catcher window compatibility.
4. **Torque and energy.** In the straight radial, constant-Ω idealization,
   ΔL = mΩ(R²−r₀²), main-drive work = mΩ²(R²−r₀²), ideal feed-brake recovery =
   ½mΩ²(R²−r₀²), and net work = ½mΩ²(R²−r₀²). Audit these balances for the
   full circulating line and attachments, loading/release kinetic energy,
   wheels and counterstream. At steady cadence, use fΔL for the payload's
   mean drive torque contribution, not the complete machine torque.
   Report gross wheel demand, brake output, net electrical demand and heat
   separately for zero, partial and ideal recovery. State whether recovered
   power can be used when generated. Evaluate 2Ωu as a lateral acceleration
   diagnostic; the associated deflection is for Stage 2.
5. **Machine mass and payoff.** Estimate both strands of every loop, all
   turnarounds, transfer/attachment hardware, drives, structures, power and
   thermal equipment. Reuse sourced component curves only where applicable;
   mark extrapolations and unknown allowances. Separate imported equipment,
   locally sourced ballast, consumed counterweight and carried useful payload.
   Compare consistently with the published spool baseline.

## Grip and other failure criteria

**Line slippage is a primary metric alongside tensile failure.** Outward payload
motion can drive substantial regenerative braking; the wheel must transmit the
required tension difference and torque without the Kevlar/Zylon line sliding.
Energy flow alone does not determine slip: calculate loaded/return tensions,
wheel radius, contact/wrap angle, normal loading and friction limits at the
actual line speed. Distinguish line/wheel slip from rover/ground slip.

- Report required versus available traction, a grip margin, limiting brake
  torque and the feed/throughput boundary where no-slip operation fails.
  Use sourced or explicitly provisional friction ranges; do not assume a
  generic wheel grips either material sufficiently in lunar conditions.
- Compare a simple pulley, increased wrap/multiple turns, and an adjacent
  tension-holding or traction device. Account for extra mass, routing, contact
  pressure, bending, heat, wear and passage of attachments. Multiple wraps
  are a candidate remedy, not an already solved payload-routing mechanism.
- Track breaking/stress margin, bend/fatigue limits, contact crushing or abrasion,
  attachment holding capacity, slack/loss of contact, drive/brake power and
  thermal limits. Geometry/stability and release transients feed into Stage 2.

## Payoff definitions and outputs

Use **mass payback**, not an unspecified financial return:

- Equivalent delivered payload count = imported machine mass / useful mass per
  captured payload; this is a gross mass-equivalence metric, not economic profit.
- Operating-time payback = imported mass / accepted useful mass-flow rate.
- Calendar-time payback includes launch-window limits, illumination, availability,
  refill downtime and capture success. Show replacement/imported-consumable
  demand separately; only define net payback if the net delivery rate is positive.
- Report any energy-payback metric separately with its energy investment defined.

Deliver a reproducible Python calculation or notebook, input/source table,
mass composition, throughput/power/payback plots and a concise candidate table.
Use sensitivity ranges for unknown hardware and losses. Show infeasible regions
rather than allowing negative margins or omitting critical masses. Verify units,
energy/angular-momentum balances and limiting cases. Select a small set of
explicit input snapshots for Stage 2; do not call a scalar optimum a validated
working machine.
