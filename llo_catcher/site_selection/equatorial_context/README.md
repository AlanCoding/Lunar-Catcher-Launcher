# Equatorial terrain and the 144° launch example

[Publication packet](../publication/README.md) · [Site-selection guide](../README.md).

These figures introduce the terrain problem in the launch-site article:

- [Elevation along the full equator](equatorial_elevation.png) ([SVG](equatorial_elevation.svg)). Markers show the original 10 m local-ground release seeds and their directions.
- [The 144° E launch clearing a later mountain range](trajectory_144.png) ([SVG](trajectory_144.svg)). The annotated clearance is 407.7 m in the original 25 km-apoapsis model.
- [Detailed elevation views](equatorial_elevation_detail.png) ([SVG](equatorial_elevation_detail.svg)).

The saved [directional seed survey](degree_survey.json), [eastward corridor results](east_corridors.json), and [westward corridors](west_corridors.json) supply marker locations and the 144° annotation. The shared [equatorial model](../support/equatorial.py) supplies terrain and trajectory geometry.

Regenerate figures from the repository root:

```bash
MPLCONFIGDIR=/tmp/lunar-sling-mpl-cache .env/hub/bin/python -m llo_catcher.site_selection.equatorial_context.plot_equator
MPLCONFIGDIR=/tmp/lunar-sling-mpl-cache .env/hub/bin/python -m llo_catcher.site_selection.equatorial_context.plot_144
```

The 695-hub selection uses the later hub-relative release geometry and has its own [outcome table and graph](../global_hills/README.md).
