"""Exclude continuous hub locations using fixed terrain witnesses inside their disks."""
import csv
import json
from concurrent.futures import ProcessPoolExecutor

import numpy as np

from . import survey as s
from .terrain import PPD, ROWS


def knots(start, end):
    """Include every DEM interpolation breakpoint between the two bounds."""
    indices = np.arange(np.ceil(start * PPD - .5), np.floor(end * PPD - .5) + 1)
    return np.unique(np.r_[start, (indices + .5) / PPD, end])


def bound(segment):
    west, east, side = segment
    midpoint = (west + east) / 2
    longitudes = knots(west, east)
    release_elevations = s.T.height(0., longitudes)
    hub_latitudes = np.degrees(side * np.arcsin(s.L / (s.RADIUS + release_elevations + 10.)))
    latitudes = knots(hub_latitudes.min(), hub_latitudes.max())
    # Every possible hub is inside this rectangle. Bilinear height reaches
    # its rectangle maximum at an interpolation knot or a clipped cell corner.
    hub_upper = float(s.T.height(latitudes[:, None], longitudes[None, :]).max())
    center_lat = (latitudes[0] + latitudes[-1]) / 2
    movement = np.radians((east - west + latitudes[-1] - latitudes[0]) / 2)
    tile_sector = int(midpoint // 45)
    tile = s.T.tiles[tile_sector]
    native_latitudes = (ROWS - .5 - np.arange(2 * ROWS)) / PPD
    native_longitudes = tile_sector * 45 + (np.arange(tile.shape[1]) + .5) / PPD
    iy = np.flatnonzero(abs(native_latitudes - center_lat) < .175)
    ix = np.flatnonzero(abs(native_longitudes - midpoint) < .175)
    elevations = tile[np.ix_(iy, ix)].astype(float) * 1000
    lat = np.radians(native_latitudes[iy, None]); lon_delta = np.radians(native_longitudes[ix] - midpoint)
    hav = np.sin((lat - np.radians(center_lat)) / 2)**2 + np.cos(lat) * np.cos(np.radians(center_lat)) * np.sin(lon_delta / 2)**2
    sin_angle = 2 * np.sqrt(hav * (1 - hav))
    # q = |r cross hub_axis|. Changing the axis by angle <= movement can
    # increase q by at most |r| * movement. Allow a further 1 mm inward margin.
    max_radius = (s.RADIUS + elevations) * (sin_angle + movement)
    safe = np.where(max_radius < s.L - .001, elevations, -np.inf)
    i, j = np.unravel_index(np.argmax(safe), safe.shape)
    lower = float(safe[i, j] - hub_upper)
    return dict(west_deg=west, east_deg=east, hub_side='north' if side==1 else 'south',
                witness_lat_deg=float(native_latitudes[iy[i]]), witness_lon_deg=float(native_longitudes[ix[j]]),
                witness_elevation_m=float(safe[i,j]), witness_max_projected_distance_m=float(max_radius[i,j]),
                hub_elevation_upper_bound_m=hub_upper, rise_lower_bound_m=lower)


def check(segment):
    witness = bound(segment)
    west, east, side = segment
    if witness['rise_lower_bound_m'] > 10.001 or east - west < 1e-7:
        return [witness]
    mid = (west + east) / 2
    return check((west, mid, side)) + check((mid, east, side))


def main():
    bands = json.loads((s.ROOT.parent/'local_corridors/results.json').read_text())['both_ranges']
    segments = []
    for band in bands:
        lo, hi = band['start_deg_east'], band['end_deg_east']
        parts = max(1, int(np.ceil((hi - lo) * 1024)))
        edges = np.linspace(lo, hi, parts + 1)
        segments.extend((a,b,side) for a,b in zip(edges,edges[1:]) for side in (-1,1))
    with ProcessPoolExecutor(max_workers=4, initializer=s.initialize) as pool:
        rows = [row for group in pool.map(check,segments,chunksize=8) for row in group]
    unresolved = [r for r in rows if r['rise_lower_bound_m']<=10.001]
    covered = sum(row['east_deg']-row['west_deg'] for row in rows)
    expected = 2 * sum(b['end_deg_east']-b['start_deg_east'] for b in bands)
    assert abs(covered-expected) < 1e-9
    with (s.ROOT/'witnesses.csv').open('w') as stream:
        writer=csv.DictWriter(stream,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    report=dict(corridors=len(bands),subintervals=len(rows),unresolved_subintervals=len(unresolved),
                minimum_proved_rise_m=min(r['rise_lower_bound_m'] for r in rows),
                release_arc_km_per_side=float(covered/2*np.pi/180*s.RADIUS/1000))
    (s.ROOT/'certificate.json').write_text(json.dumps(report,indent=2)+'\n'); print(report)

if __name__=='__main__':main()
