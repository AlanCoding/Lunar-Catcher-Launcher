# External data and mass-curve provenance

Checked 2026-10-31. These are manufacturer/research anchors for a conceptual
mass estimate, not selected hardware qualified for lunar operation. “Cost” in
this study means mass penalty, not a dollar purchase quote. Numeric constants
live in `component_sizing.py`; every result records its complete assumptions.

## Poles: SSAB steel data, calculated structural sections

[SSAB Strenx 700 E/F](https://www.ssab.com/en/brands-and-products/strenx/product-offer/700/e-f)
lists minimum yield 700 MPa through 53 mm plate thickness and 650 MPa for
thicker plate, through 160 mm. We use 650 MPa throughout, divided by 2 for
combined stress sizing. Plate thickness beyond 160 mm is flagged as outside
this source domain. Fabricated tubes are not claimed to be stocked products.

[SSAB structural hollow section handbook, §1.6.3](https://www.ssab.com/-/media/8952369CD8E149889C9AE7D6AB8D414D.ashx)
gives E=210 GPa and density=7,850 kg/m³. Those drive stiffness, self-weight and
mass; increasing yield strength alone does not increase E.

The beam-column equations are derived engineering calculations. K=2, Euler
reserve factor=2, diameter/wall<=30, 4 mm minimum wall, deflection<=L/150 and
20% joint/bracing mass are **our explicit preliminary design policies**, not
values certified by SSAB for this launcher. Lower/heavier joint allowances
are 10%/35%. Thermal fatigue, weld qualification and local details need design.

## Wheels: three Michelin mass/load/dimension anchors

| Manufacturer product | Diameter m | Width m | Tire mass kg | Maximum listed transport load, Earth kg | TKPH |
| --- | ---: | ---: | ---: | ---: | ---: |
| [XTRA LOAD PROTECT 18.00R33](https://business.michelinman.com/tires/michelin-x-tra-load-protect) | 1.888 | 0.498 | 473 | 13,100 | 194 |
| [XD GRIP 27.00R49](https://business.michelinman.com/tires/michelin-xd-grip) | 2.726 | 0.733 | 1,330 | 32,100 | 720 |
| [XDR4 EXTRA LOAD 59/80R63](https://business.michelinman.com/tires/michelin-xdr4-extra-load) | 4.027 | 1.495 | 5,350 | 115,000 | 1,840 |

Earth load ratings are converted to **newtons using Earth gravity**, then
compared with actual lunar wheel normal force. A lunar ballast mass is never
compared directly with an Earth tire's kilogram load rating.

Log-log least-squares fits supply tire mass versus diameter and load versus
diameter. Diameter must also provide the assumed ground footprint. Baseline
contact pressure is 100 kPa, width=0.35D, contact length=0.4D. Sensitivities use
250/50 kPa. These road-pressure values are assumptions, not measured site data.
A thermal-work proxy scales the largest tire's TKPH with D² and is checked
against equivalent Earth tonnes times km/h; this is an explicit extrapolation,
not a lunar vacuum cooling law. The output identifies which constraint sizes D.

Installed wheel mass is tire-analog mass ×2.1, with 1.5–3.0 sensitivity for
rim, hub, bearing, suspension/attachment and lunar adaptation. These factors
are estimates, not Michelin data. The proposed wheel can ultimately be metallic
or airless: the terrestrial tires supply a mass scale, not a claim that ordinary
rubber tires survive the lunar environment at 50–80 mph. Larger-than-anchor
wheels are flagged. Four powered and four passive wheels remain fixed counts.

## Motors and inverters: continuous ratings, not advertising peak power

| Dana model | Continuous kW | Motor kg | Inverter kg |
| --- | ---: | ---: | ---: |
| SUMO MD HV1800-3P | 100 | 180 | 13 |
| SUMO MD HV2200-3P | 145 | 225 | 13 |
| SUMO MD HV2200-6P | 190 | 225 | 25 |
| SUMO HD HV3500-9P | 260 | 340 | 38 |

Sources: [Dana SUMO MD sheet](https://www.dana.com/link/dd5c120156ee49e9a70b929c75a8b9f3.aspx)
and [Dana SUMO HD sheet](https://www.dana.com/globalassets/resource-library/crossover-resources/spec-sheets/2441_tm4_sumo_family_hd_v03r00.pdf).
The HD continuous torque is 1,970 Nm. The baseline motor curve above the anchor
uses 340/260 kg per continuous kW, with 25% installation/adaptation mass. The
inverter curve uses 38/260 kg/kW separately. Nominal motor speed is P/T; chosen
reduction and required continuous torque are checked as well as power.
Direct PDF access to the HD sheet returned 403, so its figures were checked
from the indexed manufacturer spec-sheet table; MD data are likewise indexed.

The heavier motor branch uses 4.55 kg/kW, anchored to ABB's historical
[M3BP 450 LC, 1,000 kW, 2,990 rpm, 4,550 kg](https://library.e.abb.com/public/bfb9dbeb7b84d511c1257b130057106f/PPM%20M3BP%20450%20GB%2006_2004.pdf),
printed p.7. This is a 2004 continuous industrial motor benchmark, not a current
availability claim. It is an intentionally heavier comparison, not evidence
that all modern motors need that mass. Neither terrestrial cooling system is
assumed to work unchanged in vacuum; heat rejection is separately budgeted.

The model retains **four scaled wheel motors and two scaled reel motors**.
Multi-megawatt values extrapolate the anchors; they do not secretly add dozens
of powered wheels. Every result reports the scale factor from the 260 kW anchor.

## Reduction gearing: Flender torque/mass curve

[Flender PLANUREX 3, FLE 20.3, p.2/2](https://www.flender.com/en/media-download/media/Planurex_3_Catalog),
P3DP table, supplies these nominal torque / dry mass anchors:
480 kNm / 2,250 kg; 1,050 kNm / 4,500 kg; 2,260 kNm / 11,420 kg;
4,010 kNm / 20,470 kg; 5,450 kNm / 29,500 kg.
The footnote excludes the shrink disk and oil. A 1.4 installed multiplier
covers that interface, lubricant and adaptation allowance; it is our estimate.
The indexed manufacturer's complete table was used; web extraction could not
open the 27.8 MB PDF as a whole.

A log-log torque/mass fit is evaluated at 1.5 times maximum transmitted torque.
A separate 2 kg/kW power floor (1–3 sensitivity) prevents a high-speed/high-power
gearbox being sized from torque alone. **That power floor is an assumption**;
these mass anchors do not prove a matching thermal rating or ratio for this
application. Reel torque above 5.45 MNm is an extrapolation, and strongly affects
the optimum. The power- and torque-governed estimates are not added together;
the larger governs, followed by the installed multiplier.

## Reels and heat rejection

[Marlow's rope FAQ](https://www.marlowropes.com/us/services/faqs/)
identifies larger sheaves for aramid compression fatigue and gives a typical
20:1 diameter ratio. The [UNOLS handbook, §2.1.A](https://www.unols.org/sites/default/files/handbook.pdf)
describes Kevlar bend testing at 40:1. We use 40:1 with 20/50 sensitivity,
not a claim of established fatigue life for this tapered lunar cable. Fiber
fill=0.65 and winding fill=0.75 are explicit volume estimates.

A tension-bearing capstan and low-tension storage reel are massed separately
within each apex assembly using shaft torsion, rim force and shell volume.
This avoids treating a many-layer storage drum under full line tension as
an adequately designed structure. The shaft/rim/support formulas are preliminary
engineering estimates, not supplier winch selections. Full cable-guide,
traction-capstan and bending-loss engineering remains open.

The current illustration shows one outward reel per apex and no cross-tie
reels; the above numerical allowance is unchanged. See the
[reel bend-ratio and scenario note](../../publication/REEL_ASSUMPTIONS.md)
for dimensions, physical scaling limitations and this illustration distinction.

[NASA/TM-20220013310, radiator sizing tables](https://ntrs.nasa.gov/api/citations/20220013310/downloads/TM-20220013310.pdf?attachment=true)
provides itemized lunar-radiator mass coefficients totaling approximately
7.8 kg/m². We use 8 kg/m², 6–12 sensitivity, plus 20% heat-transport allowance.
Area follows Stefan–Boltzmann net radiation with emissivity 0.85, view factor
0.7, baseline 330 K radiator and 250 K effective sink. Those temperatures/view
factor are operating assumptions, not a guarantee of equatorial daytime
performance. Shading and transport must be arranged to achieve them. Thermal
hardware is budgeted as stationary; a moving heat-transfer interface is an
unresolved integration requirement represented only by the allowance.

## Other explicit estimates and exclusions

Solar remains 100 W/kg at operating illumination, the existing study input.
Controls/harness are 2% of wheel/drive equipment; steering hardware is 10% of
passive-wheel mass. Fittings/sheathing are 10% of outward cable fiber mass.
Ballast retention takes a 0.5% mass floor or a force/strength-based member
estimate, whichever is larger. These are visible subsystem allowances, not
manufacturer measurements or a global contingency masking missing poles.
Central pivot and stabilizing-tether mass are set to zero by the user's current
instruction. Their required reaction moment remains an output. Loading/release
mechanism and road construction remain excluded under the original scope.
