"""Spherical-Moon geometry: finite-offset equator-node interception.

No terrain modules or data are imported. Distances SI; rates in rad/s internally.
"""
from pathlib import Path
import json
import numpy as np
from scipy.optimize import brentq
from scipy.integrate import solve_ivp

OUT=Path(__file__).resolve().parent
R=1737400.
MU=4.902800118e12
MOON_RATE=2*np.pi/(655.720*3600)
RPM=2.77962791161922
OMEGA=RPM*2*np.pi/60
RC=R+25000.


def offset_for_radius(r,mode='rpm'):
    """South-arm prograde launch. Acceleration mode sets omega^2*d=50 Earth g."""
    vi=np.sqrt(MU*RC)/r
    def residual(d):
        relative=OMEGA*d if mode=='rpm' else np.sqrt(50*9.80665*d)
        return relative+MOON_RATE*np.sqrt(r*r-d*d)-vi
    return brentq(residual,100,20000,xtol=1e-9)


def node_case(clearance_m,mode='rpm'):
    r=R+clearance_m;d=offset_for_radius(r,mode);x=np.sqrt(r*r-d*d)
    vi=np.sqrt(MU*RC)/r;e=RC/r-1;a=RC/(1-e*e)
    rhat=np.array([x/r,0.,-d/r]);q=np.array([0.,1.,0.])
    vc=np.sqrt(MU/RC);velocity=vc*(-rhat+e*q)
    delta=velocity-np.array([-vc,0,0])
    ec=np.arccos(e);time=(ec-e*np.sin(ec))*np.sqrt(a**3/MU)
    return dict(clearance_m=clearance_m,mode=mode,offset_m=d,
        tip_height_above_tower_foot_tangent_m=x-R,
        rpm=RPM if mode=='rpm' else np.sqrt(50*9.80665/d)*60/(2*np.pi),
        release_inertial_m_s=vi,release_surface_relative_m_s=vi-MOON_RATE*x,
        eccentricity=e,semimajor_axis_m=a,periapsis_radius_m=r,
        apoapsis_altitude_m=RC/(1-e)-R,catch_time_s=time,
        catch_relative_m_s=float(np.linalg.norm(delta)),
        catch_radial_m_s=e*vc,catch_north_m_s=float(delta[2]),
        initial_state=[x,0.,-d,0.,vi,0.],rhat=rhat.tolist())


def case_at_tip_tangent_height(tip_height,mode='rpm'):
    x=R+tip_height
    def residual(d):
        r=np.hypot(x,d)
        relative=OMEGA*d if mode=='rpm' else np.sqrt(50*9.80665*d)
        return relative+MOON_RATE*x-np.sqrt(MU*RC)/r
    d=brentq(residual,100,20000)
    return node_case(np.hypot(x,d)-R,mode)


def main():
    example=node_case(3.)  # Illustration only, not a newly imposed design constraint.
    validation={}
    def rhs(t,y):return np.r_[y[3:],-MU*y[:3]/np.linalg.norm(y[:3])**3]
    T=2*np.pi*np.sqrt(example['semimajor_axis_m']**3/MU)
    solution=solve_ivp(rhs,(0,T),example['initial_state'],method='DOP853',rtol=1e-12,atol=1e-8,max_step=20,dense_output=True)
    assert solution.success
    catch=solution.sol(example['catch_time_s'])
    error=np.linalg.norm(catch[:3]-np.array([0,RC,0]))
    assert error<.001
    closure=np.linalg.norm(solution.y[:3,-1]-np.array(example['initial_state'][:3]))
    assert closure<.001
    assert abs(example['catch_relative_m_s']-np.linalg.norm(catch[3:]-[-np.sqrt(MU/RC),0,0]))<1e-6
    validation.update(catch_position_error_m=float(error),orbit_closure_position_error_m=float(closure))
    height_results={}
    for mode in ['rpm','acceleration']:
        grazing=node_case(0.,mode)
        margins=[]
        for dh in [0,1,3,10,30]:
            revised=case_at_tip_tangent_height(grazing['tip_height_above_tower_foot_tangent_m']+dh,mode)
            assert abs(revised['clearance_m']-dh)<.001
            margins.append(dict(tower_height_added_m=dh,release_clearance_m=revised['clearance_m'],
                                minimum_orbit_clearance_m=revised['clearance_m'],offset_m=revised['offset_m']))
        height_results[mode]=dict(grazing=grazing,height_margins=margins,
            tower_zero_drop_zero_height=case_at_tip_tangent_height(0.,mode))
    # For comparison only: erroneously putting the offset orbit's apoapsis at 25 km.
    r=R+3;a_wrong=(r+RC)/2;e_wrong=(RC-r)/(RC+r)
    p_wrong=a_wrong*(1-e_wrong*e_wrong)
    # For pure eastward horizontal geometry, z at apoapsis is opposite release z.
    wrong_apo_lat=np.degrees(np.arcsin(example['offset_m']/r))
    result=dict(model='Spherical central gravity, uniform lunar rotation, prograde south-arm release',
        radius_m=R,mu_m3_s2=MU,catcher_altitude_m=25000,example_clearance_is_illustrative=True,
        example=example,height_results=height_results,
        wrong_apoapsis_target=dict(node_altitude_m=p_wrong-R,apoapsis_latitude_deg=wrong_apo_lat),
        validation=validation)
    (OUT/'results.json').write_text(json.dumps(result,indent=2)+'\n')
    plot(result)
    print(json.dumps(result,indent=2))


def plot(result):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    s=result['example'];theta=np.linspace(0,2*np.pi,1201)
    radius=RC/(1+s['eccentricity']*np.cos(theta))
    lat=np.degrees(np.arcsin(-s['offset_m']/s['periapsis_radius_m']*np.cos(theta)))
    angle=np.degrees(theta)
    fig,axs=plt.subplots(2,1,figsize=(10,7.2),sharex=True,layout='constrained')
    axs[0].plot(angle,(radius-R)/1000,color='#376d91',lw=2.5,label='Uncaught payload')
    axs[0].axhline(25,color='#b37b30',ls='--',label='Circular catcher altitude')
    axs[0].scatter([90],[25],color='#4b805f',s=70,zorder=4)
    axs[0].annotate('Catch here: equator crossing\n25 km altitude, ~27.16 minutes',xy=(90,25),xytext=(8,41),arrowprops=dict(arrowstyle='->',color='#4b805f'),fontsize=10)
    axs[0].annotate('Apoapsis: ~50.72 km\nPayload is north of equator',xy=(180,s['apoapsis_altitude_m']/1000),xytext=(212,42),arrowprops=dict(arrowstyle='->'),fontsize=10)
    axs[0].set_ylabel('Height above sphere (km)');axs[0].set_ylim(-2,58);axs[0].legend(loc='lower center',fontsize=9)
    axs[1].plot(angle,lat,color='#376d91',lw=2.5)
    axs[1].axhline(0,color='#b37b30',ls='--',label='Catcher orbital plane: equator')
    axs[1].scatter([90,270],[0,0],color='#4b805f',s=60,zorder=4)
    axs[1].set_ylabel('Payload latitude (degrees)');axs[1].set_xlabel('Orbital angle traveled since release (degrees, not ground longitude)')
    axs[1].set_xticks([0,90,180,270,360],['0°\nRelease / periapsis','90°\nFirst equator crossing','180°\nApoapsis','270°\nSecond equator crossing','360°\nPeriapsis again'])
    axs[1].legend(loc='upper right',fontsize=9)
    for ax in axs:
        ax.grid(alpha=.2);ax.set_xlim(0,360)
        for x in [90,180,270]:ax.axvline(x,color='#999999',ls=':',lw=.8)
    fig.suptitle('An equatorial circular catcher can intercept the inclined payload at a node\nIllustration: 3 m release clearance, ~5.80 km south offset; prograde catch at 25 km',fontsize=12)
    fig.savefig(OUT/'node_vs_apoapsis.png',dpi=170);fig.savefig(OUT/'node_vs_apoapsis.svg');plt.close(fig)


if __name__=='__main__':main()
