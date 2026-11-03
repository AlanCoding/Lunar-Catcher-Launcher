# The 50-g design at a glance

**The top of each A-frame is 28.68 m above the ground datum.** The vertical
steel member is shorter—25.44 m—because its bottom is at the powered wheel's
3.24 m-high axle. The other member slopes backward and is 35.97 m long.
These are the dimensions shown in the current Blender diagram.

This sheet describes the **50 mph, one-pass, 50-g reference candidate**.
It is the lowest imported-mass point sampled in the reference hardware sweep,
not a claim that every possible design has been optimized.

## Size and shape

| Part or distance | Human-readable value |
| --- | --- |
| Circular track | **76.79 m radius; 153.58 m diameter** |
| Number of A-frames | **Two**, opposite each other |
| Pole-top / tether attachment height | **28.68 m** above the central ground datum |
| Legs per A-frame | One **25.44 m vertical** leg and one **35.97 m trailing** leg |
| Vertical leg tube | **0.640 m outside diameter**, **21.3 mm wall** |
| Trailing leg tube | **0.798 m outside diameter**, **26.6 mm wall** |
| Wheels | **Four powered + four passive**, two of each per A-frame |
| Powered wheel | **6.48 m diameter × 2.27 m width** |
| Passive wheel | **3.74 m diameter × 1.31 m width** |
| Wheel arrangement | Powered/passive pair fore-and-aft at each pole foot |
| Useful payload distance from center at release | **5.787 km** |
| Each outward sling's deployed length | Approximately **5.710 km** |
| Full payload-to-countermass span | Approximately **11.574 km** |
| Outward rope diameter | About **86.7 mm near the frame**, tapering to **31.0 mm at the payload** |
| Upper cross-track tie | Approximately **153.58 m** span between apexes |
| Low cross-track connection height | Approximately **3.74 m**, near the wheels/ballast |
| Low tie cruise sag | Approximately **7 mm** |
| Reel core radius / full storage-envelope radius | **1.73 m / 2.33 m** |
| Modeled reel width | **3.47 m** |
| Assumed core-diameter / maximum rope-diameter ratio | **40:1** |
| Illustrated outward reels | **Two total**, one for payload and one for countermass; cross-ties are static |

Rope diameters include the assumed 65% fiber packing fraction. The low
connection is drawn as two half-load ties; their combined mass equals the
model's aggregate low-tie allowance. Exact end fittings remain schematic.

The 40:1 ratio is a sizing assumption, not a demonstrated fatigue-life limit.
The illustration has one reel per outward tether; the frozen mass model retains
its capstan/storage allowance. See [reel assumptions and scenario dimensions](REEL_ASSUMPTIONS.md).

## Motion and operating cycle

| Parameter | Value |
| --- | --- |
| Useful payload per successful launch | **1,000 kg** |
| Expendable rock countermass | **1,000 kg per launch** |
| Rover speed | **50 mph = 22.352 m/s** |
| Payload acceleration at release | **50 Earth g**, about **490 m/s²** |
| Payload speed at release, relative to the site | Approximately **1.685 km/s** |
| Machine rotation rate at release | **2.78 rpm**, one revolution every **21.59 seconds** |
| Powered-wheel rotation at cruise | Approximately **65.8 rpm** |
| Catcher revisit / planned launch cycle | **110.558 minutes** |
| Loading allowance | **5 minutes** |
| Payout / return time | Approximately **50.28 minutes each** |
| Timing buffer | **5 minutes** |
| Power strategy | Direct solar with simultaneous regeneration; no nighttime storage credit |

The cycle is a modeled operating target, not a demonstrated deployment,
release and capture sequence. One fast machine revolution is not one launch:
loading, payout and return occupy many revolutions within a catcher revisit.

## What the different tethers do

- **Upper apex-to-apex tie:** carries the opposing payload/counterweight radial
  forces and upper assembly loads. Those payload forces do not go through wheel
  traction.
- **Low connection between opposing wheel assemblies:** turns the rovers and
  ballast around this small track. With the adopted friction assumption, the
  road-only radius threshold is about **616 m**, so the **76.79 m** design is
  firmly in the low-tie regime. No banked track is assumed.
- **Two apex-to-ground-pivot stays:** run from the pole tops to the center
  swivel. They are highlighted muted sage green in the diagram. They are distinct from
  both cross-track connections. The small floating low-tie crossing junction
  above the pivot is not the ground-mounted swivel.

The pivot/stay mass remains excluded by instruction. Their illustration does
not constitute a strength calculation. The 1.05 m swivel height, 3.6 m
foundation diameter and stay thickness shown in Blender are schematic; the
sage-green lines are widened to make them readable. Do not cite those as optimized
structural dimensions.

## Mass and power in round numbers

| Quantity | Reference value |
| --- | ---: |
| Imported permanent equipment | **1,253 tonnes** |
| Local permanent rock ballast | **1,193 tonnes** |
| Whole permanent machine | **2,446 tonnes** |
| Four pole legs together, including joint allowance | **63.5 tonnes** |
| Low-tie fiber plus end connections | **1.27 tonnes** |
| Peak required solar output | **21.97 MW** |
| Peak modeled waste heat | **8.89 MW** |
| Radiator emitting area | **33,123 m²**, about **3.31 hectares** |
| Solar area in the illustration | **109,834 m²**, about **11.0 hectares**, assuming **200 W/m²** |

Solar area is an illustration assumption; solar mass was sized using 100 W/kg.
Radiator area is a model output under the stated temperature/view assumptions.
Motor housings, ballast-bin packaging, terrain and the depicted 22 m track
width are also illustrative, not additional optimized dimensions.

## How much does the outward tether droop?

In the illustrated fully deployed loaded pose, its centerline falls from
**28.68 m at the apex to 0.88 m above the central datum at the payload**—about
**27.80 m of drop** over 5.71 km of rope. Lunar curvature puts the terrain below
the payload roughly 9.63 m below that datum, leaving **10.51 m centerline
clearance** there. The design's **3 m clearance margin** is controlled by another
point in the cycle, not by this particular pose.

[The droop diagram](../blender/renders/droop_diagram.png) uses different horizontal
and vertical axis scales so the shape is readable. The Blender scene keeps
true position/height scales; distant views widen rope highlights explicitly.

## Blog source links

[Checkpoint](CHECKPOINT.md) · [Mass table](MASS_TABLE.md) ·
[Mass-payoff calculations](MASS_PAYOFF.md) · [Model and scenario study](../results/split_tie/README.md) ·
[Manufacturer sources and assumptions](../results/hardware_mass/SOURCES.md) ·
[Illustration guide](../blender/README.md) · [Exact candidate data](candidate_50g.json)
