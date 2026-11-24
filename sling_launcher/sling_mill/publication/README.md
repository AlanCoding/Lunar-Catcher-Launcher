# Sling mill publication packet

**Structural audit update:** This reference assumes tapered radial and torque cables, reaching a 7.26:1 area ratio in the last roller. Hub-root packing and startup-support sizing remain unresolved; the recorded mass/payoff is a conditional development estimate. [Taper table and startup-support concept](../blended/DRUM_TAPER_AND_STARTUP.md).

**Start with [ARTICLE.md](ARTICLE.md).** It contains the final reference, consolidated payload-material and cross-design comparison tables, together with the selected visuals.

The selected case uses **1.51 mm iron plates**, a **1.407 km accelerator**, **1,600 m/s exit speed** and **10 million tonnes per 365 operating days**. Included mass is approximately **9,374 tonnes with full-sun solar**, for **8.21 operating hours** of gross mass payoff.

## Article sequence

The publication copy is assembled in ARTICLE.md: motion GIF → drum and opposed-pair geometry → station spacing → cable taper → startup supports and rim web → Earth flywheel/centrifuge precedents → payload materials → iron reference → matched conveyor comparison and earlier system context → mass pie → conclusions and remaining engineering work.

All eight selected figures are embedded in the article. SVG/PNG alternatives are listed below; the original system-pattern overview remains an optional asset. Numerical values are unchanged by this editorial consolidation.

## Reading order

- **[Article](ARTICLE.md):** publication narrative, current tables and visual sequence.
- **[Technical reference](../blended/IRON_REFERENCE.md):** precise dimensions, mass ledger, operating assumptions and verification.
- **[Assumption review](../blended/ASSUMPTION_REVIEW.md):** which values are optimized, specified or provisional, and why the thickness settles near 1.51 mm.
- **[Material and payoff notes](PAYLOAD_AND_PAYOFF.md):** source references, tensile loading, feeder interpretation, oxygen options and comparison boundaries.
- **[Design tradeoffs](DESIGN_TRADEOFFS.md):** qualitative explanation of the competing effects.

## Publication assets

| Asset | Purpose | Files |
|---|---|---|
| Motion illustration | End-to-end entry and separation during acceleration | [GIF](../figures/05_mill_motion.gif), [SVG still](../figures/05_mill_motion.svg), [PNG still](../figures/05_mill_motion.png) |
| Single drum | Hub-tangent geometry and tensile members | [SVG](../figures/01_drum_geometry.svg), [PNG](../figures/01_drum_geometry.png) |
| Opposed pair | Forward traction and transverse pinch | [SVG](../figures/02_opposed_pair.svg), [PNG](../figures/02_opposed_pair.png) |
| Spacing alternatives | Independent choice of gaps between drums | [SVG](../figures/04_pitch_comparison.svg), [PNG](../figures/04_pitch_comparison.png) |
| Startup supports | Hub-deployed supports at low speed, retracted in operation | [SVG](../figures/07_startup_supports.svg), [PNG](../figures/07_startup_supports.png) |
| Rim suspension web | Branching support concept and torque path | [SVG](../figures/08_rim_suspension_web.svg), [PNG](../figures/08_rim_suspension_web.png) |
| Cable taper | Calculated last-stage profile and root/tip cross sections; 7.26:1 area taper | [SVG](../figures/09_radial_cable_taper.svg), [PNG](../figures/09_radial_cable_taper.png) |
| Current mass allocation | Optimized iron machine including solar | [SVG](../figures/06_machine_mass_pie.svg), [PNG](../figures/06_machine_mass_pie.png) |
| Optional introductory system pattern | Overall repeated arrangement | [SVG](../figures/03_system_pattern.svg), [PNG](../figures/03_system_pattern.png) |

The mechanism illustrations retain their accepted introductory geometry. The GIF is slowed and exaggerates plate thickness. Dimensions for the selected machine come from the article's reference table; the mass pie uses the selected numerical inventory.

## Numerical source and updates

[iron_reference.json](../blended/search_results/iron_reference.json) supplies the current reference. [publication_tables.py](../blended/publication_tables.py) refreshes the marked reference and comparison tables in ARTICLE.md; the article prose and materials tables remain editorial. [report_iron.py](../blended/report_iron.py) refreshes the technical reference and calls that table updater. [mass_pie.py](../blended/mass_pie.py) refreshes the SVG and PNG mass charts from the same inventory.

When changing the model, review the surrounding article prose alongside regenerated tables. Keep a common numerical source for the reference table, comparison row and mass chart.

## Earlier work

[Historical results and asset index](archive/README.md) preserves the introductory studies, old optimizer assumptions, fixed-geometry audit and 5 mm checkpoint. These belong to the development history. The article and current technical reference define the publication case.

## Drum taper and startup support

[Stage-by-stage taper ratios and root/tip dimensions](../blended/DRUM_TAPER_AND_STARTUP.md) document the structural assumption behind the 1 GPa case and the attachment-packing issue. The hub-mounted retractable supports are illustrated in [SVG](../figures/07_startup_supports.svg) and [PNG](../figures/07_startup_supports.png).

The [branching rim web](../figures/08_rim_suspension_web.svg) has a [PNG preview](../figures/08_rim_suspension_web.png). The [structural audit](../blended/DRUM_TAPER_AND_STARTUP.md) now documents peak acceleration torque, hub sizing, the 128-attachment numerical assumption and the proposed web topology.

- [Acceleration-torque reproduction and taper comparison](../blended/DRUM_TAPER_AND_STARTUP.md#reproduced-reference-with-acceleration-torque): updated belt stress, cable sizing and the effect on mass. The article comparison includes area taper and specific working stress.

- [Matched conveyor comparison and suggested article flow](PAYLOAD_AND_PAYOFF.md#matched-acceleration-conveyor-comparison): common speed, acceleration and useful flow, circulation-speed sweep, and structural-fiber-only accounting.

- [Earth precedents](ARTICLE.md#earth-precedents-flywheels-and-centrifuges): sourced operating and burst-test speed benchmarks, centrifugal pellet injection, and the role of taper in energy-storage versus launcher design.
