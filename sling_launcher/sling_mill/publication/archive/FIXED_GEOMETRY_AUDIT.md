# Historical fixed-geometry iron hardware audit

This checkpoint preceded the thinner-plate optimization and the included full-sun solar array. Its 13,401-tonne, 11.74-hour result is retained for provenance. The [current article](../ARTICLE.md) gives the selected publication case.

## Updated mill: fixed geometry, explicit hardware

The iron audit holds the rounded reference's drum diameter (1.12 m), pitch (1.14 m), bar dimensions (2.30 × 0.26 × 0.020 m), 0.8 mm squeeze and 1 GPa Zylon ceiling. Its mass flow remains **317.10 kg/s**, or **10 million tonnes per 365 operating days**. Higher payload density changes the derived acceleration and required corridor length.

| Quantity | Iron reference |
|---|---:|
| Bar mass / feed rate | 94.01 kg / 3.373 bars/s |
| Maximum acceleration | 834.62 m/s² = **85.11 Earth g** |
| Corridor / equivalent opposed pairs | 8.283 km / 7,265.6 |
| Mean electrical input | 427.41 MW |
| Installed aggregate motor rating, with 20% headroom | 512.89 MW |
| Individual motor rating, entrance to exit | 0.77–191.37 kW per drum |
| Payload center above level ground | 1.33 m |
| Upper roller axis / top of roller | 1.90 m / 2.46 m |
| Structural Zylon peak stress | 0.986 GPa |
| Conditional accelerator mass | **13,401 tonnes** |
| Gross mass payoff | **11.74 operating hours** |

The older 1.46-hour optimized result already included non-fiber hardware, but used much lighter allowances and a hypothetical 3,000 kg/m³ payload. This revision changes both material and hardware accounting; it is a fixed-geometry estimate, with substantial scope for structural redesign.

| Inventory | Tonnes |
|---|---:|
| Structural belts and radial/torque cables | 143.5 |
| Contact layers | 9.3 |
| Hubs, bearings and startup supports | 124.3 |
| Motors and installed-drive allowance | 2,917.1 |
| Power electronics / cabling allowance | 256.4 |
| Height-aware support frames | 8,185.5 |
| Foundations | 1,453.1 |
| Guides | 165.7 |
| Motor radiators | 146.0 |
| **Total** | **13,400.8** |

### Hardware sizing and its uncertainty

The [reproducible audit](../../blended/hardware_audit.py) sizes four steel uprights and two cross beams per opposed pair. Ground clearance is 0.20 m; uprights reach the upper axle. Square hollow sections are selected for 100 MPa working stress, 200 GPa modulus, Euler capacity, a 1.5 contact-load factor and a **0.1 mm lateral displacement allowance**. Each cross beam has a 0.05 mm deflection screen. Section widths range from 140 to 540 mm; wall thickness is at least 4 mm or width/30. A 25% allowance covers gussets and connections, and column loads include approximate self-weight. Full simultaneous contact force sizes frames even though motors supply mean energy.

This conservative freestanding-column model makes stiffness dominate the mass. The 0.1 mm lateral tolerance is an engineering assumption, not a derived stability requirement. Bracing, shared frames, a shallow trench, and a validated alignment tolerance could greatly reduce this term. Axial column stretch and joint compliance must be included in a future detailed nip-gap stiffness budget. Foundations retain the earlier **200 kg/pair allowance**; anchorage into lunar ground requires a separate design. Thus this is a more explicit machine budget, with support stiffness as a major open variable.

Motors reuse the slider-straw study's **4.55 kg/kW industrial mass anchor**, plus 25% installation allowance, and now have 20% rating headroom. Each stage is sized from its own mean contact power, rather than assigning the full machine's power to every roller. Rotor storage still supplies the short contact pulses. The corresponding rotor-speed range is roughly 1,700–27,400 rpm: the mass anchor is an allowance for drive development, not a selected high-speed motor product. Power electronics/cabling receive a separate assumed 0.5 kg/kW. Radiators retain the model's 95% conversion efficiency and reject about 21.37 MW of drive loss; rating headroom does not itself consume power.

A useful support-mass sensitivity is exact for this fixed performance model: each **1,000 tonnes** removed from or added to frames changes payoff by **0.876 operating hour**. The result should be improved through structural design before rerunning the global mass optimizer.

### Power plant and site boundary

The accelerator estimate includes the inventory above. A 427 MW power source, the 0–100 m/s injector, mining/refining/bar production, catcher, maintenance stocks and deployment are additional infrastructure. Illustrative power-source additions of 1, 5 and 10 kg/kW change the total to **13,828 / 15,538 / 17,675 tonnes**, and payoff to **12.11 / 13.61 / 15.48 operating hours**. Those are mass sensitivities, not selected plant technologies.

The 10-million-tonne annual target assumes continuous supply. A 50% daylight duty would halve annual output at unchanged instantaneous flow; operating-hour payoff remains unchanged, while calendar payoff depends on outages and night scheduling.
