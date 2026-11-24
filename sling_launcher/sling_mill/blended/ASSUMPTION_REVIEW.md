# What sets the dimensions?

[Current reference](IRON_REFERENCE.md) · [Publication packet](../publication/README.md)

The former **5 mm plate-thickness floor was a search-domain choice**. It was not a material or manufacturing result. The revised search permits 0.10–120 mm, expands the other geometric bounds, includes solar mass, removes the arbitrary 100 Hz feed cap and permits up to 100% inlet occupancy. Its selected thickness is compared with independently reoptimized fixed-thickness cases.

The aim is to obtain dimensions from the model's tradeoffs. Material properties, fabrication choices and model-validity criteria still need declared values: optimizing those as if they were freely attainable would produce misleading results.

## Free design variables

| Variable | Revised numerical search domain | What opposes the extremes |
|---|---|---|
| Roller radius | 0.10–3.0 m | Small: centrifugal coating peel/bond demand, local geometry. Large: rotating inventory and taller support frames. |
| Pitch / radius | 2.0001–10 | A specified 20 mm inter-drum clearance prevents overlap; wider spacing reduces station count but changes traction per travel distance and required bar engagement. |
| Bar length | 0.10–20 m | Full-end tensile load envelope grows with length; the blended treatment requires at least two pitches of engagement. |
| Bar width | 5–3,000 mm | Sets cross-section/flow scale; also changes shaft bending, heat rejection and frame span in this single-lane hardware layout. |
| Bar thickness | **0.10–120 mm** | Thin: larger width needed for fixed inlet flow, growing shaft bending demand. Thick: lower acceleration for the available contact force and longer accelerator. |
| Imposed squeeze | 1 µm–5 mm, and less than bar thickness | Loose: low traction/long machine and insufficient vertical support. Tight: contact pressure, heating, bond stress and support loads. |
| Structural belt thickness | 0.01–20 mm | Thin: working stress; thick: self-mass, support loads and the string-panel approximation. |
| Hoop-support fraction | 0.01–0.95 | Redistributes force between belt tension and radial supports; both inventories and contact compliance change. |
| Rotor speed reserve | 0–20% | Too small: stored-energy speed drop exceeds reserve; more reserve: extra slip, heat and centrifugal load. |
| Fraction of contact pulse supplied by motor | 0–1 | Less motor pulse support requires rotor storage; more raises installed motor rating and mass. |
| Hub radius / roller radius | 0.005–0.40 | Small: shaft bending/torsion capacity. Large: centrifugal hub stress and mass. |

Numerical bounds make the solver finite. The selected solution must be checked for contact with them. Width is a natural scale choice for the material stream, but the current model also includes an end-supported shaft whose bending depends on span. It therefore has a real width-dependent hardware penalty. A supported-throughout or segmented roller architecture would have a different scaling law.

## Fixed values: physical inputs, engineering assumptions and validity limits

| Item | Current value | Interpretation / next improvement |
|---|---|---|
| Delivery requirement | 10 million tonnes per 365 operating days; 1,600 m/s exit | Mission inputs. Full sunlight is assumed for this budget. |
| Modeled inlet | 100 m/s | Boundary between injector and mill. The upstream acceleration remains outside this inventory. |
| Iron | 7,860 kg/m³; 207 GPa modulus; 450 J/kg/K; 70 MPa working allowable | Selected material analogue and provisional working margin. The longitudinal load is tensile. Contact and combined local stress require further qualification. |
| Zylon | 1,560 kg/m³; 1 GPa working ceiling | Fixed structural material and selected margin. The solver sizes material within this ceiling. |
| Contact skin | 0.5 mm, 1,400 kg/m³, 1 GPa modulus, 1 W/m/K | **Hypothetical fixed material formulation**, including its chosen thickness. Establish a physical laminate and service life before treating the dimensions as fabrication-ready. |
| Friction / bond | μ=0.5; 5 MPa peel and 20 MPa shear allowables | Assumed interface performance. These limits materially influence the selected radius and squeeze. |
| Mean layer temperature | 450 K maximum | Assumed material ceiling. Steady blended thermal model. |
| Radiation | Emissivity 0.85; view factor 0.7; sink 250 K; zero external absorbed flux | Assumes thermally shaded machinery with usable radiator view. The separate solar array sees full sunlight. Shade/deployment details remain future hardware work. |
| Attachments / torque sharing | 128 attachments, 8 effective torque members | Discrete construction choices held fixed; changing these changes belt-panel and cable sizing. |
| Panel model | Belt thickness ≤10% of panel chord; contact patch ≤ chord; deflection ≤2% of R; local `aL/v² ≤0.1` | Applicability screens for the reduced equations. Active limits call for a better panel model, rather than being interpreted as material failure. |
| Bar engagement | L ≥2 pitches | Blended-contact applicability choice. A shorter bar needs an explicit handoff model. |
| Inlet occupancy | ≤1.0 | Geometric limit: rigid bars cannot overlap. The old 0.8 cap was discretionary and has been removed. |
| Launch frequency | No independent cap | Follows from throughput/bar mass. The old 100 Hz cap had no equipment model behind it and has been removed. |
| Shaft | 200 GPa modulus; 10 µm bending deflection; 100 MPa shear; 250 MPa rotational stress; 2 mm minimum wall | Engineering stiffness, strength and manufacturing assumptions. The bending/solid-section and rotational stress constraints oppose excessive span. |
| Supports | Steel; four uprights/two cross beams; 0.20 m ground clearance, 0.40 m added span; 0.1 mm lateral and 0.05 mm cross-beam displacement | A conservative freestanding support design. Stiffness tolerances and layout are choices; braces and shared supports may reduce mass. |
| Frame sections | ≥50 mm outside width; wall ≥4 mm or width/30; 25% connections allowance; load factor 1.5 | Fabrication assumptions. Numerical section-sizing bracket expanded from 0.8 m to 8 m so it does not silently reject larger supports. |
| Motors | 95% efficiency; 20% rating headroom; 4.55 kg/kW plus 25% installation | Industrial mass anchor reused from the straw study. Stage-specific power determines motor mass. |
| Other hardware | Foundations 200 kg/pair; guides 20 kg/m; startup 2 kg/drum; bearings 0.5 kg/kN; electronics 0.5 kg/kW | Explicit preliminary mass allowances. Detailed product/foundation designs are needed to improve these coefficients. |
| Motor cooling | 400 K radiator; 5 kg/m² | Heat-rejection design assumptions; area follows calculated losses. |
| Solar | **100 W/kg illuminated output; 20% headroom; 250 W/m² output density** | Same array mass anchor as the straw study. Full-sun array mass and collecting area follow calculated electrical demand. No lunar-night battery is included. |

An unconstrained choice of better friction, stronger bonding, higher temperatures or lighter motors would improve the result by assumption. Keeping those inputs explicit allows future measured properties to improve the model honestly. Wear life, bond fatigue, combined payload contact stress, exact shaft/bearing layout and the early injector remain the most important unresolved engineering items.

## Why thin bars eventually stop helping

At fixed mass flow and inlet speed, `rho * width * thickness * v_in >= mdot`. Reducing thickness eventually requires increasing width. For an end-supported shaft, bending demand grows rapidly with span. The available shaft section is bounded by its radius, while allowable hub rotation limits the hub/roller radius ratio at the high-speed end. Growing the roller to accommodate that shaft brings added support, rotating-structure and station costs. The selected thickness therefore emerges from coupled inlet-flow, shaft, rotor and contact constraints, under the stated material assumptions.

Solar adds a nearly constant mass offset because fixed exit speed and mass flow fix most of the useful kinetic power. Its mass can dominate the total without substantially moving the mechanical thickness optimum.

## Thickness comparison

Full-sun solar is included in every row. These are feasible designs found at each thickness; several local searches reached iteration limits, so the rows are cost bounds from the search rather than exact conditional minima. The selected free-thickness solution passes the finer integration checks. All cases, including the less successful 1.25 mm local search, are retained in [the numerical profile](search_results/thickness_profile.json).

| Plate thickness (mm) | Total mass with solar (t) | Mass payoff (operating h) |
|---|---:|---:|
| 0.50 | 17,254 | 15.114 |
| 1.00 | 9,846 | 8.625 |
| 1.50 | 9,376 | 8.213 |
| 2.00 | 9,566 | 8.380 |
| 3.00 | 9,781 | 8.568 |
| 5.00 | 10,275 | 9.001 |

**Selected free-thickness candidate:** 1.5079 mm, 9,373.6 tonnes including solar, 8.2113 operating hours. No geometric search bound is active in this candidate; zero motor pulse support is the physical endpoint where rotor storage supplies contact pulses. The 100% inlet occupancy is a physical packing boundary.
