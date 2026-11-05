"""Validate saved corridor boundaries, seed classifications and the 144° path."""
import json
import numpy as np
from scipy.integrate import solve_ivp
from . import survey as s


def main():
    s.c.initialize();r=json.loads((s.OUT/'results.json').read_text())
    max_boundary_residual=0.;checked=0
    for kind,key in [('outbound','outbound_ranges'),('both','both_ranges')]:
        previous=-float('inf')
        for band in r[key]:
            lo=band['start_deg_east'];hi=band['end_deg_east']
            assert hi>lo and lo>=previous;previous=hi
            assert not band['clipped_to_window']
            assert s.score((lo+hi)/2,kind)>0
            for x in [lo,hi]:
                residual=abs(s.score(x,kind));max_boundary_residual=max(max_boundary_residual,residual)
                assert residual<.001
            checked+=1
    fine_seed=[]
    for lon in s.SEEDS:
        result=s.c.classify((lon,10.,True));assert result['status']=='return_impact';fine_seed.append(result)
    # Direct Cartesian integration at the regional mountain near 195° E.
    o=s.c.orbit(144,10.);target=np.radians(194.8837890625-144)
    rad,t,_,_=s.c.at_longitude(target,o)
    def rhs(t,y):return np.r_[y[3:],-s.c.MU*y[:3]/np.linalg.norm(y[:3])**3]
    sol=solve_ivp(rhs,(0,float(t)),[o['rp'],0,0,0,o['h']/o['rp'],0],method='DOP853',rtol=1e-12,atol=1e-8,max_step=20)
    pos=sol.y[:3,-1];radius_error=abs(np.linalg.norm(pos)-rad)
    lon=np.arctan2(pos[1],pos[0])-s.c.MOON_OMEGA*float(t)
    assert sol.success and radius_error<1e-4 and abs(lon-target)<1e-10
    clearance=np.linalg.norm(pos)-s.c.RADIUS-float(s.c.terrain(o['lon']+lon))
    assert clearance>400
    out=dict(checked_intervals=checked,max_boundary_score_residual_m=max_boundary_residual,
        all_eight_seed_sites_confirmed_with_half_cell_terrain_refinement=True,
        independent_144_radius_error_m=float(radius_error),independent_144_regional_mountain_clearance_m=float(clearance))
    (s.OUT/'validation.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))

if __name__=='__main__':main()
