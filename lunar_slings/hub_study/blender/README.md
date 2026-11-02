# Blender illustration — reference 50 g lunar sling

The scene is now generated from the frozen numerical candidate. Open
**[lunar_sling_50g.blend](lunar_sling_50g.blend)** in Blender. It contains six
named cameras, separate hardware/tether/utility collections, and a static,
fully deployed loaded pose immediately before release.

## Exported views

| View | Image | Purpose |
| --- | --- | --- |
| Launcher overview | [hub.png](renders/hub.png) | Both A-frames, circular track, upper and low ties |
| One A-frame | [frame.png](renders/frame.png) | Four wheels, two poles, ballast and apex machinery |
| Center pivot | [pivot.png](renders/pivot.png) | Ground swivel, apex stays, and the separate low-tie crossing |
| Site | [site.png](renders/site.png) | Launcher, stationary solar and radiator installations |
| Full span | [span.png](renders/span.png) | The roughly 11.57 km tip-to-tip system over lunar ground |
| Cable profile | [profile.png](renders/profile.png) | True-scale loaded outward cable and lunar curvature |

An additional [axis-labeled droop diagram](renders/droop_diagram.png)
([SVG](renders/droop_diagram.svg)) makes the cable shape easier to read. Its
axes use kilometers horizontally and meters vertically; the Blender scene
itself remains at true scale.

The full-span and profile exports use **render-only gold cable highlights**
with an 8 m display diameter; the physical cable geometry remains separately
present with its actual taper. Positions and sag are not exaggerated. These
long-span highlights are explicitly labeled in those images, hidden in the saved
default view, and live in `Render annotations`. The two apex-to-pivot stays
have separate **cyan visibility highlights, 0.24 m display diameter**, enabled
in the hub/frame/pivot/site views and the default saved view. Their thin
underlying illustrative lines remain separate. Display thickness does not
represent an engineered stay diameter. Without a highlight, centimeter-scale
rope cannot be seen reliably in a kilometer-scale image.

## Reproduction

From the repository root:

```bash
.env/hub/bin/python -m lunar_slings.hub_study.blender.export_inputs
flatpak run org.blender.Blender --background --factory-startup --python "$PWD/lunar_slings/hub_study/blender/build_scene.py"
```

The exporter uses the NumPy/SciPy environment; Blender itself needs only its
bundled Python. `build_scene.py` creates the `.blend` file and exports all six
PNG pictures. For quicker iterations, append `-- --draft --views hub,frame`.
Use `-- --views site,span,profile` to select other exports. The script rebuilds
the scene from scratch each run. It does not alter the installed Blender app
or its saved user preferences.

The installed Flatpak is Blender 5.1.1. It reports an OpenColorIO configuration
version mismatch and uses fallback color management. These renders use the
Standard view and were inspected as exported; no claim of calibrated AgX/color
output is made. The warning does not prevent scene generation or rendering.

## Numerical geometry

Sources: [frozen candidate](../publication/candidate_50g.json),
[exported scene inputs](scene_inputs.json), and the
[separate-tie study](../results/split_tie/README.md).

- Track radius **76.789 m**, unbanked. Both powered and passive wheel centers
  lie on this circle. Four powered and four passive wheels are present.
- Pole apex height **28.680 m**; vertical and trailing member lengths
  **25.438 m** and **35.975 m**. Diameters are taken separately from all four
  candidate records. Trailing feet use the chord angle needed to preserve
  both the pole length and circular track radius.
- Powered wheels **6.485 m diameter × 2.270 m width**; passive wheels
  **3.744 m diameter × 1.310 m width**. Passive wheels trail their powered
  partners along the track; there are no extra side-by-side wheels.
- Two upper capstan/storage assemblies use the numerical core radius,
  storage-envelope radius and width. Storage barrels are shown without a
  full cable winding because this pose is fully deployed.
- Upper tie and low ties are separate objects. Two half-load low ties restrain
  corresponding opposing feet; their aggregate fiber mass equals the model's
  single aggregate budget. Their small central crossing junction is floating,
  not a termination of radial loads on the ground pivot.
- Two outward slings use **501 solved centerline points each** and the
  mass-derived rope taper. The payload radius is **5,787.088 m**.
- Two cyan stays run from the A-frame apexes to a **ground-mounted center
  pivot/swivel**, distinct from the upper payload tie and the floating low-tie
  crossing junction. Their crossing with the low connection is retained in
  the drawing; no invented routing mechanism has been added.
- The local spherical lunar surface uses the same **1,738,100 m** reference
  radius as the physical model. Cosmetic relief is modest and kept away from
  the prepared launcher/utility area.
- The loaded near-release pose has **10.511 m minimum cable-centerline
  clearance** over the spherical datum. The study's 3 m clearance margin is
  set elsewhere in the operating cycle; the scene does not lower this pose
  artificially to make it touch that limit.
- Radiator panel emitting area sums to **33,123.20 m²**, taken from the mass
  model. Solar and thermal systems are stationary, separate from the rovers.

The build checks four leg lengths, wheel counts, wheel track radii and total
ballast assignment. This is a geometric illustration, not a dynamics or CAD
qualification model. Static rope equilibrium is not an animation of payout,
release recoil or successful capture.

## Explicit illustration assumptions

The mass model does not determine every volume or mechanical layout. These
choices are visible packaging, not additional engineering results:

- Eight ballast bins (two per pole foot) use an assumed **1,800 kg/m³** bulk
  density, sharing the **1,193,412.95 kg** ballast equally. Inboard/outboard
  bins are balanced around each foot. Their height centers use the assumed
  low-tie/low-mass height. Local axle/retention details are schematic.
- Motor and gearbox housings use effective packaging densities of **2,000**
  and **3,000 kg/m³**, respectively. They illustrate the estimated mass scale;
  they are not supplier CAD or a validated shaft/gear arrangement.
- Solar modules assume **200 W/m² installed output** for visualization. The
  required 21.97 MW peak therefore gives approximately **109,834 m²** of panel
  area. This area is illustrative; the engineering mass estimate was based on
  W/kg. Array spacing, mounts and electrical distribution are schematic.
- Radiator layout is illustrative. Its known emitting area is preserved,
  but pipework, shading and the moving heat-transfer interface are not designed
  or implied by placing the panels on the terrain.
- The payload and rock are each shown in a **1.5 × 1.2 × 1.3 m** envelope with
  the modeled **1,000 kg** mass. Material density/actual container shape remain
  unspecified; the blocks are illustrative.
- Track width (22 m), wheel tread, tandem coupling clearance, top platforms,
  crossing-junction hardware and light stays are schematic. The center pivot
  has an illustrative 1.05 m attachment height and 3.6 m foundation diameter.
  Stay sizing remains outside the mass estimate; the underlying 24 mm lines
  and thicker display overlays are not strength calculations. The center
  pivot remains a ground-mounted stabilizing feature, separate from the main
  upper/low radial force connections.
- Terrain/crater decoration is illustrative, not a surveyed lunar site.

The final packaging has small local offsets from the mass model's concentrated
mass locations. No new mass budget, load-path certification, or collision-free
manufacturing assembly is claimed from these shapes.

## Files

- [build_scene.py](build_scene.py): Blender scene and render generation.
- [export_inputs.py](export_inputs.py): physical-model export, source hash and
  loaded-pose clearance check.
- [scene_inputs.json](scene_inputs.json): frozen candidate and numerical cables.
- [render_manifest.json](render_manifest.json): camera settings, exported image
  sizes, Blender version and packaging assumptions.
- [Publication checkpoint](../publication/README.md): the accompanying blog text,
  pie charts and mass-payoff calculations.
