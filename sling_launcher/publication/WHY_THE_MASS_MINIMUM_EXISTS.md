# Why the imported-mass curve has a minimum

**Lower acceleration makes the poles expensive; higher acceleration makes the
reel mechanisms expensive.** Near 50 g, the remaining pole-mass saving from
increasing acceleration becomes smaller than the additional reel-system mass.
That crossover produces the valley in the current reference curve.

This explanation uses the **current separate upper/low tie design**, with
50 mph rovers, one catcher pass per launch, and 1,000 kg useful payload. It is
not an explanation of the superseded upper-only restraint model.

## Lower acceleration: longer slings, more droop, taller and heavier poles

The required release speed is nearly fixed by the orbital target. Achieving
that speed at lower centripetal acceleration requires a larger release radius
and a lower angular rotation rate. With rover speed fixed at 50 mph, the track
radius also increases; it is not a separately optimized free variable.

The longer, more slowly rotating outward slings droop farther. The pole tops
must therefore be higher to keep the cables clear of the lunar surface. Tall
poles require more than just proportionally more steel: they must resist
buckling and limit bending/deflection, including their own weight and radial
inertia. Maintaining those constraints requires larger tube sections as well
as longer members.

**The four pole legs dominate the low-acceleration increase.** At 30 g their
estimated combined mass is 1,643 tonnes, versus 63.5 tonnes at 50 g. Pole-top
height increases from 28.7 m to 74.3 m. On the far low-acceleration side, heavier
hardware also demands larger wheels, adding a second mass penalty. At 25 g,
the model reaches roughly 5,812 tonnes of poles and 2,801 tonnes of wheels.
Those extreme values are diagnostics of this chosen hardware family, not
recommended construction designs.

The low cross-tie already carries the wheel/ballast inward turning force in
these cases. This pole penalty is **not** the old mistake of routing that
lower-assembly force through the pole tops. It comes from the remaining
structural loads and the difficulty of making tall members stiff and stable.

## Higher acceleration: greater line tension and larger bend radii multiply reel torque

Higher release acceleration means more force on the same payload. The outward
rope must be thicker to carry that force at the assumed working stress. The
selected reel design also requires a bending diameter proportional to rope
diameter, so the thicker rope needs a larger capstan radius.

The reel's output torque is **line tension × capstan radius**. Both factors
increase with acceleration. A shorter outward sling does not remove that
high-tension handling requirement.

The growing mass is principally **the reel reduction gearing**, with additional
shaft/rim/storage/support mass. It is not primarily larger wheel motors or a
large increase in solar power. In this model the reel motors and inverters
remain nearly constant over the central comparison range; the torque-carrying
mechanical equipment grows strongly.

For example, increasing acceleration from 50 g to 100 g:

- Capstan radius grows from **1.73 m to 2.45 m**.
- Peak holding torque per reel grows from **6.65 MNm to 18.81 MNm**.
- The two reel gearboxes together grow from **153.8 t to 468.4 t**.
- Complete reel systems grow from **235.3 t to 593.5 t**, while the four poles
  shrink from **63.5 t to 4.1 t**.

The 358 t reel-system increase exceeds the 59 t pole saving. At still higher
accelerations, wheel/reel envelopes impose a minimum apex height even when
cable droop would allow shorter poles. Once added hardware exhausts the rock
ballast it can replace, larger wheel loads create further mass growth.

## The numbers on both sides

All masses below are **tonnes of imported permanent equipment**. “Reel systems”
includes both reel motors, inverters, reduction gearing and mechanical
assemblies. “Other” is everything else in the imported budget, including wheels,
wheel drives, cables, solar, thermal equipment and smaller subsystem allowances.
With a one-tonne payload, total imported tonnes numerically equal the imported
mass ratio in kg/kg.

| Payload acceleration | Apex height m | Four poles t | Reel systems t | Other imported t | Imported mass ratio |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 30 g | 74.3 | 1,642.9 | 136.2 | 1,017.3 | 2,796.4 |
| 40 g | 43.1 | 224.3 | 182.1 | 952.7 | 1,359.1 |
| 45 g | 34.7 | 111.6 | 207.8 | 953.6 | 1,273.0 |
| 50 g | 28.7 | 63.5 | 235.3 | 954.2 | 1,253.0 |
| 55 g | 24.2 | 40.6 | 264.5 | 954.7 | 1,259.8 |
| 75 g | 14.4 | 11.7 | 396.6 | 956.5 | 1,364.8 |
| 100 g | 9.8 | 4.1 | 593.5 | 959.0 | 1,556.6 |
| 150 g | 10.2 | 5.0 | 1,078.7 | 965.1 | 2,048.9 |

The crossover is particularly clear immediately around the minimum:

- **45 → 50 g:** poles save **48.1 t**, while reels add **27.5 t**. The full
  imported budget falls by about **20.0 t**.
- **50 → 55 g:** poles save only **22.9 t**, while reels add **29.2 t**. The full
  imported budget rises by about **6.7 t**.

The minimum is therefore broad: the 55-g result is only about **0.54%** above
50 g. The exact best acceleration is less certain than the rounded 50-g label
might suggest.

## A compact physical explanation

Let a be payload release acceleration, u the approximately fixed release speed,
and v the fixed rover speed. To leading order:

    release radius = u²/a
    angular speed = a/u
    track radius = v*u/a

At fixed release speed and working stress, a useful approximate scaling is:

    rope tension ∝ a
    rope diameter ∝ sqrt(a)
    capstan radius ∝ sqrt(a)      [fixed bending-diameter / rope-diameter rule]
    reel holding torque ∝ a^(3/2)

These are explanatory scalings, not substitutes for the implemented cable
integrals. In the numerical example, doubling acceleration from 50 g to 100 g
raises holding torque by about 2.83 times, consistent with this relationship.

Meanwhile, the geometrically similar rotating-cable approximation gives droop
of order g_moon/omega², hence roughly proportional to 1/a². The actual clearance
calculation includes finite cable angles, deployed material, lunar curvature
and different cycle phases. That is why the reported heights come from the
calculation rather than directly from a power-law fit.

Thicker rope alone is not the main high-acceleration mass penalty: its greater
cross-sectional area is substantially offset by shorter length. The combined
outward-cable mass remains about **37.2 t** over the central range. The hardware
that must handle its increased tension is what becomes expensive.

## Which mass-ratio curve has the valley?

The pronounced valley belongs to **imported equipment mass / useful payload
mass**. Solar, heat rejection and wheel assemblies contribute a substantial,
nearly constant background around the minimum: approximately 219.7 t, 318.0 t
and 231.7 t respectively. They set much of the curve's height, but do not cause
its local turn near 50 g.

The curve that also counts **local ballast** has a broad plateau instead. Over
much of this range, saving imported hardware means loading more local rock to
maintain tangential traction. Reference total permanent mass stays close to
2,446 t from approximately 40 g through 150 g. Neither curve includes the
expendable payload or rock countermass as permanent machine mass.

## What “apparent global minimum” means here

The defensible publication wording is:

> Within the sampled 50-mph, single-pass reference design family, imported
> equipment mass has a minimum near 50 g: below it, tall poles dominate the
> increase; above it, high-torque reel mechanisms dominate the increase.

This is the lowest sampled reference value, not a mathematical proof of a
global optimum across all structures, materials and reel architectures. The
sweep includes failed mass iterations, which are not valid low-mass solutions.
The higher-acceleration trend depends particularly on the chosen rope bending
rule and extrapolated gearbox mass curve. Different pole families or rope-
handling mechanisms could change the crossover. The lighter/heavier component
assumptions place sampled minima near 55 g and 50 g, respectively.

[Mass-ratio graph](../results/split_tie/mass_trade.svg) ·
[Scenario table](../results/split_tie/SCENARIOS.md) ·
[Complete numerical records](../results/split_tie/all_estimates.json) ·
[Component sources and assumptions](../results/hardware_mass/SOURCES.md) ·
[Publication checkpoint](CHECKPOINT.md)

## Reel sizing assumption and illustration

The reference bend ratio is **40:1**, with 20:1 and 50:1 sensitivity cases.
See [reel dimensions and physical limitations](REEL_ASSUMPTIONS.md) for scenario values,
the 50-g geometry, and the distinction between the two illustrated outward
reels and the unchanged capstan/storage mass allowance. Cross-track ties are
static connections with no reels. A passing geometric check does not establish
loaded bending life or full-tension winding feasibility.
