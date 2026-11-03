# Mass payoff: when delivered mass equals machine mass

This is a **mass-throughput benchmark**, not financial payback, avoided rocket propellant, or Earth-delivered mass. Useful output means payload successfully delivered to the modeled lunar-orbit catcher. Expendable countermass receives no output credit.

## Inputs and definitions

- Useful payload per successful launch: **1,000 kg**.
- Imported permanent equipment: **1,253,045 kg**.
- Total permanent mass including local ballast: **2,446,458 kg**.
- One site-relative catcher revisit: **110.558104 minutes**.
- Loading and timing allowances already lie inside this cycle; do not add them again.
- Direct solar operation has no nighttime battery-storage credit.

For imported equipment mass M, useful payload P and N successful launches:

    Cumulative useful output = N * P
    Imported equipment mass per cumulative useful kg = M / (N * P)
    Successful launches to equal imported mass = ceil(M / P)

The result is **1,254 successful launches**. At 1,253 launches, output is still below imported mass. Counting local ballast too gives **2,447 successful launches**, a separate physical-inventory comparison rather than an imported-equipment payoff.

## Calendar-time scenarios

Let f be usable-sunlight fraction, u availability during sunlight, and s successful-capture fraction. With cycle duration T, the long-run useful output rate is P*f*u*s/T. The corresponding equal-mass time is approximately ceil(M/P)*T/(f*u*s). These are expected/averaged rates, not an exact event schedule.

| Operating assumption | Useful output t/calendar day | Imported-mass equality days | Whole-machine equality days |
| --- | ---: | ---: | ---: |
| Continuous operation — mathematical lower bound | 13.02 | 96.3 | 187.9 |
| Half-time sunlight; no further downtime | 6.51 | 192.6 | 375.7 |
| Half-time sunlight; 80% availability; 95% success | 4.95 | 253.4 | 494.4 |

**The 96.3-day continuous figure is not a nighttime operating claim.** With the illustrative 50% sunlight assumption, the imported-mass benchmark is approximately **193 calendar days**. The 50% value is an assumed long-run fraction, not a site-specific illumination forecast. Day/night blocks, startup phase and weather-independent operational outages change the actual crossing date.

At half-time sunlight with no further downtime or failures, expected output is about **2,379 tonnes per 365.25-day year**. The one-year equipment burden is **0.527 kg of imported launcher per kg of cumulative useful output**, without replacements.

## Countermass, replacement and system boundary

At 1,254 successful launches with no failed attempts, the launcher handles **1,254 tonnes of useful payload plus 1,254 tonnes of expendable rock countermass**. That is 2,508 tonnes handled; only the useful half counts as output. Permanent ballast is separate and is not reloaded every launch. Failed attempts can consume additional feedstock.

If imported replacement equipment totals M_replace over N launches, the appropriate cumulative ratio is (M_import + M_replace)/(N*P), and the payoff condition becomes N*P >= M_import + M_replace. If replacement consumption per successful launch is a constant c kg, the threshold is ceil(M_import/(P-c)), provided c<P. No replacement-life allowance is quantified yet.

This study does not include imported catcher construction or momentum restoration, delivery of equipment to the lunar surface, road construction, mining/loading infrastructure, or complete release/capture mechanisms. Central pivot/stabilizer mass is excluded by instruction. The assumed launch cadence and successful capture remain operational targets, not a demonstrated duty cycle. Those additions could materially lengthen the mass payoff.

The imported and whole-machine benchmarks are deliberately both shown; using local rock as if it were imported equipment would answer a different question. No literature superiority claim is made without aligning boundaries and throughput assumptions.

[Publication checkpoint](CHECKPOINT.md) · [Exact payoff inputs/results](payoff.json) · [Frozen candidate](candidate_50g.json)
