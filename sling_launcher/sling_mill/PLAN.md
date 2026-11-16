# Sling mill engineering sequence

[Overview](README.md) · [Current results](RESULTS.md)

## 1. Scalar and discrete-station reference — implemented

Fixed annual flow, independent rod dimensions, exact hub-tangent geometry, finite-patch engagement, forward-sliding schedule, power and heat integrals, conditional fiber/hardware inventory, strength/stability screens, storage alternatives and parameter sweeps. Mathematical tests validate the baseline and energy closure. The figures show the requested geometry and relative machine/payload sizes.

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
