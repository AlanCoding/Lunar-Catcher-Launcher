# 125 g, 80 mph, 1 catcher pass(es)

A conditional engineering scenario, **not a qualified buildable design**. Inputs and all outputs: [metrics.json](metrics.json). Full time history: [history.csv](history.csv). [Equations and limits](../../../METHOD.md). [All scenarios](../../../README.md).

Payload: 1,000 kg useful + 1,000 kg equal-radius rock countermass. Acceleration label means release centripetal acceleration; the vector peak is separately reported. Track radius is derived, never optimized independently.

## Geometry and mechanical demands

| Metric | Result |
| --- | ---: |
| Track radius (dependent) | 49.145 m |
| Release radius | 2,314.852 m |
| Each cable material length | 2,265.712 m |
| Apex height, including 3 m clearance | 6.972 m |
| Vertical leg / nominal pole height | 6.972 m |
| 45° trailing leg length | 9.860 m |
| Release tip speed relative to site | 1,684.523 m/s |
| Peak payload proper acceleration | 125.000 Earth g |
| Ballast, total two frames | 1,149,428.941 kg |
| Ballast lunar weight | 1,865,420.720 N |
| Ballast allocated per powered wheel | 287,357.235 kg |
| Powered-wheel normal load, average | 361,550.764 N |
| Powered contact area at assumed 100 kPa | 3.616 m² |
| Required compact-frame radial support half-width | 111.801 m |
| Extra inward ballast restraint per frame | 14,956,920.848 N |
| Main tie endpoint tension envelope | 24,539,715.397 N |
| Main tie sag estimate | 0.003 m |
| Fiber volume stored per spool (before packing allowance) | 12.664 m³ |
| Root cable equivalent solid diameter | 0.110 m |
| Empty cable tip equilibrium shift at release | 0.300 m |
| Two-cable release shape energy discontinuity | -17,566.524 J |
| Flight to catcher | 1,629.825 s |
| Catcher encounter relative speed | 19.340 m/s |

The 45° same-track geometric fit test **passes** (height must be smaller than track diameter). Passing is only a necessary condition; wheel size, frame interference, and contact moments remain unresolved.

## Mass composition

| Category | Permanent import kg | Local permanent kg | Status |
| --- | ---: | ---: | --- |
| B04: two outward Kevlar cables | 36,726.7 | — | Fiber only, static total-stress taper |
| B05: apex-to-apex main tie | 3,499.6 | — | Conditional tensile sizing; restraint geometry unresolved |
| B16: solar, no recovery | 304,240.3 | — | Assumed installed array 100 W/kg |
| B16: solar, 70% recovery (alternative) | 218,555.3 | — | Same W/kg assumption; instantaneous recovery only |
| B21: wheel rock ballast | — | 1,149,428.9 | Tangential traction model, no unsized hardware weight credit |
| B01–B03: poles, braces, apex joints | **Unsized** | — | Radial bending and tipping unresolved; old axial-only pole masses withdrawn |
| B06–B07: stabilizers, terminations, guides, sheath | Unsized | — | Small stabilizer force is not demonstrated |
| B08–B10: 4 powered + 4 passive wheels, drives, steering | Unsized | — | Capacity and speed qualification needed |
| B11: 2 operating reels and drives | Unsized | — | Cable inventory volume and power given; bend life and drums unresolved |
| B12–B13: pivot and anchors | Unsized | — | Stabilizing load path unresolved |
| B14–B15: climbers and their service hardware | Not used | — | This branch uses spooling instead |
| B17–B20: conversion, control, thermal, ballast retention | Unsized | — | These are not zero-mass equipment |

Accounted imported subtotal / useful payload: **344.5** without recovery, **258.8** with recovery. These are **incomplete subtotals, not launcher mass ratios**. Pole/total imported mass is explicitly null in JSON. Solar stays on the ground; other unsized moving hardware and this tie subtotal are not fed back into the cycle inertia/normal-load solution.

B22 rock expendable: 1,000 kg per release; B23 useful payload: 1,000 kg. Equal-radius rock **does not impact the reference sphere** in this calculation, so disposal is not closed. Loading/release machinery and prepared-road construction remain excluded.

## Timeline and power

| Segment | Minutes | Peak wheel input MW | Peak reel input MW | Available reel braking MW |
| --- | ---: | ---: | ---: | ---: |
| loading | 5.000 | 1.506 | 0.000 | 0.000 |
| payout | 50.279 | 25.860 | 0.000 | 12.241 |
| retraction | 50.279 | 1.377 | 10.221 | 0.000 |
| buffer | 5.000 | 1.496 | 0.000 | 0.000 |

Peak direct solar: **30.424 / 21.856 MW** (none / 70% recovery). Cycle solar energy: 50.483 / 29.710 GJ. Recovery has no effect on required mechanical traction. Four wheel drives share the wheel demand only under equal load sharing; two reels share the reel demand.

Peak ground force occurs in payout at 83.86% deployment. Rover speed is 35.482–35.763 m/s: cruise equals the specified operating speed; slowing during loading/buffer closes phase without exceeding it.

The release transient is **not fitted into this timeline**. The reported empty-cable displacement compares equilibria, not a predicted recoil trajectory. Its energy discontinuity is excluded from branch energy/power totals and could require a dwell or a slower cadence. Loading is a fixed 5-minute allowance, not a demonstrated service mechanism. Daylight only; no night operation or stored-energy credit.

![Cycle powers and rover speed](cycle.svg)

![Finite-angle shapes](../shapes.svg)
