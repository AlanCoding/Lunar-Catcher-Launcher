"""Extend four existing DEM sectors from +/-0.25 to +/-0.34375 degrees."""
from pathlib import Path
import json,hashlib
from concurrent.futures import ThreadPoolExecutor
from urllib.request import Request,urlopen
import numpy as np
from llo_catcher.analysis.terrain.terrain_band import CACHE as OLD,BASE,COLS,PPD,RADIUS
ROOT=Path(__file__).resolve().parent
CACHE=OLD.parent/'band_034deg'
ROWS=176

def fetch(west):
    CACHE.mkdir(parents=True,exist_ok=True);path=CACHE/f'{west:03d}.npy';meta=CACHE/f'{west:03d}.json'
    if path.exists() and meta.exists():
        record=json.loads(meta.read_text())
        record['old_sector']=f'../../terrain/data/band_025deg/{west:03d}.npy'
        return record
    bands=[];sources=[]
    for side,first in [('00n_30n',30*PPD-ROWS),('30s_00s',128)]:
        stem=f'sldem2015_512_{side}_{west:03d}_{west+45:03d}_float'
        start=first*COLS*4;end=start+48*COLS*4-1
        url=BASE+stem+'.img';req=Request(url,headers={'Range':f'bytes={start}-{end}'})
        with urlopen(req,timeout=60) as response:
            assert response.status==206
            assert response.headers.get('Content-Range')==f'bytes {start}-{end}/{30*PPD*COLS*4}'
            raw=response.read(48*COLS*4+1)
        assert len(raw)==48*COLS*4
        bands.append(np.frombuffer(raw,dtype='<f4').reshape(48,COLS))
        sources.append(dict(url=url,byte_range=[start,end],sha256=hashlib.sha256(raw).hexdigest()))
    data=np.concatenate([bands[0],np.load(OLD/f'{west:03d}.npy'),bands[1]])
    np.save(path,data);record=dict(west_deg=west,extra_sources=sources,old_sector=f'../../terrain/data/band_025deg/{west:03d}.npy')
    meta.write_text(json.dumps(record,indent=2)+'\n');print('Extended sector',west,flush=True);return record

class Terrain:
    def __init__(self, cache=CACHE, rows=ROWS):
        self.rows=rows
        self.tiles={w//45:np.load(cache/f'{w:03d}.npy',mmap_mode='r') for w in [135,180,225,270]}
    def height(self,lat,lon):
        lat,lon=np.broadcast_arrays(lat,lon);shape=lat.shape
        y=self.rows-.5-np.asarray(lat).ravel()*PPD;x=(np.asarray(lon).ravel()%360)*PPD-.5
        assert np.all((y>=0)&(y<=2*self.rows-1))
        yi=np.minimum(np.floor(y).astype(int),2*self.rows-2);wy=y-yi;xi=np.floor(x).astype(int);wx=x-xi;v=np.zeros(len(x))
        for dx,w in [(0,1-wx),(1,wx)]:
            col=(xi+dx)%(360*PPD)
            for k in np.unique(col//COLS):
                mask=col//COLS==k;a=self.tiles[k];cc=col[mask]%COLS
                v[mask]+=w[mask]*((1-wy[mask])*a[yi[mask],cc]+wy[mask]*a[yi[mask]+1,cc])
        return (1000*v).reshape(shape)

if __name__=='__main__':
    with ThreadPoolExecutor(max_workers=4) as pool:records=list(pool.map(fetch,[135,180,225,270]))
    (ROOT/'terrain_manifest.json').write_text(json.dumps(dict(latitude_pixel_center_max_deg=(ROWS-.5)/PPD,sectors=records),indent=2)+'\n')
