# Industrial lunar sling: 10 million tonnes per year from one site

[Launcher topics](../README.md) · [Early-site paired-drum reference](../lunar_slider_straw/README.md) · [Calculated budgets](results.json)

## Question and scope

Can one lunar launch site deliver **10 million metric tonnes per Earth year** by
recovering the capabilities deliberately sacrificed in the early-site design?
The primary target here is useful mass **caught in LLO, summed across both
prograde and retrograde catchers**. Onward L1 delivery is a separate accounting
case. A backup site is outside this budget.

This is an industrial architecture study. Its design variables include catcher
cadence, useful launch directions, operating availability, payload size, number
of tether lanes, exchange duration, and hub layout. The early-site design supplies
material and geometry starting points. The earlier linear-replication inventory
is retained as a baseline in the reference report; this study supersedes it as
the route toward the industrial target.

**Initial result:** recovering both directions, daylight losses and a second
catcher window gives an ideal **8× throughput multiplier before increasing
payload size**. A one-hub candidate then requires 65.7 t payloads, a useful batch
of 1,052 t every 55.3 minutes, approximately 450 MW of payload kinetic power, and
roughly **9,860–13,015 t of working tether and guide fiber** for the two schedules
below. This is a flow-and-inventory closure. The physical layout and support
systems still need a new design.

## Recover the sacrificed factors

| Architecture step | Useful directions | Operating duty | Windows per reference orbit | Useful annual delivery with 1 t loads | Gain over early site |
| --- | ---: | ---: | ---: | ---: | ---: |
| Early-site reference | 1 | 50% | 1 | 19,016 t | 1× |
| Capture the opposing payload | 2 | 50% | 1 | 38,032 t | 2× |
| Nuclear or beamed power through night | 2 | 100% | 1 | 76,065 t | 4× |
| Two prograde and two retrograde catchers | 2 | 100% | 2 | 152,130 t | 8× |

The counterweight becomes a second delivered payload. This recovers useful output
from energy and tether mass already being spent on its acceleration. It requires
a site and release geometry that can send both sides to their respective catchers.
The earlier P1 eastward design does not by itself establish this capability.

Night operation recovers calendar utilization through a new power architecture.
The 1.5 MWh early-site battery is a short-cycle buffer; industrial nighttime
operation needs continuous generation or delivered beam power. Source, receiver,
conversion, transmission and heat rejection require explicit sizing. No nuclear
reactor or beam-system mass is assumed here.

**Additional catcher windows require additional preparation capacity.** If eight
loads per side are prepared per orbit and windows double, unchanged preparation
only supplies four loads per side per window. The final row assumes eight loads
per side at *each* of the two windows. The schedules below explicitly provide this.

The initial clock uses T = 6,633.486 s and windows separated by T/2 = 3,316.743 s.
Two catchers in each direction are assumed appropriately phased. Prograde and
retrograde targeting may require different altitudes, periods, release radii and
payload masses. Consequently a permanently synchronized T/2 calendar remains an
orbital interface to solve; the arithmetic here specifies the desired service
rather than establishing an orbit constellation.

## One-hub flow requirement

10 Mt/year is **317.10 kg/s**, or **27,397 t/day**. With two useful directions,
eight payloads per direction, and one combined release window every T/2:

`payload mass = annual target × (T/2) / (seconds per year × 16)`.

| Requirement | Ideal continuous-operation candidate |
| --- | ---: |
| Payload mass per tether | 65.733 t |
| Simultaneously released mass per direction | 525.866 t |
| Combined useful batch | 1,051.732 t |
| Working tether mass per line, at inherited 3:1 ratio | 197.200 t |
| Approximate root rope diameter at inherited fiber fill | 245 mm |
| Peak individual cable tension, scaled from reference | 74.94 MN |
| Minimum payload kinetic power at inherited release speed | 449.9 MW |
| Indicative electrical supply if reference energy efficiency persists | 561.8 MW |

The kinetic-power floor counts both delivered sides. The electrical number scales
the reference energy expenditure per launch and serves as a planning estimate;
it excludes a new nuclear/beamed-power conversion budget and does not predict
industrial friction, peak power or cooling. Acceleration and the 3:1 cable ratio
retain the reference 50 g, ~1.685 km/s and 2.438 GPa working-stress assumptions.

100% duty isolates the benefit of nighttime power. For **90% actual availability**,
the same operating cadence requires 73.04 t payloads and 11.1% higher instantaneous
flow, tension, fiber inventory and approximately power. Continuous power removes
nighttime shutdown; maintenance and outages still require an availability margin.

## Two paired-hold schedules

A mirrored group has two rigid twin-drum modules and four tethers. In an exchange,
it sends one loaded tether outward on each side while retrieving one empty tether
on each side. Eight groups finish per catcher window. Each module then holds its
extended cable and retracted mate together until its next exchange.

| Parameter | A: faster exchange | B: more simultaneous exchanges |
| --- | ---: | ---: |
| Payout/return exchange duration | T/4 = 27.64 min | T/2 = 55.28 min |
| Paired extended/retracted hold | T/2 = 55.28 min | T/2 = 55.28 min |
| New group starts every | T/16 = 6.91 min | T/16 = 6.91 min |
| Active mirrored groups | 4 | 8 |
| Outgoing / incoming lines per side | 4 / 4 | 8 / 8 |
| Installed mirrored groups / modules | 12 / 24 | 16 / 32 |
| Installed working tethers | 48 | 64 |
| Full out-and-back cycle per tether | 2.764 h | 3.685 h |
| Mean cable payout speed | 3.44 m/s | 1.72 m/s |
| Working tether fiber | 9,466 t | 12,621 t |
| Two guide-fiber allowances | 394 t | 394 t |
| **Total fiber** | **9,860 t** | **13,015 t** |

The numerical event check verifies eight completions per direction per window,
release before return, and at least the inherited 300 s reload allowance. Loading
65.7 t safely in that time is a new handling requirement. The event check assumes
instantaneous scheduling transitions; torque ramps and release sequencing require
operational simulation.

Schedule A preserves the reference number of active/installed lines and doubles
exchange speed. Schedule B preserves exchange duration and uses more active and
installed lines. Both preserve paired holding. Guide mass is still the provisional
one-tether-per-guide allowance: it must be checked against larger cargo dimensions,
contact forces, more active lines in B, bending and wear.

These inventories are approximately **0.099–0.130% of one year's useful LLO
output**. They are installed fiber, with replacement consumption additional. At
continuous operation a line completes roughly 3,169 cycles/year in A or 2,377 in B;
fatigue life therefore matters directly to the annual import stream.

## Can this fit at one site?

There are two distinct architecture choices:

1. **One enlarged hub:** retain the staged-bank logic but increase payload size,
   cable cross-sections and support capacity. The flow table demonstrates the
   required operating scale. It leaves layout and construction to solve.
2. **Several hubs within one industrial site:** divide flow across machines sharing
   power, loading and orbital infrastructure. This trades individual drum/load
   size against multiple tether sweep areas and synchronized release corridors.
   It still counts as one operating site, but needs a larger terrain footprint.

The reference swept radius is ~5.79 km, giving ~105 km² per circular sweep. Larger
payloads alone do not increase that radius at fixed acceleration and speed.
Multiple coplanar hubs require separation or controlled non-intersecting envelopes;
a simple sum of capacities does not establish a site layout.

The **77 m machinery radius and 5 m machinery height are reopened design variables**.
At 65.7 t payload mass, rope diameter grows by a factor of ~8.11. Keeping the
reference 40:1 bend ratio makes the core radius approximately **4.91 m**. Keeping
the original 1.21 m winding width gives a fully wound radius around **9.87 m**;
a roughly 20 m diameter drum cannot simply replace each original module in its
6 m-spaced row. Widening drums changes that envelope and stack height. The
accepted paired-drum mechanism may survive, while its physical arrangement changes
substantially. Direct-load winding, shaft torque, wheels, captured rails and
cross-structure must be re-sized together.

The ~75 MN individual line load is another central interface. Opposing useful
payloads balance much of the external load, while frames, drums and the straw
still transmit local forces and transient imbalance. Existing metal mass
allowances cannot be multiplied into a credible industrial BOM without this
load-path and packaging work.

One site must also supply both launch directions, material handling at tens of
thousands of tonnes/day, an industrial power plant or receiver, heat rejection,
and access for replacing large loaded reels. A site's favorable eastward terrain
alone is insufficient to select it for this architecture.

## Specialized material and onward delivery

The most defensible first specialized-material figure is the **9.86–13.02 kt
fiber inventory** under the stated material/guide assumptions. The wider
specialized-equipment budget will add precision bearings and gears, clutches,
contact surfaces, motors, power electronics, cooling equipment and the continuous
power system. That total remains to be sized. Local manufacturing fractions are
also variables of an industrial site, rather than fixed early-site percentages.

For **10 Mt/year at L1**, the inherited transfer fraction is 0.71551, requiring
**13.976 Mt/year caught at LLO**. At the same cadence, payload and fiber values
increase by approximately 1.398×: the two fiber budgets become approximately
**13.78 kt and 18.19 kt**. Retrograde captured mass needs its own transfer and
catcher-reboost calculation before assuming equal high-orbit delivery efficiency
for both directions. Capture momentum, station recovery, propellant production
and transfer vehicles belong in that end-to-end budget.

## Next design decisions and calculations

1. **Orbital service contract:** choose prograde/retrograde circular catcher orbits,
   phasing and allowable release windows; solve useful-mass split and momentum
   management. Establish whether two windows per reference orbit remain usable
   across both directions over time.
2. **One-site feasibility:** screen bidirectional release terrain and compare one
   enlarged hub against a small number of hubs at the same site. Carry catcher
   targeting and real sweep clearance into the layout.
3. **Choose payload size and lane count together:** use the two schedules as
   starting points, with drum packaging, bend radius, common-rotor exchange,
   loading throughput, guide dimensions and maintenance access as constraints.
4. **Re-size specialized hardware:** compute stroke power/torque, direct winding
   loads, traction and rail forces, and structural dimensions. Separate local
   bulk material from imported precision and polymer components.
5. **Continuous power and operations:** compare nuclear and beamed supply with
   actual conversion efficiencies and radiator temperatures; add availability,
   cycle buffers, startup, maintenance and tether-replacement inventory.
6. **End-to-end delivered mass:** quantify catcher/transfer capacity and propellant
   requirements, then report installed mass and annual specialized-material use
   per useful tonne delivered.

The first decisions should establish a credible single-site architecture before
assigning an industrial whole-machine mass. The backup second site can be added
later as an availability decision.

## Reproduction

[calculate.py](calculate.py) generates [results.json](results.json) from the saved
early-site reference. It includes paired-hold event checks for both schedules.
Run from the repository root:

```sh
.env/hub/bin/python -m sling_launcher.industrial_scale.calculate
```
