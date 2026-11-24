"""Blended tightness-driven closure. All local contacts are averaged; no bar events.
Belt is a prestressed string panel with a compliant layer in series. Result is a
reduced-model solution whose validity and engineering screens remain explicit.
"""
from pathlib import Path
import sys
import numpy as np
from scipy.optimize import brentq
from scipy.integrate import cumulative_trapezoid
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from structure import cable_mass
from geometry import geometry
RHO=1560.0  # Zylon HM; fixed material rather than an optimizer-controlled strength.

def contact(u,c):
    R,W=c['radius'],c['payload_width'];n=c['attachments']
    ell=2*R*np.sin(np.pi/n)
    A=W*c['structural_belt_thickness_m']
    linear_mass=RHO*A+c['coating_density']*W*c['coating_thickness_m']
    T=c['hoop_support_fraction']*linear_mass*u*u
    C=c['coating_thickness_m']/c['coating_modulus_Pa']
    coefficient=4/3*W*np.sqrt(2*R)/C
    def indentation_from_force(N):return (N/coefficient)**(2/3)+N*ell/(4*T)
    gravity_load=c['payload_density']*W*c['payload_depth']*R*c['pitch_over_radius']*1.62
    squeeze=c['total_squeeze_m']
    if indentation_from_force(gravity_load)>=squeeze:
        raise ValueError('Squeeze cannot maintain two-sided contact while supporting lunar weight')
    def residual(upper):return indentation_from_force(upper)+indentation_from_force(upper+gravity_load)-squeeze
    upper=brentq(residual,0,coefficient*squeeze**1.5,xtol=1e-10)
    lower=upper+gravity_load
    dc=((upper/coefficient)**(2/3)+(lower/coefficient)**(2/3))/2
    db=(upper+lower)/2*ell/(4*T)
    patch=2*np.sqrt(2*R*(lower/coefficient)**(2/3))
    return (upper+lower)/2,T,dc,db,patch,linear_mass,lower,upper

def solve(c):
    if not 0<c['hoop_support_fraction']<1:raise ValueError('Hoop fraction must lie between zero and one')
    if not 0<c['total_squeeze_m']<c['payload_depth']:raise ValueError('Positive squeeze smaller than payload depth is required')
    R,W,D,L=c['radius'],c['payload_width'],c['payload_depth'],c['payload_length']
    pitch=R*c['pitch_over_radius']; h=R*c['hub_ratio'];n=c['attachments']
    ell=2*R*np.sin(np.pi/n);A=W*c['structural_belt_thickness_m']
    bar_linear=c['payload_density']*W*D
    mdot=c['annual_mass_kg']/(c['operating_days']*86400)
    v=np.geomspace(c['v_entry'],c['v_exit'],c['velocity_grid_points'])
    mu=c['friction_coefficient']
    acceleration=lambda u:2*mu*contact(u,c)[0]/(bar_linear*pitch)
    def rim(vv):
        # Local smooth contact-window approximation: center -> trailing end = L/2.
        def residual(u):return u-(np.sqrt(vv*vv+acceleration(u)*L)+c['slip_margin_m_s'])/(1-c['speed_reserve_fraction'])
        high=max(2*vv,c['v_exit']*2)
        for _ in range(10):
            if residual(high)>0:return brentq(residual,vv,high)
            high*=2
        raise ValueError('No finite local rim-speed closure')
    u=np.array([rim(vv) for vv in v]);local=np.array([contact(uu,c) for uu in u])
    N,T,dc,db,patch,linearm,lower,upper=local.T
    a=2*mu*N/(bar_linear*pitch)
    x=cumulative_trapezoid(v/a,v,initial=0)
    transit=cumulative_trapezoid(1/a,v,initial=0)
    station_density=v/a/pitch  # d(number of pairs)/dv
    total=lambda z:float(np.trapezoid(z*station_density,v))
    occupancy=mdot/(bar_linear*v)
    pair_slip=2*mu*N*(u-v)*occupancy
    slip_power=total(pair_slip)
    kinetic_power=.5*mdot*(c['v_exit']**2-c['v_entry']**2)
    electrical=(kinetic_power+slip_power)/c['motor_efficiency']
    heat_per_drum=pair_slip/2*c['heat_to_roller_fraction']
    surface=2*np.pi*R*W
    radiation_coefficient=c['emissivity']*c['radiating_view_factor']*5.670374419e-8
    absorbed=c['external_absorbed_flux_W_m2']*surface
    temperature=(c['sink_temperature_K']**4+(heat_per_drum*lower/N+absorbed)/(radiation_coefficient*surface))**.25
    # Conservative steady conduction gradient if half the generated heat crosses layer.
    layer_gradient=heat_per_drum/surface*c['coating_thickness_m']/c['coating_conductivity_W_m_K']
    radial=linearm*u*u*ell/R-2*T*np.sin(np.pi/n)
    # Peak contact traction drives the torque load path, independent of motor averaging.
    # Omission is an intentionally unphysical sensitivity diagnostic, never a design option.
    drive_force=np.zeros_like(lower) if c.get('diagnostic_omit_drive_torque',False) else mu*lower
    drive_torque=drive_force*R
    torque_tip=drive_torque/(h*c['torque_members_effective'])
    # One-sided bound: the belt transmits the whole contact traction toward one anchor.
    # Nominal tension still defines the reduced contact-compliance approximation.
    traction_increment=drive_force if c.get('include_belt_traction_envelope',False) else np.zeros_like(lower)
    peak_belt_T=T+traction_increment
    minimum_reaction=radial-lower/2-torque_tip*np.sqrt(1-c['hub_ratio']**2)-2*traction_increment*np.sin(np.pi/n)
    O,P,Q,H=geometry(R,h)
    mr,radial_root_area,radial_tip_area=cable_mass(radial,P,Q,u/R,RHO,c['working_stress_Pa'])
    mt,torque_root_area,torque_tip_area=cable_mass(torque_tip,P,H,u/R,RHO,c['working_stress_Pa'])
    wall=np.maximum(c['hub_wall_min_m'],drive_torque/(2*np.pi*h*h*c['hub_shear_allowable_Pa']))
    if c.get('hub_bending_enabled',False):
        # Simply supported hollow hub/shaft spanning the belt width; concentrated
        # resultant contact load is conservative relative to an even axial load.
        load=np.hypot(lower,drive_force)
        I_bending=load*W**3/(48*c['hub_modulus_Pa']*c['hub_deflection_limit_m'])
        I_torsion=drive_torque*h/(2*c['hub_shear_allowable_Pa'])
        I_min=np.pi/4*(h**4-max(h-c['hub_wall_min_m'],0)**4)
        I_required=np.maximum(np.maximum(I_bending,I_torsion),I_min)
        I_solid=np.pi*h**4/4
        inner=np.maximum(h**4-4*I_required/np.pi,0)**.25
        wall=h-inner
        I_actual=np.pi/4*(h**4-inner**4)
        hub_deflection=load*W**3/(48*c['hub_modulus_Pa']*I_actual)
        hub_solid_demand=I_required/I_solid
    hub=np.pi*(h*h-np.maximum(h-wall,0)**2)*W*c['hub_density']
    pair_peak=2*mu*N*u;pair_mean=pair_peak*occupancy
    rating=(pair_mean+c['motor_pulse_fraction']*(pair_peak-pair_mean))/c['motor_efficiency']
    drive_heat=electrical-kinetic_power-slip_power
    radiator_flux=radiation_coefficient*(c['motor_radiator_temperature_K']**4-c['sink_temperature_K']**4)
    masses=dict(structural_belts=total(np.full_like(v,4*np.pi*R*A*RHO)),
        contact_layers=total(np.full_like(v,4*np.pi*R*W*c['coating_thickness_m']*c['coating_density'])),
        radial_members=total(2*n*mr),torque_members=total(2*n*mt),hubs=total(2*hub),
        motors=total(rating)/1000*c['motor_kg_per_kW'],
        bearings=total(2*np.hypot(N,mu*N))/1000*c['bearing_kg_per_kN'],
        frames=total(2*N/c['frame_allowable_Pa']*(4*R+D)*c['frame_density']*c['frame_allowance']),
        foundations=x[-1]/pitch*c['foundation_kg_per_pair'],
        startup_supports=2*x[-1]/pitch*c['startup_kg_per_drum'],
        guides=x[-1]*c['guide_kg_per_m'],motor_radiators=drive_heat/radiator_flux*c['radiator_kg_m2'])
    # Smoothed rectangular contact-load energy budget, no phase-resolved rotor simulation.
    z=np.linspace(0,1,65)
    def inertia_cable(load,anchor):
        points=anchor[None,:]+z[:,None]*(P-anchor)[None,:];r2=(points*points).sum(axis=1)
        area=load[:,None]/c['working_stress_Pa']*np.exp(RHO*(u/R)[:,None]**2*(R*R-r2)/(2*c['working_stress_Pa']))
        return RHO*np.linalg.norm(P-anchor)*np.trapezoid(area*r2,z,axis=1)
    I=(2*np.pi*R*linearm)*R*R+n*(inertia_cable(radial,Q)+inertia_cable(torque_tip,H))+.5*hub*(h*h+np.maximum(h-wall,0)**2)
    deficit=(1-c['motor_pulse_fraction'])*(pair_peak-pair_mean)/2*L/v
    energy_fraction=2*deficit/(I*(u/R)**2)
    droop=1-np.sqrt(np.maximum(0,1-energy_fraction))
    pressure=(lower/(4/3*W*np.sqrt(2*R)/(c['coating_thickness_m']/c['coating_modulus_Pa'])))**(2/3)/(c['coating_thickness_m']/c['coating_modulus_Pa'])
    peel=c['coating_density']*c['coating_thickness_m']*u*u/R
    bond=np.sqrt((peel/c['bond_tensile_allowable_Pa'])**2+(mu*pressure/c['bond_shear_allowable_Pa'])**2)
    scallop=ell*ell/(8*R)*(1/c['hoop_support_fraction']-1)
    checks=dict(entrance_occupancy=float(occupancy.max()/c.get('maximum_occupancy',.8)-1),
        belt_stress=float(np.max(peak_belt_T/A)/c['working_stress_Pa']-1),
        support_reaction=float(-minimum_reaction.min()/max(1,N.max())),
        average_layer_temperature=float(temperature.max()/c['coating_temperature_limit_K']-1),
        bond_envelope=float(bond.max()-1),
        drum_clearance=(2*R+.02)/pitch-1,
        panel_deflection=float((scallop+db.max())/R/.02-1),
        local_speed_window=float(np.max(a*L/v**2)/.1-1),
        gravity_support=float(-upper.min()/max(1,lower.max())),
        stored_energy_fraction=float(energy_fraction.max()-1),
        speed_reserve=float(droop.max()-c['speed_reserve_fraction']),
        contact_smaller_than_panel=float(patch.max()/ell-1),
        thin_panel_string=float(c['structural_belt_thickness_m']/ell/.1-1))
    if c.get('hub_bending_enabled',False):
        checks['hub_solid_capacity']=float(hub_solid_demand.max()-1)
        checks['hub_deflection']=float(hub_deflection.max()/c['hub_deflection_limit_m']-1)
    summary=dict(annual_mass_kg=c['annual_mass_kg'],mass_flow_kg_s=mdot,
        feed_capacity_kg_s=c.get('maximum_occupancy',.8)*bar_linear*c['v_entry'],payload_mass_kg=bar_linear*L,
        launch_frequency_Hz=mdot/(bar_linear*L),
        acceleration_entry_m_s2=float(a[0]),acceleration_exit_m_s2=float(a[-1]),
        corridor_length_m=float(x[-1]),equivalent_pairs=float(x[-1]/pitch),transit_s=float(transit[-1]),
        ideal_kinetic_power_W=kinetic_power,slip_heat_W=slip_power,electrical_mean_W=electrical,
        bar_heating_W=slip_power*(1-c['heat_to_roller_fraction']),roller_heating_W=slip_power*c['heat_to_roller_fraction'],
        bar_bulk_temperature_rise_K=slip_power*(1-c['heat_to_roller_fraction'])/(mdot*c['payload_heat_capacity']),
        maximum_average_roller_temperature_K=float(temperature.max()),
        maximum_belt_stress_Pa=float((peak_belt_T/A).max()),working_stress_utilization=float((peak_belt_T/A).max()/c['working_stress_Pa']),
        conditional_machine_mass_kg=float(sum(masses.values())),gross_operating_payback_hours=float(sum(masses.values())/mdot/3600),
        max_contact_residual_m=float(np.max(abs(dc+db-c['total_squeeze_m']/2))),
        energy_error_fraction=float((total(2*mu*N*v*occupancy)-kinetic_power)/kinetic_power),
        constraint_residuals=checks,reduced_screen_pass=bool(all(val<=1e-8 for val in checks.values())),
        qualified_design=False)
    arrays=dict(v_m_s=v,rim_speed_m_s=u,x_m=x,acceleration_m_s2=a,
        normal_force_per_drum_N=N,lower_normal_force_N=lower,upper_normal_force_N=upper,coating_indentation_m=dc,belt_deflection_m=db,
        contact_patch_m=patch,belt_tension_N=T,belt_stress_Pa=peak_belt_T/A,nominal_belt_stress_Pa=T/A,
        peak_belt_tension_N=peak_belt_T,drive_force_per_drum_N=drive_force,drive_torque_per_drum_Nm=drive_torque,
        torque_member_rim_tension_N=torque_tip,radial_member_tip_area_m2=radial_tip_area,radial_member_root_area_m2=radial_root_area,
        torque_member_tip_area_m2=torque_tip_area,torque_member_root_area_m2=torque_root_area,
        member_taper_area_ratio=np.exp(RHO*(u/R)**2*(R*R-h*h)/(2*c['working_stress_Pa'])),
        occupancy=occupancy,slip_heat_per_pair_W=pair_slip,roller_temperature_K=temperature,
        layer_gradient_screen_K=layer_gradient,minimum_anchor_reaction_N=minimum_reaction,
        peak_contact_pressure_Pa=pressure,bond_index=bond,estimated_droop=droop)
    if c.get('hub_bending_enabled',False):
        arrays.update(hub_wall_m=wall,hub_deflection_m=hub_deflection,hub_solid_capacity_utilization=hub_solid_demand)
    return summary,arrays,{k:float(val) for k,val in masses.items()}
