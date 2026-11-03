# Lunar Catcher / Launcher Studies

This repository contains the calculations behind a published low-lunar-orbit
catcher post, along with subsequent studies and material for a forthcoming
surface sling-launcher post.

## Posts and supporting work

| Post / study | Publication status | Repository entry point |
| --- | --- | --- |
| [The Value of Low Lunar Orbit Space Stations](https://alanse.medium.com/the-value-of-low-lunar-orbit-space-stations-db1a5bb9e8af) | Published December 24, 2017 | [Original notebook and plots](llo_catcher/README.md#published-post-original-notebook-and-plots): 100 km catcher, launch-error sensitivity, downrange rise and energy/payoff calculations. |
| Wheeled Kevlar lunar sling launcher (working title) | **Upcoming; not yet published** | [Publication index](sling_launcher/publication/README.md): current 50-g design, component masses, mass optimization, payoff and Blender illustrations. The future article URL belongs in that index. |
| Frozen-retreat catcher study | Separate study; no article link assigned here | [30 km catcher / 120 km retreat study](frozen_retreat/README.md), including its own notebook and sensitivity sweep. |

The LLO catcher sensitivity analysis is **existing work from the published
post**, not a new result of the wheeled-launcher study. The original notebook and its two plots are preserved together in
`llo_catcher/`; reorganizing them did not create a new analysis. The [Python 3 baseline and review](llo_catcher/analysis/README.md)
were added later and are distinguished from the preserved original notebook.

Each study keeps its dependencies and run instructions beside its files.
The [lunar studies guide](llo_catcher/README.md) maps the original materials
to the subsequent work. The top-level folders separate catcher trajectories, launcher hardware and
orbital retreat. Notebook-relative plot paths are preserved; launcher imports
and reproduction commands use the `sling_launcher` package.

## Upcoming sling-launcher post: working documents

These are working materials for the **upcoming sling-launcher post**, not the
source documents for the 2017 article. Older upper-only and
climber checkpoints are historical, not alternative current results.

| Document | Use |
| --- | --- |
| [Publication index](sling_launcher/publication/README.md) | Figure downloads and links to the current checkpoint files. |
| [Engineering checkpoint](sling_launcher/publication/CHECKPOINT.md) | Main narrative, selected design, mass pies and scope. |
| [Dimensions and parameters at a glance](sling_launcher/publication/DESIGN_AT_A_GLANCE.md) | Pole height, wheel sizes, track/tether dimensions, speeds, timing and power. |
| [Why the mass minimum exists](sling_launcher/publication/WHY_THE_MASS_MINIMUM_EXISTS.md) | Low-acceleration pole penalty versus high-acceleration reel torque, with numbers. |
| [Reel assumptions and bend ratios](sling_launcher/publication/REEL_ASSUMPTIONS.md) | Scenario spool dimensions, physical limits, and the two-reel illustration. |
| [Mass composition table](sling_launcher/publication/MASS_TABLE.md) | Grouped masses and percentages behind the imported-equipment pie. |
| [Mass-payoff calculations](sling_launcher/publication/MASS_PAYOFF.md) | Launch counts, daylight/availability cases and replacement-mass formula. |
| [Reference design method](sling_launcher/results/split_tie/README.md) | Upper/low force paths, sizing method, assumptions and current minimum. |
| [Scenario comparison table](sling_launcher/results/split_tie/SCENARIOS.md) | Other acceleration cases at 50 mph and one pass. |
| [Sources and estimation assumptions](sling_launcher/results/hardware_mass/SOURCES.md) | Manufacturer anchors, engineering extrapolations and exclusions. |
| [Blender illustration guide](sling_launcher/blender/README.md) | Six rendered views, scripting instructions and illustration-only assumptions. |
