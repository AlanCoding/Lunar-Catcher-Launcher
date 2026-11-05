"""SLDEM2015 narrow equatorial corridor, cached by 45-degree sector.

Download: .env/hub/bin/python llo_catcher/analysis/terrain/terrain_band.py
The DEM uses DE421 ME coordinates and elevations in km above 1737.4 km.
"""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from urllib.request import Request, urlopen
import hashlib
import json
import numpy as np
try:
    from .probe_sldem_access import BASE, field
except ImportError:
    from probe_sldem_access import BASE, field

ROOT = Path(__file__).resolve().parent
CACHE = ROOT / 'data' / 'band_025deg'
PPD = 512
ROWS = 128
COLS = 45 * PPD
RADIUS = 1737400.


def download_sector(west):
    CACHE.mkdir(parents=True, exist_ok=True)
    dest = CACHE / f'{west:03d}.npy'
    meta_path = CACHE / f'{west:03d}.json'
    if dest.exists() and meta_path.exists():
        a = np.load(dest, mmap_mode='r')
        assert a.shape == (2 * ROWS, COLS)
        return json.loads(meta_path.read_text())
    bands, sources = [], []
    for side in ['00n_30n', '30s_00s']:
        stem = f'sldem2015_512_{side}_{west:03d}_{west+45:03d}_float'
        with urlopen(BASE+stem+'.lbl', timeout=45) as response:
            raw_label = response.read(65536)
        label = raw_label.decode('ascii')
        assert field(label, 'SAMPLE_TYPE') == 'PC_REAL'
        assert int(field(label, 'SAMPLE_BITS')) == 32
        assert field(label, 'UNIT') == 'KILOMETER'
        assert float(field(label, 'SCALING_FACTOR')) == 1
        assert float(field(label, 'OFFSET')) == RADIUS/1000
        assert field(label, 'COORDINATE_SYSTEM_NAME') == 'MEAN EARTH/POLAR AXIS OF DE421'
        assert int(field(label, 'LINES')) == 30*PPD
        assert int(field(label, 'LINE_SAMPLES')) == COLS
        stride = int(field(label, 'RECORD_BYTES'))
        assert stride == COLS*4
        first = 30*PPD-ROWS if side == '00n_30n' else 0
        start, end = first*stride, (first+ROWS)*stride-1
        request = Request(BASE+stem+'.img', headers={'Range': f'bytes={start}-{end}'})
        with urlopen(request, timeout=60) as response:
            if response.status != 206:
                raise RuntimeError('Byte ranges unsupported; refusing full-tile download')
            expected = f'bytes {start}-{end}/{30*PPD*stride}'
            assert response.headers.get('Content-Range') == expected
            raw = response.read(ROWS*stride+1)
        assert len(raw) == ROWS*stride
        a = np.frombuffer(raw, dtype='<f4').reshape(ROWS,COLS)
        assert np.isfinite(a).all() and np.max(np.abs(a)) < 20
        bands.append(a)
        sources.append(dict(url=request.full_url, label_url=BASE+stem+'.lbl',
            content_range=expected, bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest(),
            label_sha256=hashlib.sha256(raw_label).hexdigest()))
        (CACHE/(stem+'.lbl')).write_bytes(raw_label)
    np.save(dest, np.concatenate(bands, axis=0))
    meta = dict(west_deg=west, east_deg=west+45, sources=sources)
    meta_path.write_text(json.dumps(meta,indent=2)+'\n')
    print(f'Cached {west:03d}–{west+45:03d} E',flush=True)
    return meta


class TerrainBand:
    """Bilinear interpolation in the pixel-center grid; longitude wraps."""
    radius_m = RADIUS

    def __init__(self):
        self.tiles = [np.load(CACHE/f'{w:03d}.npy',mmap_mode='r') for w in range(0,360,45)]
        self.max_height_m = max(float(a.max())*1000 for a in self.tiles)

    def height_m(self, latitude_deg, longitude_deg):
        lat,lon = np.broadcast_arrays(np.asarray(latitude_deg,dtype=float), np.asarray(longitude_deg,dtype=float))
        shape = lat.shape
        y = (ROWS-.5)-lat.ravel()*PPD
        if np.any((y<0) | (y>2*ROWS-1)):
            raise ValueError('Trajectory left the downloaded latitude corridor')
        y0 = np.minimum(np.floor(y).astype(int),2*ROWS-2)
        fy = y-y0
        x = (lon.ravel()%360)*PPD-.5
        x0 = np.floor(x).astype(int)
        fx = x-x0
        result = np.zeros(len(x))
        for dx,wx in [(0,1-fx),(1,fx)]:
            col = (x0+dx)%(360*PPD)
            for k,tile in enumerate(self.tiles):
                mask = col//COLS == k
                cc = col[mask]%COLS
                result[mask] += wx[mask]*((1-fy[mask])*tile[y0[mask],cc]+fy[mask]*tile[y0[mask]+1,cc])
        return (result*1000).reshape(shape)


if __name__ == '__main__':
    with ThreadPoolExecutor(max_workers=4) as pool:
        sectors = list(pool.map(download_sector,range(0,360,45)))
    report = dict(dataset='SLDEM2015', frame='MEAN EARTH/POLAR AXIS OF DE421',
        reference_radius_m=RADIUS, pixels_per_degree=PPD,
        latitude_pixel_center_bounds_deg=[-(ROWS-.5)/PPD,(ROWS-.5)/PPD],
        binary_bytes=sum(x['bytes'] for s in sectors for x in s['sources']), sectors=sectors)
    (ROOT/'band_manifest.json').write_text(json.dumps(report,indent=2)+'\n')
    terrain = TerrainBand()
    print('Global corridor ready; maximum elevation (m):',terrain.max_height_m)
