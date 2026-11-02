# Publication checkpoint — 2026-11-01

Start with **[CHECKPOINT.md](CHECKPOINT.md)** for the blog-ready engineering
summary, selected dimensions, mass charts and scope. This is the current
publication checkpoint; the older `hub_study/CHECKPOINT.md` is historical.

- **[DESIGN_AT_A_GLANCE.md](DESIGN_AT_A_GLANCE.md):** a compact dimensions and
  parameters sheet, including the 28.68 m pole-top height.
- **[MASS_PAYOFF.md](MASS_PAYOFF.md):** equations, launch counts, sunlight and
  availability scenarios, and the meaning of “mass payoff.”
- **[MASS_TABLE.md](MASS_TABLE.md):** exact grouped mass totals and percentages.
- **[Imported equipment pie — SVG](imported_mass_pie.svg)** /
  **[PNG](imported_mass_pie.png):** detailed composition of imported equipment.
- **[Whole-machine pie — SVG](physical_mass_pie.svg)** /
  **[PNG](physical_mass_pie.png):** imported equipment versus local ballast.
- [Frozen 50-g candidate](candidate_50g.json), [mass groups](mass_groups.json),
  [payoff arithmetic](payoff.json), [source manifest](manifest.json).

The supporting [separate-tie study](../results/split_tie/README.md) contains
methods and scenario sweeps; the [source register](../results/hardware_mass/SOURCES.md)
identifies manufacturer data and engineering extrapolations.

The [Blender illustration](../blender/README.md) now supplies a Python-generated
scene and six render views of this frozen candidate. It was added after this
numerical publication checkpoint.

Rebuild charts, data snapshot, mass table and payoff document from repository root:

```bash
MPLCONFIGDIR=/tmp/lunar-sling-mpl-cache .env/hub/bin/python -m lunar_slings.hub_study.publication.build_publication
```

The generator asserts complete, non-overlapping mass accounting and verifies
the integer launch counts. It does not rerun or alter the engineering model.
The checkpoint prose and Blender brief are intentionally maintained separately.
