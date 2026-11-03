"""Reproducible speed-constrained scenario checkpoint (not a qualified design).

Run: MPLCONFIGDIR=/tmp/lunar-sling-mpl-cache .env/hub/bin/python -m
     sling_launcher.scenario_study
"""
from dataclasses import dataclass, asdict
from pathlib import Path
import json
import numpy as np
from scipy.interpolate import CubicSpline
from .cable_shape import Cable
from .environment import LunarEnvironment
from .orbit import point_surface_reference, finite_tip_node_intercept, counter_release_state, impact_report

@dataclass(frozen=True)
class Scenario:
    acceleration_g: float = 4.
    rover_mph: float = 50.
    payload_kg: float = 1000.
    passes: int = 1
    loading_s: float = 300.
    buffer_s: float = 300.
    friction: float = .5
    driven_fraction: float = .75
    rolling: float = .02
    drive_efficiency: float = .85
    recovery_efficiency: float = .7
    solar_w_kg: float = 100.
    stress_pa: float = 1e9
    shape_fractions: int = 241
    shape_nodes: int = 501
    time_nodes: int = 1601


def geometry(c):
    env=LunarEnvironment();u=1684.52;v=c.rover_mph*.44704
    for iteration in range(12):
        w=c.acceleration_g*env.earth_g_m_s2/u;a=v/w;b=u/w
        cable=Cable(a,b,w,c.payload_kg,env.surface_gravity_m_s2,stress=c.stress_pa)
        branches=[cable.branch(m,env.reference_radius_m,c.shape_fractions,c.shape_nodes) for m in [c.payload_kg,0.]]
        h=max(p['height'] for p in branches)
        tip_height=h-branches[0]['values'][-1,4]
        orbit=finite_tip_node_intercept(env,20000,b,tip_height)
        if abs(orbit.site_tip_speed_m_s-u)<1e-6:break
        u=orbit.site_tip_speed_m_s
    else: raise RuntimeError('Release speed/clearance iteration did not converge')
    return cable,branches,h,orbit


def calculate(c,geo=None,history=False):
    env=LunarEnvironment();g=env.surface_gravity_m_s2
    cable,branches,h,orbit=geo if geo is not None else geometry(c)
    w=cable.omega;a=cable.radius;v=w*a
    T=c.passes*point_surface_reference(env,20000)['site_revisit_s'];travel=(T-c.loading_s-c.buffer_s)/2
    if travel<=0:raise ValueError('No deployment time')
    # Always slow down to close phase: never exceed the specified operating speed.
    # Split correction over loading and final buffer to keep the 4-g case moving.
    correction=-(w*T)%(2*np.pi)
    correction=0. if correction<1e-12 else correction-2*np.pi
    duration=c.loading_s+c.buffer_s;pieces=[]
    def correction_profile(t,dt):
        x=t/dt
        return w+2*correction/duration*np.sin(np.pi*x)**2,2*correction*np.pi/(duration*dt)*np.sin(2*np.pi*x)
    n=c.time_nodes
    for name,dt in [('loading',c.loading_s),('buffer',c.buffer_s)]:
        t=np.linspace(0,dt,n);omega,alpha=correction_profile(t,dt)
        load=c.payload_kg*t/dt if name=='loading' else np.zeros(n)
        rate=2*c.payload_kg/dt if name=='loading' else 0.
        inertia=2*(cable.mass+load)*a*a
        torque=inertia*alpha+rate*a*a*omega
        pieces.append(dict(name=name,t=t,f=np.zeros(n),omega=omega,alpha=alpha,
                           radial=np.zeros(n),torque=torque,base_mass=2*(cable.mass+load),
                           kinetic=.5*inertia*omega**2,potential=np.zeros(n)))
    for index,name in [(0,'payout'),(1,'retraction')]:
        t=np.linspace(0,travel,n);x=t/travel
        f=10*x**3-15*x**4+6*x**5;fd=(30*x*x-60*x**3+30*x**4)/travel;fdd=(60*x-180*x*x+120*x**3)/travel**2
        if index:f,fd,fdd=1-f,-fd,-fdd
        b=branches[index];spl=CubicSpline(b['f'],b['values'],axis=0)
        values=spl(f);first=spl(f,1);I,U,K=values[:,:3].T;Ip,Up,Kp=first[:,:3].T
        radial=(K*fdd+.5*Kp*fd*fd+Up-.5*Ip*w*w)*fd
        torque=Ip*fd*w
        load=c.payload_kg if index==0 else 0.
        piece=dict(name=name,t=t,f=f,omega=w*np.ones(n),alpha=np.zeros(n),radial=radial,torque=torque,
                   base_mass=np.full(n,2*(cable.mass+load)),kinetic=.5*I*w*w+.5*K*fd*fd,potential=U)
        if index==0:
            # Proper acceleration applied to payload: meridional + Coriolis + gravity.
            rp,zp=first[:,3],-first[:,4];second=spl(f,2);rpp,zpp=second[:,3],-second[:,4]
            ar=rpp*fd*fd+rp*fdd-w*w*values[:,3]
            az=zpp*fd*fd+zp*fdd
            piece['payload_proper_g']=np.sqrt(ar*ar+(2*w*rp*fd)**2+(az+g)**2)/env.earth_g_m_s2
        pieces.insert(1+index,piece)
    low=0.;upper=np.inf;k=c.friction*c.driven_fraction*g
    for p in pieces:
        p['f0']=p['torque']/a+c.rolling*g*p['base_mass'];p['coef']=a*p['alpha']+c.rolling*g
        for sign in [-1,1]:
            coeff=sign*p['coef']-k;rhs=k*p['base_mass']-sign*p['f0']
            neg=coeff < -1e-12;pos=coeff>1e-12
            if np.any(neg):low=max(low,float(np.max(rhs[neg]/coeff[neg])))
            if np.any(pos):upper=min(upper,float(np.min(rhs[pos]/coeff[pos])))
    ballast=max(0.,low)
    if ballast>upper:raise ValueError('No traction solution')
    summaries=[];peak0=peakr=0.;energy0=energyr=0.;forcepeak=0.;location=None
    for p in pieces:
        force=p['f0']+p['coef']*ballast;wheel=force*a*p['omega'];radial=p['radial']
        positive=np.maximum(wheel,0)+np.maximum(radial,0);negative=np.maximum(-wheel,0)+np.maximum(-radial,0)
        solar0=positive/c.drive_efficiency;solarr=np.maximum(solar0-c.recovery_efficiency*negative,0.)
        p.update(force=force,wheel=wheel,solar0=solar0,solarr=solarr)
        e0=float(np.trapezoid(solar0,p['t']));er=float(np.trapezoid(solarr,p['t']))
        peak0=max(peak0,float(max(solar0)));peakr=max(peakr,float(max(solarr)));energy0+=e0;energyr+=er
        i=int(np.argmax(abs(force)))
        if abs(force[i])>forcepeak:
            forcepeak=float(abs(force[i]));location=dict(phase=p['name'],deployed_fraction=float(p['f'][i]))
        summaries.append(dict(phase=p['name'],duration_s=float(p['t'][-1]),peak_wheel_w=float(max(wheel)),
                              peak_reel_input_w=float(max(np.maximum(radial,0))),peak_reel_braking_w=float(max(np.maximum(-radial,0))),
                              solar_no_recovery_j=e0,solar_with_recovery_j=er))
    # Tie endpoint envelope before its own inertia; use maximum of root cable load
    # plus stored cable and ballast centrifugal force. New unsized hardware excluded.
    tie_end=0.
    for branch in branches:
        for shape in branch['shapes']:
            stored=cable.mass-shape['deployed_mass']
            tie_end=max(tie_end,float(shape['tr'][0]+(ballast/2+stored)*w*w*a))
    xx=np.linspace(0,a,1001);tieT=tie_end*np.exp(cable.density*w*w*(a*a-xx*xx)/(2*c.stress_pa))
    tie_mass=2*float(np.trapezoid(cable.density*tieT/c.stress_pa,xx))
    tie_sag=cable.density*g*a*a/(2*c.stress_pa) # negligible angle approximation for tie alone
    # Instantaneous release does NOT actually make the empty cable take its new
    # quasi-static shape. Report the discontinuity, do not hide it in cycle energy.
    loaded=branches[0]['shapes'][-1];empty=branches[1]['shapes'][-1]
    def empty_energy(p):return float(np.trapezoid(p['lam']*(.5*w*w*p['r']**2-g*p['drop']),p['s']))
    jump=2*(empty_energy(empty)-empty_energy(loaded))
    counter=impact_report(env,counter_release_state(env,orbit))
    minomega=min(float(min(p['omega'])) for p in pieces);maxomega=max(float(max(p['omega'])) for p in pieces)
    halfwidth=h*w*w*a/g # compact-frame necessary support lever without strong stays
    powered_normal=(2*cable.mass+2*c.payload_kg+ballast)*g*c.driven_fraction/4
    out=dict(inputs=asdict(c),status='conditional quasi-static scenario; not a buildable certified design',
       release_centripetal_g=c.acceleration_g,peak_payload_proper_g=float(max(pieces[1]['payload_proper_g'])),
       release_speed_m_s=orbit.site_tip_speed_m_s,omega_rad_s=w,track_radius_m=a,release_radius_m=cable.tip_radius,
       cable_length_m=cable.length,pole_apex_height_m=h,vertical_leg_m=h,leg_45deg_m=np.sqrt(2)*h,
       controlling_clearance=[dict(branch=name,height_m=b['height'],fraction=b['controlling_fraction']) for name,b in zip(['loaded','empty'],branches)],
       frame_45deg_same_track_fits=bool(h<2*a),required_horizontal_45deg_span_m=h,available_track_diameter_m=2*a,
       compact_frame_required_radial_halfwidth_m=halfwidth,halfwidth_over_track_radius=halfwidth/a,
       ballast_total_kg=ballast,ballast_lunar_weight_n=ballast*g,ballast_per_powered_wheel_kg=ballast/4,
       powered_wheel_normal_n=powered_normal,powered_contact_area_at_100kpa_m2=powered_normal/100000,
       total_outward_cable_kg=2*cable.mass,main_tie_conditional_kg=tie_mass,main_tie_endpoint_n=tie_end,
       main_tie_sag_estimate_m=tie_sag,extra_ballast_radial_force_per_frame_n=ballast/2*w*w*a,
       empty_spool_fiber_volume_per_side_m3=cable.mass/cable.density,
       max_cable_solid_equivalent_diameter_m=float(np.sqrt(4*max(cable.lam)/cable.density/np.pi)),
       max_static_cable_stress_pa=max(b['max_tensile_stress_pa'] for b in branches),
       peak_solar_no_recovery_w=peak0,peak_solar_recovery_w=peakr,
       solar_no_recovery_kg=peak0/c.solar_w_kg,solar_recovery_kg=peakr/c.solar_w_kg,
       accounted_imported_subtotal_no_recovery_kg=2*cable.mass+tie_mass+peak0/c.solar_w_kg,
       accounted_imported_subtotal_recovery_kg=2*cable.mass+tie_mass+peakr/c.solar_w_kg,
       pole_mass_kg=None,total_imported_mass_kg=None,
       solar_cycle_no_recovery_j=energy0,solar_cycle_recovery_j=energyr,
       peak_ground_force_n=forcepeak,peak_traction_location=location,
       phase_correction_rad=correction,min_rover_speed_m_s=minomega*a,max_rover_speed_m_s=maxomega*a,
       interval_s=T,phases=summaries,
       release_tip_altitude_m=float(np.linalg.norm(orbit.initial_state[:3])-env.reference_radius_m),
       catcher_flight_s=orbit.flight_s,catcher_relative_speed_m_s=float(np.linalg.norm(orbit.catch_relative_vector_m_s)),
       equal_radius_countermass_impacts=counter['impacts_reference_sphere'],
       release_shape_energy_discontinuity_j=jump,
       release_empty_tip_displacement_m=float(np.hypot(empty['r'][-1]-loaded['r'][-1],empty['drop'][-1]-loaded['drop'][-1])),
       model_exclusions=['Release transient/recoil power and clearance', 'Drum spin/bend/guide losses',
                         'Cable tangential lag and dynamic shape', 'Frame, wheel, motor and retention structural mass',
                         'Normal loads and moments at individual contacts', 'Startup/shutdown and lunar night'])
    if history:out['history']=pieces
    return out


def main():
    from .scenario_report import produce
    produce()

if __name__=='__main__':main()
