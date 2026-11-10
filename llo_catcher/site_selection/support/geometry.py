"""Spherical destination and local map projection helpers."""
import numpy as np
from .constants import RADIUS

def destination(lat,lon,bearing,angle):
    phi=np.radians(lat);lam=np.radians(lon)
    p=np.arcsin(np.sin(phi)*np.cos(angle)+np.cos(phi)*np.sin(angle)*np.cos(bearing))
    q=lam+np.arctan2(np.sin(bearing)*np.sin(angle)*np.cos(phi),np.cos(angle)-np.sin(phi)*np.sin(p))
    return np.degrees(p),np.degrees(q)

def project(lat,lon,lat0,lon0):
    p,p0=np.radians(lat),np.radians(lat0);d=np.radians(lon-lon0)
    cosc=np.clip(np.sin(p0)*np.sin(p)+np.cos(p0)*np.cos(p)*np.cos(d),-1,1)
    c=np.arccos(cosc);k=np.divide(c,np.sin(c),out=np.ones_like(c),where=np.abs(c)>1e-12)
    return RADIUS/1000*k*np.cos(p)*np.sin(d),RADIUS/1000*k*(np.cos(p0)*np.sin(p)-np.sin(p0)*np.cos(p)*np.cos(d))

