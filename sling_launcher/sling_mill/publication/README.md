# Sling mill: illustration and publication workspace

[Study overview](../README.md) · [Numerical results](../RESULTS.md) · [Model](../MODEL.md)

This is the initial concept/model packet. The supplied nominal drum geometry is illustrated at operating radius; the structural screen's thick-belt failure is described with the results. The drawings communicate architecture and dimensions while contact shape is being resolved.

| Asset | Purpose | Preview |
|---|---|---|
| [Exact single-drum SVG](../figures/01_drum_geometry.svg) | Hub-tangent cable H–P, shared attachment P, radial member, right angle, dimensions and force components | [PNG](../figures/01_drum_geometry.png) |
| [Opposed-pair SVG](../figures/02_opposed_pair.svg) | Opposite rotation, forward traction, compressive normal forces and rod depth relative to drum diameter | [PNG](../figures/02_opposed_pair.png) |
| [System-pattern SVG](../figures/03_system_pattern.svg) | True-scale rods spanning several drums and a compressed full-machine overview; two rods use acceleration-corrected spacing | [PNG](../figures/03_system_pattern.png) |
| [Spacing comparison SVG](../figures/04_pitch_comparison.svg) | Four layouts with identical drums and rods, showing the effect of independently changing pitch | [PNG](../figures/04_pitch_comparison.png) |
| [Pitch tradeoffs](../results/pitch_tradeoffs.svg) | Station count, individual loads, heat and conditional fiber inventory at fixed throughput | [PNG](../results/pitch_tradeoffs.png) |
| [Station results](../results/stage_results.svg) | Fixed speeds, sliding heat, mean/peak local power and stress screens | [PNG](../results/stage_results.png) |
| [Whole-mill power](../results/whole_mill_power.svg) | Two injection periods, including rods simultaneously in the accelerator | [PNG](../results/whole_mill_power.png) |
| [Rotor transient](../results/rotor_transient.svg) | Late-station two-launch energy-storage screen | [PNG](../results/rotor_transient.png) |
| [Structural screen](../results/structural_screen.svg) | Required belt thickness and cable tension versus position | [PNG](../results/structural_screen.png) |
| [Parameter sweeps](../results/parameter_sweeps.svg) | Radius family, acceleration, hub fraction and rod-depth sensitivity | [PNG](../results/parameter_sweeps.png) |
| [Sampled Pareto plot](../results/pareto.svg) | Conditional mass/length/heat trade space, with drive rating included in dominance calculation | [PNG](../results/pareto.png) |

Illustrations are generated mathematically by [draw.py](../draw.py) and
[pitch_study.py](../pitch_study.py), with a white background and editable SVG text.
The system pattern uses **200 mm drums on 300 mm pitch**, leaving a 100 mm gap.
Its configuration is [config_spaced.json](../config_spaced.json); its station
count belongs to that layout. The [pitch study](../PITCH_STUDY.md) retains the
handoff's touching-drum case as a comparison and explores progressively wider gaps.

A concise eventual article can introduce the repeated opposed-drum pattern, explain intentional sliding and strong manufactured rods, present fixed-flow energy figures, then describe the flexible-contact and rotor-storage constraints that determine viability. The current model has no publication-ready feasible mass optimum.
