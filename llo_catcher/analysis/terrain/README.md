# Initial terrain-data and impact-model reconnaissance

**Study split, 2026-11-04:** the [single equatorial release height survey](../single_equatorial_release/README.md)
now has initial results. The [two-offset-payload branch](../dual_offset_release/README.md)
remains deferred. This folder supplies the common terrain cache and preserves
the earlier two-arm results unchanged. The [spherical geometry study](../heading_optimization/RESULT.md)
is complete.

2026-11-03. **Data access, initial demonstration and the 360-site equatorial sweep completed.**

See the [results index](results/README.md) for the 1-degree equatorial sweep
and the [preserved initial demo](results/INITIAL_DEMO.md). The original plots
and numerical output remain in `demo_results/`; the sweep writes separately to
`results/sweep_1deg/`. The notes below retain the data-source and model context.
Supports the [equatorial failed-shot work item](../../work_items/EQUATOR_TERRAIN_AND_FAILED_SHOTS.md).

## Selected starting dataset

Use **SLDEM2015**, the merged LRO LOLA laser-altimetry / Kaguya Terrain Camera
DEM, for an equatorial survey. NASA's [product description](https://pgda.gsfc.nasa.gov/products/54)
explains the particular benefit near the equator, where LOLA tracks alone leave
coverage gaps. The merged grid covers 60 S–60 N at 512 pixels/degree, about
59.2 m spacing at the equator, with typical 3–4 m vertical accuracy. Pixel spacing
is not guaranteed feature resolution; the underlying stereo DEM resolves roughly
60–100 m. Local artifacts and shallow grazing paths need uncertainty treatment.
This is a credible regional survey product, not certification of metre-scale
clearance around equipment.

Primary distribution: [NASA PDS SLDEM2015 archive](https://pds-geosciences.wustl.edu/lro/lro-l-lola-3-rdr-v1/lrolol_1xxx/data/sldem2015/),
including [float-image tiles](https://pds-geosciences.wustl.edu/lro/lro-l-lola-3-rdr-v1/lrolol_1xxx/data/sldem2015/tiles/float_img/).
Dataset citation: Barker et al., 2016, Icarus 273, 346–355,
[doi:10.1016/j.icarus.2015.07.039](https://doi.org/10.1016/j.icarus.2015.07.039).

## Access demonstrated, not just a download proposal

[probe_sldem_access.py](probe_sldem_access.py) retrieved the nearest northern and
southern pixel-center rows spanning 0–45 E, using HTTP byte ranges. Both responses
were HTTP 206 with the expected ranges; the script rejects a whole-tile response.

- 23,040 longitude samples, each 1/512 degree apart.
- Only **184,320 bytes of binary elevation data** downloaded, plus two labels.
- Rows at latitude +0.0009765625 and -0.0009765625 degrees, averaged to latitude zero.
- Interpolated strip heights range approximately -2,898 to +2,019 m relative
  to the dataset reference sphere. This is one longitude sector, not a global survey.
- Each source tile is 1,415,577,600 bytes; a full global equatorial two-row strip
  would need only 1,474,560 bytes from 16 tiles if range access remains available.
  A finite latitude corridor needs more rows, sized to the trajectories.

[access_probe.json](access_probe.json) records URLs, byte ranges, checksums,
coordinates and summary values. Downloaded row data, labels and the NumPy extract
are cached in ignored `data/`; rerun to reproduce them:

```bash
.env/hub/bin/python llo_catcher/analysis/terrain/probe_sldem_access.py
```

The probe is intentionally small, not a generalized DEM service. Next implement
`terrain_radius(latitude, longitude)` with seam wrapping and bilinear interpolation,
then corridor extraction/caching and tests at tile boundaries.

## Critical metadata details

These float tiles contain little-endian 32-bit **kilometres of elevation** above
**1,737.4 km**. Decode radial distance in metres as
`1000 * (1737.4 + stored_value)`. The label's formula comment calls the result
metres although its UNIT and OFFSET are kilometres; explicit unit conversion
avoids that ambiguity. Other LOLA products use different scaling; do not reuse
this decoder without checking their labels.

Coordinates are east-positive and in the **Mean Earth/Polar Axis of DE421** frame.
Use the actual mapping and pixel registration in the labels. The current sling
model's reference radius is 1,738.1 km: blindly adding DEM elevations to that
radius would introduce a **700 m datum error**. Preserve physical radii and
translate height conventions; do not silently change the published design.

## A well-defined impact function

Longitude alone does not specify an impact. Define the underlying solver as:

```text
first_impact(release_epoch, release_position, release_velocity,
             terrain_model, gravity_model, orientation_model, time_horizon)
 -> status, impact_latitude, impact_longitude, flight_time, impact_velocity,
    closest_approaches_to_installation_and_both_catchers
```

Return a distinct `no_impact_within_horizon` status when appropriate, not a
fabricated landing point. With release height/geometry, direction, target orbit,
error prescription and epoch fixed, the longitude sweep becomes a function of
longitude. Sweep speed, heading, elevation-angle and timing errors separately.
Payload mass enters the sling release model; it does not independently change
a ballistic trajectory under the same initial state and gravitational model.

Proposed numerical sequence:

1. Construct the actual release state (not necessarily the track-center state).
2. Transform Moon-fixed position/velocity into an inertial frame, including
   surface rotation. For a fixed-axis model, `v_inertial = Q v_fixed + omega × r`.
3. Integrate the trajectory. At each time, transform back to the terrain frame
   and compute `clearance = |r| - terrain_radius(latitude, longitude)`.
4. Locate the earliest contact, including near-tangent contact. Limit spatial
   stepping near terrain so a narrow ridge cannot be skipped merely because
   the endpoints of a long time step are both above the DEM.
5. Return terrain contact and closest approaches to both stations/installation.
   Continue missed captures rather than terminating at intended arrival time.

Start with spherical two-body gravity and fixed-axis rotation as a comparison,
then quantify changes with a GRAIL field and time-dependent lunar orientation.
NASA provides [GRGM1200A gravity coefficients](https://pgda.gsfc.nasa.gov/products/50);
choose harmonic degree through convergence rather than assume full degree is
needed or low degree is sufficient. Earth/Sun perturbations and longer-lived
missed shots require an explicit accuracy/horizon assessment.

## Tilt, rotation and return: distinctions to preserve

**Idealized derivation:** in central gravity with a fixed rotation axis, a release
exactly on the lunar equator with velocity in that plane remains in that plane.
Tilting the entire system relative to Earth's orbit does not change that result.
There is no need to insert an arbitrary lunar-inclination correction into it.

Rotation about the axis does matter. A nominal low-orbit transfer ellipse with
perilune near the surface takes roughly 110 minutes to complete. Using the existing
study's sidereal rotation period (655.720 hours), that is approximately one degree
of surface rotation, or 30 km at the equator. If it completes a full orbit without
contact, its inertial perilune returns over a longitude about one degree west of
its original ground longitude. This applies to either direction for the same
orbital period. It is **not** a computed terrain-impact location or a clearance
proof: earlier terrain interception and no-intersection trajectories are possible.
For example, an elevated tangential release whose entire ellipse clears a smooth
sphere does not hit that sphere simply because its catcher misses it.

For realistic mapping, use orientation kernels and the DEM's stated frame.
[JPL's lunar frame kernel](https://naif.jpl.nasa.gov/pub/naif/generic_kernels/fk/satellites/moon_de440_250416.tf)
connects principal-axis and mean-Earth frames; the compatible lunar orientation
kernel is `moon_pa_de440_200625.bpc`. The Moon's orbital inclination, axial
orientation, libration and map-frame convention are different concepts. Do not
substitute one scalar tilt for this transformation.

Actual sling release geometry is a separate source of latitude motion: an
on-equator center with horizontal slings releasing east/west can have release
points north/south of the equator. This must be represented geometrically rather
than attributed to lunar tilt. Noncentral gravity also need not preserve an
exactly equatorial orbital plane.

## Selected first trajectory case (user clarification, 2026-11-03)

- Use the actual two-arm sling geometry. The **5,787.088 m** historical radius
  is a comparison; after the latest clarification, the free inputs are **catcher
  altitudes and common sling RPM**, and each arm radius is solved. The demo uses
  25 km prograde, 35 km retrograde and 2.7796279 RPM.
- **Release height is 3 m above the local lunar surface at the release point.**
  This is the user-specified release-clearance design constraint, not an apex
  height or a clearance assigned to some other point in the operating cycle.
  Initialize each release at the local DEM radius plus 3 m; keep the specified
  horizontal offset consistent when constructing that position.
- Start with a **correct launch followed by missed capture**, for each useful
  payload direction. Launch-speed and pointing-error sweeps follow later.
- Keep prograde/retrograde masses and target circular catcher altitudes as
  inputs. The heavier/lighter direction assignment is not yet fixed. Evaluate
  the surface-rotation contribution in the release-state calculation rather
  than assigning the heavier payload by assertion. Unequal target altitudes
  and sling balance/control requirements also affect that choice.
- Retain adequate active station control for nominal targeting; a missed payload
  receives no post-release correction in this first failure case.

The earlier Blender snapshot reports about 10.51 m loaded clearance over its
spherical datum. **That value must not replace the explicitly specified 3 m
release clearance in this study.** The frozen publication files are retained
as historical outputs; the initial conditions here follow the user's clarified
requirement. On real terrain, full cable clearance and compatibility of both
release points with a common launcher structure remain subsequent checks.

The DEM's typical 3–4 m vertical uncertainty must be propagated separately from
the specified 3 m physical release height; this dataset alone does not establish
metre-level launch-site clearance.

The requested horizon is now **1.5 payload orbital periods**, then classify as
`not_arrested`. Require both departures to reach the nominal catches before
counting later terrain contacts as successful failure arrest. Wider station-risk,
ejecta and beyond-horizon questions are outside this capped demonstration.

Both prograde and retrograde circular catchers, unequal payload masses and
active nominal station control remain in scope. No post-release correction of
failed payloads is assumed unless explicitly introduced as a separate scenario.
