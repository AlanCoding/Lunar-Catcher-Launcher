# Development plan and repository assessment

Current status: the user approved the diagram architecture with a wheel-layout
correction and requested proceeding. Phase 4 orbit/cycle calculations and an
executed companion notebook are now provided in `orbit_cycle_review.md`.
Tether/structure/installed-power sizing and optimization remain pending.

## Inspection, 2026-10-31

Repository was clean before this work. No applicable AGENTS.md was found.
Read both notebooks' cells, Python modules, READMEs, dependency lists, and the
frozen-retreat prompt. The existing PNGs are preserved historical outputs.

- `lunar_slings/variations analysis ...ipynb`: Python 2, Astropy units,
  nominal 100 km catcher; launch errors, downrange geometry, historical
  solar/battery energy-payoff estimates. No wheeled rotating launcher model.
- `lunar_slings/analysis/baseline.py`: deterministic SI, standard library,
  two-body tangential surface-to-apoapsis transfer, checks on energy and angular
  momentum. Running it reproduces its documented 30/100 km results.
- `frozen_retreat/`: Python 3 helper modules, immutable Scenario, separate
  30/120 km orbital/catcher/EP/bridge budget. Runner executes successfully.
  Its notebook also duplicates assumptions and some runner calculations; do not
  replicate this duplication. Its 0.71 sunlight fraction is for that scenario,
  not this equatorial surface station. Its orbital-average ground power and
  EP budget cannot size a storage-free launcher.
- Existing requirements are broad, unpinned, and topic-specific. No existing
  dedicated test suite or packaging configuration was found.
- Existing lunar constants differ: original radius 1737 km and G times mass;
  frozen-retreat radius 1737.4 km and mu 4902.800 km^3/s^2. New constants need
  explicit sources and reference-surface definitions before numerical work.

## Phase boundaries

1. **Current:** separate directory, scope/configuration and accounting foundation,
   variable map, initial BOM, source and question registers. Review architecture,
   exclusions, and BOM before physical implementation.
   User clarification: main radial tie runs directly apex-to-apex; separate
   stabilizers meet a ground-level pivot. Slings remain extended; calculate
   droop to determine pole height with 3 m terrain clearance.
2. **BOM review:** confirm required subsystems and sizing/source strategy. Initial
   catalog is supplied now as requested; numerical masses remain unresolved.
3. **Mechanics derivation:** Matplotlib/SVG top view, radial and tangential
   free bodies, wheel contacts, apex/spool loads, whole-system balance. State
   force/moment equations and feasibility constraints, including elastic/slack
   tether behavior and loaded/unloaded/release cases. Stop for review before
   implementing these equations as the engineering solver.
4. **Orbit and operations:** independently derive release/intercept/countermass
   trajectories and terrain checks; distinguish orbit period and rotating-site
   revisit period. Establish complete climber cycle and sunlight-limited launch
   windows; report catcher encounter impulse and gravity-anomaly limitations.
   Limited calculation scripts/figures support this deliverable, without an
   optimizer. Stop for review before optimization.
5. **Model/notebook:** implement approved derivations, subsystem modules,
   configuration with provenance, feasible/infeasible reports, and conservation
   checks. Execute the notebook end-to-end with a recorded environment. Stop for
   physical-assumption review before proposing a final optimized design.
6. **Optimization:** logarithmic payload/acceleration sweeps, explicit constraint
   filtering and bounded optimization where justified. Distinguish interior
   optima from imposed bounds or monotone asymptotes. Deliver complete masses,
   margins, operations, and named geometry JSON; no Blender scene.

User approval is required at each boundary by the supplied task prompt. No
approval is inferred from silence. This is a proposed workflow, not approval
of any unverified physical premise.

## Planned small modules (not implemented)

`geometry.py`, `orbit.py`, `tethers.py`, `structure.py`, `contacts.py`,
`drives.py`, `climbers.py`, `cycle.py`, `power.py`, `feasibility.py`, and
`trade_study.py`, alongside existing `config.py` and `accounting.py`.
Use dataclasses for environment/material/design/control inputs and named outputs;
avoid hidden constants or mutable module-global scenarios. Notebook owns narrative
and figures, modules own calculations. Use plain SI with independent analytic
limit checks; add a unit library only if demonstrated useful.

Start with lumped bodies, axial/beam/buckling formulas and a 1D elastic tapered
tether, with distributed mass integrated along length. Use a few tether segments
if sag/lag makes a straight-tether bound inadequate. No continuum or finite-element
solver is planned. Unresolved instabilities stay feasibility conditions, not
precise mass predictions.

## Physical validation to implement after approval

- Rigid/symmetric, zero angular acceleration, zero radial travel, and massless
  tether limits; force and moment residuals in a declared reference frame.
- Energy/angular-momentum conservation for isolated cases; boundary work and
  released mass flux in driven/open cases. Physical rotational kinetic energy
  must be tracked, without assuming it is an available flywheel buffer.
- Nonnegative tension and wheel normal force; coupled lateral/longitudinal
  traction and rolling loss; structural stress and buckling margins.
- Tether elastic strain, climber speed/acceleration, sling/ground clearance.
- Independent orbital invariants, intercept state residuals, and integration
  convergence; launch site rotation and countermass terrain intersection.
- Instantaneous electrical demand never exceeds derated incident solar supply;
  no regenerative credit without a contemporaneous demonstrated power sink.
- Complete imported/local/expendable accounting and component power/energy
  reconciliation. Unresolved masses block a complete objective value.
