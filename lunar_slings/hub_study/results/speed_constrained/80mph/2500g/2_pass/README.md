# 2500 g, 80 mph, 2 catcher pass(es)

A conditional engineering scenario, **not a qualified buildable design**. Inputs and all outputs: [metrics.json](metrics.json). Full time history: [history.csv](history.csv). [Equations and limits](../../../METHOD.md). [All scenarios](../../../README.md).

Payload: 1,000 kg useful + 1,000 kg equal-radius rock countermass. Acceleration label means release centripetal acceleration; the vector peak is separately reported. Track radius is derived, never optimized independently.

## Geometry and mechanical demands

| Metric | Result |
| --- | ---: |
| Track radius (dependent) | 2.457 m |
| Release radius | 115.743 m |
| Each cable material length | 113.285 m |
| Apex height, including 3 m clearance | 3.010 m |
| Vertical leg / nominal pole height | 3.010 m |
| 45° trailing leg length | 4.257 m |
| Release tip speed relative to site | 1,684.524 m/s |
| Peak payload proper acceleration | 2,500.000 Earth g |
| Ballast, total two frames | 527,210.152 kg |
| Ballast lunar weight | 855,615.085 N |
| Ballast allocated per powered wheel | 131,802.538 kg |
| Powered-wheel normal load, average | 172,212.144 N |
| Powered contact area at assumed 100 kPa | 1.722 m² |
| Required compact-frame radial support half-width | 965.343 m |
| Extra inward ballast restraint per frame | 137,206,140.017 N |
| Main tie endpoint tension envelope | 328,861,427.732 N |
| Main tie sag estimate | 0.000 m |
| Fiber volume stored per spool (before packing allowance) | 12.664 m³ |
| Root cable equivalent solid diameter | 0.494 m |
| Empty cable tip equilibrium shift at release | 0.001 m |
| Two-cable release shape energy discontinuity | -43.916 J |
| Flight to catcher | 1,629.824 s |
| Catcher encounter relative speed | 19.213 m/s |

The 45° same-track geometric fit test **passes** (height must be smaller than track diameter). Passing is only a necessary condition; wheel size, frame interference, and contact moments remain unresolved.

## Mass composition

| Category | Permanent import kg | Local permanent kg | Status |
| --- | ---: | ---: | --- |
| B04: two outward Kevlar cables | 36,726.5 | — | Fiber only, static total-stress taper |
| B05: apex-to-apex main tie | 2,344.9 | — | Conditional tensile sizing; restraint geometry unresolved |
| B16: solar, no recovery | 144,914.3 | — | Assumed installed array 100 W/kg |
| B16: solar, 70% recovery (alternative) | 104,101.6 | — | Same W/kg assumption; instantaneous recovery only |
| B21: wheel rock ballast | — | 527,210.2 | Tangential traction model, no unsized hardware weight credit |
| B01–B03: poles, braces, apex joints | **Unsized** | — | Radial bending and tipping unresolved; old axial-only pole masses withdrawn |
| B06–B07: stabilizers, terminations, guides, sheath | Unsized | — | Small stabilizer force is not demonstrated |
| B08–B10: 4 powered + 4 passive wheels, drives, steering | Unsized | — | Capacity and speed qualification needed |
| B11: 2 operating reels and drives | Unsized | — | Cable inventory volume and power given; bend life and drums unresolved |
| B12–B13: pivot and anchors | Unsized | — | Stabilizing load path unresolved |
| B14–B15: climbers and their service hardware | Not used | — | This branch uses spooling instead |
| B17–B20: conversion, control, thermal, ballast retention | Unsized | — | These are not zero-mass equipment |

Accounted imported subtotal / useful payload: **184.0** without recovery, **143.2** with recovery. These are **incomplete subtotals, not launcher mass ratios**. Pole/total imported mass is explicitly null in JSON. Solar stays on the ground; other unsized moving hardware and this tie subtotal are not fed back into the cycle inertia/normal-load solution.

B22 rock expendable: 1,000 kg per release; B23 useful payload: 1,000 kg. Equal-radius rock **does not impact the reference sphere** in this calculation, so disposal is not closed. Loading/release machinery and prepared-road construction remain excluded.

## Timeline and power

| Segment | Minutes | Peak wheel input MW | Peak reel input MW | Available reel braking MW |
| --- | ---: | ---: | ---: | ---: |
| loading | 5.000 | 0.674 | 0.000 | 0.000 |
| payout | 105.558 | 12.318 | 0.000 | 5.830 |
| retraction | 105.558 | 0.655 | 4.868 | 0.000 |
| buffer | 5.000 | 0.664 | 0.000 | 0.000 |

Peak direct solar: **14.491 / 10.410 MW** (none / 70% recovery). Cycle solar energy: 49.972 / 29.199 GJ. Recovery has no effect on required mechanical traction. Four wheel drives share the wheel demand only under equal load sharing; two reels share the reel demand.

Peak ground force occurs in payout at 83.86% deployment. Rover speed is 35.717–35.763 m/s: cruise equals the specified operating speed; slowing during loading/buffer closes phase without exceeding it.

The release transient is **not fitted into this timeline**. The reported empty-cable displacement compares equilibria, not a predicted recoil trajectory. Its energy discontinuity is excluded from branch energy/power totals and could require a dwell or a slower cadence. Loading is a fixed 5-minute allowance, not a demonstrated service mechanism. Daylight only; no night operation or stored-energy credit.

![Cycle powers and rover speed](cycle.svg)

![Finite-angle shapes](../shapes.svg)
