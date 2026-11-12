# Conveyor versus tapered sling — publication packet

A short technical note centered on the accepted fixed-mass-flow figure.
The mass frontier is preserved. A matched-hardware stopped-feed calculation adds
shape and stress context.

- **[Technical note](TECH_NOTE.md):** concise problem, fixed inputs, result, and interpretation; ready to adapt for publication.
- **Main figure:** [PNG](fixed_mass_flow.png) · [SVG](fixed_mass_flow.svg), copied unchanged from the accepted results.
- **[Conveyor shapes and stress](SHAPES_AND_STRESS.md):** solved 2D geometry, stress profiles, and a moving-versus-stopped-feed table; [figure PNG](conveyor_shape_and_stress.png) · [SVG](conveyor_shape_and_stress.svg).
- **[Numerical table](mass_table.csv):** working tether mass versus specific working stress and conveyor feed speed, in kg per useful arm. Blank conveyor entries indicate no finite solution in the modeled family.
- **[Full method and results](../README.md):** equations, assumptions, cycle-time sensitivity, and reproduction commands.
- **[Solved frontier](../results/stress_frontier.json)** · **[Validation](../results/frontier_validation.json)** · **[Packet provenance](manifest.json)**.

Suggested presentation: introduce the two architectures, show the main figure,
then give the stress floor and 5 m/s crossover. The small table in the note is
optional. The separate cycle-time plot remains supporting material in the full
analysis.

Published article link: add here when available.
