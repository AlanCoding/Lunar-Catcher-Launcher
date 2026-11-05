"""Optimize horizontal launch heading for first-node equatorial capture.
Fixed release position; no terrain, propulsion after release, or hardware model.
"""
from pathlib import Path
import json
import numpy as np
from scipy.optimize import minimize_scalar, brentq
from scipy.integrate import solve_ivp
from llo_catcher.analysis.spherical_release.calculate import R,MU,MOON_RATE,OMEGA,node_case
OUT=Path(__file__).resolve().parent
D=node_case(3)['offset_m']

def case(theta_deg,clearance=3.,altitude=25000.,offset=D,direction=1):
    r0=R+clearance;rc=R+altitude;b=np.arcsin(offset/r0)
    t=np.radians(theta_deg)
    # Prograde southern tip; retrograde northern tip is the mirrored case.
    beta=np.arcsin(np.tan(b)/np.tan(t))
    rh=np.array([np.cos(b),0.,-direction*np.sin(b)])
    north_away_sign=np.array([np.sin(b),0.,direction*np.cos(b)])
    q=np.array([0.,direction*np.cos(beta),0.])+np.sin(beta)*north_away_sign
    e=(rc-r0)/(r0-rc*np.cos(t));p=r0*(1+e);a=p/(1-e*e)
    speed=np.sqrt(MU*p)/r0;v0=speed*q
    rc_hat=np.cos(t)*rh+np.sin(t)*q
    vc_payload=np.sqrt(MU/p)*(-np.sin(t)*rh+(e+np.cos(t))*q)
    east=np.cross([0.,0.,1.],rc_hat);east/=np.linalg.norm(east)
    vc_station=direction*np.sqrt(MU/rc)*east
    dv=vc_payload-vc_station
    E=2*np.arctan2(np.sqrt(1-e)*np.sin(t/2),np.sqrt(1+e)*np.cos(t/2))
    flight=(E-e*np.sin(E))*np.sqrt(a**3/MU)
    hhat=np.cross(rh,q)
    relative=v0-np.cross([0,0,MOON_RATE],r0*rh)
    return dict(angle_deg=float(theta_deg),heading_toward_equator_deg=float(np.degrees(beta)),
        inclination_from_corresponding_equatorial_plane_deg=float(np.degrees(np.arccos(abs(hhat[2])))),
        relative_catch_m_s=float(np.linalg.norm(dv)),radial_catch_m_s=float(dv@rc_hat),
        north_catch_m_s=float(dv[2]),along_track_catch_m_s=float(dv@(direction*east)),
        apoapsis_altitude_m=float(p/(1-e)-R),flight_time_s=float(flight),period_s=float(2*np.pi*np.sqrt(a**3/MU)),
        release_speed_inertial_m_s=float(speed),release_speed_surface_relative_m_s=float(np.linalg.norm(relative)),
        release_velocity_m_s=v0.tolist(),initial_state=np.r_[r0*rh,v0].tolist(),catch_position_m=(rc*rc_hat).tolist(),
        catch_velocity_m_s=vc_payload.tolist(),minimum_clearance_m=clearance,offset_m=offset,
        equivalent_speed_over_offset_rpm=float(np.linalg.norm(relative)/offset*60/(2*np.pi)))

def sling_case(phase_deg):
    """Horizontal rigid-circle kinematics, reference RPM, radius retargeted.

    Phase zero is the southernmost tip; negative phase releases just before it.
    Three-metre radial clearance held by adjusting the rotation-plane height.
    """
    ph=np.radians(phase_deg);r0=R+3;rc=R+25000
    def state(d):
        r=np.array([np.sqrt(r0*r0-d*d),d*np.sin(ph),-d*np.cos(ph)])
        v=np.array([0.,OMEGA*d*np.cos(ph),OMEGA*d*np.sin(ph)])+np.cross([0,0,MOON_RATE],r)
        vi=np.linalg.norm(v);rh=r/r0;q=v/vi
        theta=np.arctan2(-rh[2],q[2]);p=r0*r0*vi*vi/MU;e=p/r0-1
        return p/(1+e*np.cos(theta))-rc,theta,r,v
    d=brentq(lambda d:state(d)[0],4000,8000,xtol=1e-9)
    _,theta,r,v=state(d)
    c=case(np.degrees(theta),offset=-r[2])
    assert abs(c['release_speed_inertial_m_s']-np.linalg.norm(v))<1e-6
    c.update(hub_frame_initial_state=np.r_[r,v].tolist(),sling_phase_deg=float(phase_deg),sling_horizontal_radius_m=float(d),
        release_east_offset_from_hub_m=float(r[1]),release_north_offset_from_hub_m=float(r[2]),
        rotation_plane_height_over_hub_tangent_m=float(r[0]-R),
        sling_rpm=float(OMEGA*60/(2*np.pi)),
        centripetal_acceleration_earth_g=float(OMEGA**2*d/9.80665))
    return c

def main():
    # e<1 and forward-east/west tangent direction restrict the branch.
    rc=R+25000;r0=R+3
    low=np.degrees(np.arccos(2*r0/rc-1))+1e-5
    high=180-np.degrees(np.arcsin(D/r0))-1e-5
    angles=np.linspace(low,high,6001)
    rows=[case(t) for t in angles];f=np.array([c['relative_catch_m_s'] for c in rows])
    candidates=[]
    for j in range(1,len(rows)-1):
        if f[j]<f[j-1] and f[j]<f[j+1]:
            opt=minimize_scalar(lambda x:case(x)['relative_catch_m_s'],bounds=(angles[j-1],angles[j+1]),method='bounded',options={'xatol':1e-10})
            candidates.append(case(opt.x))
    best=min(candidates+[rows[0],rows[-1]],key=lambda x:x['relative_catch_m_s'])
    selected=[case(t) for t in [90,120,150,160,170,175]]
    def rhs(t,y):return np.r_[y[3:],-MU*y[:3]/np.linalg.norm(y[:3])**3]
    checks=[]
    for c in [case(90),best,case(170)]:
        sol=solve_ivp(rhs,(0,c['period_s']),c['initial_state'],method='DOP853',rtol=1e-12,atol=1e-8,max_step=20,dense_output=True)
        y=sol.sol(c['flight_time_s']);err=np.linalg.norm(y[:3]-c['catch_position_m']);ve=np.linalg.norm(y[3:]-c['catch_velocity_m_s'])
        assert sol.success and err<.001 and ve<1e-6
        assert abs(y[2])<.001
        checks.append(dict(angle_deg=c['angle_deg'],catch_position_error_m=float(err),catch_velocity_error_m_s=float(ve)))
    phase_opt=minimize_scalar(lambda phase:sling_case(phase)['relative_catch_m_s'],bounds=(-5.,0.),method='bounded',options={'xatol':1e-10})
    physical=sling_case(phase_opt.x)
    physical_sol=solve_ivp(rhs,(0,physical['flight_time_s']),physical['hub_frame_initial_state'],method='DOP853',rtol=1e-12,atol=1e-8,max_step=20)
    end=physical_sol.y[:,-1];rad=np.linalg.norm(end[:3]);east=np.cross([0.,0.,1.],end[:3]);east/=np.linalg.norm(east)
    physical_speed=np.linalg.norm(end[3:]-np.sqrt(MU/(R+25000))*east)
    assert physical_sol.success and abs(rad-(R+25000))<.001 and abs(end[2])<.001
    assert abs(physical_speed-physical['relative_catch_m_s'])<1e-6
    physical['validation_node_z_error_m']=float(abs(end[2]))
    phase_scan=[sling_case(phase) for phase in np.linspace(-85,0,1001)]
    assert physical['relative_catch_m_s']<=min(c['relative_catch_m_s'] for c in phase_scan)+1e-6
    result=dict(reference_rpm_phase_optimization=physical,assumptions='Fixed 5796.553 m south offset, 3 m release/periapsis clearance, 25 km equatorial prograde catcher; locally horizontal release, free heading and speed',best=best,selected=selected,search_bounds_deg=[low,high],interior_minima=len(candidates),checks=checks)
    (OUT/'results.json').write_text(json.dumps(result,indent=2)+'\n')
    import csv
    columns=['angle_deg','heading_toward_equator_deg','relative_catch_m_s','radial_catch_m_s','north_catch_m_s','along_track_catch_m_s','apoapsis_altitude_m','flight_time_s','period_s']
    with (OUT/'sweep.csv').open('w') as stream:
        w=csv.DictWriter(stream,fieldnames=columns,extrasaction='ignore');w.writeheader();w.writerows(rows)
    plot(rows,best)
    print(json.dumps(result,indent=2))

def plot(rows,best):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    rows=[r for r in rows if r['angle_deg']>=90]
    t=[r['angle_deg'] for r in rows]
    fig,axes=plt.subplots(3,1,figsize=(10,10),sharex=True,layout='constrained')
    for key,label,color in [('relative_catch_m_s','Total relative speed','#265e80'),('radial_catch_m_s','Radial component','#b37b30'),('north_catch_m_s','North component','#4d865e'),('along_track_catch_m_s','Along-track mismatch magnitude','#986c91')]:
        axes[0].plot(t,[abs(r[key]) for r in rows],label=label,color=color,lw=2)
    axes[0].set_ylim(0,70);axes[0].set_ylabel('Capture velocity (m/s)');axes[0].legend(fontsize=9)
    axes[0].scatter([best['angle_deg']],[best['relative_catch_m_s']],color='black',zorder=5)
    axes[1].plot(t,[r['apoapsis_altitude_m']/1000 for r in rows],color='#265e80',label='Uncaught apoapsis')
    axes[1].axhline(25,color='#b37b30',ls='--',label='Catcher altitude');axes[1].legend();axes[1].set_ylabel('Altitude (km)')
    axes[2].plot(t,[r['flight_time_s']/60 for r in rows],label='Release to capture',color='#265e80')
    axes[2].plot(t,[r['period_s']/60 for r in rows],label='Uncaught orbital period',color='#986c91')
    axes[2].legend();axes[2].set_ylabel('Time (minutes)');axes[2].set_xlabel('Orbital angle from release to first equator crossing (degrees)')
    for ax in axes:ax.axvline(best['angle_deg'],ls=':',color='black');ax.grid(alpha=.2);ax.set_xlim(90,180)
    fig.suptitle(f'Launch-heading tradeoff: minimum catch speed at {best["angle_deg"]:.2f}°\n25 km equatorial catcher; 5.797 km offset; 3 m periapsis clearance')
    fig.savefig(OUT/'heading_tradeoff.png',dpi=160);fig.savefig(OUT/'heading_tradeoff.svg');plt.close(fig)

if __name__=='__main__':main()
