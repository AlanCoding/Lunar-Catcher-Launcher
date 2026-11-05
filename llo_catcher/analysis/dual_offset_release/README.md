# Sub-analysis 2: two useful payloads from opposite offset release points

**Deferred. No new terrain computation in this branch has been requested.**

This branch concerns useful payloads released simultaneously toward prograde and
retrograde catchers, from north/south-offset positions of an equatorial sling.
It is separate from [sub-analysis 1: a single equatorial useful payload](../single_equatorial_release/README.md),
whose counterweight is disposable and whose useful launch can be modeled exactly
on the equator.

## Existing material to retain

- [Accepted spherical heading optimum](../heading_optimization/RESULT.md): a
  prograde 25 km catcher targeting solution for an offset tip; 141.557° orbital
  angle to capture. This remains an accepted orbital example, not a full
  two-catcher terrain study.
- [Previous two-arm, 3 m terrain sweep](../terrain/results/sweep_1deg/README.md):
  historical due-east/west 25/35 km node-targeted cases. These are preserved
  comparisons, not a revised design recommendation.
- [Release-state audit](../terrain/results/release_audit/README.md): why the
  historical sweep collided even though its release states were at periapsis.
- [Spherical tower/drop geometry](../spherical_release/README.md).

## Future question, not current work

Starting with a geometry more faithful to the installed launcher, assess release
clearance (10 m as the requested reference, plus a scan if authorized), both
outbound paths and both failed-capture returns through 1.5 payload orbits.
Choose the two catcher altitudes, release phases and radii explicitly; ensure
that both tips are compatible with the same physical installation.

The single-equator height survey is useful context but its 50% threshold is not
a universal terrain-roughness constant. Offset paths sample different terrain,
orbital targeting changes the height gained downrange, and simultaneous success
requires the intersection of two sets of acceptable sites. Do not assume their
probabilities are independent or that one-way 50% means paired 50%.
