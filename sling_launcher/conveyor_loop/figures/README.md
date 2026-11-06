# Conveyor concept illustrations — first review

[Concept and research plan](../README.md)

Editable SVGs for an introductory post, with PNG previews from the same source.
Muted brown denotes tether, green denotes line transport/recovery, and blue
denotes payloads and overall motion. Numbered parts are consistent across views.

## 1. Overall machine

[Download SVG](01_system_overview.svg)

![Two opposing loops around the rotating rover hub](01_system_overview.png)

Shows the hub, rover track, opposing frames, cross-tie, feed wheels and paired
payload/countermass streams. The blue rotation arrow and green feed arrows
represent different motions. Release arrows indicate the dominant tangential
launch direction, not a solved velocity vector. The line width, strand spacing,
track and wheels are enlarged independently for readability. The gray center
line summarizes static ties/supports in projection, not a cable running through
a feed spool. Individual pivot stays and separate upper/lower ties are omitted.

## 2. Feed wheel and attachment

[Download SVG](02_feed_and_attachment.svg)

![Loop feed and payload attachment detail](02_feed_and_attachment.png)

The dark clip denotes a proposed attachment device, not a specified clamp design.
Payload icons are offset from the line for visibility; their stems do not denote
vertical hangers in this top view. Attachment return, opening, wheel passage and
release routing remain unresolved. Brake/drive coupling is symbolic. The large
wheel illustrates wrap contact, without assigning a diameter or proving grip.
The outgoing strand carries loads; the unloaded line returns. Any reusable
fixtures on that return would add mass and need an explicit path.

## 3. Two-stage conveyor

[Download SVG](03_two_stage_loop.svg)

![Thick inner and thin outer loop with intermediate transfer](03_two_stage_loop.png)

Only one arm is shown. The dashed intermediate assembly contains two separately
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
| 5 | Outer turnaround wheel/assembly |
| 6 | Intermediate wheel assembly and payload-transfer interface |

## Reproduce

From the repository root:

```bash
MPLCONFIGDIR=/tmp/lunar-sling-mpl-cache .env/hub/bin/python sling_launcher/conveyor_loop/figures/build_figures.py
```

[Source](build_figures.py) writes all three SVGs and matching PNGs. SVG text stays
editable. These illustrations and the grip-analysis additions are initial review
material; they do not change the published spool design.
