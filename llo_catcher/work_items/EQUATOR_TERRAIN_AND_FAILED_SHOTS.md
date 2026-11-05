# Equatorial terrain, targeting and failed-shot survey

Status: **Closed at the agreed exploratory scope, 2026-11-04.**
The [closing checkpoint and reading guide](../analysis/LAUNCH_SITE_CHECKPOINT.md)
links the final six-site catalog, east/west impact checks and all supporting
results. The comprehensive paired-release branch remains deferred.

## Preserved scope and progression

The study was split into two sub-analyses; the notes below record its earlier
scope and assumptions, not a request to resume the completed survey.

1. [Single equatorial useful release](../analysis/single_equatorial_release/README.md):
   global height-percentage survey closed at user request, with results preserved.
   The [local fixed-10-m corridor follow-up](../analysis/single_equatorial_release/local_corridors/README.md)
   now gives refined longitude intervals and summed lengths. The historical study includes
   the requested 10 m comparison and the height for 50% of longitudes to clear.
2. [Two offset useful releases](../analysis/dual_offset_release/README.md):
   deferred. The notes below retain the original paired-study scope; do not
   treat its historical 3 m due-east/west cases as the new single-point result.

The [spherical-Moon geometry study](../analysis/heading_optimization/RESULT.md)
is complete. Historical demo and sweep outputs remain preserved.

[One-degree sweep](../analysis/terrain/results/sweep_1deg/README.md): three
prograde and six retrograde departures clear; all nine hit terrain after missed
capture within 1.5 orbits. No sampled longitude clears both directions. Finer
site sampling or changed assumptions await review of these results.
[Preserved first-demo graphs](../analysis/terrain/results/INITIAL_DEMO.md).

[Initial demo results](../analysis/terrain/demo_results/README.md): solved two-arm
release states and catch speeds; all eight sampled longitudes had outbound
terrain collisions, so none yet meets the paired missed-capture arrest objective.
[Terrain access and frame conventions](../analysis/terrain/README.md).

Topic: LLO catcher orbit and surface-to-orbit delivery, separate from launcher
hardware design. [Work-item index](../../WORK_ITEMS.md).

## Objective

Survey lunar equatorial elevations and propagate nominal and failed launches
against the terrain. Determine where failed shots return or impact, whether they
can threaten the installation, and what this implies for targeting a catcher.
The goal is **avoiding the Newton's-cannonball return problem**, not choosing a
mountaintop to minimize launch energy or maximize altitude.

## Capped task and selected demo inputs (2026-11-03)

**Objective:** find a launcher longitude where both nominal payloads can reach
their catchers and, if capture fails, both hit terrain within **1.5 of their own
payload orbital periods**. Stop each trajectory at its first impact or this
cutoff. Classify an uninterrupted 1.5-orbit trajectory as **not arrested**; do
not investigate its later fate here. Distinguish outbound collisions from
post-missed-capture impacts: a blocked departure is not a suitable launch site.
Launch-error sweeps, station collision avoidance, ejecta and broader risk analyses
are deferred beyond this task.

Inputs are the **two circular catcher altitudes and a common sling RPM**. The
first demo assigns **25 km prograde / 35 km retrograde**, relative to the DEM's
1,737.4 km reference sphere, and **2.7796279 RPM**. These are explicit adjustable
choices; the 25/35 km direction assignment is a demo interpretation. Solve each
arm's horizontal radius from the required first equator-node intercept, retaining
the actual north/south-offset geometry. The prior 5.787 km radius is a reference,
not a simultaneous fixed constraint. Small changes in acceleration are reported.

Each release is **3 m above local terrain**, an explicit design constraint.
Both payloads are released horizontally east/west with zero payout velocity in
the initial model. Do not substitute apex height or the old rendered clearance.
Report the full **relative capture velocity**, including radial and out-of-plane
components, rather than just the difference between speed magnitudes.

Unequal masses are allowed. With payload-only force balance the shorter arm can
carry the heavier payload; a final loading ratio must also include cable and
support loads. Mass itself does not change a given ballistic release trajectory.
The initial demo solves release states, not a rebuilt asymmetric launcher.

The eight initial longitudes are 0, 45, 90, 135, 180, 225, 270 and 315 degrees E.
This is a demonstration, not an exhaustive site search. The later expanded
longitude sweep retains the same crisp cutoff and two successful-departure
requirement. Preserve the published 50-g snapshot as a separate prior result.

## Bidirectional useful-payload scenario

Include an **equatorial sling delivering useful payloads in both directions**:
prograde to one catcher and retrograde to another. Both catcher stations may
occupy **circular equatorial orbits at different altitudes**. Assume adequate
active station control and launch coordination for nominal operation, and state
that assumption explicitly. The primary question here is: **under that assumed
control, where do the failed shots go?** Designing the stations' control systems
is outside this work item's scope.

Treat prograde payload mass, retrograde payload mass, and the two circular
catcher altitudes as separate scenario inputs. Unequal payload masses are
allowed; equal-mass, equal-radius rock disposal is not the governing assumption
for this new branch. Preserve that published launcher case as a comparison.

Determine compatible release states for each altitude and direction rather
than assuming unequal masses alone create different trajectories. Payload mass
affects sling balance and controlled release dynamics; the subsequent ballistic
trajectory is determined by release position and velocity in the gravity model.
Record each arm's deployed length, release phase, velocity and payload mass,
and the common launcher rotation state. Establish which combinations are
compatible with the specified asymmetric loading and active control; do not
silently require the published symmetric launcher to realize every case.

Include catcher phases and the intersection of their launch/capture windows:
different target altitudes need not yield matching revisit or flight times.
Evaluate simultaneous paired releases and, if needed, explicitly declared
separate-release schedules. Keep these alternatives distinct.

For the primary failed-shot calculation, assume no successful capture and no
post-release payload correction unless a separate scenario specifies it. Active
catcher control is not a guarantee that a missed payload is recovered or removed.
For this capped task, propagate each missed payload against terrain only,
through at most 1.5 periods. Approaches to the other station are a deferred
question; different nominal altitudes are not a collision-avoidance proof.

## Questions and scope

- What are elevation and terrain clearance versus longitude along the equator?
  Survey a latitude band as well, with its width justified by trajectory results,
  rather than assuming every nominal or failed shot stays exactly on that line.
- Where and when do under-speed, over-speed, pointing-error and timing-error
  shots first intersect terrain? Include missed capture after an otherwise
  nominal launch. Report trajectories with no impact during the integration
  horizon as unresolved/remaining aloft, not as safe landings.
- For this initial scope, where is first contact and does it occur before or
  after nominal capture? Wider installation-exclusion and station-risk metrics
  are deferred; do not extend propagation past the 1.5-orbit cutoff.
- How do launch epoch, lunar rotation/orientation, equator definition, catcher
  orbital plane and their relative orientation affect targeting and return?
  Make the user's question about lunar tilt explicit; do not assume a return
  to the launch latitude or longitude, or add an arbitrary 'tilt correction.'
- Distinguish the center's equatorial location from the actual sling release
  position and velocity. In the bidirectional branch, distinguish useful
  prograde cargo, useful retrograde cargo and failures of either. Retain the
  published westward rock-disposal trajectory only as a separate comparison.

## Proposed workflow

1. Select and cite a lunar elevation dataset, reference surface, coordinates,
   resolution, coverage and uncertainty. Record data provenance and download
   instructions; start with equator profiles and an adjacent terrain corridor.
2. Define compatible Moon-fixed and inertial frames, epoch/time standard, lunar
   orientation model and both circular catcher states, including their altitudes,
   directions and controlled phases. Select authoritative ephemerides and
   gravity data during implementation, with versions and assumptions recorded.
3. Establish spherical two-body regression cases, then add rotating coordinates,
   terrain intersection and the chosen orientation model. Assess nonspherical
   gravity and other perturbations over the relevant flight/return horizon;
   state which effects are included and which need sensitivity checks.
4. For the next sweep, propagate nominal release states over hub longitude
   for the stated catcher-altitude pair and RPM. Record first terrain contact
   time, coordinates, speed and whether intended capture was reachable. Stop
   at contact or 1.5 periods. Defer launch-error and broader parameter sweeps.
5. Compare sites/corridors by failed-shot clearance and targeting constraints.
   Do not reduce site selection to elevation ranking or infer that one nominal
   impact point establishes clearance for the error envelope.

## Deliverables and completion criteria

- Reproducible Python notebook/scripts, dataset/coordinate provenance, equatorial
  elevation plots, latitude-band maps and launch/impact/return overlays.
- A scenario table defining the error envelope and propagation horizon, with
  nominal interception and failure outcomes kept separate. Label direction,
  payload mass, both catcher altitudes, release state, station-control assumption
  and release schedule; show prograde and retrograde impact corridors separately.
- A clear answer to whether the modeled return paths threaten the selected
  installation footprint, with uncertainty and unmodeled effects visible.
- A machine-readable interface for operations: frame/epoch, site and release
  state and mass per arm, both catcher states/windows, terrain query and
  exclusion geometry. Clearly distinguish feasible release-state inputs from
  asymmetric sling-control combinations still requiring validation.
- Numerical convergence checks for trajectory and terrain intersection, plus
  recovery of the spherical reference cases. No claim that all failures are
  cleared until the declared envelope has actually been evaluated.

This is a survey/trajectory work item, not a terrain calculation already done.
The existing [ballistic baseline](../analysis/README.md) is a starting comparison;
the [operations plan](../../sling_launcher/work_items/01_OPERATIONS_SIMULATION.md)
will consume its results as they become available.
