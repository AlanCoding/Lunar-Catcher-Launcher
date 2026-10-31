# Initial BOM for review — unsized

> Historical baseline/review. The current speed-constrained spooling model and
> engineering status are in [CHECKPOINT.md](../CHECKPOINT.md) and the
> [scenario method](../results/speed_constrained/METHOD.md). Earlier independent
> track-radius and fixed-deployed-sling assumptions do not govern that branch.

The [force-diagram review document](force_diagram_review.md#complete-named-parts-key)
assigns stable IDs B01–B23 to these rows in order and shows their load paths.

I = permanent imported; L = permanent lunar-sourced; E = lunar expendable per
launch; P = useful captured payload. Importance is a hypothesis to test, not a
computed ranking. Counts refer to the complete two-sided machine. Source IDs
refer to [sources.md](sources.md); TBD means no defensible sizing data yet.

| Component | Class / initial assumption | Proposed mass method | Data source / gap | Expected importance |
| --- | --- | --- | --- | --- |
| Four primary A-frame legs | I; one near-vertical and one trailing per assembly | Axial plus bending sizing; Euler/local buckling and joints; integrate section volume times density | Structural material supplier data and beam handbooks TBD; compare metal tubes and composite tubes | Likely high; geometry/load dependent |
| Braces, cross-members, wheel mounts | I; include radial support width if needed | Force/moment load paths, section sizing and joint allowance reconciled separately | Stability derivation first; joint/catalog data TBD | Potentially high; not presumed a massless truss |
| Two apex housings/joints | I | Combined sling/stay/leg reactions, spool support bending and bearing loads | Load envelope then bearing/joint supplier data TBD | Medium to high |
| Two tapered outward slings | I; Kevlar, grade/construction pending | Integral of load-bearing area times density including own rotational load; explicit sheath/end masses | S1 preliminary yarn guide; finished-cable and lifetime evidence missing | Likely high; test rather than assume dominance |
| Main apex-to-apex radial tie | I; one direct tether crossing the center, material pending | Distributed-mass rotating elastic cable sizing, sag/clearance, peak tension and asymmetric load paths; no assumed ground reaction at center crossing | Supplier cable/termination data TBD | Potentially high; carries principal opposing radial loads |
| Two small pivot stabilizing stays | I; apexes to ground-level pivot, tension only | Force/moment equations with main tie present, pretension, sag, dynamic and asymmetric load envelope | Supplier cable/termination data TBD | Intended small; verify rather than impose low force |
| Tether terminations, guides, sheaths | I; all cable ends and wear interfaces | Rated end-fitting loads; sheath linear mass and wear-life bounds | S1 environment discussion; actual supplier data TBD | May be substantial; avoid counting twice in sling totals |
| Four large powered wheels, hubs, bearings | I; ordinary mechanical wheels, speed target unverified | Wheel load/contact footprint, hoop/centrifugal stress, speed rating, endurance; catalog minima | S2/S3 context, high-speed design data TBD | Uncertain; 80 mph is not supported by rover heritage alone |
| Four drive motors and transmissions | I; separate from wheel mass | Individual torque-speed-duty envelopes and efficiency maps; gearbox/bearing thermal limits | Manufacturer continuous/peak ratings and mass TBD | Potentially high at sustained power |
| Four smaller passive steering wheels | I; one fore/aft of each powered wheel; shown ahead for illustration | Wheel/steering hardware mass allowance; detailed passive-contact traction and load sharing omitted per user | Steering catalog data TBD | Low to medium; mass counted, individual contact feasibility unresolved |
| Two apex spools and tension-holding drives | I; slings remain extended during each cycle | Required holding/management envelope, stored cable volume if needed, bend radius, drum torque/inertia, holding/braking hardware; no cyclic full-length payout assumption | Cable bend/fatigue and drum/drive data TBD | Potentially high; not a zero-power or massless device |
| Central pivot, bearing and rotating attachments | I; stabilizing role, at ground level | Stabilizer resultant and transient reactions; bearing capacity and ground-level support sizing; main tie does not terminate here | Bearing supplier data TBD | Intended secondary; verify actual load envelope |
| Ground-level pivot anchors | I plus L if rock foundation used | Stabilizer anchor reaction/pullout bound, imported fittings separately | Regolith/rock anchoring evidence TBD | Uncertain until stability loads are calculated |
| Two reusable climbers | I; both return | Separate chassis/grip, onboard motor/drive, rollers, electronics and thermal masses sized for load/speed/traction | Kevlar-compatible grip and drive data TBD | Potentially high; travel power and sling contact unresolved |
| Climber support/guidance and service hardware | I; only if required | Explicit required parts and lineal/rated masses; avoid overlap with chassis and slings | Architecture-dependent, TBD | Uncertain |
| Distributed solar panels and support/deployment hardware | I; direct supply, no batteries | Installed area/mass from time-resolved demand and incidence/temperature/dust losses; distinguish bare-panel from installed specific power | S4 context; chosen product/assembly data TBD | Likely high; peak load governs |
| Power conversion, motor controllers, permanent electrical equipment | I | Simultaneous power/current ratings, efficiency, cooling and mass; bounded aggregate power-transfer hardware allowance | Converter/controller catalog data TBD | Medium to high; transfer network design is waived, its hardware mass is not automatically zero |
| Controls, sensing, communications, wiring | I | Functional inventory, rated equipment minima and harness allowance | Catalog and environment data TBD | Size floor at small payloads |
| Thermal and environmental protection | I; radiators, insulation, dust covers, shielding as needed | Heat rejection at operating temperatures, area and areal density; component environmental limits | S4/S5 context; qualified components TBD | Could be important for continuous operation and night survival |
| Ballast retention and adjustment hardware | I | Container/attachment sizing for full local ballast loads, not imported ballast mass | Mechanical loads and catalog data TBD | Coupled to ballast solution |
| Regolith/rock wheel ballast and optional foundation fill | L | Minimum from feasible wheel-contact/traction/stability equations, including its own acceleration and rolling losses | S2/S3 and derived equations | Potentially very large physical mass/inertia |
| Rock countermass | E | Per-launch released mass from chosen mass ratio; trajectory and clearance feasibility | Orbit and balance derivation | Direct consumption and energy cost |
| Useful payload | P | Captured useful kg denominator, separate from both returning climbers | User-selected scale, capture condition | Normalization, excluded from permanent machine |

## Explicit boundaries

- Loading interface and payload-release mechanism are excluded by request. Do
  not assign invented detailed masses. Release timing and removal of payload
  forces still belong in the dynamic load envelope. Report the objective as
  subject to these mechanism exclusions.
- Prepared road, grading, and road construction are site assumptions/exclusions.
  If imported road surfacing becomes essential, add it explicitly or reject the
  branch under the initial site assumption.
- Catcher hardware is outside the primary objective. Report encounter velocity,
  momentum and station-keeping implications separately.
- Local rock extraction/transport infrastructure is an unresolved logistics
  boundary. Do not silently treat dedicated permanent imported machinery as free;
  identify what existing site service supplies and add dedicated launcher
  equipment if it is needed inside the agreed scope.
- No batteries, separate flywheel, or unspecified regeneration credit. Night
  survival cannot assume powered heaters without a permitted energy source.
- No arbitrary bulk contingency disguises unmodeled subsystems: first itemize,
  then apply explicit subsystem margins once supported.

All masses remain **unsized**, not zero. A finite mass ratio cannot yet be
reported. Future accounting will produce one row per physical item/category,
absolute kg, kg/captured-payload-kg, assumptions, uncertainty, and mass margin.
