"""Small access/format probe, not an impact solver or full terrain survey.

Run with the existing NumPy environment:
  .env/hub/bin/python llo_catcher/analysis/terrain/probe_sldem_access.py
Downloads only the two rows bordering the equator between 0 and 45 E.
"""
from pathlib import Path
from urllib.request import Request, urlopen
import hashlib
import json
import re
import numpy as np

BASE = 'https://pds-geosciences.wustl.edu/lro/lro-l-lola-3-rdr-v1/lrolol_1xxx/data/sldem2015/tiles/float_img/'
OUT = Path(__file__).resolve().parent
CACHE = OUT / 'data'


def field(label, name):
    match = re.search(r'^\s*' + re.escape(name) + r'\s*=\s*([^\r\n]+)', label, re.M)
    if not match:
        raise ValueError(f'Missing metadata field: {name}')
    return match.group(1).strip().strip('"')


def fetch_row(stem, side):
    label_url = BASE + stem + '.lbl'
    with urlopen(label_url, timeout=30) as response:
        raw_label = response.read(65536)
    label = raw_label.decode('ascii')
    assert field(label, 'SAMPLE_TYPE') == 'PC_REAL'
    assert int(field(label, 'SAMPLE_BITS')) == 32
    assert field(label, 'UNIT') == 'KILOMETER'
    assert float(field(label, 'SCALING_FACTOR')) == 1
    assert float(field(label, 'OFFSET')) == 1737.4
    assert field(label, 'COORDINATE_SYSTEM_NAME') == 'MEAN EARTH/POLAR AXIS OF DE421'
    nrow = int(field(label, 'LINES'))
    ncol = int(field(label, 'LINE_SAMPLES'))
    stride = int(field(label, 'RECORD_BYTES'))
    assert stride == ncol * 4
    assert nrow == 30 * 512 and ncol == 45 * 512
    row = nrow - 1 if side == 'north' else 0
    start, end = row * stride, (row + 1) * stride - 1
    request = Request(BASE + stem + '.img', headers={'Range': f'bytes={start}-{end}'})
    with urlopen(request, timeout=30) as response:
        # Refuse a whole-tile response (1.4 GB); never silently download it.
        if response.status != 206:
            raise RuntimeError(f'Server did not honor byte range: {response.status}')
        content_range = response.headers.get('Content-Range')
        assert content_range == f'bytes {start}-{end}/{nrow * stride}', content_range
        raw = response.read(stride + 1)
    assert len(raw) == stride
    heights = np.frombuffer(raw, dtype='<f4').astype(float) * 1000
    assert np.all(np.isfinite(heights)) and np.all(np.abs(heights) < 20000)
    (CACHE / (stem + '.lbl')).write_bytes(raw_label)
    (CACHE / (stem + '.row.bin')).write_bytes(raw)
    return heights, dict(label_url=label_url, image_url=request.full_url,
        row_zero_based=row, bytes_downloaded=len(raw), content_range=content_range,
        latitude_deg=(.5 / 512) * (1 if side == 'north' else -1),
        raw_sha256=hashlib.sha256(raw).hexdigest(),
        label_sha256=hashlib.sha256(raw_label).hexdigest(),
        minimum_height_m=float(heights.min()), maximum_height_m=float(heights.max()))


def main():
    CACHE.mkdir(exist_ok=True)
    north, nmeta = fetch_row('sldem2015_512_00n_30n_000_045_float', 'north')
    south, smeta = fetch_row('sldem2015_512_30s_00s_000_045_float', 'south')
    lon = (np.arange(len(north)) + .5) / 512
    equator = (north + south) / 2
    np.savez_compressed(CACHE / 'equator_000_045.npz', longitude_deg_east=lon,
        height_m=equator, north_height_m=north, south_height_m=south)
    report = dict(status='Access and decoding demonstrated; no trajectories propagated',
        checked_on='2026-11-03', dataset='SLDEM2015', frame='MEAN EARTH/POLAR AXIS OF DE421',
        reference_radius_m=1737400, samples=len(lon), sample_spacing_deg=1/512,
        sample_spacing_m_equator=float(2*np.pi*1737400/360/512),
        interpolation='Average nearest north/south pixel-center rows to latitude zero',
        first_longitude_deg=float(lon[0]), last_longitude_deg=float(lon[-1]),
        minimum_height_m=float(equator.min()), maximum_height_m=float(equator.max()),
        binary_bytes_downloaded=nmeta['bytes_downloaded']+smeta['bytes_downloaded'],
        rows=[nmeta,smeta])
    (OUT / 'access_probe.json').write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
