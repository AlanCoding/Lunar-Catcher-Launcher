"""Add outer SLDEM2015 rows required for shifted summit and actual tip-rim checks."""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from urllib.request import Request, urlopen
import hashlib
import json
import numpy as np
from ..hub_footprints.terrain import CACHE as INNER, ROWS as INNER_ROWS, BASE, COLS, PPD

ROOT = Path(__file__).resolve().parent
ROWS = 248
CACHE = INNER.parent/'band_summit'

def fetch(west):
    CACHE.mkdir(exist_ok=True)
    dest = CACHE/f'{west:03d}.npy'
    metadata = dest.with_suffix('.json')
    if dest.exists() and metadata.exists():
        return json.loads(metadata.read_text())
    outer = []
    sources = []
    count = ROWS - INNER_ROWS
    for side, first in [('00n_30n', 30*PPD-ROWS), ('30s_00s', INNER_ROWS)]:
        url = BASE + f'sldem2015_512_{side}_{west:03d}_{west+45:03d}_float.img'
        start = first*COLS*4
        end = start + count*COLS*4 - 1
        with urlopen(Request(url,headers={'Range':f'bytes={start}-{end}'}),timeout=90) as response:
            assert response.status==206 and response.headers['Content-Range']==f'bytes {start}-{end}/{30*PPD*COLS*4}'
            raw=response.read(end-start+2)
        assert len(raw)==end-start+1
        outer.append(np.frombuffer(raw,dtype='<f4').reshape(count,COLS))
        sources.append(dict(url=url,start=start,end=end,sha256=hashlib.sha256(raw).hexdigest()))
    inner=np.load(INNER/f'{west:03d}.npy')
    extended=np.concatenate([outer[0],inner,outer[1]])
    assert np.isfinite(extended).all()
    np.save(dest,extended)
    meta=dict(west_deg=west,extra_sources=sources)
    metadata.write_text(json.dumps(meta,indent=2)+'\n')
    return meta

if __name__=='__main__':
    with ThreadPoolExecutor(max_workers=4) as pool:
        sectors=list(pool.map(fetch,[135,180,225,270]))
    (ROOT/'terrain_manifest.json').write_text(json.dumps(sectors,indent=2)+'\n')
