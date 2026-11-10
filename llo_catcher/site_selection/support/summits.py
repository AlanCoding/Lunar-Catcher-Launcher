"""Native-grid disk extrema and projected rim checks."""
import numpy as np
from .terrain import Terrain,CACHE,ROWS,PPD,RADIUS
from .geometry import destination
terrain=None

def vertex_extrema(lat, lon, radius):
    sector = int(lon//45)
    tile = terrain.tiles[sector]
    pad = np.degrees(radius/(RADIUS-10000))+.003
    y = np.arange(max(0,int(ROWS-.5-(lat+pad)*PPD)),min(2*ROWS,int(ROWS-.5-(lat-pad)*PPD)+2))
    x = np.arange(int((lon-sector*45-pad)*PPD)-1,int((lon-sector*45+pad)*PPD)+2)
    phi = (ROWS-.5-y)/PPD
    lam = sector*45+(x+.5)/PPD
    hav = (np.sin(np.radians((phi[:,None]-lat)/2))**2 +
           np.cos(np.radians(lat))*np.cos(np.radians(phi[:,None]))*np.sin(np.radians((lam-lon)/2))**2)
    h = tile[np.ix_(y,x)].astype(float)*1000
    inside = (RADIUS+h)*2*np.sqrt(hav*(1-hav)) <= radius
    i,j = np.unravel_index(np.argmax(np.where(inside,h,-np.inf)),h.shape)
    return float(phi[i]),float(lam[j]),float(h[i,j]),float(h[inside].min())

def rim(lat, lon, radius, count=7200):
    bearings = np.linspace(0,2*np.pi,count,endpoint=False)
    angle = np.full(count,np.arcsin(radius/(RADIUS+float(terrain.height(lat,lon)))))
    for _ in range(4):
        y,x = destination(lat,lon,bearings,angle)
        h = terrain.height(y,x)
        angle = np.arcsin(radius/(RADIUS+h))
    y,x = destination(lat,lon,bearings,angle)
    h = terrain.height(y,x)
    return h,(RADIUS+h)*np.cos(angle)

