# Low lunar orbit catcher studies

- **[Launch-site publication packet](site_selection/publication/README.md):** the article’s ordered figures, tables and local copy folder, including the lowered-release closing example.
- **[Site selection](site_selection/README.md):** hub search, four featured hilltops, named ridges, equatorial maps and radial terrain profiles.
- **[Original catcher notebook](<variations analysis for lunar catcher-launcher system.ipynb>):** transfer geometry and sensitivity calculations for [The Value of Low Lunar Orbit Space Stations](https://alanse.medium.com/the-value-of-low-lunar-orbit-space-stations-db1a5bb9e8af).

Launcher hardware, cable dynamics and future sag/taper work live in [sling_launcher](../sling_launcher/README.md).

## Original catcher article

The notebook explores the original electromagnetic mass-driver/catcher concept and nominal 100 km catcher orbit. Its accompanying figures are [downrange_rise.png](downrange_rise.png) and [downrange_rise2.png](downrange_rise2.png); [requirements.txt](requirements.txt) lists its dependencies. The notebook retains Python 2 syntax and its historical assumptions.

The separate [frozen-retreat study](../frozen_retreat/README.md) contains the 30 km catcher / 120 km retreat notebook and sensitivity sweep.

## Current launch-site work

Published article: [Lunar Equator to LLO Mass Launcher Sites](https://alanse.medium.com/lunar-equator-to-llo-mass-launcher-sites-145d9351a255?sharedUserId=alanse).

All current site-selection outputs and their calculation dependencies are under `site_selection/`. Shared terrain/orbit routines are in [support](site_selection/support/README.md), and the introductory equator figures are in [equatorial_context](site_selection/equatorial_context/README.md).
