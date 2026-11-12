# Is the straw needed? Paired drums with independent cables

[Straw overview](../README.md) · [Concept packet](../publication/concept/README.md) · [Engineering packet](../publication/engineering/README.md)

- **[Constant-speed angular histories](constant_speed/README.md):** a new free-cable run at 1.72 m/s with a 3 t tapered cable and 1 t payload; loaded extension, release and empty return, checked on two meshes.

## Question

Delete the two continuous straw guides and retain the paired drums, tapered
working cables, payloads, release batches and nominal schedule. Can independently
moving cables deliver the same useful flow with acceptable separation, stress,
recovery efficiency and control demands?

This comparison sits between [single-tether inertial dynamics](../../spooled_tether_2d/README.md)
and the [shared-guide screens](../screening/README.md). Its purpose is to determine
whether the guide earns its place. Either design may win. The comparison is between a continuous tensile straw
and independent cables. Maintaining an orderly, mechanically coupled corridor
over kilometers under high rotational acceleration is central to the straw
proposal.

## What already follows without a new simulation

| Feature | Guide-free counterpart |
| --- | --- |
| Gradual preparation and common release | Retained through independent tether schedules and ready-load holds |
| Tapered high-tension working cables | Retained |
| Rigid opposed payout/return drums | Retained; shaft torque can transfer through the common rotor |
| Equal drum angular motion | Retained; geometry and effective cable speeds still need consistent treatment |
| Continuous transverse contact between streams | Removed; individual cable shapes and root reactions carry those demands |
| Straw opening loads and sliding friction | Removed with the guide; ordinary reel/fairlead contacts remain |
| Shared spatial corridor | Must be replaced by adequate free-cable spacing or other guidance |

The guide is therefore a candidate means of **controlling relative motion and
transferring transverse force**. Simultaneous batches and rigid-drum energy exchange
do not establish that a guide is necessary.

Deleting the two assigned 3 t guides removes **6 t**, about **4.2% of the 144 t
working-cable inventory**. That is the direct fiber credit. The 26 t combined
jacket/termination/opening allowance contains several functions, so it cannot all
be removed. Additional savings or costs require a new contact/support ledger.

## Why the trajectories could change

A payload moving outward while co-rotating needs tangential acceleration. An
independent cable supplies it through its changing direction and tension. Returning
material has the opposite Coriolis demand. A guide permits local contact forces
between the streams; separate cables send their individual reactions back through
their attachments and develop their own angular shapes.

The rigid shaft still couples drum torque, but this does not fix each cable's
spatial trajectory or guarantee the same recovered power history. Actual cable
geometry, angular momentum, endpoint loads and length constraints must be solved
together. Fully extended lines might remain orderly while moving or newly unloaded
lines occupy a much broader angular envelope. Existing single-tether results
motivate that question but do not settle neighboring-line clearance.

## Matched first experiment

**Hold fixed:** material/taper, payload and opposing mass, mean delivery rate,
release speed, drum pairing, nominal start times, required catcher windows and
root support geometry. Begin with the accepted 48-line reference. Use the same
finite acceleration/deceleration ramps and release-force ramp in both cases.

**Change:** shared-guide contact on/off. For the guide-free case, allow cable
angles and shapes to evolve rather than imposing the straw's radial trajectory.
Initially retain the same nominal winding program; if it fails, search for a
feasible program at the same delivery rate and report the required changes.

1. Run one representative loaded outward/empty inward paired exchange with full
   cable and payload inertia. Include the full-extension hold, a release event
   and unloaded return in a continuous history. Carry the actual state through
   release so the unloading wave is included.
2. Repeat at the scheduled phase offsets and assemble the bank's spatial envelope.
   Independent histories are a first collision screen. If trajectories overlap,
   that result identifies a conflict; it does not simulate cables passing through
   one another. Add coupled contact only when a configuration needs it.
3. Compare both designs at equal delivery rate, with cable diameter, payload size,
   timing uncertainty and a declared separation margin. Start in-plane; vertical
   lane offsets and true 3D routing follow if the 2D result requires them.
4. If necessary, adjust payout timing, lane separation and root placement while
   retaining common release windows. Quantify any larger hub, extra reserve cables,
   support hardware or reduction in usable throughput.

## Decision metrics

- Minimum cable-to-cable and payload-to-cable distance over the complete cycle;
  angular envelope versus deployed length, including hold and release.
- Maximum stress, slack/re-tension events, endpoint motion and release-wave loads.
- Common-rotor torque, energy transferred between mates, net ground-drive demand,
  and total losses including guide contact where present.
- Guide/support/hardware mass and working cable inventory per useful mass flow.
- Timing sensitivity, loading access, wear and required control authority.

A guide-free design is attractive if separation and controllability can be met
with modest packaging or timing changes. A shared guide is attractive if its
contact and opening costs buy materially smaller envelopes or simpler feasible
operation. 

**Status:** single-cable constant-speed dynamics are available in the linked study.
Matched guide-equipped and guide-free bank dynamics remain to be run.
The publication should explain this open alternative. The current mass budget
continues to describe the guide-equipped reference until a comparison supplies
replacement values.
