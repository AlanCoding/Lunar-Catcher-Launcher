# Sling mill engineering sequence

**Search checkpoint:** [conditional optimized parameters](blended/OPTIMIZATION.md)
are available at 1.0 and 1.5 GPa working ceilings, with nearby-start and finer-grid
checks. The next scope decision is whether complete-system payoff includes a
dedicated continuous power supply and a feed/injection plant, or treats them
as supplied industrial services.

**Current progress:** [the blended model](blended/README.md) implements the
requested reduced mechanical closure, steady 50/50 friction-heat split and
consistent component inventory. Tightness and strength-ceiling sweeps expose
constraint failures. Next: support-sharing sensitivity and better hardware
mass laws, then a constrained search within declared material scenarios.

[Overview](README.md) · [Current results](RESULTS.md)

## 1. Scalar and discrete-station reference — implemented

Fixed annual flow, independent rod dimensions, exact hub-tangent geometry, finite-patch engagement, forward-sliding schedule, power and heat integrals, conditional fiber/hardware inventory, strength/stability screens, storage alternatives and parameter sweeps. Mathematical tests validate the baseline and energy closure. The figures show the requested geometry and relative machine/payload sizes.

The [mass-payback optimizer framework](optimization/README.md) now classifies
every input and adds contact-layer mass/retention, compliant gap-pressure,
thermal and wear screens. Its constraint audit exposes the remaining patch,
belt-shape and material closures before optimization. The [article draft](publication/ARTICLE.md)
preserves the accepted spacing illustration and gathers the publication sequence.

## 2. Resolve flexible contact and rotating members — next decision

Build a planar rotating-string/belt model with an elastic closed belt, tension-only radial members, curved torque members and a prescribed rigid rod contact surface. Use unilateral normal contact, sliding friction and distributed centrifugal loading. Solve steady moving-load snapshots first; record belt shape, contact patch, pressure, spoke unloading and required joint loads. Then integrate the rotating contact passage to assess oscillations and repeated loading.

Key equations are `ρA r̈ = ∂s(T t) + f_contact + f_body`, `T=max(0,EA ε)`, normal gap ≥0, normal force ≥0, gap × force=0, and signed sliding traction opposed to relative slip. In a rotating frame include centrifugal and Coriolis terms; torque-member curvature changes the force direction and moment arm. Resolve attachment transitions and the difference between circumferential material motion and spatial contact location.

The scalar screen found excessive entrance-belt thickness. Test whether distributed contact and a realistic membrane shape alleviate it. Explore higher entry speed, lower early acceleration, differing station radii, attachment counts and contact lengths. Any new support element must have an explicit force path and mass. Preserve deliberate sliding and the single lane.

## 3. Couple drive transients and startup

Integrate actual rim speed, motor torque limits, friction work, payload speed and belt shape together. Select operating headroom and rotor inertia jointly. Compare steady motor recharge with motor-supplied pulses, including realistic torque–speed envelopes and electrical bus buffering. Qualify high-speed hubs, shafts and bearings before using generic kg/kW estimates for a design optimum.

Model deployed startup supports, increasing tension, withdrawal, loss of a payload, shutdown and braking. Determine a practical minimum operating speed from the full loaded geometry. Assess rotor burst/fragment energy and infrastructure implications as part of machine design.

## 4. Payload and contact trials

Choose plausible manufactured metal, mineral/oxide or carrier-based payload recipes. Characterize flaw-sensitive bending strength, abrasion, surface friction versus speed and temperature, heat partition and thermal shock. Include processing and injection power. Establish straightness and dimensional tolerances, handling yield, achievable 44-Hz feed and throughput availability.

A reduced rigid-body/beam model should include guide contact, vertical clamping control and pitch/yaw/roll. Evaluate resonance with belt circulation, station passage and launch cadence. A nominal bulk strength or low average temperature rise cannot establish contact life.

## 5. Select and compare an architecture

After the contact and transient gates close, jointly optimize acceleration, stage radius/spacing, hub ratio, payload geometry, entry speed and allowable stress. Extend to variable station spacing and acceleration. Report Pareto candidates in installed mass, length, heat and power, filtering on validated constraints. Compare equal useful delivered flow and identical operating-day assumptions with the slider straw, tapered sling, conveyor and electromagnetic mass-driver studies. Include feed processing, power source and maintenance in the economic comparison.

## Iron and hardware audit follow-up

See [payload and payoff checkpoint](publication/PAYLOAD_AND_PAYOFF.md). Adopt unalloyed iron (7,860 kg/m³, 207 GPa modulus, 70 MPa provisional working allowable). Before re-optimizing: replace the assumed end-compression Euler limit with the front-pulling tensile traction-distribution envelope; develop braced/shared supports and nip-gap compliance; select high-speed motors; size foundation anchorage and external power/injection infrastructure. Preserve the original searches as checkpoints.

## Iron optimization checkpoint

The [optimized iron reference](blended/IRON_REFERENCE.md) now uses the selected material, the tensile front-pulling assumption and explicit support/drive masses. The initial 15 mm and 5 mm bounds were followed by a 0.10 mm lower bound and a review of the other arbitrary limits. The current publication reference selects about 1.51 mm and includes full-sun solar; finer integration grids verify it. Further thin-strip handling, combined contact stresses, braced frame design and the upstream injector remain follow-up work.

## Structural architecture audit

The [drum taper/startup audit](blended/DRUM_TAPER_AND_STARTUP.md) exposes the existing 7.26:1 area taper assumption. Before updating the mass optimum, resolve the 129.5% ideal radial-root packing demand, non-radial torque-member shape/support, and the hub-deployed support mass and controlled handoff. The existing inventory is conditional on these unresolved details.

The selected rim-support concept is a branching tensile web, with support repeated across belt width. Recompute junction resultants from radial and tangential loads, peak sharing, taper and attachment packing. Include the retractable supports' actuation, own centrifugal load and startup torque. The old independent-member mass estimate remains conditional.
