# Material, loading and payoff notes

[Publication article and polished tables](ARTICLE.md) · [Selected numerical reference](../blended/IRON_REFERENCE.md) · [Assumption review](../blended/ASSUMPTION_REVIEW.md)

The current publication uses the **1.51 mm iron plate case with full-sun solar included**: approximately **9,374 tonnes** and **8.21 operating hours** of gross mass payoff. ARTICLE.md contains the publication tables. This page supplies supporting reasoning and sources; [historical calculations](archive/README.md) are kept separately.

## Material choice and numerical allowables

The selected iron analogue uses density 7,860 kg/m³, heat capacity 450 J/kg/K, elastic modulus 207 GPa and a provisional 70 MPa axial working allowable. [ARMCO pure-iron data](https://www.aksteel.nl/files/downloads/clf_productdata__armco_pure_iron_pdb_euro_final_072022_92.pdf) gives typical annealed yield strengths of 138–186 MPa and requires testing for design. The modeled payload reaches a conservative axial-load envelope of 60.32 MPa and peak contact pressure of 14.44 MPa; a combined local stress check remains necessary.

The [article's materials table](ARTICLE.md#what-material-should-the-bars-carry) assigns five other provisional axial allowables for comparison: low-carbon steel 120 MPa, Fe–Si 20 MPa, unalloyed aluminum 15 MPa, Al–Si 50 MPa and Al–Mg–Si 100 MPa. These are explicit screening inputs; each candidate still needs a composition, process and contact qualification. Material substitution must also update density, stiffness and thermal properties.

Relevant manufacturing and composition sources:

- [NASA lunar-material hydrogen-reduction experiments](https://ntrs.nasa.gov/citations/19950035561): metallic iron production from ilmenite.
- [MIT molten-regolith electrolysis study](https://dspace.mit.edu/entities/publication/bfae866b-95b0-4bd6-ab26-65796015b23f): oxygen production with iron and silicon at the cathode.
- [Lunar metals production-process comparison](https://www.sciencedirect.com/science/article/pii/S0094576522006579): low-carbon steel, ferrosilicon and aluminum–silicon routes.
- [Hydro Al–Mg–Si alloy family](https://www.hydro.com/en/global/aluminium/products/extruded-profiles/alloys-for-extruded-profiles/6061-alloy/) and [European Aluminium casting-alloy guide](https://european-aluminium.eu/wp-content/uploads/2022/11/aam-products-6-cast-alloys-and-products.pdf): composition and processing choices for aluminum cargo.

## Longitudinal loading: stronger pull toward the front

For a coordinate s running from the rear to the front of a bar, tensile axial force is

`N(s) = lambda * a * s - integral_0^s f(x) dx`,

where lambda is mass per unit length and f is forward traction per unit length. When f increases toward the front, its average over a rear portion is at most its whole-bar average. Thus N(s) is nonnegative and returns to zero at the free ends. The blended operating mode places the bar in longitudinal tension. Normal roller pressure remains a separate contact load.

The current search disables the historical full-end-compression Euler limit. The conservative full-end-force magnitude remains an axial tensile envelope. Explicit engagement transitions, strip flexibility and combined contact stress are follow-up work.

## Entry spacing

For steady delivery, `dt = bar_mass / mdot`. At a given station, center spacing is approximately `v * dt`; end-to-end entry satisfies `mdot = rho * width * thickness * v_entry`.

The selected 5.028 kg bars arrive at 63.07 bars/s and fill the 100 m/s modeled inlet continuously. They separate as they accelerate downstream. A slower upstream feeder can likewise carry touching bars; its speed and the speed at the first modeled station must be distinguished. The injector that brings cargo to 100 m/s remains outside the current equipment budget.

## Oxygen-bearing cargo

[ESA](https://www.esa.int/Science_Exploration/Human_and_Robotic_Exploration/Turning_Moon_dust_into_oxygen) reports approximately 40–45% chemically bound oxygen in lunar regolith. Pure-oxide oxygen fractions, from stoichiometry, are FeO 22.3%, Al₂O₃ 47.1% and SiO₂ 53.3%. These percentages precede packaging and extraction losses.

A [regolith-simulant processing study](https://www.sciencedirect.com/science/article/pii/S0094576525002097) reports about 8 MPa tensile strength alongside much larger compressive and flexural strengths. Those properties describe different tests and cannot be exchanged. The 5 MPa axial working input in the article's oxide row is provisional; meter-long bar defects and roller contact still require qualification.

A metal-skinned oxide bar would assign longitudinal and contact loads to its shell, initially giving the core zero tensile-load credit. It therefore requires a shell/core model. The shell/core extension is outside the solid-iron optimization.

## Cross-design accounting

The [comparison table in ARTICLE.md](ARTICLE.md#comparison-with-earlier-lunar-launcher-designs) uses useful delivery to LLO and operating-time payoff. The mill includes solar at 100 W/kg illuminated output with 20% headroom, assuming full sunlight. Its injector, feedstock production, catcher and deployment are additional. Other rows retain their source studies' inventory boundaries.

The slider-straw model imports tapered cable sizing from [staged_spool_bank/model.py](../../staged_spool_bank/model.py). Its chosen 3:1 tether/payload mass ratio back-solves to 2.438 GPa working stress. The [recorded straw budget](../../lunar_slider_straw/RING_REFERENCE.md) uses that choice. Lower working stress requires more taper and cable mass plus revised drums and hardware; the architecture retains that tradeoff.

The straw's separate 47.4-calendar-day L1 payoff includes imported equipment, descent propellant, ascent yield and 50% duty. ARTICLE.md instead uses 22.4 operating days from total installed mass divided by useful LLO flow.

The conveyor's 2.41 operating hours counts only its useful-arm working loop. A whole-machine conveyor mass budget remains open. The go-kart's 188 operating days includes its local ballast and solar within the documented equipment boundary.

## Matched-acceleration conveyor comparison

[Reproduction script](../blended/compare_conveyor.py) · [Numerical results](../blended/search_results/conveyor_matched_acceleration.json) · [Original conveyor equations](../../conveyor_loop/steady/model.py).

The comparison holds release speed at **1,600 m/s**, useful flow at **317.0979 kg/s**, and maximum modeled loaded acceleration at **4,840.085 m/s² (493.55 g)**. The conveyor solves the existing steady 2D free-turn boundary-value problem with payload loading on the outbound leg. Its uniform-section Zylon operates at a **2.9 GPa** working ceiling. The mill retains its **1.0 GPa** ceiling and tapered drum cables. Thus material quantity is compared alongside the differing stress requirements.

For each circulation speed (1, 5, 10 and 20 m/s), solve for payload/line-density ratio and rotational velocity scale to satisfy release speed and working stress. Then scale all lengths together and angular speed inversely until the maximum loaded acceleration matches the mill. Feed-wheel radius / loop radius and hub position / loop radius retain the source model's proportions. These geometric ratios are fixed assumptions. This produces release radii of approximately **534–538 m** and feed-wheel radii near **2.35 m**.

The inertial acceleration is evaluated as `a = -omega² r + 2 omega u n + u² kappa n`, including rotational, Coriolis and conveyor-curvature terms. Here `u` is circulation speed, `n` is the local normal and `kappa` is line curvature. The loaded domain extends through the source model's smooth release transition to `release_center + 5*release_width`, where more than 99.995% of the payload has unloaded. Feed attachment transients and payload internal stresses are outside this continuous-load model. The re-evaluated scaled solution checks speed, stress, acceleration and mass flow; boundary-value residuals are below 2e-8.

Cross-section follows directly from throughput: `A = mdot/(q*rho*u)`. At 5 m/s it is approximately **0.0985 m² per loop**. This is a large idealized fiber bundle; manufacturing, bending, load sharing and friction at this scale remain unresolved. Dividing the same total flow among parallel geometrically identical units preserves the summed fiber requirement under this model's linear area scaling.

Accounting includes a symmetric opposing conveyor arm whose discharged mass receives no useful-delivery credit. The mill fiber total includes **6.822 t outer belts + 9.711 t radial members + 0.777 t torque members = 17.310 t**. Coatings, hubs, machinery, foundations, solar and radiators are excluded from both fiber-only totals. Their inclusion in the mill's 9,374 t total explains the difference between its 54.6-second fiber payoff and 8.21-hour installed-system payoff. The earlier 2.41-hour conveyor figure used a different acceleration scale, speed and one-arm boundary and remains in its original study as historical context.

If both conveyor arms deliver useful material, useful throughput and the accounting convention must be changed together. The current comparison assumes disposable countermass. No catcher logistics or guaranteed orbital capture is modeled here.

### Suggested article narrative

1. Introduce the compact drum and the sequence of accelerating stations with the SVGs and GIF.
2. Establish the bar requirement with the consolidated material table, then give the iron reference dimensions, speed and acceleration.
3. Explain the tapered radial load path and show working stress alongside area taper.
4. Present the matched fiber-only comparison, with circulation speed visible. Lead with the 5 m/s case and use the other rows to show the throughput tradeoff.
5. Use the mill mass pie to bridge from fiber inventory to installed equipment: the machinery and solar array dominate the final mass.
6. Close with the 8.21-hour conditional system payoff and the remaining structural packaging, support and manufacturing questions. A whole-machine conveyor ranking awaits comparable hardware sizing.
