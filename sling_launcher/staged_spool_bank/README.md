# Staged multi-tether lunar sling: a bank of spools

**New design variation and article working outline — 2026-11-08.**
Status: signed-power baseline implemented; shared
[2D spool dynamics](../spooled_tether_2d/README.md) now has initial shape/stress results.
Multi-arm clearance and controlled return remain unresolved.
[Launcher guide](../README.md) · [Original spool design](../publication/README.md) ·
[Conveyor comparison](../architecture_comparison/README.md)

## Article thesis: prepare separately, release as a group

Instead of a single payload–counterweight pair, give the rotating launcher many
independently operated tapered tethers. Extend them at different times and hold
the payloads at full radius until the desired LLO release window. In this proposal,
a rotating tether can retain a prepared payload at launch speed; the preparation
schedule need not coincide with the release schedule. A group could then be sent
toward the catcher as a batch rather than one payload per preparation cycle.

This is the proposed distinguishing advantage to develop in the article. Exact
release headings, times and common-catcher arrival geometry are not solved here,
and no historical-priority or exclusivity claim has been established. “All ready
for one window” is the design objective; simultaneous detachment in the power
model is a mechanical scheduling simplification, not a demonstrated intercept.

Tapered lines retain the mass-versus-working-stress tradeoff from the
[architecture comparison](../architecture_comparison/README.md). They can trade
more material and taper for lower stress rather than encounter the uniform
single-loop conveyor's self-stress floor. The illustrative **3:1 cable/load mass
ratio** below is one point on that tradeoff, not evidence that any low-grade
material meets its required stress.

## First result: one pair, two complete cycles

Positive power means shaft work supplied to the moving system. Negative power
means shaft work available for regeneration. “Hub” means the drive maintaining
rotation; it need not be a motor at the physical center pivot. “Spools” sums the
two opposed reels. No electrical efficiencies are folded into these curves.

![One pair: signed hub and spool power](results/single_pair_power.png)

[PNG](results/single_pair_power.png) · [SVG](results/single_pair_power.svg)

| Phase | Hub | Spools | Reason |
| --- | --- | --- | --- |
| Extend loaded | Positive | Negative | Main drive supplies angular momentum; outward payout drives the reel brake. |
| Hold fully extended | Zero in ideal model | Zero in ideal model | Nonzero holding tension, but no radial motion or change in rotational inertia. |
| Release | No resolved shaft-power pulse | No resolved shaft-power pulse | Released masses carry away their kinetic energy; release transients are excluded. |
| Retract empty tether | **Negative** | **Positive** | Decreasing rotational inertia returns work through the main drive; reels pull inward. |

The return-side hub regeneration is real in this imposed constant-RPM energy
balance. An unbraked assembly would instead tend to speed up as its inertia falls.
Finite retraction work remains even after payload release because the tethers
have mass. Friction and holding-system losses would make the ideal zero-power
holds nonzero in a real installation.

### Declared baseline

| Input / derived quantity | Value |
| --- | ---: |
| Useful payload / opposite disposable mass | 1,000 / 1,000 kg per pair |
| Tether per arm / per pair | 3,000 / 6,000 kg |
| Payload pairs in bank | 15, hence **30 moving tethers** |
| Total bank tether inventory | 90 tonnes |
| Rotation | 0.2910819542 rad/s = 2.77963 RPM |
| Feed-station radius / release radius | 76.789 / 5,787.088 m |
| Release speed | 1,684.517 m/s |
| Period T | 6,633.486 s = 110.558 min; inherited comparison clock |
| Loaded extension duration | T/5 = 1,326.697 s |
| Empty retraction duration | T/5 = 1,326.697 s |
| Reload duration | 300 s |
| Single-template loaded hold | 300 s |
| Remaining single-template idle time | 3,380.092 s |
| Payout law | Quintic smoothstep: zero speed and acceleration at both ends |
| Peak payout / retraction speed | About 8.07 m/s |
| Required specific working stress for 3:1 taper | 1.68129 MJ/kg |
| Root/tip fiber-area ratio | 2.3250 |
| Stress if density is 1,450 kg/m³ | **2.43787 GPa**; illustrative, not a qualified allowable |

The travel duration is an explicit initial scheduling choice. It leaves room
within the inherited period for different holds and phase offsets. It is not
an optimized control law or an inferred mechanical speed limit.

The model uses straight radial cable inventory with rigid rotation, adapting
[spooling_cycle.py](../spooling_cycle.py). A real flexible tether must develop
angles to transmit tangential force. That geometry is not established by these
energy curves; it is the next study described below. No additional radial guide
hardware has been designed or counted.

## Fifteen identical cycles, evenly phased

Each pair runs the single template shifted by **T/15 = 442.232 s**. Faint lines
show each individual contribution; heavy lines show their sum. These figures
show an already-running periodic bank over two periods, not a startup from rest.

![Fifteen phase-shifted power histories and their sums](results/staggered_bank_power.png)

[PNG](results/staggered_bank_power.png) · [SVG](results/staggered_bank_power.svg)

| Metric | One pair | 15 evenly shifted pairs |
| --- | ---: | ---: |
| Hub minimum / maximum | −9.885 / +19.629 MW | +11.912 / +13.937 MW |
| Spool minimum / maximum | −9.815 / +4.943 MW | −6.969 / −5.956 MW |
| Average hub power | +0.8554 MW | +12.8308 MW |
| Average spool power | −0.4277 MW | −6.4154 MW |
| Average ideal net shaft power | +0.4277 MW | +6.4154 MW |
| Net peak-to-peak variation | 14.756 MW | **1.012 MW** |

The summed net ripple is **15.8% peak-to-peak relative to its mean**. This supports
the power-smoothing premise, without claiming perfect flatness. Shape/time control
has not been optimized. The bank carries 15 times the useful mass per period:
**15 tonnes per T, or 2.26125 kg/s**, plus equal opposite discarded mass. It is not
a free increase in throughput at fixed installed tether mass. Rescaling each pair's
payload and cable mass by 1/15 would preserve the waveform shape at the original
single-pair mean throughput.

**Exact phase shifts also shift release times.** Thus this smooth graph does not
by itself demonstrate a bank that waits for one shared release window.

## A first common-release schedule

To represent the new concept explicitly, a second schedule starts immediately
after all pairs have released. Empty tethers wait at full extension until their
staggered retraction starts, retract, reload, extend, then hold loaded until the
next common release at T. The retraction starts are spread over 3,380.092 s;
individual loaded holds range from **300 to 3,680.092 s**. This is a feasible
sequence of the imposed radial motions, not a collision-checked trajectory.

![Staged bank: retract, reload, extend and hold](results/staged_schedule.png)

[Schedule PNG](results/staged_schedule.png) · [SVG](results/staged_schedule.svg)

![Signed power for a common-release bank](results/synchronized_bank_power.png)

[Power PNG](results/synchronized_bank_power.png) · [SVG](results/synchronized_bank_power.svg)

This initial common-release schedule has hub power from **−19.17 to +42.80 MW**,
and spool power from **−21.40 to +9.58 MW**. Its average ideal net power remains
**6.415 MW**, but net peak-to-peak variation is **30.98 MW**. It demonstrates holding
and common readiness, but does not inherit the evenly phased graph's smoothness.
We have not optimized this schedule. More overlap, changed travel programs,
multiple banks, or a finite release window may improve it; none is assumed solved.

Holding separates preparation from release, but after a shared release all pairs
are empty. A steady balance between loaded extension and unloaded return is
therefore a scheduling problem. This is a useful result to keep visible in the
article rather than label the evenly phased graph as a demonstrated common-release
solution.

## Power equations and energy accounting

Let q be deployed cable length, I(q) rotational inertia of both deployed and
stored tether plus the two attached masses, and Mr(q) the combined moving radial
mass. Primes below differentiate with respect to q. Cable material deployed first
is the thin distal end; material still on the spool remains in the rotational
inventory at station radius a. At constant Ω:

```
P_hub   = I'(q) qdot Ω²
P_spool = [Mr(q) qddot + ½ Mr'(q) qdot² − ½ I'(q) Ω²] qdot
K       = ½ I(q) Ω² + ½ Mr(q) qdot²
```

Within each fixed-load phase, `P_hub + P_spool = dK/dt`. Numerical cable moments
supply the inertia and its derivative. This includes deployed and stored cable
mass, radial motion and the changing radial moving mass; it is not a payload-only
power estimate. The taper is the same constant-stress exponential used in the
[comparative analysis](../architecture_comparison/README.md), sized by solving
for specific stress until each cable mass equals three times its attached load.

Loading is modeled as attaching a payload already co-rotating at station radius,
at zero radial speed. Its initial energy is an explicit boundary input:
**0.4996 MJ per pair**. This plot does not resolve the loader motor or its losses.
The two released masses carry **2,837.60 MJ per pair**. Over a closed cycle, modeled
net shaft work is their difference, **2,837.10 MJ**. The tether returns to its
initial state. Release impulses/waves and recovery of hardware attached to the
payload are excluded.

“Hub + spool” is ideal net mechanical work. Physically using negative power needs
regenerative drives and a power-transfer path; electrical losses increase input.
The common-release schedule has net-regenerating intervals, so without storage
or another simultaneous consumer that energy would need disposal. These curves
are not solar-array sizing or a claim of storage-free electrical feasibility.

## Shared follow-up: angle histories and full 2D cable dynamics

The [separate 2D work item](../spooled_tether_2d/README.md) now implements an initial
elastic single-tether model, shape snapshots and angular envelopes. It applies
to all spooled designs, rather than only this bank. The requirements below remain
the broader control/clearance agenda; they are not all solved by that first run.
Revisit the
[point-mass payout GIF study](../payout_control/README.md) as a geometric starting
point, then model a single tapered tether with its distributed mass and elastic
response. The massless point model alone cannot establish neighboring-cable safety.

The principal outputs should be:

1. Payload inertial angle θ(t), rotating-frame lag θ(t) − Ωt, angular velocity,
   and angle versus radius through extension, hold, release and empty retraction.
2. The angular envelope of **every tether segment**, not only the payload. Record
   peak deviation, oscillation frequency, damping and settling time after stopping.
3. Tension, peak stress and slack events along the taper, including release and
   unloaded-tip retraction. A massless free endpoint cannot stand in for the whole
   returning cable; specify actual retained end-device mass as an input.
4. Beyond a configurable hub-clearance radius, test whether the entire angular
   envelope stays within its assigned neighbor corridor. Close to the hub, allow
   deliberately slower or otherwise non-optimal payout to avoid conflicts.
5. Compare extension/retraction control programs that trade duration and power
   ripple against angular excursions. Establish tolerable neighboring-arm spacing
   only after specifying their arrangement and physical clearance.

For an illustrative equally spaced 30-arm arrangement, nominal angular spacing
would be 12°, but that is not an established safe envelope or a selected mechanical
layout. First solve one arm; then use its swept envelope to assess phase-separated
neighbors. Do not assume ideal mirrored force cancellation removes collision risk.

A later scheduling step should use the dynamically acceptable histories to smooth
bank power while maintaining full-extension readiness. A separate orbital step
must find the individual release times/headings that deliver the prepared group
to one catcher. Neither angle-control optimization nor the intercept work is
implemented here.

## Reusable artifacts and reproduction

- [Model](model.py): taper/inventory integrals and reusable phase functions.
- [Report generator](report.py): two-period curves, sums and common-release schedule.
- [Saved taper profile](results/taper_profile.npz): material coordinate, linear
  density and fiber area for subsequent cable dynamics.
- [Single-cycle template](results/cycle_template.npz): time, deployed length,
  radial speed, signed hub/spool powers, kinetic energy and load state in SI.
- [All individual bank histories](results/bank_histories.npz): 15 × time arrays
  for both schedules, plus common-release deployed-length histories.
- [Inputs, summaries, timings and validation](results/summary.json).

The saved templates are intended for reuse in the next design/scheduling work;
plots are not the only retained representation. Regenerate from repository root:

```bash
MPLCONFIGDIR=/tmp/lunar-sling-mpl-cache \
  .env/hub/bin/python -m sling_launcher.staged_spool_bank.report
```

Checks enforce the 3:1 tether ratio, integrated energy conservation for all three
cases, cable-inventory grid refinement and fully extended, radially stationary
readiness of every pair before common release. These checks validate the reduced
model's bookkeeping; they do not certify the imposed radial motion as realizable
by an unconstrained flexible tether.
