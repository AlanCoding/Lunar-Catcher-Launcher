"""Copy original bank figures into the concept packet without recalculating them."""
from pathlib import Path
import csv,json,hashlib,shutil
P=Path(__file__).parent;SOURCE=P.parents[2]/'staged_spool_bank/results';OUT=P/'power_smoothing';OUT.mkdir(exist_ok=True)
names=['single_pair_power','bank_reference_sequence']+[f'bank_{n}_reference' for n in [4,8,16,32]]
manifest=[]
for name in names:
 for ext in ['png','svg']:
  src=SOURCE/f'{name}.{ext}';dest=OUT/src.name;shutil.copyfile(src,dest)
  manifest.append(dict(asset=dest.name,source=str(src.relative_to(P.parents[3])),sha256=hashlib.sha256(dest.read_bytes()).hexdigest()))
with (SOURCE/'power_utilization.csv').open() as f:rows=[r for r in csv.DictReader(f) if float(r['reuse_windows'])==2 and int(r['released_per_window'])==int(r['tethers_per_side'])//2]
assert [int(r['tethers_per_side']) for r in rows]==[4,8,16,32]
with (OUT/'comparison.csv').open('w') as f:w=csv.DictWriter(f,fieldnames=rows[0].keys());w.writeheader();w.writerows(rows)
(OUT/'manifest.json').write_text(json.dumps(dict(method='Exact copies of original figures; four reference rows selected from source CSV',assets=manifest,source_table_sha256=hashlib.sha256((SOURCE/'power_utilization.csv').read_bytes()).hexdigest()),indent=2)+'\n')
text='''## Power smoothing: the multi-tether motivation

This is a benefit of phased multi-tether operation shared by free-cable and
straw architectures. Divide the same delivered mass among smaller payloads and
start their preparation at staggered times. Individual power pulses overlap,
while ready payloads still release in a common batch.

These are the **original smooth-profile scheduling figures**, copied directly
from the [staged-bank study](../../../staged_spool_bank/README.md). They precede
the constant-speed straw and rigid paired-drum choices. They establish the power-
smoothing opportunity; later mechanism and control choices determine how much
of it a particular machine realizes.

### Start with one payload–countermass pair

![One pair over two cycles](power_smoothing/single_pair_power.png)

[Single-pair SVG](power_smoothing/single_pair_power.svg) · [PNG](power_smoothing/single_pair_power.png)

Positive power supplies work and negative power is available for recovery.
During extension the hub supplies angular momentum while outward payout
regenerates through the spools. During empty retraction the spool pulls inward
while the hub can recover rotational energy. The tapered cable's own mass is
included in both terms. The graph shows a 1 t payload with a 1 t opposing mass,
3 t of cable per arm, and two complete cycles. Its illustrative travel phases
last 0.4T each; the bank comparison below uses 0.5T each.

### Subdivide the workload: 4 → 8 → 16 → 32

![Original power-smoothing sequence](power_smoothing/bank_reference_sequence.png)

[Sequence SVG](power_smoothing/bank_reference_sequence.svg) · [PNG](power_smoothing/bank_reference_sequence.png)

**What stays fixed:** 2,000 kg useful delivery per catcher window, the same mass
on the opposing side, T = 110.558 minutes between windows, ~1.685 km/s release
speed, 2.78 rpm rotation and 3:1 cable/payload mass. Each outward and inward stroke
lasts 55.279 minutes. Each spool repeats every two windows. Reloading takes five
minutes; completed payloads wait for their common release boundary.

N counts tethers **per side**. Powers include both sides, while useful delivered
mass counts one side. The bank contains 2N working tethers. Every row has **24 t
of ideal working tether**, and the same **0.8554 MW average net shaft demand**.
Increasing N changes the overlap and the size of each module.

| Tethers per side | Released together per window | Payload each (kg) | Extending + returning per side | Net input utilization | Net minimum / maximum (MW) |
| ---: | ---: | ---: | ---: | ---: | ---: |
'''
for r in rows:
 n=int(r['tethers_per_side']);text+=f"| {n} | {r['released_per_window']} | {float(r['payload_kg']):.0f} | {n//4} + {n//4} | {float(r['net_input_utilization_percent']):.2f}% | {float(r['net_min_MW']):.4f} / {float(r['net_max_MW']):.4f} |\n"
text+='''
[Download the comparison table](power_smoothing/comparison.csv).

**Utilization = average net shaft power / maximum net shaft power.** It measures
how fully the peak supply capacity is used, rather than conversion efficiency.
The 4-tether case has periods of net regeneration, which require another consumer,
storage or disposal. At 16 per side, net demand stays between 0.841 and 0.877 MW:
**97.55% utilization**, while eight 250 kg payloads release together each window.
At 32 per side, sixteen 125 kg payloads release together and utilization reaches
**99.50%**. Larger batches and nearly steady input coexist in these schedules.

The smoothness comes from overlapping preparation, while batching comes from
holding completed loads. The common release itself has no resolved shaft-power
pulse in this ideal model. Real release and cable transients remain a separate
engineering problem.

### Show how the overlapping pulses add up

![Sixteen tethers per side: individual contributions, total power and common release](power_smoothing/bank_16_reference.png)

The faint curves are individual contributions; the dark curves are their totals.
The schedule beneath shows eight payloads releasing together at each window.
This is a useful companion to the overview because it exposes the mechanism
behind the smoothing.

Individual original figures, including their schedules:

| Tethers per side | SVG | PNG |
| --- | --- | --- |
'''
for n in [4,8,16,32]:text+=f'| {n} | [SVG](power_smoothing/bank_{n}_reference.svg) | [PNG](power_smoothing/bank_{n}_reference.png) |\n'
text+='''
### What the comparison establishes

The travel commands are quintic smoothsteps with zero endpoint velocity and
acceleration. Radial co-rotation is imposed in the energy model, and ideal
regeneration is combined with hub demand. Losses, motor and reel hardware,
guide contacts, battery smoothing and transverse cable dynamics are outside
these original curves. The free-cable angle study addresses part of that missing
dynamics; the paired-drum straw reference has its own revised power history.

The common two-window cycle requires twice the cable inventory of one 2 t payload
pair with 3:1 cables completing a one-window cycle. Once that two-window inventory
is established, subdivision from 4 to 32 per side adds no ideal tether mass.
It does add reels, attachments and control channels. This is the conceptual
trade: more parallel mechanisms can reduce peak power while preserving delivered
mass and common releases.

These original plots establish the power benefit of multi-tether scheduling
shared by both free-cable and straw-guided architectures.
[Asset provenance](power_smoothing/manifest.json) records exact-copy hashes.
Regenerate this packet section and its copies with
`python -m sling_launcher.lunar_slider_straw.publication.concept.package_power`.

'''
p=P/'README.md';doc=p.read_text();heading='## Power smoothing: the multi-tether motivation'
start=doc.find(heading)
if start>=0:
 end=doc.find('\n## ',start+len(heading))
 if end<0:end=len(doc)
 doc=doc[:start]+text.rstrip()+'\n'+doc[end:]
else:doc=doc.rstrip()+'\n\n'+text
p.write_text(doc)
