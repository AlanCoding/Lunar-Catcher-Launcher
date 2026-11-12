from pathlib import Path
import json
import numpy as np
P=Path(__file__).parent
s=json.loads((P/'summary.json').read_text());a=np.load(P/'constant_speed_n64.npz');e,r=s['phase_results'];hold=a['tip_angle_deg'][a['phase']=='loaded_hold']
text=f'''## Results for the reference inputs

**Loaded payout averages {e['cruise_mean_tip_angle_deg']:.2f}° of lag during cruise**,
with a most-negative tip angle of **{e['tip_min_deg']:.2f}°**. Maximum sideways tip
displacement reaches **{e['max_lateral_tip_m']:.0f} m**. After the length command stops,
the loaded hold still swings between **{hold.min():.2f}° and {hold.max():.2f}°** in
this run. Constant cruise speed therefore does not imply a fixed angle or a
settled payload at the end of the stroke.

![Loaded extension](extension_angles.png)

![Empty retraction](retraction_angles.png)

The return panel shows the first 80% of its stroke. The [complete stroke and
stress figure](angular_deviation.png) retains the provisional final portion.

| Stroke time | Loaded extension tip angle | Empty retraction tip angle |
| --- | ---: | ---: |
'''
for x,y in zip(e['samples'],r['samples']):text+=f"| {x['elapsed_min']:.2f} min ({100*x['stroke_time_fraction']:.0f}% of stroke) | {x['tip_angle_deg']:.2f}° | {y['tip_angle_deg']:.2f}° |\n"
text+=f'''
These are snapshots within oscillatory histories. During the first 80% of return,
the tip angle spans **{r['first80pct_tip_min_deg']:.2f}° to {r['first80pct_tip_max_deg']:.2f}°**.
The late-return and post-return orientation becomes much more sensitive and can
wind through whole relative revolutions in the contact-free model. The figures
retain that diagnostic behavior and mark the late return as provisional.

Both meshes complete the modeled extension and return without triggering the
3 GPa stop. The 64-cell peak stresses are **{e['peak_stress_GPa']:.3f} GPa during
extension** and **{r['peak_stress_GPa']:.3f} GPa during return**; abrupt release peaks
at **{next(x['accepted_step_peak_stress_Pa']/1e9 for x in s['reference']['solver'] if x['phase']=='release_settle'):.3f} GPa**.
These are simulated fiber stresses under an assumed damping law, with material
qualification and neighboring hardware contact still outside the model.

| Mesh comparison, 32 versus 64 cells | Maximum tip-angle difference through first 80% | Maximum over full stroke |
| --- | ---: | ---: |
'''
for c in s['mesh_comparison']:text+=f"| {c['phase'].capitalize()} | {c['first80pct_max_difference_deg']:.3f}° | {c['max_tip_angle_difference_deg']:.3f}° |\n"
text+='''
The stable publication conclusion is that this simple open-loop program has a
substantial payout lag and growing return oscillations. Two meshes help separate
the repeatable early/mid-stroke result from the sensitive late behavior. They do
not validate the damping or establish a converged hardware trajectory.

**What this says about the straw:** a shared guide has a concrete task—keeping
phased cables in a controlled common corridor through these changing demands.
The free-cable alternative would need separate corridors, more carefully shaped
commands, feedback, or another demonstrated way to preserve separation. This
experiment supplies a motivation for the guide; it leaves the comparative cost
and feasibility of those alternatives open.

'''
p=P/'README.md';old=p.read_text();start=old.find('## Results for the reference inputs');end=old.find('## Matched design numbers and scope')
if start>=0:old=old[:start]+old[end:]
old=old.replace('## Matched design numbers and scope',text+'## Matched design numbers and scope');p.write_text(old)
