# Summit catalog for hubs north and south of the equator

The [six-hub missed-capture study](missed_capture/README.md) gives east and opposite-tip west impact coordinates, distances from the hub, and checks for passage through the tether footprint.


Six summits satisfy the movable-hub terrain screen. Four lie south of the equator and two lie north. The closest pair is 16.51 km apart. The earlier fixed-latitude screen and this result address different placements of the hub.

## Hub coordinates

The coordinates use the SLDEM2015 body-fixed Mean Earth/Polar Axis of DE421 frame. The coordinate-only CSV uses signed floating-point degrees, positive north and east. [Download hub_coordinates.csv](hub_coordinates.csv)

| Hub | Latitude | Longitude | Elevation (m) |
| --- | --- | --- | ---: |
| S1 | 0° 11′ 46.6″ S | 144° 10′ 36.3″ E | 4344.9 |
| S2 | 0° 10′ 36.3″ S | 92° 55′ 22.3″ W | 2967.7 |
| S3 | 0° 11′ 39.6″ S | 77° 06′ 58.4″ W | 2877.1 |
| N1 | 0° 13′ 04.0″ N | 66° 14′ 56.5″ W | 85.7 |
| S4 | 0° 09′ 19.0″ S | 65° 51′ 09.1″ W | -346.6 |
| N2 | 0° 07′ 47.6″ N | 64° 02′ 52.3″ W | -1273.9 |

The highest sampled terrain in each recentered 5 km disk is at the hub. All six therefore satisfy the requested 10 m maximum-rise test. The elevation range within each disk can still be substantial.

## Release and rotation checks

For a due-east equatorial release from a horizontal circle, the equatorial release point lies on the summit's meridian. Shifting the summit east or west therefore changes the release longitude. The actual radius follows from the summit latitude. At each new release longitude the payload starts 10 m above local ground, reaches periapsis at release, and targets the 25 km circular prograde catcher at apoapsis. We solve for the corresponding release speed and RPM and check first terrain contact through 1.5 payload periods.

| Hub | Latitude shift from nominal (+ north) | Radius to equatorial tip | Required RPM | Equatorial trajectory | Minimum clearance around actual horizontal tip circle |
| --- | ---: | ---: | ---: | --- | ---: |
| S1 | -0.963 km | 5.966 km | 2.6866 | Outbound impact | -264.7 m |
| S2 | -0.367 km | 5.367 km | 2.9881 | Outbound impact | -435.3 m |
| S3 | -0.900 km | 5.902 km | 2.7173 | Outbound impact | -105.2 m |
| N1 | +1.602 km | 6.602 km | 2.4324 | Outbound impact | -734.9 m |
| S4 | +0.293 km | 4.707 km | 3.4119 | Missed catch, return impact | -119.2 m |
| N2 | -1.066 km | 3.935 km | 4.0830 | Outbound impact | -221.2 m |

S4 at **294.147461° E** retains the desired release outcome. The uncaught payload hits terrain after **87.32 minutes**. Its horizontal tip circle intersects terrain elsewhere in the rotation by approximately **119 m** with 10 m equatorial release clearance. All six circles have negative minimum clearance under these assumptions. The summit list answers the hub-placement question. The trajectory and rotation columns specify what the same sites support under the existing launch model.

S2 illustrates why moving to the top of a hill changes the orbital result. It sits near the best southern placement in the earlier footprint study. The summit's meridian is about 0.30 km east of the 267° seed's viable interval. A release on this meridian hits terrain after approximately 3.84 seconds.

## Search and checks

- Start from the 49 previously identified release intervals that clear outbound and hit terrain after a missed capture. Place nominal hubs 5 km north and south of trial equatorial releases. Sample at about 14.8 m longitude spacing, with near-edge and midpoint samples.
- At each nominal hub, find the highest native terrain vertex inside a 7 km horizontal circle. Keep nominees whose latitude lies within 2 km of the nominal latitude at the summit meridian. Require a local peak, check the interpolated rim of a nominating 7 km disk, and test maximum rise over a new 5 km disk centered on the summit.
- Search both sides independently. Traverse verified summits eastward. Skip another site within the next 7 km on the same side and require 7 km actual hub-to-hub separation across the final list. All six qualified without a spacing conflict.
- The 12,550 nominal placements yielded 295 distinct in-band grid nominees. Six met the summit and footprint checks. The longitude sampling and interpolated DEM define the scope of this local search. Additional summits may exist outside the neighborhoods examined or between search samples.
- Extend the existing terrain strips for the wider disks. Check the original overlapping data and hashes of all eight new strips. Recheck all selected 5 km and 7 km rims with 36,000 bearings. The largest sampled elevation above any selected summit in these checks was 0.0 m.

The [site CSV](sites.csv) includes signed coordinates, launch RPM, and release outcomes. The [full results](results.json) also identify the nominating search center for each peak. See the [verification](validation.json), [terrain source manifest](terrain_manifest.json), and [earlier release corridors](../local_corridors/README.md).

From the repository root with the parent terrain caches available, run:

```bash
.env/hub/bin/python -m llo_catcher.analysis.single_equatorial_release.summit_sites.extend
.env/hub/bin/python -m llo_catcher.analysis.single_equatorial_release.summit_sites.find_sites
.env/hub/bin/python -m llo_catcher.analysis.single_equatorial_release.summit_sites.validate
```
