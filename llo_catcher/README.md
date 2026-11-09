# Low lunar orbit catcher studies: reader guide

**For the completed equatorial launch-site study, start with the
[checkpoint and reading guide](analysis/LAUNCH_SITE_CHECKPOINT.md).** It leads to
the six-site catalog and final east/west impact results, then the earlier graphs
and calculations. The [analysis directory guide](analysis/README.md) also maps
the separate spherical heading result and historical notebook review.

This directory preserves the original LLO catcher calculations for
[The Value of Low Lunar Orbit Space Stations](https://alanse.medium.com/the-value-of-low-lunar-orbit-space-stations-db1a5bb9e8af)
(published December 24, 2017). The post assumes an electromagnetic mass driver;
its ballistic transfer and launch-error calculations are not a sling design.
The later wheeled launcher work lives separately in [sling_launcher/](../sling_launcher/README.md).

## Work items and results

- **[Orbital and terrain analyses](analysis/README.md):** offset-release geometry,
  launch-clearance studies and the original notebook review. The guide distinguishes
  completed results from historical or deferred branches.
- **[Launch sites and impacts](analysis/LAUNCH_SITE_CHECKPOINT.md):** where can an
  equatorial shot clear terrain and where does a missed catch land? The completed
  exploratory study includes six hilltop hubs, maps and east/west impact tables.
- **[Original catcher notebook](<variations analysis for lunar catcher-launcher system.ipynb>):**
  the published mass-driver study's catcher transfer and sensitivity calculations,
  preserved as historical source material.

## Published post: original notebook and plots

- [Original catcher notebook](<variations analysis for lunar catcher-launcher system.ipynb>):
  preserved without edits during the repository reorganization. It explores a
  nominal 100 km catcher orbit, launch-speed and pointing errors, downrange rise,
  and energy/payoff estimates. These are the existing calculations associated
  with the published post, not new sling-launcher results.
- [Downrange plot](downrange_rise.png) and [second downrange plot](downrange_rise2.png):
  original notebook outputs, kept beside it so relative output paths still apply.
- [requirements.txt](requirements.txt): dependencies moved with the original notebook.

## Later review and published launcher post

- [Baseline review](analysis/README.md) and [baseline.py](analysis/baseline.py):
  a later Python 3 consistency calculation and assessment of the historical
  ballistic model. These are not the original notebook or a replacement for it.
- [Wheeled Kevlar hub study](../sling_launcher/README.md): the subsequent surface-launcher
  hardware, cable, operating-cycle and mass-optimization analysis.
- [Sling post's publication index](../sling_launcher/publication/README.md): current
  50-g checkpoint, mass charts, dimensions, payoff and Blender illustrations;
  includes the published article link. Its sampled mass minimum
  is conditional on the documented model assumptions.
- [Frozen-retreat study](../frozen_retreat/README.md): a separate 30 km catcher /
  120 km retreat calculation with its own notebook and sensitivity sweep.

## Run the baseline analysis

From the repository root:

```bash
python3 llo_catcher/analysis/baseline.py
```

This runs the model's consistency checks and prints a Markdown results table. It does not modify the notebook or plots.

## Original notebook

The notebook uses Python 2 `print` statements and historical assumptions. Its dependency list alone does **not** make it runnable in a modern Python 3 environment; modernization is separate work. For inspection using Jupyter:

```bash
python3 -m pip install -r llo_catcher/requirements.txt
cd llo_catcher
python3 -m jupyter notebook 'variations analysis for lunar catcher-launcher system.ipynb'
```

The original notebook describes a ballistic transfer to an orbital catcher. It does not yet specify a rotating tether, material, length, tip speed, or capture mechanism.

## Completed catcher-orbit follow-up

- [Equatorial launch-site checkpoint](analysis/LAUNCH_SITE_CHECKPOINT.md): final
  findings, six-site coordinates, impact results, and a reading path through
  preserved terrain surveys and figures. Closed at the agreed exploratory scope.
- [Accepted spherical heading optimum](analysis/heading_optimization/RESULT.md):
  the completed offset-release geometry study for a 25 km equatorial catcher.
- [Two offset useful payloads](analysis/dual_offset_release/README.md): deferred
  comprehensive paired study; the approximate six-site westward check is recorded
  in the checkpoint above.
- [Repository work queue](../WORK_ITEMS.md): current launcher investigations and
  deferred topics; terrain work remains closed at its agreed exploratory scope.
