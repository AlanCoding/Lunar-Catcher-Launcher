# Publication checkpoint — 2026-11-01

**Article status:** Upcoming; not yet published.

**Working topic:** Wheeled Kevlar lunar sling launcher.

**Published article URL:** To be added here when the new post goes public.

<!-- Publication update: replace the URL placeholder above with the article link,
     set Article status to Published, and update the status in the root README. -->

These are working materials for a **new post**, separate from
[The Value of Low Lunar Orbit Space Stations](https://alanse.medium.com/the-value-of-low-lunar-orbit-space-stations-db1a5bb9e8af)
(December 24, 2017). That earlier post's original notebook, catcher sensitivity
analysis and plots are indexed in the [lunar studies guide](../../llo_catcher/README.md#published-post-original-notebook-and-plots).
The checkpoint date in this document's title is a study snapshot date, not an
article publication date.

Start with **[CHECKPOINT.md](CHECKPOINT.md)** for the blog-ready engineering
summary, selected dimensions, mass charts and scope. This is the current
publication checkpoint; the older `sling_launcher/CHECKPOINT.md` is historical.

- **[DESIGN_AT_A_GLANCE.md](DESIGN_AT_A_GLANCE.md):** a compact dimensions and
  parameters sheet, including the 28.68 m pole-top height.
- **[MASS_PAYOFF.md](MASS_PAYOFF.md):** equations, launch counts, sunlight and
  availability scenarios, and the meaning of “mass payoff.”
- **[WHY_THE_MASS_MINIMUM_EXISTS.md](WHY_THE_MASS_MINIMUM_EXISTS.md):** which
  components drive each side of the mass-ratio valley, with numerical comparisons.
- **[REEL_ASSUMPTIONS.md](REEL_ASSUMPTIONS.md):** bend ratios and spool dimensions
  by scenario, physical limits, and the two-reel illustration.
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
MPLCONFIGDIR=/tmp/lunar-sling-mpl-cache .env/hub/bin/python -m sling_launcher.publication.build_publication
```

The generator asserts complete, non-overlapping mass accounting and verifies
the integer launch counts. It does not rerun or alter the engineering model.
The checkpoint prose and Blender brief are intentionally maintained separately.
