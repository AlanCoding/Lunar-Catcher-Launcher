# Lunar Slings

Workspace for the lunar surface-launch / orbital-catcher concept and future rotating sling analysis.

The new [wheeled Kevlar hub study](hub_study/README.md) is separate from the
historical ballistic calculations. Start with its [current checkpoint](hub_study/CHECKPOINT.md): finite-angle
cable shapes, spooling cycles, ballast, power and scenario graphs. A complete
buildable launcher and imported mass optimum have not yet been established.

## Files

- `variations analysis for lunar catcher-launcher system.ipynb`: original notebook, preserved without edits. It explores a nominal 100 km catcher orbit, launch-speed and pointing errors, downrange rise, and energy/payoff estimates.
- `downrange_rise.png`, `downrange_rise2.png`: original notebook plots. They remain beside the notebook so its relative output paths still apply.
- `requirements.txt`: dependencies moved with the original notebook.
- `analysis/README.md`: initial assessment and analysis roadmap.
- `analysis/baseline.py`: dependency-free Python 3 calculation of ideal transfer geometry, launch sensitivity, and rendezvous timing.

## Run the baseline analysis

From the repository root:

```bash
python3 lunar_slings/analysis/baseline.py
```

This runs the model's consistency checks and prints a Markdown results table. It does not modify the notebook or plots.

## Original notebook

The notebook uses Python 2 `print` statements and historical assumptions. Its dependency list alone does **not** make it runnable in a modern Python 3 environment; modernization is separate work. For inspection using Jupyter:

```bash
python3 -m pip install -r lunar_slings/requirements.txt
cd lunar_slings
python3 -m jupyter notebook 'variations analysis for lunar catcher-launcher system.ipynb'
```

The current notebook describes a ballistic transfer to an orbital catcher. It does not yet specify a rotating tether, material, length, tip speed, or capture mechanism.
