Create a new GitHub repo that reproduces, in a single Jupyter notebook, all calculations and key numerical results from the “lunar mass driver → 30 km equatorial catcher → 0.8 km/s bridge to stable staging orbit” discussion.

REPO GOALS
- Provide a notebook that is runnable end-to-end and regenerates every number, table, and key derived quantity.
- Use plain Python with numpy; no obscure dependencies.
- Clearly define constants, assumptions, and selected design values at the top.
- Structure the notebook into small, verifiable sub-problems with unit checks.
- Produce final “summary tables” suitable for pasting into a report.
- All computations should be deterministic and show intermediate steps.

REPO STRUCTURE
- README.md: what the notebook does, how to run, what assumptions are baked in.
- environment.yml or requirements.txt (minimal).
- notebooks/:
  - 01_lunar_catcher_trade_study.ipynb (the main notebook)
- src/ (optional helper functions):
  - orbital.py (vis-viva, Hohmann, eclipse estimate)
  - ep.py (electric propulsion power/thrust relations)
  - unit_helpers.py (simple unit conversions)

NOTEBOOK OUTLINE (must implement each section)

0) Constants and Selected Values (single source of truth)
Define:
- Moon radius R_moon_km = 1737.4 km
- Moon mu_km3_s2 = 4902.800 km^3/s^2
- Gauntlet orbit altitude h_gauntlet_km = 30 km
- “Escape” orbit altitude for quick exit h_escape_km = 120 km
- Stable depot transfer Δv per leg dv_bridge_m_s = 800 m/s (accepted; treat as given, not derived)
- Electric thruster exhaust velocity ve_m_s = 3000 m/s (Isp ≈ ve/g0)
- Thruster efficiency eta = 0.60
- Sunlight fraction f_sun = 0.71
- Catch window duration t_catch_hr = 50 hr
- Total mass cap at gauntlet departure m_depart_gauntlet_t = 1000 t (includes rocks + remaining prop + dry)
- Target dry mass m_dry_t = 50 t
- Solar specific power sp_solar_W_per_kg = 100 W/kg (conservative)
- Solar constant S_W_m2 = 1361.6 W/m²
- Assumed net PV conversion factor (efficiency*packing*pointing): pv_net_fraction = 0.27 (or explicitly choose values; show sensitivity)
Compute net PV W/m² = S_W_m2 * pv_net_fraction
Also define g0 = 9.80665 m/s²

Make a single “Assumptions table” (markdown + printed dict) at top.

1) Basic orbital speeds at 30 km
Compute:
- r30_km = R + 30
- circular speed v_c_30 = sqrt(mu/r30)
Output v_c_30 in m/s and km/s.

2) HIGH-SCHOOL Δv: surface → 30 km circular orbit (two-impulse)
Model:
- payload starts at r=R with v=0
- first burn puts it on ellipse with rp=R, ra=R+30
- second burn circularizes at ra
Compute:
- semimajor axis a = (rp+ra)/2
- v_p (perigee of ellipse) by vis-viva
- v_a (apoapsis of ellipse) by vis-viva
- v_c at ra
- Δv1 = v_p (since initial v=0)
- Δv2 = v_c - v_a
- total Δv = Δv1 + Δv2
Print Δv1, Δv2, Δv_total. (Δv2 should be ~7.14 m/s.)

3) Relative velocity at catch at 30 km
Assume catch occurs at ra (30 km) before circularization.
Compute v_rel_catch = v_c - v_a
Report v_rel_catch in m/s.
(This is the accepted “catch delta-v scale” used for momentum drag.)

4) Impact velocity if periapsis drops to the surface (failure mode)
Assume an ellipse with rp=R and ra=R+30 (apo stays 30 km).
Compute v_p at rp using vis-viva and report v_impact ~ 1.69 km/s.

5) Hohmann escape Δv: 30 km circular → 120 km circular
Compute classic two-burn Hohmann between circular orbits:
- dv1_raise = v_c(r1)*(sqrt(2r2/(r1+r2)) - 1)
- dv2_circ  = v_c(r2)*(1 - sqrt(2r1/(r1+r2)))
Total dv_30_to_120
Print dv_total (~40.9 m/s).

6) Escape power sizing (2-day and 3-day)
Define two cases:
- t_escape_days = [2, 3]
Assume thrusting only during sunlight fraction f_sun.
For each:
- compute required average thrust T_avg = M_loaded * dv_30_to_120 / (t_escape_sec)
- thrust during sunlight T_sun = T_avg / f_sun
- EP power during sunlight P_sun = (T_sun * ve) / (2*eta)
Also compute a “catch makeup” thrust and power during the 50 hr window:
- Use captured mass = delivered rock mass per cycle (derived later)
- Impulse J = v_rel_catch * captured_mass
- Average thrust during 50 hr: T_catch = J / t_catch_sec
- P_catch = (T_catch * ve)/(2*eta)

7) Solar array mass & area (catcher) using 100 W/kg
For each escape case:
- total required sunlit power P_total = P_sun + P_catch + housekeeping_margin
Use housekeeping_margin = 0.03 MW and then multiply by 1.2 (20% margin) to match the discussion.
Then compute:
- array_mass_kg = P_total_W / sp_solar_W_per_kg
- array_area_m2 = P_total_W / (S_W_m2 * pv_net_fraction)
Output a table: escape_days, P_total_MW, array_mass_t, array_area_m2

8) Rocket equation for LOX-only electric at ve=3000 m/s (bridge leg)
Use dv_bridge=800 m/s.
Compute mass ratio MR = exp(dv/ve).
Given m_depart_gauntlet = 1000 t:
- m_arrive_depot = 1000 / MR
Interpretation:
- assume up-leg propellant is “spent” to reach depot, so arrival mass is dry + delivered rocks (no up-leg prop remaining).
Thus:
- delivered_rocks_t = m_arrive_depot - m_dry_t
- up_leg_prop_t = m_depart_gauntlet - m_arrive_depot
Down-leg prop requirement:
- starting at depot with only dry + down_prop, arriving gauntlet with dry:
  (dry + down_prop) / dry = MR
  down_prop = (MR - 1)*dry
Compute:
- MR (~1.305)
- delivered_rocks (~716 t when dry=50 t)
- up_prop (~234 t)
- down_prop (~15.3 t)
Output these in a summary table.

9) Time to climb from gauntlet to depot (0.8 km/s leg) at the sized power
Use the chosen catcher sizing (pick 2-day case as baseline):
- Determine sunlit thrust available from P_total (or just P_sun for propulsion)
- T_sun_available = 2*eta*P_sun / ve
- average thrust = f_sun * T_sun_available
Use average mass over the up-leg:
- m0 = 1000 t
- m1 = 1000 / MR
- m_avg = (m0+m1)/2
Estimate time:
- a_avg = T_avg / m_avg
- t = dv_bridge / a_avg
Report in days; should be O(weeks) (~26 days in the discussion for ~1.1 MW class).
Also provide scaling note: time ∝ 1/P.

10) Ground mass-driver power & PV area for delivering rocks per cycle
Using the derived delivered mass (~716 t) and t_catch_hr=50:
Compute:
- specific energy from surface rest to 30 km orbit: Δε = μ(1/R - 1/(2r30)) (convert km units carefully) or use the earlier result directly after recompute.
Compute:
- energy_total = Δε * delivered_mass_kg
- average power ideal = energy_total / t_catch_sec
- assume wall-to-kinetic efficiency eff_driver = 0.5 (explicit; sensitivity)
- power_elec = power_ideal / eff_driver
- PV area on surface = power_elec / (S_W_m2 * pv_net_fraction_surface)
Use the same pv_net_fraction as baseline unless you define a different derating for dust/thermal; document it.
Output the ground PV area in m² and as an equivalent square side length.

11) Final consolidated “Report Summary” cell
Print:
- All selected assumptions
- Key results:
  - catch relative velocity (7.14 m/s)
  - impact velocity (~1.69 km/s)
  - dv_30_to_120 (~40.9 m/s)
  - rock delivered per cycle (~716 t)
  - LOX prop burned up and down (~234 t up, ~15 t down)
  - escape power & array mass/area (2 and 3 day)
  - travel time gauntlet→depot at chosen power (~weeks)
  - ground power and PV area for mass driver ops
Include tables with units.

QUALITY REQUIREMENTS
- Every function should state inputs/outputs and units.
- Use assertions to catch unit mistakes (e.g., km vs m).
- No hidden constants; every key parameter declared once in the assumptions section.
- Keep plots minimal; tables are preferred.
- Provide at least one “sensitivity” cell showing how results scale with:
  - ve (or Isp), eta
  - dry mass
  - solar specific power
  - pv_net_fraction

DELIVERABLE
Output complete repo content: README + requirements + notebook (as .ipynb JSON).
If generating notebook JSON is too heavy, output a .py (jupytext-style) that can be converted to .ipynb.

