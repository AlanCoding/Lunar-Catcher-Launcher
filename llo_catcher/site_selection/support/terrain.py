"""SLDEM2015 summit-band interpolation shared by all site-selection work."""
from pathlib import Path
import numpy as np
from .constants import RADIUS
PPD=512
COLS=45*PPD
ROWS=248
CACHE=Path(__file__).resolve().parents[1]/'terrain_data/band_summit'
class Terrain:
    def __init__(self, cache=CACHE, rows=ROWS):
        self.rows=rows
        self.tiles={w//45:np.load(cache/f'{w:03d}.npy',mmap_mode='r') for w in range(0,360,45)}
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

