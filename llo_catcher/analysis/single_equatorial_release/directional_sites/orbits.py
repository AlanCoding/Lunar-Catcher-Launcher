"""Independent east/west equatorial shots using a reflected coordinate for west."""
import importlib.util
from .. import calculate as base
import numpy as np
MODELS={}
def initialize():
    base.initialize()
    for direction in ['east','west']:
        spec=importlib.util.spec_from_file_location('directional_'+direction,base.__file__)
        m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
        m._GROUND=base._GROUND if direction=='east' else base._GROUND[::-1]
        if direction=='west':m.MOON_OMEGA=-base.MOON_OMEGA
        MODELS[direction]=m

def classify(lon,direction,refine=False):
    m=MODELS[direction];sign=1 if direction=='east' else -1
    r=m.classify((sign*lon%360,10.,refine));r['longitude_deg_east']=float(lon%360);r['direction']=direction
    if r['impact_longitude_deg_east'] is not None:r['impact_longitude_deg_east']=sign*r['impact_longitude_deg_east']%360
    return r

def clearance(lon,direction):
    return MODELS[direction].minimum_outbound((lon if direction=='east' else -lon)%360,10.)
