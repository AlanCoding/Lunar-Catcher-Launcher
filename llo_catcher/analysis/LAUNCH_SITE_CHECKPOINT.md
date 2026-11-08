# Equatorial LLO launch sites: completed study

**Closed at the agreed exploratory scope, 2026-11-04.**
[Repository guide](../../README.md) · [LLO guide](../README.md) · [Work queue](../../WORK_ITEMS.md)

## The question and the result

Where can a near-surface lunar launch clear the terrain, reach a low equatorial
catcher, and strike terrain away from the launcher if capture fails? Stop at
first terrain contact or **1.5 payload orbital periods**; surviving that cutoff
means “not arrested,” not a claim of permanent orbital survival.

The study progressed from equatorial release corridors to nearby hilltop hubs,
then checked eastward and opposite-tip westward trajectories at six selected
hubs. **The site search and requested follow-up are complete. These are terrain
candidates, not six validated launcher installations.**

- At 10 m release clearance, eight of 360 integer-longitude equatorial eastward
  launches reach the 25 km catcher; all eight hit terrain after a missed catch.
- Refining their neighborhoods gives **49 suitable release intervals totaling
  90.727 km**. The eight intervals connected to the original seeds total
  **22.604 km**. These lengths describe the searched neighborhoods, not a
  globally exhaustive fine-resolution survey.
- Fixed nominal hub latitudes fail the requested 10 m maximum terrain-rise
  screen within 5 km. Allowing a ±2 km latitude adjustment and climbing to
  nearby summits yields **six hilltop candidates**, four south and two north.
  A terrain-rise pass does not by itself establish cable or release clearance.
- Rechecking releases at the actual summit meridians leaves **S4 east** reaching
  the 25 km catcher and **S3 west** reaching the 35 km catcher under the declared
  independently targeted speeds. After a miss they impact **2,255.70 km** and
  **601.17 km** from their respective hubs. No hub passes both directions in
  this comparison.
- S3 west briefly re-enters the projected tether disk, remaining **4.98–5.08 m
  above the ideal tip plane**. This is not a resolved moving-cable contact test.

The westward comparison mirrors the east tip across the hub in the same plane;
its ground clearance follows from the terrain. It is an approximate counterpart
check, **not a simultaneous two-payload solution at a shared RPM**. The final
report documents that constraint and the alternative local-10-m west releases.

## Start with the final deliverables

| Document / data | What to use it for |
| --- | --- |
| [Terrain maps for the post](single_equatorial_release/summit_sites/maps/README.md) | Six 15 km summit maps, two 80 km context maps, track/tip overlays, saved impacts and links to longitude figures. |
| [Six-site east/west results](single_equatorial_release/summit_sites/missed_capture/README.md) | Final trajectory outcomes, impact coordinates, hub distances, sweep re-entry, assumptions and reproduction. |
| [Summit catalog](single_equatorial_release/summit_sites/README.md) | Hilltop selection, terrain checks and formal lunar coordinates. |
| [Numeric hub coordinates](single_equatorial_release/summit_sites/hub_coordinates.csv) | Strict floating-point latitude/longitude; positive north/east, signed longitude. No map-service links. |
| [East and local-clearance west data](single_equatorial_release/summit_sites/missed_capture/shots.csv) | Machine-readable impacts for those release assumptions. |
| [Same-plane opposite-tip west data](single_equatorial_release/summit_sites/missed_capture/opposite_tip.csv) | Primary westward comparison. |

## How the result was reached

Read these only as needed; their original figures and calculations are preserved.

| Step | Document and status |
| --- | --- |
| Terrain intuition | [Full equatorial elevation profile](single_equatorial_release/equatorial_elevation.png), explained in the [height-survey report](single_equatorial_release/README.md). |
| Initial single-release survey | [Height survey](single_equatorial_release/README.md): the global 50%-clearance approach was abandoned; results remain historical context. |
| Refined release locations | [Local corridors](single_equatorial_release/local_corridors/README.md): 10 m releases, interval lengths, and the 144° terrain/orbit overlay. |
| First installation screen | [Fixed-latitude hub footprints](single_equatorial_release/hub_footprints/README.md): null result that motivated movable summit hubs. |
| Final installation screen | [Movable summit catalog](single_equatorial_release/summit_sites/README.md), followed by the final east/west report above. |
| Orbital geometry side study | [Accepted heading optimum](heading_optimization/RESULT.md): offset release to a 25 km equatorial catcher; selected 141.557° launch-to-catch solution. [Spherical baseline](spherical_release/README.md) explains periapsis and height margins. |
| Earlier two-arm experiments | [Preserved demo figures](terrain/results/INITIAL_DEMO.md), [one-degree sweep](terrain/results/sweep_1deg/README.md), and [release-state audit](terrain/results/release_audit/README.md). These use earlier geometry and clearance assumptions. |
| Data and methods | [Terrain source/access](terrain/README.md); each analysis folder contains its code, assumptions, data tables and verification instructions. |

The calculations use a two-body trajectory model with lunar rotation and
SLDEM2015 terrain intersections. Terrain spacing is approximately 59 m at the
equator, with metre-scale vertical uncertainty. Numerical intersection precision
is not site-survey accuracy. This work does not establish detailed installation
clearance, capture control, or a fully coupled launcher design.

## What comes next

The new launcher priority is [conveyor-loop scalar screening followed by 2D
dynamics](../../sling_launcher/conveyor_loop/README.md). The earlier spool-based
[operations](../../sling_launcher/work_items/01_OPERATIONS_SIMULATION.md) and
[3D tether dynamics](../../sling_launcher/work_items/02_DYNAMIC_TETHERS.md) plans
are on hold at the user's request; neither has started. The comprehensive
[two-offset useful-payload terrain study](dual_offset_release/README.md) remains
deferred; the six-site westward check does not complete that separate design
problem. No further launch-site sweep is scheduled as part of this closed item.
