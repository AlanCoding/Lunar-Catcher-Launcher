# Method and verification

[Result and scope](README.md)

## Orbit and frame

Let z(lambda) be the interpolated equatorial terrain elevation above reference
radius R, H the release height above local ground, and lambda0 the release
longitude. Set

```text
r_p = R + z(lambda0) + H
r_a = R + 25,000 m
a = (r_p + r_a)/2
e = (r_a - r_p)/(r_a + r_p)
p = r_p (1 + e)
h = sqrt(mu p)
v_release_inertial = h/r_p
v_release_surface_relative = v_release_inertial - Omega_Moon r_p
```

Initial Cartesian position/velocity can be written (r_p, 0, 0) and
(0, v_release_inertial, 0). Radial speed is zero and speed is supercircular,
so release is periapsis. The body-fixed longitude is

```text
lambda(f) = lambda0 + f - Omega_Moon t(f)
r(f) = p / (1 + e cos(f))
t(f) = (E - e sin(E))/n, with orbital cycles unwrapped
n = sqrt(mu/a^3)
```

Capture occurs at f=pi and t=T/2. A failure is followed to f=3pi and t=1.5T.
At the catcher the payload is slower than the circular station, with no
north/south component; the relative speed is sqrt(mu/r_a) - h/r_a.

The useful launch is prograde only. Fixed constants are R=1,737,400 m,
mu=4.902800118e12 m³/s², and lunar sidereal rotation period 655.720 hours.
Catcher altitude is above the reference sphere, not a constant distance above
the variable surface below it.

## Terrain intersections without missing a dip between time samples

The equatorial DEM profile is the average of its two bracketing latitude rows,
with interpolation between adjacent longitude pixel centers. This exactly
matches the existing bilinear sampler at latitude zero. Longitude wraps.
It is a piecewise-linear elevation function, with approximately 59 m grid spacing.

The solver visits **every interpolation knot** within each possible-contact
interval. It also finds the interior minimum of clearance within any cell whose
endpoint derivatives straddle a minimum. This catches even a grazing contact
when both cell endpoints are above the ground. First contact is then solved
within the corresponding segment by a bracketed root solve.

This works particularly well here because all possible contacts lie near
periapsis. Radii above the maximum equatorial terrain elevation cannot collide;
those portions of the orbit are skipped analytically. In every examined case,
the resulting intervals lie within 90 degrees of a periapsis (checked in code).
There r(f) is convex. Body-fixed angular travel x=f-Omega*t(f) is monotonic, and
r(x) remains convex: its second derivative has a positive r'' term and a
nonnegative term proportional to (r')². Subtracting linear terrain within a
cell therefore yields a convex clearance curve with at most one interior
minimum. Endpoints plus that minimum suffice to find the lowest clearance in
that cell.

Only the initial outbound interval near f=0 and the return interval around
f=2pi can contain terrain contact before the f=3pi cutoff. The latter interval
includes descending and ascending portions; it is not truncated at the second
periapsis. This is an intersection method for the interpolated DEM, not a
claim to resolve unmeasured small-scale lunar topography.

## Height scan

For each of the 360 release longitudes, solve for zero minimum outbound
clearance as a function of H, holding the catcher radius fixed. Root tolerance
is 0.001 m. Heights equal to the boundary graze; positive margin is required.
A site with no negative clearance at H=0 has a threshold of zero.

The 180th ordered site threshold sets the height at which at least half the
sample clears. Round upward to 0.1 m, giving 2,310.7 m, and actually propagate
and classify all 360 cases at that height. Also classify all sites at 3, 10,
30, 100, 300, 1,000, 3,000, 6,000 and 10,000 m. The independently classified
outbound outcomes at all ten heights agree with the per-site thresholds.

## Validation performed

- At the selected 50% height, repeat all 360 classifications with each DEM
  cell additionally split at its midpoint. Categories are identical; maximum
  first-contact time change is below 5e-12 seconds.
- Verify the equatorial terrain slice agrees with the original bilinear
  sampler, including longitude seams.
- Verify a constant-radius terrain sphere produces no impacts for a clear
  periapsis release.
- Verify longitude inversion and the exact 1.5-period horizon.
- Check a constructed interior grazing dip whose cell endpoints are clear.
- Independently integrate 12 representative first-contact states using
  Cartesian two-body differential equations, covering outbound and post-capture
  collisions at both 10 m and 2,310.7 m. Their sampled terrain clearances at
  the predicted impact agree with zero within 0.1 mm.

All five unittest methods pass. Numerical agreement does not remove the DEM's
metre-scale vertical uncertainty, interpolation limitations, or missing gravity
harmonics. In particular, quoted sub-metre threshold digits identify the model's
solution rather than a surveyed engineering clearance. The empirical 360-site
fraction is also not a randomized uncertainty estimate.

The source-code and terrain-manifest hashes are saved in results.json.
