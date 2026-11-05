"""Independent Cartesian impact and close-pass checks."""
import json
import numpy as np
from scipy.integrate import solve_ivp
from . import calculate as c

def main():
    dem=c.Heights()
    sites=dict(zip(c.IDS,json.loads((c.ROOT.parent/'results.json').read_text())['sites']))
    rows=json.loads((c.ROOT/'results.json').read_text())+json.loads((c.ROOT/'mirrored_west.json').read_text())
    errors=[]
    for row in rows:
        if row['status']=='no_clear_release':
            assert row['release_clearance_m']<0
            continue
        site=sites[row['site']]
        sol=c.release(site,row['direction'],dem,row['release_geometry']=='equal_plane')
        y0=np.r_[c.state(sol,0.)[0],c.state(sol,0.)[1]]
        t=row['impact_time_min']*60
        def rhs(t,y):
            return np.r_[y[3:],-c.MU*y[:3]/np.linalg.norm(y[:3])**3]
        ivp=solve_ivp(rhs,(0,t),y0,method='DOP853',rtol=1e-12,atol=1e-8,max_step=12,dense_output=True)
        pos=ivp.y[:3,-1];r=np.linalg.norm(pos)
        lat=np.degrees(np.arcsin(pos[2]/r))
        lon=site['hub_lon_deg_east']+np.degrees(np.arctan2(pos[1],pos[0])-c.MOON_OMEGA*t)
        error=abs(float(r-c.RADIUS-dem.height_m(lat,lon)))
        assert ivp.success and error<.0001
        assert abs(lat-row['impact_lat_deg'])<1e-8 and abs(c.signed(lon)-row['impact_lon_deg'])<1e-8
        errors.append(error)
        for event in row['sweep_events']:
            phi=np.radians(site['hub_lat_deg'])
            for minute in [event['entry_min'],event['exit_min']]:
                tj=minute*60
                pos=ivp.sol(tj)[:3]
                angle=c.MOON_OMEGA*tj
                radial=pos[0]*np.cos(angle)+pos[1]*np.sin(angle)
                east=pos[1]*np.cos(angle)-pos[0]*np.sin(angle)
                north=pos[2]*np.cos(phi)-radial*np.sin(phi)
                assert abs(np.hypot(north,east)-site['actual_radius_km']*1000)<.001
                axial=radial*np.cos(phi)+pos[2]*np.sin(phi)
                assert 4.9<axial-c.relative_position(sol,site,0.)[1]<5.2
    report=dict(integrated_first_contacts=len(errors),maximum_impact_terrain_residual_m=max(errors),
                sweep_entry_exit_cartesian_check='within 1 mm')
    (c.ROOT/'validation.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report)

if __name__=='__main__':
    main()
