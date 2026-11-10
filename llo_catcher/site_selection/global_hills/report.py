"""Default report and figures use only the non-overlapping hub selection."""
from pathlib import Path
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
OUT=Path(__file__).parent
LABEL={'outbound_collision':'Blocked','return_impact':'Clears; historical return impact','not_arrested':'Clears; historical no impact'}
def main():
    d=json.loads((OUT/'nonoverlap_results.json').read_text());rows=d['candidates'];s=d['stats']
    # Use the saved raw-pool count only; do not plot or reanalyse that population.
    raw_count=json.loads((OUT/'results.json').read_text())['all_peaks_stats']['count']
    assert s['count']==len(rows)
    assert s['either_clear']==s['east_clear']+s['west_clear']-s['both_clear']
    text=f'''# Non-overlapping equatorial hub candidates

[Site-selection guide](../README.md). This is the default catalog and plotting
set. The raw peaks and old fixed-7-km selection are retained only in the
[archive](ARCHIVE.md); they are no longer the default analysis population.

**[Four featured hilltop sites and publication table](../featured_four/adjusted_hilltops/PUBLICATION.md)** give the subsequently adjusted summit placements and their new flight checks. The counts here describe the original global catalog, before those four local adjustments.

## Selection and counts

**{s['count']} hubs have non-overlapping projected tether-sweep disks.**
The exclusion uses both latitude and longitude, including longitude wraparound,
and each candidate's own arm radius. Two 6 km sweeps need approximately 12 km
between hubs, not the previous fixed 7 km.

### Search stages: what population is being counted?

| Stage | Locations | Meaning / appearance in the current graph |
| --- | ---: | --- |
| Candidate peaks whose tip circumference clears terrain | {raw_count:,} | Initial pool, including many overlapping sweeps; **not plotted** |
| Select non-overlapping sweep disks, prioritizing equatorial alignment | {s['count']:,} | **All dots in each panel**, red and green together |
| Of those selected hubs, launch clears in at least one direction | {s['either_clear']:,} | Green in one or both panels; not a separate plotted population |

The 17,572 count is candidate peak locations, not 17,572 independent installation
sites. Selecting 695 removes overlapping footprints; it does **not** select for
successful launches. A clear rotating tip circle and a clear outbound flight
path are different tests.

### Launch outcomes within the 695 selected hubs

These four categories are mutually exclusive and add up to 695:

| Launch outcome | Hubs | East panel | West panel |
| --- | ---: | --- | --- |
| East clears; west hits terrain before catcher | {s['east_clear']-s['both_clear']} | Green | Red |
| West clears; east hits terrain before catcher | {s['west_clear']-s['both_clear']} | Red | Green |
| Both east and west clear to catcher | {s['both_clear']} | Green | Green |
| Both east and west hit terrain before catcher | {s['count']-s['either_clear']} | Red | Red |
| **Total distinct hubs** | **{s['count']}** | | |

The last outcome was previously called “Neither clears.” It means neither
**launch direction** clears; it does not mean the tether tip hits the ground.
It also does not describe what happens after a missed capture.

Eastward clearance totals {s['east_clear']} = {s['east_clear']-s['both_clear']} + {s['both_clear']}; westward clearance totals
{s['west_clear']} = {s['west_clear']-s['both_clear']} + {s['both_clear']}. There are {s['either_clear']} distinct hubs with at least one clear direction,
not {s['east_clear']+s['west_clear']}, because the {s['both_clear']} both-clear hubs occur in both directional totals.

**[Main candidate table](CANDIDATES.md)** · **[CSV](nonoverlap_candidates.csv)** ·
**[Launch-capable shortlist](LAUNCHABLE.md)** · [Selection data](nonoverlap_results.json).

![Non-overlapping hubs, east/west launch clearance](outcomes.png)

**Figure reading guide:** each panel shows the same {s['count']} hubs. The east panel
has {s['east_clear']} green dots and {s['count']-s['east_clear']} red dots; the west panel has {s['west_clear']} green dots and
{s['count']-s['west_clear']} red dots. Red and green encode flight outcome only. The initial
{raw_count:,} candidates are absent from this graph. Markers can visually overlap.
The two panels contain {2*s['count']} plotted markers but only {s['count']} distinct hubs.

**Suggested caption:** “Of {raw_count:,} candidate peaks with terrain-clear tip
circumferences, {s['count']} non-overlapping launcher footprints were selected. Each
panel shows these same hubs: green indicates an outbound launch clearing terrain
to the 25 km catcher, and red indicates a terrain collision before capture.
{s['either_clear']} hubs clear at least one direction; {s['count']-s['either_clear']} clear neither direction.”

The original dense plot showed all raw peaks, which explains its vertical
clustering. The old 793-site subset did use full two-coordinate hub separation,
but its 7 km distance was insufficient to exclude overlapping variable-radius
sweeps. This selection replaces that rule and regenerates the default plots.

## Preference for an equatorial tip

Existing trajectories adjust each arm radius to reach the equator exactly; all
selected candidates therefore have zero ideal equatorial offset **at their
modeled arm radius**. That alone cannot rank them.

To apply the requested preference, rank by how close the **original go-kart arm
of {d['reference_arm_m']:.3f} m** would place the tip to the equator at that hub.
The candidate with the smallest reference-arm miss is considered first; greater
terrain clearance breaks ties. Keep it if its sweep does not overlap a previously
chosen sweep. Launch outcomes do not influence this ranking. The CSV reports
the reference-arm miss; actual trajectories retain their tested individual arm
radii and are not silently recomputed with the reference arm.

This is a deterministic greedy selection, not an optimization of maximum site
count or throughput. It spans all longitudes and retains the prior 3–7 km arm
range. No launch-corridor prefilter is used.

## Non-overlap geometry and validation

A ground-projected sweep fits inside a spherical cap centered on the hub, with
angular radius `asin(arm_radius / minimum_terrain_radius)`. The minimum terrain
elevation across the cached equatorial band is **{d['cached_terrain_floor_m']:.3f} m**;
using it for every cap conservatively encloses the projected circles despite
terrain-height variations. Require center angular separation to exceed the sum
of both cap radii. This excludes overlap of the disks, not only crossing of
their circumferences, and does not rely on vertical separation between machines.

Every selected pair was independently checked using haversine angular distance.
The smallest gap between these conservative cap boundaries is
**{d['minimum_sweep_separation_m']:.3f} m**. No additional engineering spacing margin
has been imposed; this is geometric non-overlap in the DEM model, not a surveyed
installation-clearance guarantee.

The stored tip-circle and trajectory calculations are reused unchanged. Their
[validation](validation.json) includes independent contact propagation and recovery
of earlier sites. No new orbit integrations were needed to change selection.

## Interpretation of the missed-capture result

**User conclusion recorded, November 9, 2026:** the finding that candidates
clearing both directions survive the 1.5-orbit cutoff is theoretically expected;
the requested 1.5-orbit simulation was unnecessary for the intended selection
argument. It is no longer used as a selection or ranking criterion. Existing
return results are retained as historical checks, not presented as a new surprise.

For the ideal nonrotating, spherical-gravity geometry, reversing the periapsis
velocity traverses the opposite half of the same ellipse. Clearing outbound in
both directions therefore clears that ellipse's terrain crossings. The computed
model also rotates the Moon under the orbit, so exact ground-track time-reversal
symmetry is broken; this note records the intended ideal-model reasoning, not
a proof of permanent survival with rotation, gravity anomalies or perturbations.
No further 1.5-orbit runs are requested as part of this selection update.

The main plots and tables consequently emphasize **eastward/westward catch
clearance**. Historical return labels remain available in the CSV. Here the
{s['both_clear']} two-direction candidates have no recorded impact in either
direction by the old cutoff; the remaining launch-capable candidates clear one
direction and have a historical return impact in that direction.

## Reproduction and archive

```bash
MPLCONFIGDIR=/tmp/lunar-sling-mpl-cache OPENBLAS_NUM_THREADS=1 .env/hub/bin/python -m llo_catcher.site_selection.global_hills.select_nonoverlap
MPLCONFIGDIR=/tmp/lunar-sling-mpl-cache .env/hub/bin/python -m llo_catcher.site_selection.global_hills.report
```

The selection reads the raw saved candidates once to choose representatives.
Default plots and summaries read only `nonoverlap_results.json`.
[Archived raw-peak search and old 7 km subset](ARCHIVE.md) retain the original
search method, complete data, counts, diagrams and reproduction instructions.
'''
    (OUT/'README.md').write_text(text)
    def table(items,title):
        out=f'# {title}\n\n[Selection, assumptions and statistics](README.md). Catch clearance is independent of whether a missed shot later impacts.\n\n| Hub | Latitude (°) | Longitude (°) | Arm (km) | Reference-arm equator miss (m) | Tip-circle clearance (m) | East clears? | West clears? |\n| --- | ---: | ---: | ---: | ---: | ---: | --- | --- |\n'
        for r in items:
            out+=f"| {r['id']} | {r['hub_latitude_deg']:.6f} | {r['hub_longitude_deg']:.6f} | {r['arm_radius_km']:.3f} | {r['reference_arm_equator_miss_m']:.1f} | {r['min_tip_circle_clearance_m']:.2f} | {'Yes' if r['east_status']!='outbound_collision' else 'No'} | {'Yes' if r['west_status']!='outbound_collision' else 'No'} |\n"
        return out
    (OUT/'CANDIDATES.md').write_text(table(rows,'Non-overlapping candidate hubs'))
    (OUT/'LAUNCHABLE.md').write_text(table([r for r in rows if any(r[x+'_status']!='outbound_collision' for x in ['east','west'])],'Non-overlapping launch-capable hubs'))
    fig,axes=plt.subplots(2,1,figsize=(13,7),sharex=True,layout='constrained')
    for ax,direction in zip(axes,['east','west']):
        for clear,color,label in [(False,'#b85543','Blocked before catcher'),(True,'#53866a','Clears to catcher')]:
            rr=[r for r in rows if (r[direction+'_status']!='outbound_collision')==clear]
            ax.scatter([r['longitude_deg_east'] for r in rr],[r['hub_latitude_deg'] for r in rr],s=17,color=color,label=f'{label} · {len(rr)} hubs')
        ax.set(title=direction.capitalize()+'ward catch clearance',ylabel='Hub latitude (degrees)',xlim=(0,360),xticks=np.arange(0,361,30));ax.grid(alpha=.2);ax.legend(ncol=2,fontsize=9)
    axes[-1].set_xlabel('Hub longitude east (degrees)')
    fig.suptitle(f'{len(rows)} selected hubs in EACH panel · red + green = {len(rows)}\nSelected from {raw_count:,} circle-clear peaks; the raw pool is not plotted',fontsize=13)
    for ext in ['png','svg']:fig.savefig(OUT/f'outcomes.{ext}',dpi=180)
    plt.close(fig);p=OUT/'outcomes.svg';p.write_text('\n'.join(x.rstrip() for x in p.read_text().splitlines())+'\n')
if __name__=='__main__':main()
