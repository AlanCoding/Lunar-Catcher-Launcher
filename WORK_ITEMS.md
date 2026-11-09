# Planned work after the sling publication

Updated 2026-11-08. **The equatorial launch-site study is closed at its agreed
exploratory scope**, including the six summit hubs and east/west impact checks.
Start with its [checkpoint](llo_catcher/analysis/LAUNCH_SITE_CHECKPOINT.md).
The spherical heading study is also complete. **Point-mass payout control is accepted; optimal control is deferred.
The first [steady conveyor stress/grip results](sling_launcher/conveyor_loop/steady/README.md) are available. The earlier spool-based operations and
3D tether-dynamics plans are on hold at the user’s request.** The comprehensive two-offset-payload terrain
branch remains deferred.

The [conveyor concept post](https://alanse.medium.com/conveyor-belt-lunar-mass-sling-7abc7bac7a05) and its
[four illustrations](sling_launcher/conveyor_loop/figures/README.md) are now
published (recorded 2026-11-06). Its first steady screen is complete; full scalar sizing and time dynamics remain planned.
The [Lunar Mass Launchers collection](https://alanse.medium.com/list/lunar-mass-launchers-9a765f4e596a) is the broader publication index.

The [published sling study](sling_launcher/publication/README.md) remains the
reference snapshot. New simulations must distinguish inherited assumptions
from tested operating limits and new results.

| Work item | Home | Sequence / dependency |
| --- | --- | --- |
| [Equatorial launch sites: closing checkpoint](llo_catcher/analysis/LAUNCH_SITE_CHECKPOINT.md) | LLO catcher / terrain | **Completed:** corridors, movable summit catalog and six-site east/west missed-capture follow-up. Terrain candidates are distinct from demonstrated launcher installations. |
| [Spherical-Moon release clearance](llo_catcher/work_items/SPHERICAL_MOON_RELEASE_CLEARANCE.md) | LLO catcher / orbital mechanics | **Completed at agreed scope:** [accepted reference-RPM heading optimum](llo_catcher/analysis/heading_optimization/RESULT.md); spherical clearance/height-margin baseline retained. Tower height remains conditional on tether drop. |
| [Local 10 m corridors](llo_catcher/analysis/single_equatorial_release/local_corridors/README.md) | LLO catcher / terrain | **Completed:** eight seed-connected intervals total 22.604 km; all 49 nearby intervals passing departure and return-impact criteria total 90.727 km. |
| [Single equatorial release](llo_catcher/analysis/single_equatorial_release/README.md) | LLO catcher / terrain | **Historical; further height-percentage surveying abandoned:** 360 sites; 50% outbound clearance at 2,310.7 m; 95 subsequent impacts and 85 unarrested through 1.5 orbits among 180 clear departures. |
| [Two offset useful releases](llo_catcher/analysis/dual_offset_release/README.md) | LLO catcher / terrain | **Deferred:** separate branch, preserving the historical two-arm survey and accepted spherical heading solution. |
| [Point-mass payout controls](sling_launcher/payout_control/README.md) | Sling launcher / prerequisite | **Accepted initial simulation; optimal control deferred:** four prescribed payout laws, slack/re-tension events, torque/energy histories and GIFs. No cable material dynamics. |
| [Spooled tether in 2D](sling_launcher/spooled_tether_2d/README.md) | Sling launcher / shared dynamics | **Initial model and snapshots:** distributed tapered Kevlar mass, elastic stress, extension/release/retraction and angular occupancy. Extension checked across meshes; late retraction and neighbor-safe control remain unresolved. |
| [Staged multi-tether spool bank](sling_launcher/staged_spool_bank/README.md) | Sling launcher / new variation | **Initial power curves complete:** single pair, exact T/15 phase sums and common-release readiness. Shared [2D tether results](sling_launcher/spooled_tether_2d/README.md) now available; neighbor clearance, controlled return, power scheduling and orbital batch targeting remain open. |
| [Conveyor versus tapered-spool material](sling_launcher/architecture_comparison/README.md) | Sling launcher / architecture comparison | **Initial screen complete:** matched throughput/speed/material, strength-sized tether masses, equal-mass stress comparison and feed/cadence/allowance sensitivities. Full-machine and delivered-flow comparisons remain open. |
| [Conveyor-loop scalar screening](sling_launcher/conveyor_loop/01_SCALAR_ANALYSIS.md) | Sling launcher / new conveyor concept | **Broader sizing still planned:** single-loop Zyling and two-stage Kevlar, material checks, mass flow, power and mass-payback periods. |
| [Conveyor-loop 2D dynamics](sling_launcher/conveyor_loop/02_PLANAR_DYNAMICS.md) | Sling launcher / new conveyor concept | **Steady screen complete:** [results](sling_launcher/conveyor_loop/steady/README.md), adjustable feed/payload density, stress and grip. Time dynamics and two-stage shared pulley remain planned; see the [one-arm plan](sling_launcher/conveyor_loop/03_SIMULATION_STACK.md). |
| [Time-stepped launcher operations](sling_launcher/work_items/01_OPERATIONS_SIMULATION.md) | Sling launcher | **On hold; not started:** use frozen design parameters as constraints; model batch loading, spinup, repeated launches, spindown and refill. Can start with a declared provisional terrain/catcher interface. |
| [3D segmented tether dynamics](sling_launcher/work_items/02_DYNAMIC_TETHERS.md) | Sling launcher | **On hold; not started:** follows the spool operations stage; replace quasi-static tether treatment while retaining its controls, inventory, energy accounting and event sequence. |

The terrain survey is for failed-shot clearance and targeting, **not mountain
height optimization**. The operations model is forward simulation of an existing
design, **not another mass optimization**. The dynamics extension resolves
motion and loads along tapered cables rather than prescribing their static shapes.

Record any required redesign separately; do not silently modify the frozen
50-g candidate to make a simulation succeed. The work items have deliverables
and completion criteria in their own documents. A [small SLDEM2015 extract and access probe](llo_catcher/analysis/terrain/README.md)
now demonstrate terrain access. The [initial 25/35 km catcher demo](llo_catcher/analysis/terrain/demo_results/README.md)
now solves release states and first terrain contact, with a strict 1.5-orbit
cutoff. The [one-degree equatorial sweep](llo_catcher/analysis/terrain/results/sweep_1deg/README.md)
is preserved as the historical two-arm comparison: three prograde and six retrograde departures clear, all nine
hit after missed capture, and no sampled longitude clears both directions.
No ephemeris run or launcher operations simulation has been completed.
