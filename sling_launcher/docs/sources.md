# Source register

Initial discovery/access: 2026-10-31. These are source leads and scope evidence,
not approved engineering inputs. Store exact edition/page/table and applicability
with each numerical property before using it in the model.

| ID | Source | Current use and limitation |
| --- | --- | --- |
| S1 | DuPont, *Kevlar Aramid Fiber Technical Guide*, historical March 2019 filename, [manufacturer URL](https://www.dupont.com/content/dam/aramids/amer/us/en/safety/public/documents/en/Kevlar_Technical_Guide_0319.pdf) | Search-indexed yarn data identify Kevlar 49 as a stiffness-oriented candidate and Kevlar 29 as a comparison. Direct URL currently redirects; alternate DuPont path returns 404. Obtain an accessible authoritative copy or current supplier sheet before adopting any numbers. Finished cable efficiency, terminations, fatigue/creep, bend limits, UV/vacuum/thermal life, and sheath mass remain unresolved. No working stress is selected. |
| S2 | NASA NTRS, [NASA-CR-127695, Performance of Boeing LRV wheels in a lunar soil simulant, Report 1](https://ntrs.nasa.gov/citations/19720021195), 1971 | Record verified: single-wheel tests vary soil consistency and tread. Obtain report tables for relevant contact assumptions; neither a universal friction coefficient nor validation of 35.76 m/s operation. |
| S3 | NASA Glenn, [Planetary Exploration Test Facilities](https://www.nasa.gov/centers-and-facilities/glenn/planetary-exploration-test-facilities/) | Source lead for single-wheel traction testing and simulator conditions; numerical high-speed/contact data still needed. |
| S4 | NASA, [Industry to Mature Vertical Solar Array Technologies for Lunar Surface](https://www.nasa.gov/technology/nasa-industry-to-mature-vertical-solar-array-technologies-for-lunar-surface/), 2021 | Supports inclusion of deployment/support, terrain stability and dust protection. Does not supply selected installed W/kg or permit equatorial continuous sunlight. |
| S5 | NASA NSSDCA, [Moon Fact Sheet](https://nssdc.gsfc.nasa.gov/planetary/factsheet/moonfact.html), page dated 2024-01-11 | Verified distinctions between equatorial and mean radius, sidereal rotation and synodic daylight cycle; environment/reference-surface input lead. Precision mu and terrain/gravity models still to select. |
| S6 | User-provided handoff, *Design and optimize a Kevlar lunar sling launcher* | Architecture, objective, exclusions, targets and review gates; not evidence for material properties or physical feasibility. |
| S7 | Existing repository catcher notebooks | Regression comparisons only. Their 30/100 km cases, constants and average-power assumptions do not become new 20 km launcher defaults. |
| S8 | JPL, [Astrodynamic Parameters, DE440](https://ssd.jpl.nasa.gov/astro_par.html) | Adopted Moon mu 4902.800118 km³/s², converted once to SI; Julian year 365.25 days. |
| S9 | Yarndley, Lantoine and Armellin, [Station-Keeping Approach for Extremely Low Lunar Orbits with Solar Sailing](https://arxiv.org/abs/2606.05601), 2026 | Irregular-gravity and station-keeping context, not a demonstration of this 20 km equatorial catcher. No lifetime or station-keeping rate adopted. |
| S10 | NASA, [LRO Moves Closer to the Lunar Surface](https://www.nasa.gov/missions/nasas-lro-moves-closer-to-the-lunar-surface/), 2015 | The described 20 km close pass is part of a polar elliptical orbit reaching 165 km over the opposite pole, not this circular equatorial orbit. |
| S11 | NASA, [Astrodynamics assessment, 20240013031](https://ntrs.nasa.gov/api/citations/20240013031/downloads/20240013031.pdf) | Source lead for future GRAIL low/high-fidelity comparison and model-specific constants; no gravity harmonics used in Phase 4 calculations. |

Next source work: current finished Kevlar cable/construction supplier data,
structural tube/connection allowables, realistic lunar contact bounds, motor and
gearbox torque-speed-efficiency/mass maps, installed solar subsystem data,
climber grip feasibility, bearings/anchors, and lunar low-orbit gravity-anomaly
studies. Record uncertainties and applicability explicitly; do not synthesize
precise mass coefficients from unrelated product ratings.


## Current scenario input provenance (2026-10-31)

The speed-constrained checkpoint uses the [Toray–DuPont Kevlar material
table](https://www.td-net.co.jp/kevlar/data/) for the Kevlar 49 fiber density
1,450 kg/m³. The 1 GPa working stress is an explicit unqualified study
assumption, not a supplier cable rating. The [NASA terramechanics white
paper](https://ntrs.nasa.gov/citations/20220010732) informs the need to distinguish
traction and rolling behavior; it does not supply or validate our mu=0.5,
powered fraction=0.75, rolling=0.02 or 50–80 mph capability. Both pages were
checked for this checkpoint. Installed array 100 W/kg and recovery 70% remain
scenario assumptions; no product selection is claimed.
