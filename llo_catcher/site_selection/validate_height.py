"""Independent Cartesian contact checks for the hub-relative height audit."""
from pathlib import Path
import json
import numpy as np
from scipy.integrate import solve_ivp
from ..analysis.single_equatorial_release.directional_sites import orbits
ROOT=Path(__file__).parent

def main():
    orbits.initialize();e=orbits.MODELS['east'];checks=[]
    for row in json.loads((ROOT/'height_audit.json').read_text()):
        lon=row['hub_longitude_deg']%360;h=row['new_release_height_above_local_ground_m']
        for d,sign in [('east',1),('west',-1)]:
            m=orbits.MODELS[d];a=m.classify((sign*lon%360,h,False));b=m.classify((sign*lon%360,h,True))
            assert a['status']==b['status']==row[d+'_status']
            t=a['impact_time_s'];assert abs(t-b['impact_time_s'])<1e-5
            rp=a['release_radius_m'];v=a['inertial_release_speed_m_s']
            def rhs(t,y):return np.r_[y[3:],-e.MU*y[:3]/np.linalg.norm(y[:3])**3]
            sol=solve_ivp(rhs,(0,t),[rp,0,0,0,sign*v,0],method='DOP853',rtol=1e-12,atol=1e-8,max_step=20)
            assert sol.success
            pos=sol.y[:3,-1];angle=np.radians(lon)+np.arctan2(pos[1],pos[0])-e.MOON_OMEGA*t
            gap=float(np.linalg.norm(pos)-e.RADIUS-e.terrain(angle));assert abs(gap)<.001
            checks.append(dict(site=row['id'],direction=d,status=a['status'],independent_contact_gap_m=gap))
    (ROOT/'height_validation.json').write_text(json.dumps(dict(contacts=checks,half_cell_classifications_agree=True),indent=2)+'\n')
    print('Validated',len(checks),'contacts; maximum Cartesian residual m:',max(abs(x['independent_contact_gap_m']) for x in checks))
if __name__=='__main__':main()
