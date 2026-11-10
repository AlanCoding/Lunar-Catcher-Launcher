"""Check nearest summit contacts with denser paths and source provenance."""
import json,hashlib
import numpy as np
from .calculate import ROOT
from ..calculate import GlobalTerrain,RADIUS,RA
from ...featured_four.adjusted_hilltops.check_launches import trajectory

def main():
    terrain=GlobalTerrain();source=ROOT/'results.json';data=json.loads(source.read_text());comp=json.loads((ROOT/'comparison.json').read_text());checks=[]
    f=np.linspace(0,np.pi,int(np.ceil(np.pi*RA/15))+1)
    for c in comp:
        r=c['nearest_hub_contact'];gaps=[]
        for dh in [-.5,.5]:
            y,x,rad,t=trajectory(r['start_latitude_deg'],r['start_longitude_deg'],RADIUS+r['required_release_elevation_m']+dh,1)(f)
            gaps.append(float(np.min(rad-RADIUS-terrain.height(y,x))))
        assert gaps[0]<0<gaps[1],(c['site'],gaps)
        assert r['contact_anomaly_deg']>.05 and r['extra_release_height_m']>.1
        checks.append(dict(site=c['site'],threshold_minus_half_m_gap=gaps[0],threshold_plus_half_m_gap=gaps[1]))
    assert len(data['rows'])==3564
    assert all(r['minimum_gap_m']>-.1 for r in data['rows'])
    (ROOT/'validation.json').write_text(json.dumps(dict(results_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),samples=len(data['rows']),nearest_contact_checks=checks),indent=2)+'\n')
    print('Validated 3,564 seed results and four 15 m threshold brackets.')
if __name__=='__main__':main()
