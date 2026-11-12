# Supporting guide and material screens

[Accepted design and mass model](../README.md)

These calculations establish the taper, approximate guide shapes and sheet/contact
load scales. They use the earlier 32-tether constant-line-speed schedule. The
accepted design has 48 working tethers and rigid paired winding, so these shapes
are **supporting evidence**, with a new-inventory contact/dynamics solve still due.
Their old machine mass and throughput totals are superseded by the accepted design.

- [Reference guide shapes](results/shapes/reference_shapes.png): small bow and overall lean under imposed common contact.
- [Material stress](results/shapes/material_stress.png): guide self-stress and conditional transverse sheet loads.
- [Passage and opening loads](results/shapes/passage_and_opening.png): contact losses can exceed the Coriolis-only estimate if cargo forces a collapsed sleeve open.
- [Numerical shape results](results/shapes/summary.json) and [construction screens](results/shapes/construction.json).
- `scalar.py`, `shapes.py`, `construction.py` retain the reproducible inputs and numerical checks.

The 3:1 moving-tether taper requires 2.438 GPa working stress. A guide assigned the
same mass/taper has 1.389 GPa maximum axial self-stress. Guide material, fatigue,
contact and opening structures require qualification. This work does not establish
service life for either the earlier schedule or the accepted machine.

Reproduce from the repository root, in order:

```sh
MPLCONFIGDIR=/tmp/lunar-sling-mpl-cache .env/hub/bin/python -m sling_launcher.lunar_slider_straw.screening.scalar
MPLCONFIGDIR=/tmp/lunar-sling-mpl-cache .env/hub/bin/python -m sling_launcher.lunar_slider_straw.screening.shapes
MPLCONFIGDIR=/tmp/lunar-sling-mpl-cache .env/hub/bin/python -m sling_launcher.lunar_slider_straw.screening.construction
```
