# Sling mill: model, variables and engineering boundaries

The [connected blended model](blended/README.md) is the current development
path: tightness is independent and acceleration is derived. This document
retains the original constant-acceleration/discrete-contact baseline.

[Topic and results](README.md) · [Original handoff](BRIEF.md) · [Parameter file](config.json)

The [optimizer development](optimization/README.md) extends this baseline with
an optional bonded contact layer and a derived gap/pressure model. Coating mass
enters the belt/cable force balance and rotor inertia when enabled; the original
configuration retains zero coating. The new contact-law patch still requires
feedback into the baseline engagement calculation, tracked as an explicit
closure constraint.

## Design contract

A single straight lane delivers 10 million metric tonnes in 365 operating days, at a reference exit speed of 1,600 m/s. Opposed drums accelerate manufactured rectangular rods by deliberate sliding friction. The upper drum turns counterclockwise and the lower drum clockwise in the side elevation, moving both contact surfaces forward. The rigid hub drives a flexible outer belt through tensile members.

The exit-speed reference defines a launcher comparison. Catcher interception, site elevation, flight direction, curved surface placement and final aiming require an orbital/site interface. The model uses a horizontal straight corridor. Entrance injection, rod manufacture, power generation, distribution infrastructure, redundant capacity and catcher hardware remain outside the installed accelerator inventory.

The baseline assumes continuous available power and 100% operating availability. Set fewer `operating_days` to increase the required instantaneous flow. No lunar-night reduction is applied.

## Independent variables

Every parameter below is stored in `config.json`. Values are SI unless a different unit is stated. The material library is in `structure.py`.

| Inputs | Meaning and baseline |
|---|---|
| `annual_mass_kg`, `operating_days` | 10¹⁰ kg/year; 365 operating days/year |
| `v_entry`, `v_exit`, `acceleration` | 100 m/s, 1,600 m/s, 9,806.65 m/s² (1,000 Earth g) |
| `radius`, `hub_ratio`, `pitch` | Belt R=0.10 m, hub r/R=0.25, station spacing 0.20 m |
| `payload_length`, `payload_width`, `payload_depth` | Independent L=1 m, W=0.060 m, D=0.040 m |
| `payload_density`, `payload_modulus`, `payload_allowable`, `payload_heat_capacity` | Illustrative manufactured rod: 3,000 kg/m³, 70 GPa, 100 MPa, 800 J/(kg K); these describe a hypothetical material envelope |
| `mu`, `contact_patch`, `belt_width` | Assumed sliding coefficient 0.5, effective patch length 20 mm, width 60 mm |
| `material` | Kevlar 49, Zylon AS or Zylon HM; baseline Zylon HM |
| `strength_safety_factor`, `joint_efficiency`, `environment_factor` | 2, 0.8, 0.8; manufactured working stress = nominal strength × efficiencies / safety factor |
| `attachments`, `torque_members_effective` | 64 radial and 64 torque members per drum; 8 torque members share the peak drive load |
| `belt_deflection_fraction`, `minimum_belt_thickness` | Panel deflection allowance δ/R=0.005; manufacturing floor 0.2 mm |
| `dynamic_factor` | 1.25 multiplier on peak structural traction/normal loads |
| `slip_margin`, `speed_droop` | Added end-contact sliding speed, m/s; reserved fractional speed loss. Baseline both zero |
| `storage_design_droop` | 1% allowable speed loss for the separate stored-energy sizing calculation |
| `motor_supply_mode`, `motor_efficiency` | `contact_following` or `constant_mean`; efficiency 0.95 |
| `radiator_temperature`, `radiator_sink_temperature`, `emissivity` | 400 K, equivalent sink 250 K, ε=0.85 |
| `heat_to_belt_fraction`, `radiator_kg_m2` | Half the friction heat enters the machine; radiator allowance 5 kg per m² of effective emitting area |
| `hub_density`, `hub_shear_allowable`, `hub_wall_min` | 7,800 kg/m³, 100 MPa, 2 mm wall; torque shell screen only |
| `motor_kg_per_kw`, `bearing_kg_per_kn` | Explicit provisional allowances: 2 kg/kW of electrical drive rating, 0.5 kg/kN resultant bearing load |
| `frame_allowable`, `frame_density`, `frame_buckling_allowance` | 100 MPa, 7,800 kg/m³, factor 4 on axial member volume |
| `startup_support_kg_per_drum`, `foundation_kg_per_pair`, `guide_kg_per_m` | Provisional 2 kg/drum, 200 kg/pair, 20 kg/m |
| `contact_modulus` | 1 GPa reserved effective indentation input; the current membrane panel screen does not use this parameter. A coupled contact constitutive law is a next-stage task |
| `normal_mismatch_fraction`, `traction_mismatch_fraction`, `misalignment_radians` | Perturbation screens: 1%, 1%, 0.001 rad |
| `integration_steps_per_pitch` | Numerical resolution; baseline 30; verification at 60; sweep uses 8 |

Independent L, W and D remain available. The **radius sweep** explicitly chooses L=10R and pitch=2.2R, while W and D stay fixed. Other sweeps change one input. Thus the radius sweep explores a declared family of machines. Variable station spacing and joint multi-variable optimization are future extensions.

Pitch is also independently varied in the [station-spacing study](PITCH_STUDY.md),
with R and all payload dimensions fixed. This explicitly tests pitch greater than
2R. The main system illustration uses the 300 mm pitch case; the baseline result
tables continue to validate the handoff's 200 mm pitch example.

## Dependent variables and flow

```
m = ρp L W D                   ṁ = annual_mass / (operating_days × 86400)
f = ṁ/m                        launch interval = 1/f
S = (v_exit² − v_entry²)/(2a)    flight through machine = (v_exit − v_entry)/a
entrance occupancy = f L/v_entry
minimum clear gap = v_entry/f − L
```

As rods accelerate, their spacing increases. For equal trajectories displaced by Δt, the rear-position difference is `v(t)Δt + aΔt²/2`. The diagrams use this expression. Entrance occupancy above 1 rejects a single lane. Final steady spacing is `v_exit/f`; the final clear gap subtracts L.

Stations cover the rod from the start through its final acceleration: the rod occupies `[x,x+L]`, and a station has a finite patch centered at `x_i`. Overlap fractions set the force-sharing weights. At every numerical step the weights normalize to total force `ma`. Patch edge engagement therefore changes each station's force continuously. Actual clamping control is required to realize this prescribed sharing.

The 130.0138 m acceleration distance contains approximately 650 pitch lengths (651 after rounding upward). Supporting a complete 1 m rod through entry and exit gives **655 installed pairs**. This distinction explains the slight departure from the handoff's approximate 650.

## Sliding, work and energy

```
v(x) = sqrt(v_entry² + 2ax)
u_i = [v(min(x_i + patch/2, S)) + slip_margin] / (1 − speed_droop)
P_slip_i = F_i (u_i − v)
E_kin_i = ∫ F_i dx             E_slip_i = ∫ F_i (u_i − v) dt
```

Spatial midpoint quadrature assigns exactly `ma dx` kinetic work at each step, so global energy closure can be tested independently of friction. The selected nominal rim speed exceeds payload speed throughout each contact in the prescribed-speed solution. Actual storage-mode droop must pass a second check.

For constant station force and zero speed margin, `E_slip = F (v_leave−v_enter)²/(2a)` is an independent analytic test. The baseline's finite patches and edge contacts give 4.19 MW sliding heat; a point-contact five-station approximation gives a nearby value. Contact slip, adjacent-stage speed increments, and full launch speed change are separate quantities in the stage CSV.

Mean electrical input is `(P_kin + P_slip)/η`. Heat rejection includes drive inefficiency and the assigned fraction of sliding heat. The other friction-heat fraction leaves in the payload. Radiator area is `Q/[εσ(T⁴−T_sink⁴)]` in **effective emitting area**; physical footprint needs view factors, panel layout and lunar illumination. Bulk payload temperature rise is an energy average; local flash temperatures and ablation can be much more severe.

## Exact torque-member geometry

```
P=(R,0); Q=(r_h,0)
H=(r_h²/R, r_h sqrt(1−(r_h/R)²))
H·(P−H)=0
length(QP)=R−r_h; length(HP)=sqrt(R²−r_h²)
θ=asin(r_h/R)
```

A tensile force on P points toward H, giving positive counterclockwise torque `T r_h` and an inward radial component `T sqrt(1−(r_h/R)²)`. Mirroring H reverses drive direction for the other drum. Radial and torque members end at the same P. The diagram and tests use these coordinates directly.

## Flexible belt and contact: conditional panel screen

The free-ring benchmark is `σ=ρu²`. Radial members can change the load distribution, so the screen also considers short belt panels between hub-supported attachments. Let `ell=2R sin(π/n)` be a panel chord and δ its allowed transverse deflection. A small-deflection membrane approximation gives

```
T ≈ A ρ Ω² R ell²/(8δ) + N ell/(4δ)
    = A σ_self_panel + T_contact
A_strength = T_contact / (σ_allow − σ_self_panel)
```

This is a reduced load envelope combining distributed centrifugal loading with a concentrated contact load. It assumes the full normal force acts on one panel and applies peak panel tension around the drum for the anchor screen. Actual moving contact covers multiple panels, redistributes tension and changes shape; consequently this approximation can be conservative and loses validity at large deflection or large thickness.

For each attachment, inward-only support requires a nonnegative reaction. The screen subtracts adjacent panel tension components, a half contact normal load at the contacted anchors, and the torque member's inward component from the centrifugal outward load assigned to that anchor. Belt area is increased to leave 10% reserve over this local requirement. If its area coefficient is nonpositive, the panel geometry has no solution under these assumptions.

**Crucial result:** at low rim speed, centrifugal support is weak while normal traction force remains substantial. The baseline screen asks for a belt as thick as about 280 mm on a 100 mm radius drum. That exceeds the model's thin-belt range dramatically. These numbers diagnose a force-path problem worth solving next. They cannot establish the mass or operating shape of a buildable rotor.

Cables are sized with a constant-stress taper including their own rotating mass:

```
T(r)=T_tip exp[ρ Ω²(R²−r²)/(2σ_allow)]
A(r)=T(r)/σ_allow
mass=∫ρA ds; inertia=∫ρA r² ds
```

This relation is exact for the radial straight-cable axial balance. On the diagonal member it describes the axial projection on the prescribed straight line. Its transverse centrifugal loading bends it; a tension-only rotating-string boundary-value solution is required to recover its operating shape and actual torque arm. Attachments, belt/cable crossings, joint manufacturing, repeated bending and fatigue need explicit design.

The unloaded gravity threshold `u > sqrt(gR)` is only a necessary startup bound (0.40 m/s here). Required contact tension, disturbances and retraction of temporary supports set much larger practical thresholds. The force screen itself is evaluated at every station's operating speed. Startup/shutdown support allowances remain provisional.

## Rotor energy versus motor size

Each station has a periodic payload load with a long recharge gap, especially near the exit. Two alternatives are retained:

1. **Contact-following motors:** the motor supplies each contact pulse while maintaining fixed rim speed. Installed rating sums individual station peaks. Actual simultaneous plant demand sums the phased rods throughout the corridor and is much smaller.
2. **Constant-mean motors:** the motor delivers steady average station power while the drum supplies the pulse. `dE/dt=P_motor−P_contact`, and `ω=sqrt(2E/I)`. The code integrates the periodic deficit and computes required inertia for a chosen droop. Added belt mass `ΔI/R²` is only an inertia lower bound: its centrifugal loads need complete re-sizing before it can enter a valid BOM.

The original zero-margin rim schedule cannot tolerate any droop at the end of contact. A separate 3% headroom case tests whether the prescribed speed reserve covers the integrated rotor energy loss. The energy-screen calculation uses the fixed-speed contact work; when droop is substantial, friction work and load history must be coupled iteratively. `drive_cases.csv` retains the failures.

The current mass allowance for motors is a freely changeable 2 kg/kW. High-speed pulsed motors need dedicated engineering; this assumption is not manufacturer qualification. Similarly, the hub torque-shell estimate omits rotational strength design. Its final peripheral speed is 400 m/s, and the free-ring steel stress benchmark is about 1.25 GPa. A rotating disk/shaft design must address that separately.

## Payload strength and cargo processing

The baseline rod needs about **29.4 MPa** under the conservative assumption that its entire acceleration force is transmitted through one end. Distributed drum traction can substantially reduce internal axial stress; the actual traction density must be integrated along the rod to establish tensile and compressive regions. The current screen also evaluates Euler buckling between stations, gravity sag, bending due to normal-force mismatch, and small rigid-body pitch/yaw/vertical perturbations during one entry-pitch interval.

The payload material is specified by density, modulus, strength and heat capacity, independently of geometry. Metallic rods, sintered mineral/oxide rods and material in a load-bearing carrier are possible study families. Oxide content alone does not determine viability: porosity, flaws, tensile/bending strength, fracture toughness, surface abrasion and thermal shock matter. A brittle rod can meet a compressive-strength specification and still fail during handling or uneven contact. No particular lunar oxide product has been qualified here.

A ground plant would need to form straight rods with controlled cross-section and surface finish, inspect them, establish the 100 m/s injection velocity, and synchronize release at roughly 44 Hz. Metal refining, sintering or carriers add processing/return logistics to the mass-flow comparison. Loose granular cargo requires containment with adequate structural and contact properties.

## Mass accounting and limits

`mass.csv` separates outer belts, radial cables, torque cables, hubs, motors/drives, bearings, frames, startup supports, foundations, guides and cooling. Fiber mass derives from the conditional force screen; hubs from torque; frames from axial load with a factor for buckling. The remaining entries use declared per-load, per-power or per-unit allowances. Motors/drives are an integrated allowance; their rotor inertia is omitted from the stored-energy credit, making that credit conservative.

The reference motor-following inventory is dominated by an assumption about individually installed pulse-power ratings. The alternative constant-mean inventory is much smaller, but must close the stored-energy and forward-slip conditions. Neither inventory supports an economic ranking against electromagnetic launchers or the other sling architectures until belt contact, drum dynamics and real hardware design are closed.

A complete stability claim requires coupled payload rigid-body and beam modes, nonlinear moving contact, rotating belt/member modes, friction versus temperature and sliding speed, rotor imbalance, motor bandwidth, guides and controls. The present perturbation estimates identify loads and tolerance scales. They do not establish stability eigenvalues, wear life, geometric tolerance limits, or operational safety margins.
