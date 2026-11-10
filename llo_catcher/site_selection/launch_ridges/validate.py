"""Independent height brackets and 15 m path sampling for representative seeds."""
import json,hashlib
import numpy as np
from .calculate import ROOT,GlobalTerrain,RADIUS,RA
from ..featured_four.adjusted_hilltops.check_launches import trajectory

def main():
    source=ROOT/'results.json';d=json.loads(source.read_text());terrain=GlobalTerrain();checks=[]
    chosen=[]
    for lon in d['seed_longitudes_deg']:
        rr=[r for r in d['rows'] if r['start_longitude_deg']==lon]
        chosen.extend([min(rr,key=lambda r:abs(r['source_north_m'])),max(rr,key=lambda r:r['contact_fresh_launch_extra_height_m'])])
    f=np.linspace(0,np.pi,int(np.ceil(np.pi*RA/15))+1)
    for r in chosen:
        gaps=[]
        for dh in [-.5,.5]:
            lat,lon,radius,t=trajectory(r['start_latitude_deg'],r['start_longitude_deg'],RADIUS+r['required_release_elevation_m']+dh,1)(f)
            gaps.append(float(np.min(radius-RADIUS-terrain.height(lat,lon))))
        assert gaps[0]<0<gaps[1],gaps
        checks.append(dict(seed_lon=r['start_longitude_deg'],seed_lat=r['start_latitude_deg'],below_threshold_minimum_gap_m=gaps[0],above_threshold_minimum_gap_m=gaps[1]))
    (ROOT/'validation.json').write_text(json.dumps(dict(source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),test='Threshold minus/plus 0.5 m, independent 15 m full outbound sampling',checks=checks),indent=2)+'\n')
    print('Passed',len(checks),'representative threshold brackets at 15 m sampling')
if __name__=='__main__':main()
