# What sets the dimensions of a sling mill?

[Article draft](ARTICLE.md) · [Blended model](../blended/README.md)

A useful design balances material inventory against the loads needed to accelerate the bars. The objective is mass-payback time: the installed mass divided by useful delivery rate, with a stated operating duty and equipment boundary. Replacement consumption remains future work.

The model starts with roller tightness. The gap and structural compliance determine normal force, normal force determines sliding traction, and traction determines acceleration. Integrating that acceleration gives the required machine length. Feed dimensions and spacing separately determine how much material can pass through the lane.

| Design choice | What disfavors the small/low extreme? | What disfavors the large/high extreme? |
|---|---|---|
| Squeeze / normal force | Weak traction requires a longer machine with more stations and foundations; very low preload loses opposed contact. | Higher pressure, structural loading, bond shear, payload loading and heating. |
| Drum radius | Higher RPM, contact-layer retention loads and bending strain. | Larger drum/support envelopes and potentially fewer simultaneous contacts if pitch increases with radius. |
| Station pitch | More stations and hardware; adjacent drums eventually touch. | Greater load per engaged station and longer unsupported bar spans; sufficiently large gaps lose continuous engagement. |
| Lamination thickness | Less wear life and less tolerance for surface damage. | More rotating mass, attachment load and changed contact compliance. |
| Structural Zylon thickness | Larger stress or deflection under the required load. | Added material and centrifugal loading. |
| Hub radius relative to drum | Poor torque leverage requires greater tensile-member loads. | More rigid-hub material and greater hub peripheral speed. |
| Bar length | Higher feed frequency and fewer simultaneous contacts. | Larger contact-speed range during acceleration, plus greater handling/alignment burden. |
| Bar depth | Reduced stiffness and strength; higher feed occupancy at fixed flow. | Larger individual loads and heavier contact machinery. |
| Bar width | At fixed throughput, higher feed frequency and occupancy. | Larger individual loads and wider supporting machinery. |
| Roller speed above bar speed | Insufficient forward sliding, especially if the roller slows under load. | More frictional heat and rotational loading. |
| Inlet speed | Greater feed occupancy and weaker low-speed centrifugal support. | More injection machinery and power; part of the acceleration burden moves upstream. |
| Attachment count | Longer unsupported belt panels and larger panel deflection. | More joints, terminations, packaging and assembly effort. |

The entries describe mechanisms to include or constrain. Some hardware and material laws remain preliminary. An optimum can lie at a real engineering limit, and some dimensions may approach a scaling plateau.

The effects must be calculated together. Increasing squeeze raises traction but also shortens the accelerator; its total heating and total mass follow from the combined solution. Likewise, if width and throughput scale together, much of the material-per-flow ratio can remain unchanged.

## Throughput and acceleration are connected through constraints

For a bar of density ρ, width W and depth D moving into the machine at speed v₀, the maximum single-lane flow is bounded by the permitted inlet occupancy φ:

`ṁ ≤ φ ρ W D v₀`.

For the fixed 10-million-tonne/year study, the required feed occupancy and launch frequency are derived. Tightness then determines how long the accelerator must be to reach the target speed. Alternatively, for a fixed available site length, the acceleration must be high enough to reach that speed within the site. Power and cooling capacity provide additional flow limits.

The first [blended calculation](../blended/README.md) now closes squeeze, belt deflection, layer compression, traction and local acceleration in one reduced model. Its comparisons show the loose-setting length penalty and the tight-setting bond/thermal penalties directly.

### Payload-load clarification

The [iron and hardware audit](PAYLOAD_AND_PAYOFF.md#longitudinal-loading-stronger-pull-toward-the-front) distinguishes front pulling, rear pushing and distributed traction. The old full-end-force Euler constraint is an assumed compression case; establish the traction distribution before treating it as a design limit.
