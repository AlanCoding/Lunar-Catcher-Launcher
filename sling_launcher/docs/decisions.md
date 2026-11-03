# Running assumptions, questions, and decisions

**Chronological history. Current decisions are at the end; the current numerical
authority is [CHECKPOINT.md](../CHECKPOINT.md), not the initial review gates below.**

2026-10-31: foundation created; Phase 1/BOM review pending. No approved geometry,
material allowable stress, contact coefficients, panel performance, or payload
scale has been selected.

## Established by the user prompt

- Preserve the architecture and historical results; use small Python modules
  and a notebook, no continuum analysis initially.
- Kevlar outward slings, two returning climbers, one useful payload at a time,
  separate expendable rock, four powered wheels, ordinary prepared road.
- No storage/buffer, no assumed braking recovery, peak direct solar sizing.
- User approval between phases. Current work stops before the physical solver.

## User clarifications, 2026-10-31

1. Slings stay extended during each launch cycle; climbers travel along them.
   Do not introduce cyclic full-length payout/retraction. Spools retain their
   management/holding role, subject to later load definition.
2. Use approximately local-horizontal rotation and eastward useful/westward rock
   release as the initial geometry.
3. Corrected load path: a main tether connects the two apexes directly across
   the circle. It transfers the principal opposing outward sling loads between
   assemblies. It is distinct from two small stabilizing stays running from
   the apexes to the ground-level central pivot. The pivot is not the intended
   primary radial reaction structure, and its height is not a design variable.
   Low stabilizer force is the design intent, to be tested in force/moment
   equations, including asymmetric, accelerating and release load cases.
4. Pole/apex height follows calculated rotating-sling droop plus 3 m clearance,
   rather than being a freely selected independent dimension. Include loaded,
   unloaded and moving-climber states, and transients where material. Faster
   rotation may reduce droop; compute the coupled load/geometry rather than
   presuming a universal trend. Check lunar curvature and terrain explicitly.

These clarify architecture; they do not constitute blanket approval of the
initial BOM or subsequent engineering-model implementation.

## Diagram review deliverable, 2026-10-31

At the user's request, created `force_diagram_review.md` with six embedded,
editable SVG diagrams, equation cross-references, and a complete B01–B23 parts
key. The user will review this document before numerical Python development.
SVG generation uses Python only for drawing; it performs no engineering sizing.
Rendered all six drawings for visual inspection and verified their embedded
paths, SVG XML, and unique parts IDs. No numerical model or optimized design
has been developed during this step.

## Diagram review approved and numerical phase begun, 2026-10-31

User approved the rest of the force-diagram document and instructed a small
wheel drawing correction, then proceeding to the next phase. One frame means
one A structure/two poles; each pole has a powered and passive fore/aft wheel.
Total machine: four powered and four passive wheels. Passive wheels are drawn
ahead illustratively; their detailed traction and contact-load sharing are
omitted per user instruction. Aggregate traction remains a feasibility issue.

Implemented the next orbital/operations phase as reviewed-equation calculations,
with an executed companion notebook, test suite and generated results. The
finite horizontal-sling tip cannot use the point-equatorial apoapsis intercept
without addressing its orbital-plane offset. An exact eastward first-node
branch is provided. Equal-radius opposite rock release does not impact the
reference sphere in the illustrative cases; shorter-side geometry is a separate
sensitivity requiring review and balance calculation.

Cadence, sunlight and direct-drive power are conditional/idealized bounds, not
an achieved complete cycle. Phase restoration, cable droop and elasticity,
structure, actual climber drive and installed solar sizing remain pending.
No mass optimization has begun. Next review: `orbit_cycle_review.md`.

## Further issues for the phase reviews

- Are useful payload and rock releases simultaneous? Initially propose this as
  the balanced case, with timing errors and individual release as load cases.
- How much sling retraction is allowed during darkness? Continuous operation
  applies during illuminated launches, not an unsupported claim of operation
  through lunar night. Include startup/shutdown as separate operational events.
- What range of payload sizes, minimum throughput, and service life should bound
  optimization? No mandatory numerical choice is needed for repository setup.
- Which site services already supply rock loading/handling, and which permanent
  imported hardware must the launcher carry? Loading interface remains excluded.
- Are radial leg spacing/support width and extra bracing permitted when necessary
  for three-dimensional stability? Do not quietly assume a two-dimensional
  free-body diagram establishes lateral stability.
- Does a tapered tether permit the chosen climber grip and motion without damage?
  Can selected cable survive spool bends, cycles, dust, vacuum and UV? Yarn
  tensile data alone cannot establish this.
- A release westward is not itself proof of impact. Propagate its state and
  intersect actual/reference terrain; do not invent a disposal trajectory.
- Acceleration tolerance must include radial, tangential and climber-motion
  contributions, and specify whether it is proper acceleration or coordinate
  acceleration. Payload stress follows applied force, not gravity alone.
- A maximum one catch per orbit is an operational upper target; the site-relative
  pass interval and available release phases require a separate calculation.

## Feasibility status

No design has been demonstrated feasible. Pending checks include the direct
apex-to-apex tie and stabilizer load paths, wheel contact and lateral traction,
terrain clearance and derived pole height, stable
unloaded slings, release transients, cable life, peak power, and 20 km catcher
orbit sustainability. Report bounds where data are missing rather than precise
invented hardware masses.

## User concern about climber mass and outward energy, 2026-10-31

User noted that climber mass is unspecified and outward motion can generate
radial-drive power. The previous 10 kg value was an unsized sensitivity, not
a design result. The total constant-spin electrical headline obscured the
wheel-input/radial-output split. Revised the primary comparison to the
zero-climber-mass limit and added explicit mass-ratio sensitivities and
channel-separated powers. Constant spin is not a user requirement. Added
and tested the variable-spin work/energy identity; actual inertia and control
history remain to be solved. The revised suite passes 15 tests.

User raised spooling as a possible alternative, not an instruction to replace
the architecture. Documented how payout relocates radial energy extraction
without eliminating the angular-momentum/energy balance. Neither electrical
recovery nor spooling has been adopted as a demonstrated design.

## Timed spooling and ballast correction

User challenged the missing cable retraction energy and traction sizing. Added
a reduced-order cable-inventory payout/return model with time histories, phase
closure, simultaneous recovery and local ballast. Old payload-only solar and
end-state pole estimates are superseded for payout-machine use. Results and
limitations are in spooling_cycle_review.md. User authorization covers further
cycle, structural and mass optimization work; no new permission gate is added.


## Speed-constrained scenario consolidation, 2026-10-31

User fixed track radius as a dependent variable: R = rover operating speed /
release angular speed. Compare 50 and 80 mph, reach down to 4 Earth g, report
representative accelerations and clarify the former maximum-acceleration claim.
The former fixed-50-m speed cutoff is not a universal physical maximum.

Implemented finite-angle cable shapes and generalized cable-inventory energy
integrals, with height/release speed iterated against orbital interception.
The 44-case catalogue includes high-g geometric rejection diagnostics. Loading
remains 300 s; phase correction slows below cruise without changing release
speed or using track radius as an independent choice. The current branch uses
spooling in place of climbers, as authorized in the earlier numerical request.

Buildability review exposes compact-frame radial moment closure, failed 4-g
45-degree footprint geometry, release-shape recoil and equal-radius countermass
nonimpact. The catalogue distinguishes conditional demands from demonstrated
feasibility. Pole and full imported masses remain null; no complete optimum
is invented. User requested consolidating all work and committing it to git.
