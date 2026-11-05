"""Check terrain extension, selected positions, spacing, and signed decimal coordinates."""
from itertools import combinations
import csv
import hashlib
import json
import numpy as np
from . import find_sites as search
from .extend import INNER, INNER_ROWS

def main():
    search.terrain=search.Terrain(search.CACHE,search.ROWS)
    records=json.loads((search.ROOT/'results.json').read_text())
    sites=records['sites']
    for rec in json.loads((search.ROOT/'terrain_manifest.json').read_text()):
        west=rec['west_deg']
        data=search.terrain.tiles[west//45]
        rows=search.ROWS-INNER_ROWS
        assert np.array_equal(data[rows:-rows],np.load(INNER/f'{west:03d}.npy',mmap_mode='r'))
        for part,source in zip([data[:rows],data[-rows:]],rec['extra_sources']):
            assert hashlib.sha256(part.tobytes()).hexdigest()==source['sha256']
    min_distance=min(search.separation(a,b) for a,b in combinations(sites,2))
    assert min_distance>=7
    checks=[]
    with (search.ROOT/'hub_coordinates.csv').open() as stream:
        coordinates=list(csv.DictReader(stream))
    assert len(coordinates)==len(sites)
    for site_index,site in enumerate(sites):
        lat,lon=site['hub_lat_deg'],site['hub_lon_deg_east']
        assert float(coordinates[site_index]['latitude_deg'])==lat
        assert float(coordinates[site_index]['longitude_deg'])==(lon+180)%360-180
        assert abs(site['shift_from_nominal_latitude_km'])<=2
        height=site['hub_elevation_m']
        # Finer perimeter checks complement the native interior grid vertices.
        for cy,cx,radius in [(lat,lon,5000),(site['search_center_lat_deg'],site['search_center_lon_deg_east'],7000)]:
            edge,_=search.rim(cy,cx,radius,36000)
            _,_,inside,_=search.vertex_extrema(cy,cx,radius)
            max_rise=float(max(edge.max(),inside)-height)
            assert max_rise<.001
            checks.append(max_rise)
        _,z=search.rim(lat,lon,site['actual_radius_km']*1000,count=36000)
        r=search.RADIUS+float(search.terrain.height(0,lon))+10
        assert abs((r*np.cos(np.radians(lat))-z.max())-site['actual_horizontal_tip_min_clearance_m'])<1.
    out=dict(site_count=len(sites),minimum_hub_separation_km=min_distance,
             maximum_sampled_terrain_above_selected_summits_m=max(checks),
             finer_perimeter_bearings=36000,new_strip_hashes_verified=8,signed_decimal_coordinates_verified=True)
    (search.ROOT/'validation.json').write_text(json.dumps(out,indent=2)+'\n')
    print(out)

if __name__=='__main__':
    main()
