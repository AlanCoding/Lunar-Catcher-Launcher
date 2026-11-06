# Technical Context Update: Zyling and the Two-Loop Kevlar Sling

Update the existing lunar sling blog work to incorporate two new launcher architectures. These are developments of the earlier two-rover lunar sling, not replacements for its fundamental operating principle.

The new concepts solve a major logistical problem: **how to continuously feed payloads into a rotating lunar sling without retracting kilometers of tether between launches or manufacturing disposable climbers.**

The post should introduce both systems and explain their mechanical operation. This is a short concept announcement, not a full feasibility analysis.

## 1. Zyling — Single-Loop Continuous-Feed Lunar Sling

The first concept is called **Zyling**, a combination of "Zylon" and "sling."

### Basic operating principle

The original lunar sling consisted of two opposing ground-driven vehicles, Haulin' Hank and Ballast Bubba, traveling around a relatively small circular track. Each vehicle supports a tall structural mast or A-frame, with long tethers extending radially outward to a payload and countermass.

The vehicles supply **tangential driving force**, accelerating the rotating assembly. The enormous radial forces are primarily handled through the tensioned structure, not through wheel traction.

The original design had a significant operational limitation: the tethers would need to be reeled back onto spools to load new payloads. The spools themselves, mounted near the tops of the vehicle masts, were particularly awkward.

Landis previously considered payloads sliding outward along a rotating tether. However, such sliders need to manage the energy released as they move outward and potentially need to be manufactured and recovered for each launch.

Zyling takes the idea further by making the tether itself into a **continuous circulating conveyor loop**.

### Mechanical arrangement

- A continuous tether loop extends radially outward from a central feed wheel to an outer turnaround.
- The loop has two strands: an outbound strand carrying payloads outward and an empty return strand traveling inward.
- The entire arrangement rotates around the central lunar hub at angular velocity Ω.
- A separate conveyor motion circulates the tether through the central wheel at feed speed u, much slower than the approximately orbital tangential speed of the sling tip.
- New payloads attach near the hub and travel outward while the machine keeps rotating.
- Multiple payloads are simultaneously attached at different radii.
- At the outer end, payloads detach at the appropriate orbital insertion point. The tether itself returns inward, completing the loop.
- The conveyor never needs to retract its entire tether between launches.

The opposite side of the system retains a corresponding counterweight arrangement. **The counterweight mass must be released nearly simultaneously with the payload.** A permanent fixed counterweight cannot cancel the sudden change in radial load when a payload detaches. Coordinated release is an important part of the design, although dynamic stress waves remain a concern.

### Forces and energy

As each payload moves outward, its tangential velocity increases because the entire machine maintains approximately constant angular velocity.

This increase in angular momentum must be supplied by the main rotating hub.

Meanwhile, centrifugal effects tend to accelerate the payload outward along the tether. The conveyor feed mechanism restrains this motion and therefore acts primarily as a **regenerative brake**, extracting mechanical energy.

In an idealized constant-angular-speed model:

- Main hub work on a payload: m Ω² (R² − r₀²)
- Energy extracted by the conveyor brake: ½ m Ω² (R² − r₀²)
- Net mechanical energy supplied: ½ m Ω² (R² − r₀²)

Here R is the release radius and r₀ is the loading radius. These expressions exclude losses and assume the idealized radial feed geometry.

This regenerative balance also existed implicitly in the earlier spool concept, but Zyling provides a much more industrial, continuously operating mechanism for exploiting it.

### Coriolis geometry and throughput

Because the system rotates, moving material experiences Coriolis acceleration:

**a = 2 Ω u**

The force acts in opposite tangential directions on the outbound and returning strands.

The expected geometry has the outbound strand trailing the hub's rotation and the return strand leading it. The exact strand trajectories must eventually be determined through mechanics and simulation.

The conveyor feed speed creates a fundamental tradeoff:

- **Slow feed:** many payloads accumulate along the outbound strand, substantially increasing its centrifugal tensile load.
- **Fast feed:** fewer payloads are attached simultaneously, reducing their combined radial loading, but increasing Coriolis acceleration, cable deflection and potentially lateral stress or instability.

This suggests an optimization problem involving conveyor speed, tether strength, mass and desired payload throughput.

The main drive also faces a throughput-dependent torque requirement. Increasing the radius of the central ground track allows the vehicles to deliver greater torque for a given tangential driving force.

### Material limitation

A uniform untapered tether carrying no payload has approximately the following centrifugal self-stress:

σ = ½ ρ v²

At a lunar orbital launch velocity of approximately **1.67 km/s**, this implies a required working specific strength of:

**1.394 MJ/kg**

This is a severe demand. With a safety factor of two, conventional high-strength Kevlar is not sufficient even before payload loading.

Zyling therefore probably requires a more advanced material, such as Zylon, or another improvement to the structure. The material choice is not finalized.

The outer turnaround mechanism is also an open engineering challenge, particularly because it must operate at enormous centrifugal acceleration.

## 2. Two-Loop Kevlar Sling — One Stage of Tapering

The second concept is a direct development of Zyling.

It preserves continuous feeding but introduces **one discrete stage of tether tapering** by replacing the single circulating loop with two successive loops of different cross-sectional area.

This is a particularly exciting variation because it may permit high-strength Kevlar rather than requiring a more exotic material.

### Mechanical arrangement

The machine now has:

1. **A thicker inner conveyor loop**, extending from the central hub to an intermediate radius.
2. **A thinner outer conveyor loop**, extending from that intermediate radius to the final release radius.

The two loops meet at a **shared intermediate wheel assembly**.

Each loop has its own outbound and return strands. The intermediate wheel provides the outer turnaround for the inner loop and the inner turnaround for the outer loop.

The wheel assembly may use two coaxial sheaves or grooves. Both loops must have compatible feed speeds, while the entire system continues rotating around the central hub.

The intermediate wheel is not attached to the hub by a kilometers-long rigid arm.

Instead, it is proposed to remain at its radial operating position through the balance of tether tensions and centrifugal forces associated with the rotating assembly. Its stability and practical mechanical design remain unproven.

### Payload transfer

A payload:

1. Attaches to the thick inner conveyor near the central hub.
2. Moves outward along that conveyor while gaining tangential speed.
3. Arrives at the intermediate wheel.
4. Transfers from the inner loop to the outer loop.
5. Continues outward on the thinner outer conveyor.
6. Detaches at the final launch radius.

**The intermediate handoff is the essential new mechanical challenge.**

Ideally, the two conveyors have matched radial feed velocities and the same angular velocity around the lunar hub. Thus, the handoff changes which conveyor supports the payload without requiring a major change in the payload's velocity.

However, transferring the full centrifugal load safely and reliably at this junction is an unresolved engineering problem.

The system must also preserve the paired-release principle on the opposite side of the launcher.

### Why two loops help

A conventional tapered rotating tether is thicker toward the center because the inner sections must support the centrifugal loading of material farther outward.

A uniform conveyor cannot easily reproduce this taper because the entire cable continuously passes through the same wheels.

Two separate conveyor loops solve part of that problem.

The inner loop can have a larger cross-sectional area than the outer loop. The intermediate wheel transfers the radial load between them, producing a **stepped approximation of a tapered tether** while retaining continuous circulation.

This can substantially lower the material specific strength needed to support the moving tether.

### Preliminary material comparison

For the same approximately 1.67 km/s lunar launch velocity, considering tether self-loading alone:

| Arrangement | Required working specific strength |
|---|---:|
| Single uniform loop (Zyling) | 1.394 MJ/kg |
| Two loops, approximately optimized with 6:1 cross-sectional area ratio | 0.761 MJ/kg |

For the two-loop example:

- Intermediate wheel radius approximately 0.674 times the final release radius.
- Inner conveyor cross-sectional area six times the outer conveyor area.
- Peak calculated stress is approximately equal in both loops.
- For Kevlar density 1,440 kg/m³, maximum idealized self-stress is approximately 1.10 GPa.
- Representative Kevlar ultimate specific strength is around 2.08 MJ/kg.
- With safety factor 2, nominal working specific strength is approximately 1.04 MJ/kg.

Thus, **the two-loop design passes the idealized tether self-loading check for Kevlar at safety factor 2, while the single-loop version does not.**

These figures exclude payload loading, pulley masses, bending, dynamic stresses, environmental degradation and release transients. They are not a demonstration of a feasible full machine.

The 6:1 ratio approximately balances peak self-stress between the two loops. It is not necessarily the ratio that minimizes total system mass or maximizes throughput.

### Engineering implications

The double-loop configuration adds complexity:

- An intermediate wheel suspended within a rotating, tensioned system.
- Two independent circulating tether loops.
- A payload handoff mechanism operating under substantial centrifugal load.
- Multiple load-bearing pulley paths.
- Additional transient loads and possible vibration modes.

However, it potentially replaces a large material-strength obstacle with a mechanical-engineering challenge.

The result is an unusual, gear-driven lunar launcher with substantial opportunity for retro-futuristic industrial imagery. A playful reference to *The Jetsons* and Spacely Sprockets fits the character of this machinery.

## Scope of the new blog post

The post should focus on the conceptual progression:

**Original retracting go-kart sling → Zyling continuous-feed conveyor → single-loop material limitation → two-loop Kevlar conveyor with discrete tapering.**

Explain the energy recovery, simultaneous payload feeding, central importance of Coriolis effects, and the added intermediate handoff.

Use the planned four image assets: Zyling hero illustration, Zyling engineering schematic, two-loop hero illustration, and intermediate handoff detail.

Keep the writing relatively short and concept-focused. Avoid presenting preliminary calculations as validated engineering results.

The broader goal is to record these two new architectures publicly so that the actual tether dynamics, optimum feed speeds, material mass, intermediate wheel stability, coordinated release and handoff mechanics can be investigated rigorously later.
