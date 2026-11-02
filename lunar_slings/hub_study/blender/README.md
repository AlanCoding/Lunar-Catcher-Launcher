# Reserved Blender workspace — do not build the scene yet

The user requested this folder and handoff only. **No Blender script, scene,
render or dependency installation is part of this checkpoint.** Creation will
start in the next authorized phase, after review of the publication materials.

## Intended scene

A Python-scripted Blender diagram of the **reference 50-g, 50-mph, single-pass**
case, shown in operation above a lunar surface. Construct geometry from the
model's numerical values wherever available, including actual calculated
outward-tether droop. Use an engineering illustration, with labeled schematic
choices where the numerical study has not supplied mechanical geometry.

## Authoritative inputs

- [Frozen candidate](../publication/candidate_50g.json): dimensions, four distinct
  leg records, powered/passive wheel sizes, reel dimensions, mass budget,
  radiator area, low-tie height and calculated cruise sag.
- [Publishable checkpoint](../publication/CHECKPOINT.md) and
  [selected design's force paths](../results/split_tie/README.md).
- `scenario_study.py`: `Scenario(acceleration_g=50, rover_mph=50, passes=1)` and
  `geometry(...)` reconstruct the corresponding loaded/unloaded cable branches.
- `cable_shape.py`: use its solved radial/vertical geometry and taper, not a
  decorative guessed catenary. Keep lunar curvature/ground clearance consistent
  with the physical model. Dimensions in Blender should use meters.
- [Manufacturer/assumption register](../results/hardware_mass/SOURCES.md).

## Layout requirements for the later script

- Two opposing A-frames; four pole legs total.
- Four powered and four passive wheels total. Each foot has a fore-and-aft
  powered/passive pair, not side-by-side wheels. Smaller passive wheels need
  their own axle height and an explicitly schematic attachment structure.
- Track radius 76.789 m; upper apex height 28.680 m. Pole lengths are measured
  from axle height. Fit the trailing feet on the circular track; do not treat
  the tangential schematic as an exact flat rectangle with all feet at equal
  track radius.
- Payload/counterweight at opposite release radii 5,787.088 m for the chosen
  loaded near-release depiction. Both have 1,000 kg modeled mass; their shape
  and density are not defined. Mark any illustrative dimensions as assumed.
- Separate upper payload tie and low rover/ballast connection. The low tie
  stays included: this is well below the approximately 616 m switch radius.
  Aggregate fiber mass must not be doubled if rendered as two parallel ties.
  Central crossing/bridle routing and startup preload are still layout details.
- Two apex capstan/storage assemblies, four wheel drives, local ballast,
  stationary solar and stationary heat rejection. Mass alone does not define
  their physical volume; identify additional density/area/packaging assumptions.
- Lunar surface and an unbanked circular track. Terrain should not intrude into
  the model's clearance envelope just to make the landscape visually dramatic.
- Solar is not mounted on the rotating poles; thermal placement must not imply
  an already engineered moving heat-transfer interface.
- Ground central pivot/stabilizing stays may be schematic; the main upper tie
  connects opposing apexes directly, not to the ground pivot.
- Preserve physical scale in the scene. Use separate close-up and full-span
  cameras rather than silently shortening the roughly 11.6 km tip-to-tip span.

Potential later files: a `build_scene.py` generator, generated `.blend` scene,
render outputs and a documented list of illustration-only assumptions. None
are created now. Do not imply that a rendered static near-release configuration
validates deployment dynamics, recoil, capture or component qualification.
