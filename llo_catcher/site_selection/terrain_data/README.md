# Site-selection terrain data

The working cache is `band_summit/`: eight 45° SLDEM2015 sectors, each containing 496 latitude rows at 512 samples per degree. Pixel centers span ±0.4833984375°. Heights are stored in kilometres above the 1,737.4 km lunar reference sphere, in the DE421 mean-Earth/polar-axis frame.

The `.npy` files are local download caches excluded from Git. Source metadata and labels are retained. `provenance/` contains metadata from the earlier staged downloads, including their original acquisition paths. The [global-search manifest](../global_hills/manifest.json) records the final arrays’ hashes.

To prepare missing sectors from the repository root:

```bash
.env/hub/bin/python -m llo_catcher.site_selection.support.fetch_terrain
```

The downloader now fetches the complete final band directly. Interpolation is provided by [support/terrain.py](../support/terrain.py).
