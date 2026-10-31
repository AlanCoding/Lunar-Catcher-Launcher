"""One-dimensional cable inventory and rigid-rotation payout cycle; SI.

Straight radial cables, ideal reversible radial guides, point storage at apex.
Includes deployed/stored cable orbital inertia, radial kinetic energy, wheel
rolling loss, radial retraction work, phase closure, and traction ballast.
Drum self-inertia, bending/contact loss, elastic transients and wheel sinkage
remain outside this reduced-order bound. No added flywheel or energy storage.
"""
from dataclasses import dataclass, asdict
from pathlib import Path
import json
import numpy as np
from scipy.integrate import cumulative_trapezoid
from .environment import LunarEnvironment
from .orbit import point_surface_reference

@dataclass(frozen=True)
class PayoutCase:
    payload_kg: float = 1000.
    acceleration_g: float = 100.
    track_radius_m: float = 50.
    release_speed_m_s: float = 1684.52
    cable_density_kg_m3: float = 1450.
    cable_allowable_pa: float = 1e9
    passes: int = 1
    loading_s: float = 300.
    phase_buffer_s: float = 300.
    friction: float = .5
    driven_normal_fraction: float = .75
    rolling_coefficient: float = .02
    drive_efficiency: float = .85
    recovery_efficiency: float = 0.
    # No credit for unsized hardware weight or inertia. This is a known-mass
    # calculation; adding real hardware changes phase and normal-load balances.
    fixed_hardware_kg: float = 0.
    nodes: int = 10001
    time_nodes: int = 2001


def run(c=PayoutCase(), include_history=False):
    env=LunarEnvironment();g=env.surface_gravity_m_s2
    a=c.track_radius_m;w=c.acceleration_g*env.earth_g_m_s2/c.release_speed_m_s
    b=c.release_speed_m_s/w;L=b-a
    if L<=0 or w*a>35.76:
        return dict(inputs=asdict(c),status='release wheel-speed constraint',wheel_speed_m_s=w*a)
    interval=c.passes*point_surface_reference(env,20000)['site_revisit_s']
    trip=(interval-c.loading_s-c.phase_buffer_s)/2
    if trip<=0: raise ValueError('No time for payout and return')
    s=np.linspace(0,L,c.nodes);rfull=a+s
    density=c.cable_density_kg_m3*c.payload_kg*w*w*b/c.cable_allowable_pa*np.exp(
        c.cable_density_kg_m3*w*w*(b*b-rfull*rfull)/(2*c.cable_allowable_pa))
    # Full inventory always aboard. Material s=L is the distal tip, deployed first.
    moments=[cumulative_trapezoid(density*s**k,s,initial=0) for k in range(3)]
    cable_mass=moments[0][-1]
    def inventory(q,load):
        start=L-q
        ms=[f[-1]-np.interp(start,s,f) for f in moments]
        M0,M1,M2=ms;shift=a-start
        J1=shift*M0+M1
        I=2*((cable_mass-M0)*a*a+shift*shift*M0+2*shift*M1+M2+load*(a+q)**2)
        Ip=4*(J1+load*(a+q))
        Mr=2*(M0+load)
        Mrp=2*np.interp(start,s,density)
        return I,Ip,Mr,Mrp
    delta=(w*interval+np.pi)%(2*np.pi)-np.pi
    phase_area=-delta
    pieces=[]
    def add(name,t,q,qd,qdd,omega,alpha,load,loading_rate=0.):
        I,Ip,Mr,Mrp=inventory(q,load)
        # Wheel shaft torque about hub, including material angular momentum.
        torque=I*alpha+Ip*qd*omega+loading_rate*a*a*omega
        radial=(Mr*qdd+.5*Mrp*qd*qd-.5*Ip*omega*omega)*qd
        base_mass=2*cable_mass+2*load+c.fixed_hardware_kg
        torque+=c.fixed_hardware_kg*a*a*alpha
        f0=torque/a+c.rolling_coefficient*g*base_mass
        coeff=a*alpha+c.rolling_coefficient*g
        pieces.append(dict(name=name,t=t,q=q,qd=qd,omega=omega,alpha=alpha,
                           radial=radial,base_mass=base_mass,f0=f0,coeff=coeff,
                           inertia=I,radial_mass=Mr,load=load))
    n=c.time_nodes
    t=np.linspace(0,c.loading_s,n);z=np.zeros(n);o=np.ones(n)
    add('loading',t,z,z,z,w*o,z,c.payload_kg*t/c.loading_s,2*c.payload_kg/c.loading_s)
    for name,reverse,load in [('payout',False,c.payload_kg),('retraction',True,0.)]:
        t=np.linspace(0,trip,n);x=t/trip
        f=10*x**3-15*x**4+6*x**5
        fd=(30*x*x-60*x**3+30*x**4)/trip
        fdd=(60*x-180*x*x+120*x**3)/trip**2
        q=L*(1-f if reverse else f);qd=L*(-fd if reverse else fd);qdd=L*(-fdd if reverse else fdd)
        add(name,t,q,qd,qdd,w*np.ones(n),np.zeros(n),load*np.ones(n))
    t=np.linspace(0,c.phase_buffer_s,n);x=t/c.phase_buffer_s
    omega=w+2*phase_area/c.phase_buffer_s*np.sin(np.pi*x)**2
    alpha=2*phase_area*np.pi/c.phase_buffer_s**2*np.sin(2*np.pi*x)
    add('phase correction',t,np.zeros(n),np.zeros(n),np.zeros(n),omega,alpha,np.zeros(n))
    if max(np.max(p['omega'])*a for p in pieces)>35.76 or min(omega)<=0:
        return dict(inputs=asdict(c),status='phase wheel-speed constraint')
    # Solve both signed tangential traction inequalities for a SINGLE ballast
    # mass carried continuously, including ballast's phase angular acceleration.
    k=c.friction*c.driven_normal_fraction*g
    low=0.;high=np.inf
    for p in pieces:
        for sign in [1,-1]:
            coef=sign*p['coeff']-k
            rhs=k*p['base_mass']-sign*p['f0']
            positive=coef>1e-12;negative=coef< -1e-12
            if np.any(positive):high=min(high,float(np.min(rhs[positive]/coef[positive])))
            if np.any(negative):low=max(low,float(np.max(rhs[negative]/coef[negative])))
            if np.any((abs(coef)<=1e-12)&(rhs<0)): high=-1
    ballast=max(0,low)
    if ballast>high:
        return dict(inputs=asdict(c),status='no ballast satisfying traction and phase profile')
    summaries=[]; peak=0;energy=0; minmargin=np.inf
    maxforce=0; location=None
    for p in pieces:
        F=p['f0']+p['coeff']*ballast
        wheel=F*a*p['omega'];radial=p['radial']
        incoming=(np.maximum(wheel,0)+np.maximum(radial,0))/c.drive_efficiency
        generation=c.recovery_efficiency*(np.maximum(-wheel,0)+np.maximum(-radial,0))
        solar=np.maximum(incoming-generation,0)
        traction=k*(p['base_mass']+ballast)-abs(F)
        minmargin=min(minmargin,float(min(traction)))
        idx=int(np.argmax(abs(F)))
        if abs(F[idx])>maxforce:
            maxforce=abs(F[idx]);location=dict(phase=p['name'],phase_time_s=float(p['t'][idx]),deployed_fraction=float(p['q'][idx]/L))
        E=float(np.trapezoid(solar,p['t']));energy+=E;peak=max(peak,float(max(solar)))
        summaries.append(dict(phase=p['name'],duration_s=float(p['t'][-1]),
            peak_solar_w=float(max(solar)),solar_energy_j=E,
            peak_wheel_mechanical_w=float(max(wheel)),
            peak_radial_input_w=float(max(np.maximum(radial,0))),
            peak_radial_braking_w=float(max(np.maximum(-radial,0))),
            max_ground_tangential_n=float(max(abs(F)))))
        p.update(wheel=wheel,solar=solar,force=F)
    # Quasi-static small-slope clearance throughout deployment/retraction.
    # Unloaded free tip uses limiting slope g/(w²r_tip), not a fictitious tip mass.
    heights={}
    for name,load in [('loaded',c.payload_kg),('unloaded',0.)]:
        hmax=3.;qmax=0;maximum_slope=0.
        for q in np.linspace(L/300,L,300):
            ss=np.linspace(L-q,L,1001); rr=a+ss-(L-q)
            lam=np.interp(ss,s,density)
            m=cumulative_trapezoid(lam,ss,initial=0);j=cumulative_trapezoid(lam*rr,ss,initial=0)
            Tv=g*(load+m[-1]-m);Tr=w*w*(load*(a+q)+j[-1]-j)
            slope=np.divide(Tv,Tr,out=np.full_like(Tr,g/(w*w*(a+q))),where=Tr>0)
            maximum_slope=max(maximum_slope,float(np.max(slope)))
            sag=cumulative_trapezoid(slope,ss,initial=0)
            ground=np.sqrt(env.reference_radius_m**2-rr*rr)-env.reference_radius_m
            height=float(max(sag+ground)+3)
            if height>hmax:hmax=height;qmax=q/L
        heights[name]=dict(minimum_apex_height_m=hmax,at_deployed_fraction=qmax,maximum_small_slope=maximum_slope,small_slope_valid=maximum_slope<=.1)
    # Main-tie additional radial restraint to accelerate ballast around circle.
    out=dict(inputs=asdict(c),status='reduced-order cycle; structural/contact certification pending',
        interval_s=interval,omega_rad_s=w,wheel_release_speed_m_s=w*a,
        tip_radius_m=b,outward_cables_kg=2*cable_mass,ballast_total_kg=ballast,
        ballast_per_powered_wheel_kg=ballast/4,peak_solar_w=peak,
        solar_energy_j=energy,solar_mass_at_assumed_100_w_kg=peak/100,
        maximum_ground_tangential_n=maxforce,peak_traction_location=location,
        minimum_traction_margin_n=minmargin,
        phase_correction_rad=phase_area,
        extra_tie_tension_from_ballast_n=ballast/2*w*w*a,
        wheel_radial_acceleration_m_s2=w*w*a,
        phases=summaries,clearance=heights)
    if include_history:out['history']=pieces
    return out


def main():
    from dataclasses import replace
    cases=[]
    for acc,track in [(10,50),(30,50),(100,50),(300,50),(300,20)]:
        for passes in [1,2]:
            for recovery in [0,.7]:
                cases.append(run(PayoutCase(acceleration_g=acc,track_radius_m=track,passes=passes,recovery_efficiency=recovery)))
    # Friction uncertainty is a scenario, not a measured lunar high-speed value.
    friction=[run(PayoutCase(friction=mu)) for mu in [.3,.5,.7]]
    out=Path(__file__).parent/'results'
    (out/'spooling_cycle.json').write_text(json.dumps(dict(cases=cases,friction_sensitivity=friction),indent=2)+'\n')
    rows=['# Timed spooling cycle with cable mass','',
          'Conditional straight-cable dynamics; solar mass assumes 100 W/kg. Ballast is TOTAL local rock for both frames. Height values for 10 g and 30 g FAIL the small-slope validity check; those entire scenarios require a nonlinear shape recalculation.','',
          '| g | track m | passes | recovery | wheel m/s | height loaded / unloaded m | ballast t | solar MW | solar t |',
          '| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |']
    for r in cases:
        c=r['inputs']
        if 'ballast_total_kg' not in r:
            rows.append(f"| {c['acceleration_g']} | {c['track_radius_m']} | {c['passes']} | {c['recovery_efficiency']} | {r['status']} | — | — | — | — |")
        else:
            h=r['clearance']
            rows.append(f"| {c['acceleration_g']} | {c['track_radius_m']} | {c['passes']} | {c['recovery_efficiency']} | {r['wheel_release_speed_m_s']:.2f} | {h['loaded']['minimum_apex_height_m']:.2f} / {h['unloaded']['minimum_apex_height_m']:.2f} | {r['ballast_total_kg']/1000:.1f} | {r['peak_solar_w']/1e6:.2f} | {r['solar_mass_at_assumed_100_w_kg']/1000:.1f} |")
    (out/'spooling_cycle.md').write_text('\n'.join(rows)+'\n');print('\n'.join(rows))
if __name__=='__main__':main()
