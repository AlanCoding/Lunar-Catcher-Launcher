# Wheeled Kevlar lunar sling hub study

**For publication, start here:** [current checkpoint and chart index](publication/README.md).
The [checkpoint](publication/CHECKPOINT.md) gives the selected design and pie charts;
[mass payoff](publication/MASS_PAYOFF.md) gives launch counts and calendar scenarios.
[Blender scene and renders](blender/README.md) illustrate the frozen 50-g case.

**Current reference: [50 mph, one pass, separate upper and low ties](results/split_tie/README.md).**
The low tie is included below the approximately 616 m road-grip radius; the
previous upper-only tipping screen is superseded. The revised reference
imported-mass minimum is sampled at 50 g.

The earlier **[hardware-inclusive mass study](results/hardware_mass/README.md)**:
all four legs, eight wheels, wheel/reel motors and gearing, thermal hardware,
source-based component curves, coupled ballast, and 300 scenario estimates.
Its upper-only force path and 70–75 g minima are preserved for comparison;
the separate-tie study above is the selected design.

The [earlier engineering checkpoint](CHECKPOINT.md) and
[44-scenario catalogue](results/speed_constrained/README.md) preserve the
underlying spooling/cable/trajectory analysis. The earlier
[subtotal-only mass-ratio analysis](results/mass_ratio_trade/README.md) is
superseded for hardware mass estimates by the new study.

Two opposing A-frames carry four powered and four passive wheels in total.
The main apex-to-apex tie transmits opposing radial loads; separate stays run
to a ground-level central pivot. The separate low tie carries the lower assembly's radial turning loads on small tracks. One useful payload and one rock
countermass are loaded per cycle. Solar provides direct power without storage.

## Current parameterization

- Scenario inputs: 50 / 80 mph rover speed, payload release acceleration,
  one / two catcher passes, payload mass, stated material/traction/power assumptions.
- Derived: angular speed, **track radius**, release radius, cable length/taper,
  cable clearance plus 3 m margin, hardware-limited apex height, four leg sections,
  wheel/drive sizes, ballast and power time histories.
- Cruise and release use the specified rover speed. Loading/buffer slowdowns
  close phase while staying below it.
- Objective: permanent imported launcher mass per successfully captured payload.
  Local ballast and expendable rock are separate. Hardware estimates now include
  explicit sourced curves and allowances; pivot/stability mass is excluded as
  requested. No stable, lunar-qualified design is yet established.

## Current deliverables

- [Hardware mass study](results/hardware_mass/README.md): component curves, complete
  scoped budget, four-leg sizing, sensitivity, constraints and reproducible data.
- [Hardware sources](results/hardware_mass/SOURCES.md): manufacturer anchors and
  the boundary between published data and engineering extrapolation.

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
MPLCONFIGDIR=/tmp/lunar-sling-mpl-cache .env/hub/bin/python -m lunar_slings.hub_study.split_tie_report
MPLCONFIGDIR=/tmp/lunar-sling-mpl-cache .env/hub/bin/python -m lunar_slings.hub_study.publication.build_publication
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
