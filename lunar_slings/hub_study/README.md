# Wheeled Kevlar lunar sling hub study

Start with the **[current engineering checkpoint](CHECKPOINT.md)**, then the
[44-scenario catalogue and graphs](results/speed_constrained/README.md).
The latest model uses spooling, finite-angle cable shapes, cable-inventory
energy integrals, timed return, traction ballast and direct solar sizing.
No complete buildable launcher or full imported mass optimum is established.

Two opposing A-frames carry four powered and four passive wheels in total.
The main apex-to-apex tie transmits opposing radial loads; separate stays run
to a ground-level central pivot. Their intended small loads remain to be
verified against radial frame moments. One useful payload and one rock
countermass are loaded per cycle. Solar provides direct power without storage.

## Current parameterization

- Scenario inputs: 50 / 80 mph rover speed, payload release acceleration,
  one / two catcher passes, payload mass, stated material/traction/power assumptions.
- Derived: angular speed, **track radius**, release radius, cable length/taper,
  quasi-static pole height plus 3 m clearance, ballast and power time histories.
- Cruise and release use the specified rover speed. Loading/buffer slowdowns
  close phase while staying below it.
- Objective: permanent imported launcher mass per successfully captured payload.
  Local ballast and expendable rock are separate. Unknown component masses are
  unset, not zero; partial mass sums are not the objective's completed value.

## Current deliverables

- [Checkpoint](CHECKPOINT.md): representative numbers and buildability findings.
- [Scenario catalogue](results/speed_constrained/README.md): 44 detailed records,
  geometry and power SVG/PNG plots, JSON metrics, sampled CSV time histories.
- [Method](results/speed_constrained/METHOD.md): equations, free/dependent variables,
  time allocation, phase, assumptions, acceleration bounds and unresolved loads.
- [Complete JSON](results/speed_constrained/all_scenarios.json) and
  [source/version manifest](results/speed_constrained/manifest.json).
- `cable_shape.py`: finite-angle quasi-static cable shape and total-stress taper.
- `scenario_study.py`: shape-dependent inventory, power, ballast and orbit coupling.
- `scenario_report.py`: reproducible detailed reports and scientific figures.

## Preserved supporting work

- [Reviewed force diagrams and named BOM parts](docs/force_diagram_review.md).
- [Orbital/climber review](docs/orbit_cycle_review.md) and
  [executed orbital notebook](notebooks/02_orbit_cycle_feasibility.ipynb).
- [Radial energy clarification](docs/radial_energy_review.md).
- [Initial BOM](docs/bom.md), [source register](docs/sources.md),
  [decision history](docs/decisions.md), and [original plan](docs/plan.md).
- `mass_screen.py` and `spooling_cycle.py` preserve historical screens. Their
  fixed-radius numerical outputs are superseded for the current scenario study.
- `orbit.py`, `environment.py`, `accounting.py` retain shared physical/accounting
  foundations. `config.py` and `cycle.py` describe the earlier climber branch.

## Reproduce

From the repository root, using the isolated numerical environment:

```bash
MPLCONFIGDIR=/tmp/lunar-sling-mpl-cache .env/hub/bin/python -m lunar_slings.hub_study.scenario_study
.env/hub/bin/python -m unittest discover -s lunar_slings/hub_study/tests -v
```

Set up a fresh environment with Python 3.12 and `requirements-lock.txt` if needed:

```bash
python3.12 -m venv .env/hub
.env/hub/bin/python -m pip install -r lunar_slings/hub_study/requirements-lock.txt
```

Use SI internally; Earth-g is an input/display convention. The report manifest
records the actual Python/NumPy/SciPy/Matplotlib versions and source hashes.
See `notebooks/README.md` for the earlier orbital notebook's kernel setup.
Historical notebooks, plots and the separate `frozen_retreat/` work are unchanged.
