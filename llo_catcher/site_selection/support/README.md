# Shared terrain and orbit methods

[Site-selection guide](../README.md).

These numerical helpers support the current hub search, ridge catalog, radial terrain profiles and publication figures.

- [terrain.py](terrain.py): bilinear SLDEM2015 interpolation across all eight longitude sectors and the cached ±0.483° latitude band.
- [fetch_terrain.py](fetch_terrain.py): downloads the required byte ranges directly into the final cache, validates units and coordinates, and records hashes.
- [constants.py](constants.py): lunar reference radius, gravity parameter, spin rate and the published endpoint-height convention.
- [geometry.py](geometry.py): spherical destination and map projection.
- [summits.py](summits.py): native-grid extrema and tip-rim terrain projection.
- [equatorial.py](equatorial.py) and [orbits.py](orbits.py): equatorial flight intersections for the global hub survey and the introductory figures.
- [maps.py](maps.py): shared hub, track and tether-footprint renderer.

The helpers were extracted from earlier surveys during repository consolidation. Their terrain values and representative orbit outputs were checked against the previous implementation. [Relocation validation](../REORGANIZATION.json) records the checks. The current off-equator trajectory routine remains with the [adjusted hilltop checks](../featured_four/adjusted_hilltops/check_launches.py).

The final terrain cache and download metadata live in [terrain_data](../terrain_data/README.md).
