# Historical sling mill studies

[Current publication article](../ARTICLE.md) · [Current technical reference](../../blended/IRON_REFERENCE.md)

The selected publication case is the thinner-plate iron optimization **with full-sun solar included**: approximately **9,374 tonnes and 8.21 operating hours**. Earlier results below preserve the sequence of modeling decisions. Each belongs to its own material, geometry and inventory assumptions.

## Earlier numerical checkpoints

| Checkpoint | Characteristic numbers | Why it differs from the current case | Record |
|---|---|---|---|
| Introductory constant-acceleration example | 1,000 g, roughly 130 m; 200 mm drums | Prescribed acceleration and early flexible-panel screen | [Baseline results](../../RESULTS.md), [early article](EARLY_ARTICLE.md) |
| Hypothetical-payload optimum | 1,665 t; 1.46 h | Density 3,000 kg/m³; 100 MPa payload allowable; assumed compressive buckling bound; lighter hardware allowances; external power source | [Search checkpoint](../../blended/OPTIMIZATION.md), [JSON](../../blended/search_results/freehub_10gpa.json) |
| Fixed-geometry iron audit | 13,401 t; 11.74 h | Actual iron density substituted into retained geometry; explicit support/drive audit; external power source | [Audit narrative](FIXED_GEOMETRY_AUDIT.md), [JSON](../../blended/search_results/iron_hardware_audit.json) |
| Iron search with 5 mm thickness floor | 5,154 t; 4.515 h | Arbitrary 5 mm lower bound, 80% occupancy cap and 100 Hz feed cap; external power source | [Preserved reference JSON](../../blended/search_results/iron_5mm_reference.json) |

The current model permits plates down to 0.10 mm, selects approximately 1.51 mm, removes the arbitrary occupancy/feed caps and includes a full-sun solar array. Its comparison table uses the current 8.21-hour result.

## Development documents

- [Original study overview](ORIGINAL_STUDY_README.md) preserves the prior navigation and early-result discussion.
- [Independent pitch study](../../PITCH_STUDY.md) explores introductory fixed drum/bar sizes. Its accepted spacing illustration remains useful for explaining the mechanism.
- [Original model register](../../MODEL.md) and [optimizer development](../../optimization/README.md) retain the evolving equations and assumptions.
- [Early blended sweeps](../../blended/README.md#historical-development-results) document how squeeze was connected to force, acceleration, heat and mass.

## Earlier diagnostic figures

These figures refer to the introductory models; the publication asset list is in the [current packet](../README.md#publication-assets).

| Figure | Record |
|---|---|
| Pitch tradeoffs | [SVG](../../results/pitch_tradeoffs.svg), [PNG](../../results/pitch_tradeoffs.png) |
| Station results | [SVG](../../results/stage_results.svg), [PNG](../../results/stage_results.png) |
| Whole-mill power | [SVG](../../results/whole_mill_power.svg), [PNG](../../results/whole_mill_power.png) |
| Rotor transient | [SVG](../../results/rotor_transient.svg), [PNG](../../results/rotor_transient.png) |
| Early structural screen | [SVG](../../results/structural_screen.svg), [PNG](../../results/structural_screen.png) |
| Parameter sweeps | [SVG](../../results/parameter_sweeps.svg), [PNG](../../results/parameter_sweeps.png) |
| Sampled Pareto plot | [SVG](../../results/pareto.svg), [PNG](../../results/pareto.png) |

Numerical files and scripts remain in their existing locations so their relative paths and reproducibility are preserved.
