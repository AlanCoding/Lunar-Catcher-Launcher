# Conveyor concept illustrations — second review

[Concept and research plan](../README.md)

Editable SVGs for an introductory post, with PNG previews from the same source.
Muted brown denotes tether, green denotes line transport/recovery, and blue
denotes payloads and overall motion. Numbered parts are consistent across views.

## 1. Overall machine

[Download SVG](01_system_overview.svg)

![Two opposing loops around the rotating rover hub](01_system_overview.png)

Shows the hub, rover track, opposing frames, cross-tie, feed wheels, free outer loop turns and paired
payload/countermass streams. The blue rotation arrow and green feed arrows
represent different motions. Small green quarter-circle arrows show both feed
wheels circulating counterclockwise, in the same sense as the hub. Countermasses
ride the upper left strand; useful payloads ride the lower right strand. Release arrows indicate the dominant tangential
launch direction, not a solved velocity vector. The line width, strand spacing,
track and wheels are enlarged independently for readability. The gray center
line summarizes static ties/supports in projection, not a cable running through
a feed spool. Individual pivot stays and separate upper/lower ties are omitted.

## 2. Feed wheel and attachment

[Download SVG](02_feed_and_attachment.svg)

![Loop feed and payload attachment detail](02_feed_and_attachment.png)

The dark clip is a reusable attachment device: it returns on the upper strand
and receives a new payload halfway around the feed wheel’s inboard contact arc.
The left-side loader is intended to read as integrated with the rover/A-frame;
this placement is illustrative, not a selected loading mechanism. Payload icons are
offset from the line for visibility; their stems do not denote vertical hangers.
Brake/drive coupling is symbolic. Wheel passage and loading hardware are not
specified. There is **no wheel drawn at the free outer turn**. Its shape is
schematic; a dynamically sustainable wheel-free turn remains to be modeled.

The inset shows a controlled extension from attachment to payload: progressively
reduce support force, then detach. The suggested **approximately 10 m** stroke
is an unsized concept input, not a demonstrated sufficient release distance.
The little force curve is a desired qualitative profile, not simulation output.
The attachment remains with the line and returns for reuse.

[Rüdiger's tether-dynamics simulation](https://blog.klaehn.org/blog/lunar-sling-launcher-tether-dynamics/)
shows reflected release waves breaking his modeled tether and explores controlled
unloading and active damping. It motivates this feature, but does not validate
our conveyor or a 10 m stroke. His example uses different geometry and loading;
our release duration, stroke and remaining waves require simulation.

## 3. Two-stage conveyor

[Download SVG](03_two_stage_loop.svg)

![Thick inner and thin outer loop with intermediate transfer](03_two_stage_loop.png)

Only one arm is shown. Return clips and the wheel-free outer turn carry over
from figure 2; the two intermediate wheels remain part of this concept. The dashed intermediate assembly contains two separately
drawn wheels joined by a short local structure. This is a readable alternative
schematic to the handoff's possible coaxial sheaves, not a selected mechanism.
It does not imply a rigid support from the hub. The transfer arrow represents
handoff of one payload, not two simultaneous copies or unsupported free flight.
Widths distinguish the two constant-section loops; they do not encode a sized
area ratio. Straight spans are schematic: no Coriolis shape or stress result is
claimed. A mirrored machine needs the corresponding opposite arm and release.

## Part key

| ID | Part |
| --- | --- |
| 1 | Central hub / ground pivot |
| 2 | Rover and A-frame assembly, viewed from above |
| 3 | Inner conveyor feed / regenerative brake wheel |
| 4 | Payload and line attachment device |
| 5 | Free outer loop turn (no tip pulley in this iteration) |
| 6 | Intermediate wheel assembly and payload-transfer interface |

## Reproduce

From the repository root:

```bash
MPLCONFIGDIR=/tmp/lunar-sling-mpl-cache .env/hub/bin/python sling_launcher/conveyor_loop/figures/build_figures.py
```

[Source](build_figures.py) writes all three SVGs and matching PNGs. SVG text stays
editable. These illustrations and the grip-analysis additions are initial review
material; they do not change the published spool design.
