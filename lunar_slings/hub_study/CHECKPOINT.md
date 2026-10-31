# Lunar sling checkpoint — 31 October 2026

**Track radius now follows rover speed; it is not a free design variable.**
The study compares 50 and 80 mph, with acceleration from 4 g through moderate
cases and deliberately extreme geometry-boundary checks. There are 44 timed
scenarios: 11 accelerations × 2 speeds × 1 or 2 catcher passes.

[Detailed scenario catalogue and graphs](results/speed_constrained/README.md) ·
[Equations, assumptions and buildability review](results/speed_constrained/METHOD.md) ·
[Complete numerical results](results/speed_constrained/all_scenarios.json)

## What is established

For release speed u and release centripetal acceleration A, omega=A/u,
release radius=u²/A, and **track radius=rover speed/omega**. Release speed is
iterated with the finite-offset orbital intercept and actual release height.
The calculation keeps cruise/release rover speed at the specified 50 or 80 mph;
controlled slowdowns during loading/buffer restore phase without overspeed.

A one-dimensional finite-angle cable calculation replaces the invalid low-g
small-slope approximation. It sizes a total-tension Kevlar taper, scans loaded
payout and unloaded return, and derives minimum quasi-static apex height with
3 m clearance. Cable material length, horizontal release radius and pole
height are distinct outputs. No continuum/finite-element model is introduced.

Cable mass and shape enter inertia, gravity, meridional kinetic energy, wheel
torque and reel power integrals. Outward reel braking and wheel input are both
included, as are cable retraction, rolling losses, ballast inertia during phase
correction and simultaneous energy recovery. Unknown hardware mass is not zero.

## Representative numbers

All rows: 1,000 kg useful payload + 1,000 kg equal-radius rock countermass.
Ballast is **total lunar rock mass for both frames**, not imported hardware.
These are conditional demands, not demonstrated feasible machines.

| Rover speed | Release acceleration | Track radius | Release radius | Apex height | Ballast, one / two passes |
| --- | ---: | ---: | ---: | ---: | ---: |
| 50 mph | 4 g | 959.2 m | 72.24 km | 4,016.9 m | 1,875 / 873 t |
| 80 mph | 4 g | 1,534.8 m | 72.25 km | 3,882.3 m | 1,152 / 528 t |
| 50 mph | 30 g | 128.0 m | 9.65 km | 74.3 m | 1,872 / 871 t |
| 80 mph | 30 g | 204.8 m | 9.65 km | 72.0 m | 1,149 / 527 t |
| 50 mph | 100 g | 38.4 m | 2.89 km | 9.42 m | 1,872 / 871 t |
| 80 mph | 100 g | 61.4 m | 2.89 km | 9.21 m | 1,149 / 527 t |
| 50 mph | 300 g | 12.8 m | 0.965 km | 3.71 m | 1,872 / 871 t |
| 80 mph | 300 g | 20.5 m | 0.965 km | 3.69 m | 1,149 / 527 t |

The acceleration label denotes release centripetal acceleration. Full applied
payload acceleration is reported separately (the nominal 4-g case peaks at
about 4.004 g). Masses depend strongly on assumed traction: mu=0.5, 75% of
normal force on powered wheels, rolling coefficient=0.02. These are study
inputs, not measurements validating 50–80 mph operation on a lunar road.

At fixed rover speed, acceleration mostly trades size for force: **ballast and
power are nearly flat across acceleration**, while pole height changes sharply.
Slower rover operation requires more ballast for the same cycle. More time
reduces torque and power; it does not reduce centripetal acceleration or the
ratio of overturning moment to ballast weight.

## Timeline and mass composition

**Loading is the same five-minute allowance in every case.** One pass allocates
5.00 min loading, 50.28 min payout, 50.28 min return, and 5.00 min final buffer,
total 110.56 min. Two passes retain both five-minute allowances and allow
105.56 min each for payout and return, total 221.12 min. Loading/buffer also
provide phase correction; they are not wholly unused reserve. These allocations
do not yet include settling after release.

For the 100-g, 50-mph one-pass case, the accounted imported masses are roughly
37 t of outward cables, 2.2 t of main tie and 219.7 t of solar at the assumed
100 W/kg with 70% simultaneous recovery. Without recovery, solar is about
306 t. Peak input is about 30.6 MW without recovery / 22.0 MW with recovery;
two passes reduce this to about 14.6 / 10.5 MW. Each scenario includes exact
mass composition, wheel/reel power channels, ballast weight in newtons, wheel
normal-load demand, cable storage volume, peak tension, geometry and timing.

**Pole, wheel, motor, drum, retention, thermal and electrical equipment masses
remain unsized.** The quoted subtotal is not a full launcher mass ratio, and no
complete mass optimum is established. The old axial-only pole masses are
withdrawn. The height calculation finds minimum quasi-static clearance, not
minimum structural mass for an actually stable frame.

## The acceleration limit, stated precisely

The earlier approximately 123-g maximum at 80 mph was only the speed limit
for a **fixed 50 m track radius**. At 50 mph that same fixed-radius test would
be about 77 g. Both disappear when track radius is derived from speed.

A different bound applies **if the road alone must provide the ballast's inward
force**: omega times rover speed must be less than mu times lunar gravity.
With mu=0.5, this corresponds to roughly **6.2 g at 50 mph or 3.9 g at 80 mph**
of payload acceleration. At equality, the lateral load consumes all available
friction, leaving none for simultaneous spin-up. Adding ballast cannot cure
this ratio because inertia and available friction grow together. The present
cycle instead assigns radial ballast restraint to the main tie/frame, so these
are road-only limits, not universal limits for a successfully braced structure.

A separate, generous geometry bound comes from a 45° trailing leg with both
feet on the same circular road: its horizontal span H must be less than 2R.
At the high-acceleration end this fails near **2,551 g at 50 mph** and
**4,090 g at 80 mph**. Equality already places a foot at the other frame;
actual hardware requires more room. These are necessary rejection bounds,
**not useful operating limits**. The catalogue includes extreme diagnostic
rows to bracket them. A true maximum buildable acceleration has not been found.

At the other extreme, **4 g also fails the same 45°-leg geometry test**:
the required height exceeds the track diameter. Changing the leg angle or
support footprint would be an architectural change, not a free correction
inside these results.

## What prevents calling a scenario buildable

1. **Ballast restraint and overturning.** The main tie can balance outward
   payload tension, but the rotating ballast itself needs inward force. Applying
   that force at an elevated apex creates a radial moment. For a compact frame
   the support-lever diagnostic H omega²R/g exceeds the track radius throughout
   this sweep. The reviewed fore/aft A-frame has no demonstrated radial moment
   solution under those loads. Small stabilizing stays cannot simply be assumed
   sufficient. A full 3D frame/contact solution or an explicitly changed load
   path is needed before sizing poles and declaring a feasible mass ratio.
2. **Release recoil.** Removing the payload changes the cable equilibrium.
   At 4 g / 50 mph, the empty tip's equilibrium moves about 299 m and the
   two cables' empty-state energy difference is about −18 MJ. The model reports
   this discontinuity; it does not predict or absorb the transient. Three metres
   of quasi-static clearance is not a proven recoil margin, and the timeline
   has not demonstrated room for settling.
3. **Wheel, cable and reel hardware.** Four powered and four passive wheels
   remain the configuration. Contact footprints, high-speed capability, drum
   bending/fatigue, retention and heat rejection are not selected designs.
   Each reel stores approximately 13 m³ of fiber before packing allowances;
   high-g shrinking tracks cannot treat such equipment as points indefinitely.
4. **Countermass disposal and orbit.** The equal-radius opposite rock release
   does not hit the reference sphere. A changed rock-side release needs balance
   and trajectory analysis. The 20 km catcher still uses ideal two-body dynamics,
   with lunar gravity anomalies/station keeping outside this checkpoint.

These are specific failures or open load paths, not reasons to conceal the
numerical trade study. The useful next design work is to resolve radial
frame/contact moments and the release transient before refining a pole-mass
optimum. The latest calculations provide the force and energy envelopes for it.

## Reproduction and history

Run the commands in the [method document](results/speed_constrained/METHOD.md).
The suite has 26 passing tests, including finite-angle arclength and tension,
release targeting, work-energy identities on continuous branches, phase/speed
closure, traction, and doubled-resolution convergence. SVG/PNG scientific plots,
sampled CSV histories, JSON metrics and source hashes are included.

Earlier force diagrams and orbital/climber analyses are preserved. The
fixed-radius `mass_screen` and `spooling_cycle` outputs are historical screens;
use **this checkpoint and `results/speed_constrained/`** for current numerical
claims. Historical notebooks and the separate `frozen_retreat` study are unchanged.
