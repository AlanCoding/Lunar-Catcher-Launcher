"""Couple pole/wheel/drive estimates back to mass, traction, phase and power.

Component curves are best-effort analogs. Output distinguishes a converged
conditional budget from a design satisfying geometry/contact/life constraints.
"""
from dataclasses import asdict
import numpy as np
from scipy.optimize import brentq
from .environment import LunarEnvironment
from .component_sizing import HardwareAssumptions,wheel,drive,pole,reel


def cross_track_tie(radius,omega,endpoint_force,stress,rho=1450.,gravity=1.6229):
    """Aggregate diametral fiber with self-inertia; short end bridles separate.

    Horizontal stress uses 99.9% of allowance to leave sag-force headroom.
    Two parallel half-load ties have the same aggregate fiber mass/inertia.
    """
    sh=.999*stress
    x=np.linspace(0,radius,401)
    tension=endpoint_force*np.exp(rho*omega**2*(radius**2-x**2)/(2*sh))
    density=rho*tension/sh
    return dict(mass_kg=2*float(np.trapezoid(density,x)),
                inertia_kg_m2=2*float(np.trapezoid(density*x*x,x)),
                endpoint_force_n=endpoint_force,center_tension_n=float(tension[0]),
                sag_m=rho*gravity*radius**2/(2*sh))


def evaluate(base,geo,c=HardwareAssumptions(),max_iterations=120,radial_policy='split'):
    # upper_only preserves the historical report; split is the current design.
    if radial_policy not in ['upper_only','split']:raise ValueError('Unknown radial policy')
    env=LunarEnvironment();g=env.surface_gravity_m_s2
    cable,branches,clearance,orbit=geo
    a=cable.radius;omega=cable.omega;speed=a*omega;ar=omega*omega*a
    pieces=base['history'];inputs=base['inputs'];mu=inputs['friction'];frac=inputs['driven_fraction'];roll=inputs['rolling'];eta=inputs['drive_efficiency']
    split=radial_policy=='split'
    threshold=speed**2/(mu*g)
    use_low_tie=bool(split and a<=threshold)
    effective_mu=mu
    k=mu*frac*g
    tie_inertia_correction=0.
    core_force=max(float(np.hypot(p['tr'][0],p['tv'][0])) for b in branches for p in b['shapes'])
    tie_base_endpoint=max(float(sh['tr'][0]+(cable.mass-sh['deployed_mass'])*ar) for b in branches for sh in b['shapes'])
    drum=reel(cable.mass,float(np.sqrt(4*max(cable.lam)/1450/np.pi)),core_force,c)
    # Four identical principal poles in two pairs; additional hardware is split
    # into apex and near-axle masses so self-weight and moment credit are visible.
    moving=100000.;ground_hardware=60000.;apex_hardware=40000.;wheel_mass=20000.;pole_mass=0.
    last=None;trace=[];failure=None;first_poles=None
    for iteration in range(max_iterations):
        low=0.;upper=np.inf
        for p in pieces:
            f0=p['torque']/a+(moving+wheel_mass+tie_inertia_correction)*a*p['alpha']+roll*g*(p['base_mass']+moving)
            coef=a*p['alpha']+roll*g
            for sign in [-1,1]:
                coeff=sign*coef-k;rhs=k*(p['base_mass']+moving)-sign*f0
                neg=coeff< -1e-12;pos=coeff>1e-12
                if np.any(neg):low=max(low,float(np.max(rhs[neg]/coeff[neg])))
                if np.any(pos):upper=min(upper,float(np.min(rhs[pos]/coeff[pos])))
        ballast=max(0.,low)
        if split and not use_low_tie:
            def road_margin(B):
                margin=np.inf
                for p in pieces:
                    mass=p['base_mass']+moving+B
                    tang=p['torque']/a+(moving+wheel_mass+tie_inertia_correction+B)*a*p['alpha']+roll*g*mass
                    # Only lower hardware, ballast and lower pole reactions.
                    # Payload/counterweight/cable radial force is absent.
                    rad=(ground_hardware+B+.5*pole_mass)*a*p['omega']**2
                    capacity=frac*np.sqrt(np.maximum((mu*g*mass)**2-rad**2,0.))
                    margin=min(margin,float(np.min(capacity-abs(tang))))
                return margin
            if road_margin(ballast)<0:
                hi=max(1.,2*ballast)
                while road_margin(hi)<0 and hi<1e12:hi*=2
                if road_margin(hi)<0:
                    failure='combined road grip could not be bracketed for this cycle';break
                ballast=brentq(road_margin,ballast,hi,xtol=1e-6)
        if ballast>upper:failure='no traction solution for the selected phase history';break
        gross=2*cable.mass+2*inputs['payload_kg']+moving+ballast
        normal=gross*g
        wd=wheel(normal*frac/4,speed,c);wp=wheel(normal*(1-frac)/4,speed,c)
        wheel_new=4*(wd['mass_kg']+wp['mass_kg'])
        apex_height=max(clearance,wd['diameter_m']+drum['outer_radius_m']+.5)
        length=apex_height-wd['radius_m']
        # Envelope of cable/apex tangential forces, not the ballast radial force.
        tangential=max(float(max(abs(p['torque']/a+apex_hardware*a*p['alpha'])))/2 for p in pieces)
        vertical=g*(cable.mass+inputs['payload_kg']+apex_hardware/2)
        ground_total=ballast+ground_hardware
        radial_per_leg=0. if split else ground_total*ar/4
        vertical_pole=pole(length,vertical+tangential,radial_per_leg,ar,0.,g,c,radial_both_ends=split)
        trailing_pole=pole(np.sqrt(2)*length,np.sqrt(2)*tangential,radial_per_leg,ar,np.pi/4,g,c,radial_both_ends=split)
        pole_new=2*(vertical_pole['mass_with_joints_kg']+trailing_pole['mass_with_joints_kg'])
        peak_wheel=peak_reel=peak_solar=peak_heat=peak_torque=0.;max_qdot=0.;cycle_energy=0.;traction_margin=np.inf
        phase_summary=[];history=[]
        for p in pieces:
            physical_mass=p['base_mass']+moving+ballast
            force=p['torque']/a+(moving+wheel_mass+ballast+tie_inertia_correction)*a*p['alpha']+roll*g*physical_mass
            pw=force*a*p['omega']
            radial=p['radial'].copy()
            if p['name'] in ['payout','retraction']:
                qdot=cable.length*np.gradient(p['f'],p['t'],edge_order=2)
                stored=np.array([cable.mass-b['deployed_mass'] for b in branches[0]['shapes']])
                mass_stored=np.interp(p['f'],branches[0]['f'],stored)
                # Both capstan/storage rotors and cable wound on storage drums.
                spin_energy=drum['rotor_inertia_kg_m2']*(qdot/drum['core_radius_m'])**2
                spin_energy+=mass_stored*.5*(drum['core_radius_m']**2+drum['outer_radius_m']**2)*(qdot/drum['outer_radius_m'])**2
                radial+=np.gradient(spin_energy,p['t'],edge_order=2)
                max_qdot=max(max_qdot,float(max(abs(qdot))))
            positive=np.maximum(pw,0)+np.maximum(radial,0);negative=np.maximum(-pw,0)+np.maximum(-radial,0)
            incoming=positive/eta;generation=c.recovery*negative
            solar=np.maximum(incoming-generation,0)
            # Conversion/drive losses + unused regeneration, with no storage.
            heat=(incoming-positive)+(1-c.recovery)*negative+np.maximum(generation-incoming,0)
            peak_wheel=max(peak_wheel,float(max(abs(pw))));peak_reel=max(peak_reel,float(max(abs(radial))))
            peak_torque=max(peak_torque,float(max(abs(force)))*wd['radius_m']/4)
            peak_solar=max(peak_solar,float(max(solar)));peak_heat=max(peak_heat,float(max(heat)))
            capacity=k*physical_mass
            if split and not use_low_tie:
                rad=(ground_hardware+ballast+.5*pole_mass)*a*p['omega']**2
                capacity=frac*np.sqrt(np.maximum((mu*g*physical_mass)**2-rad**2,0.))
                effective_mu=min(effective_mu,float(np.min(capacity/(frac*g*physical_mass))))
            traction_margin=min(traction_margin,float(min(capacity-abs(force))))
            cycle_energy+=float(np.trapezoid(solar,p['t']))
            phase_summary.append(dict(phase=p['name'],wheel_peak_abs_w=float(max(abs(pw))),reel_peak_abs_w=float(max(abs(radial))),solar_peak_w=float(max(solar)),heat_peak_w=float(max(heat))))
            history.append(dict(phase=p['name'],t=p['t'],wheel=pw,reel=radial,solar=solar,heat=heat))
        wheel_drive=drive(peak_wheel/4,peak_torque,speed/wd['radius_m'],c)
        reel_drive=drive(peak_reel/2,drum['holding_torque_nm'],max_qdot/drum['core_radius_m'],c)
        # Itemized conceptual allowances, not supplier ratings.
        steering=.1*4*wp['mass_kg']
        retention=ballast*np.hypot(g,ar)*2/(c.steel_yield_pa)*c.steel_density*max(1.,wd['diameter_m'])
        retention=max(retention,.005*ballast) # local containers/fasteners mass floor
        fittings=.10*2*cable.mass
        tie_end=tie_base_endpoint+((apex_hardware+.5*pole_new) if split else (moving+ballast))*ar/2
        xx=np.linspace(0,a,401);tieT=tie_end*np.exp(1450*omega*omega*(a*a-xx*xx)/(2*inputs['stress_pa']))
        tie=2*float(np.trapezoid(1450*tieT/inputs['stress_pa'],xx))
        low_tie=dict(mass_kg=0.,inertia_kg_m2=0.,endpoint_force_n=0.,center_tension_n=0.,sag_m=0.)
        upper_tie_inertia=0.;low_fittings=upper_fittings=0.
        if split:
            high_tie=cross_track_tie(a,omega,tie_end,inputs['stress_pa'],gravity=g)
            tie=high_tie['mass_kg'];upper_tie_inertia=high_tie['inertia_kg_m2']
            if use_low_tie:
                low_tie=cross_track_tie(a,omega,(ground_total+.5*pole_new)*ar/2,inputs['stress_pa'],gravity=g)
            low_fittings=.1*low_tie['mass_kg'];upper_fittings=.1*tie
        controls=c.controls_fraction*(wheel_new+4*wheel_drive['mass_kg']+2*reel_drive['mass_kg'])
        ground_new=wheel_new+4*wheel_drive['mass_kg']+steering+retention+controls/2+low_fittings
        apex_new=2*(drum['mass_kg']+reel_drive['mass_kg'])+fittings+(upper_fittings if split else tie)+controls/2
        moving_new=ground_new+apex_new+pole_new+(tie+low_tie['mass_kg'] if split else 0.)
        flux=c.radiator_emissivity*5.670374419e-8*(c.radiator_temp_k**4-c.radiator_sink_k**4)*c.radiator_view_factor
        radiator_area=peak_heat/flux
        radiator=radiator_area*c.radiator_kg_m2*(1+c.thermal_transport_fraction)
        solar=peak_solar/c.solar_w_kg
        imported=moving_new+2*cable.mass+solar+radiator
        tip_shift=apex_height-clearance
        # Force moment diagnostic uses actual vertical distribution, not the old
        # assumption that every gram sits at ground level.
        height_arm=max(0.,apex_height-(wd['radius_m']+.5))
        tipping_moment=ar/2*(ground_total*height_arm+pole_new*length/2)
        needed_lever=tipping_moment/(normal/2)
        available_lever=wd['width_m']/2+length*length/(4*a)
        chord_fit=length<2*a
        drum_fit=drum['outer_radius_m']<a
        wheels_fit=2*(wd['radius_m']+wp['radius_m'])<np.pi*a
        section_fit=all(p['plate_thickness_within_source'] and p['slender_beam'] for p in [vertical_pole,trailing_pole])
        # Lower/upper poles carry a declared reaction envelope. The free wheeled
        # supports are not silently replaced by fixed foundations.
        flags=[]
        if not chord_fit:flags.append('45-degree leg cannot fit track chord')
        if not drum_fit:flags.append('opposing reel envelopes overlap')
        if not wheels_fit:flags.append('fore/aft wheel envelopes exceed half-track arc')
        if not section_fit:flags.append('pole section exceeds source plate/beam domain')
        if not split and needed_lever>available_lever:flags.append('radial contact moment needs additional stabilizing reaction')
        if wd['extrapolated'] or wp['extrapolated']:flags.append('wheel diameter extrapolated beyond manufacturer anchors')
        if split and use_low_tie and low_tie['sag_m']>=wd['radius_m']+.5:flags.append('low tie ground clearance needs routing adjustment')
        flags+=['50/80 mph lunar wheel qualification unresolved','release transient unresolved','equal-radius rock disposal unresolved']
        residual=abs(moving_new-moving)/max(moving_new,1.)
        last=dict(assumptions=asdict(c),acceleration_g=inputs['acceleration_g'],rover_mph=inputs['rover_mph'],passes=inputs['passes'],
          converged=False,iterations=iteration+1,fixed_point_relative_residual=residual,
          track_radius_m=a,release_radius_m=cable.tip_radius,clearance_height_m=clearance,apex_height_m=apex_height,
          pole_legs=[dict(id='frame_A_vertical',**vertical_pole),dict(id='frame_A_trailing',**trailing_pole),
                     dict(id='frame_B_vertical',**vertical_pole),dict(id='frame_B_trailing',**trailing_pole)],
          powered_wheel=wd,passive_wheel=wp,wheel_drive=wheel_drive,reel_drive=reel_drive,reel=drum,
          masses_kg=dict(poles=pole_new,wheels=wheel_new,wheel_motors=4*wheel_drive['motor_kg'],
            wheel_inverters=4*wheel_drive['inverter_kg'],wheel_gearboxes=4*wheel_drive['gearbox_kg'],
            reel_motors=2*reel_drive['motor_kg'],reel_inverters=2*reel_drive['inverter_kg'],reel_gearboxes=2*reel_drive['gearbox_kg'],
            reel_mechanical=2*drum['mass_kg'],steering=steering,retention=retention,fittings_sheath=fittings,
            main_tie=tie,low_tie=low_tie['mass_kg'],tie_end_fittings=low_fittings+upper_fittings,controls=controls,outward_cables=2*cable.mass,solar=solar,thermal=radiator,
            central_pivot_and_stabilizers=0.,ballast_local=ballast),
          imported_total_kg=imported,permanent_physical_total_kg=imported+ballast,
          imported_ratio=imported/inputs['payload_kg'],physical_ratio=(imported+ballast)/inputs['payload_kg'],
          moving_hardware_kg=moving_new,ballast_kg=ballast,
          peak_solar_w=peak_solar,peak_heat_w=peak_heat,radiator_area_m2=radiator_area,radiator_net_flux_w_m2=flux,
          solar_cycle_energy_j=cycle_energy,minimum_traction_margin_n=traction_margin,
          radial_policy=radial_policy,low_tie_used=use_low_tie,
          road_only_radius_threshold_m=threshold,effective_tangential_friction=effective_mu,
          low_tie=low_tie,upper_tie_endpoint_force_n=tie_end,
          low_tie_attachment_height_m=wd['radius_m']+.5,
          apex_radial_restraint_per_frame_n=((apex_hardware+.5*pole_new) if split else (moving+ballast))*ar/2,
          pole_ground_radial_force_each_n=radial_per_leg,frame_apex_tangential_n=tangential,
          tipping_moment_per_frame_nm=None if split else tipping_moment,required_support_lever_m=None if split else needed_lever,available_support_lever_m=None if split else available_lever,
          missing_stabilizing_moment_nm=None if split else max(0.,tipping_moment-normal/2*available_lever),
          frame_chord_fits=bool(chord_fit),reel_envelopes_fit=bool(drum_fit),wheel_envelopes_fit=bool(wheels_fit),
          pole_source_domain_ok=bool(section_fit),height_increase_m=tip_shift,
          orbit_speed_fractional_error_estimate=abs(tip_shift)/env.reference_radius_m,
          flags=flags,phases=phase_summary)
        if first_poles is None:first_poles=last['pole_legs']
        trace.append(dict(iteration=iteration+1,moving_hardware_kg=moving_new,ballast_kg=ballast))
        if residual<2e-5:
            last['converged']=True;break
        if moving_new>1e9 or not np.isfinite(moving_new):
            failure='hardware self-mass feedback exceeds 1 billion kg; no closed design';break
        # Under-relax a geometry/mass fixed point. No damping hides divergence.
        if split:
            correction=(upper_tie_inertia+low_tie['inertia_kg_m2'])/a**2-tie-low_tie['mass_kg']
            tie_inertia_correction=.5*tie_inertia_correction+.5*correction
        moving=.5*moving+.5*moving_new
        ground_hardware=.5*ground_hardware+.5*ground_new;apex_hardware=.5*apex_hardware+.5*apex_new
        wheel_mass=.5*wheel_mass+.5*wheel_new;pole_mass=pole_new
    if last is None:return dict(acceleration_g=inputs['acceleration_g'],rover_mph=inputs['rover_mph'],passes=inputs['passes'],assumptions=asdict(c),converged=False,failure=failure)
    if not last['converged']:
        last['failure']=failure or 'hardware mass fixed point did not converge'
        last['last_iterate_imported_ratio']=last.pop('imported_ratio');last['last_iterate_physical_ratio']=last.pop('physical_ratio')
        last['imported_ratio']=None;last['physical_ratio']=None
        last['last_iterate_imported_total_kg']=last.pop('imported_total_kg')
        last['last_iterate_physical_total_kg']=last.pop('permanent_physical_total_kg')
        last['imported_total_kg']=None;last['permanent_physical_total_kg']=None
    last['initial_load_pole_estimates']=first_poles
    last['iteration_trace']=trace
    last['feasible_design']=False # contact, environment and release not validated
    return last
