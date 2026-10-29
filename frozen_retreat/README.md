# Frozen Retreat Lunar Catcher Trade Study

This folder reproduces the full calculation chain from the prompt in `frozen_retreat/PROMPT.md`:
- lunar surface -> 30 km catcher transfer
- catcher catch kinematics and failure velocity
- 30 km -> 120 km Hohmann escape
- EP power sizing for 2-day and 3-day escape
- solar array mass/area sizing
- 0.8 km/s bridge-leg rocket equation mass budget
- bridge-leg travel time estimate
- ground mass-driver energy/power/PV sizing
- final consolidated summary tables and a sensitivity sweep

## Structure

- `notebooks/01_lunar_catcher_trade_study.ipynb`: main end-to-end notebook.
- `src/orbital.py`: orbital helper equations.
- `src/ep.py`: electric propulsion helper equations.
- `src/unit_helpers.py`: unit conversion + markdown table helper.
- `src/scenario.py`: `Scenario` dataclass and `run_trade_study()` for reusable scenario execution.
- `run_scenario.py`: minimal script runner for baseline summary.

## Run with your venv

From repo root:

```bash
~/venvs/gb/bin/python frozen_retreat/run_scenario.py
```

Notebook:

```bash
~/venvs/gb/bin/python -m jupyter notebook frozen_retreat/notebooks/01_lunar_catcher_trade_study.ipynb
```

## Scenario-driven usage (Python or Jupyter)

```python
from frozen_retreat.src.scenario import Scenario, run_trade_study

scenario = Scenario(
    ve_m_s=3200.0,
    eta=0.65,
    m_dry_t=60.0,
)
results = run_trade_study(scenario)
print(results["section_8"]["delivered_rocks_t"])
```

All assumptions are declared once in `Scenario` (single source of truth), and all outputs are deterministic.
