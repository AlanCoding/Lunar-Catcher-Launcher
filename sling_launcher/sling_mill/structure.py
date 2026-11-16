"""Conditional force-based inventory. Contact shape is a small-deflection panel
screen, with explicit inward-only anchor reactions. A coupled moving-contact
string solution remains a feasibility gate, even when these screens pass.
"""
import numpy as np

MATERIALS = {'Kevlar 49': (1440.,3e9,112.4e9),
             'Zylon AS': (1540.,5.8e9,180e9), 'Zylon HM': (1560.,5.8e9,270e9)}

def cable_mass(load, p, h, omega, rho, allowable):
    """Constant-stress tapered straight cable, including own centrifugal mass.
    dT/ds=-rho*A*omega²*(r dot tangent); A=T/allowable.
    T(r)=T_tip*exp[rho*omega²*(R²-r²)/(2*allowable)].
    Fixed straight geometry needs transverse support for a non-radial cable;
    tangent-member result is an axial-load screen, not a shape solution.
    """
    z = np.linspace(0,1,81)
    points = h[None,:]+z[:,None]*(p-h)[None,:]
    length = np.linalg.norm(p-h)
    exponent = rho*omega[:,None]**2*(np.dot(p,p)-(points**2).sum(axis=1)[None,:])/(2*allowable)
    areas = load[:,None]/allowable*np.exp(exponent)
    return rho*length*np.trapezoid(areas,z,axis=1), areas[:,0], areas[:,-1]

def size(c, k, st):
    from geometry import geometry
    rho, strength, E = MATERIALS[c['material']]
    allow = strength*c['joint_efficiency']*c['environment_factor']/c['strength_safety_factor']
    R, h, n = c['radius'], c['radius']*c['hub_ratio'], c['attachments']
    u = st['rim_speed_m_s']; omega = u/R
    F = st['force_pair_peak_N']/2*c['dynamic_factor']
    normal = F/c['mu']+k['payload_mass_kg']*1.62/(2*k['interior_pairs'])
    span = 2*R*np.sin(np.pi/n); delta = c['belt_deflection_fraction']*R
    # Small-deflection centrifugal distributed-load + central contact load.
    self_stress = rho*omega**2*R*span**2/(8*delta)
    added_T = normal*span/(4*delta)
    strength_denominator = allow-self_stress
    invalid_strength = strength_denominator<=0
    A_strength = np.where(invalid_strength,np.nan,added_T/strength_denominator)
    torque_T = F*R/h/c['torque_members_effective']
    torque_radial = torque_T*np.sqrt(1-(h/R)**2)
    # Conservative contacted-anchor inward reaction: all panels carry peak T.
    reserve_per_area = rho*u*u*span/R-2*self_stress*np.sin(np.pi/n)
    needed = 2*added_T*np.sin(np.pi/n)+normal/2+torque_radial
    A_reserve = np.where(reserve_per_area>0,1.1*needed/reserve_per_area,np.nan)
    A = np.maximum(np.maximum(A_strength,A_reserve),c['minimum_belt_thickness']*c['belt_width'])
    T = self_stress*A+added_T
    # Off-contact radial anchors carry largest inward load; torque cable unloading
    # and contact unloading reduce it. Largest load sizes every radial member.
    radial_T = rho*A*u*u*span/R-2*T*np.sin(np.pi/n)
    contacted_reaction = radial_T-normal/2-torque_radial
    O,P,Q,H = geometry(R,h)
    mr, ar, art = cable_mass(radial_T,P,Q,omega,rho,allow)
    mt, at, att = cable_mass(torque_T,P,H,omega,rho,allow)
    # All attachments have a torque member, only k are assumed to share peak load.
    belt = 2*np.pi*R*A*rho
    radial = mr*n; torque = mt*n
    wall = np.maximum(c['hub_wall_min'],F*R/(2*np.pi*h*h*c['hub_shear_allowable']))
    hub = np.pi*(h*h-np.maximum(h-wall,0)**2)*c['belt_width']*c['hub_density']
    # Integrate inertia using exact tapered areas along each cable.
    z = np.linspace(0,1,81)
    def cable_inertia(load,anchor):
        pts=anchor[None,:]+z[:,None]*(P-anchor)[None,:]
        r2=(pts**2).sum(axis=1)
        area=load[:,None]/allow*np.exp(rho*omega[:,None]**2*(R*R-r2)/(2*allow))
        return rho*np.linalg.norm(P-anchor)*np.trapezoid(area*r2,z,axis=1)
    inertia = belt*R*R+n*(cable_inertia(radial_T,Q)+cable_inertia(torque_T,H))+.5*hub*(h*h+np.maximum(h-wall,0)**2)
    droop=c['storage_design_droop']
    I_required = st['energy_swing_pair_J']/(omega*omega*(2*droop-droop*droop))
    storage_extra = np.maximum(0,I_required-inertia)/R**2
    reserve_fraction=1-st['energy_swing_pair_J']/(inertia*omega**2)
    achieved_droop=np.where(reserve_fraction>=0,1-np.sqrt(np.maximum(0,reserve_fraction)),np.nan)
    # Extra inertia is only a lower bound; it must be structurally re-sized.
    motor_rating = st['motor_pair_peak_W'] if c['motor_supply_mode']=='contact_following' else st['motor_pair_mean_W']
    motor = motor_rating/1000*c['motor_efficiency']**-1*c['motor_kg_per_kw']
    bearings=2*np.hypot(normal,F)/1000*c['bearing_kg_per_kn']
    frame = (2*normal/c['frame_allowable'])*(4*R+c['payload_depth'])*c['frame_density']*c['frame_buckling_allowance']
    mechanical_mean=k['ideal_power_W']+k['slip_heat_W']
    electrical=mechanical_mean/c['motor_efficiency']
    machine_heat=k['slip_heat_W']*c['heat_to_belt_fraction']+electrical-mechanical_mean
    flux=c['emissivity']*5.670374419e-8*(c['radiator_temperature']**4-c['radiator_sink_temperature']**4)
    radiator_area=machine_heat/flux
    mass=dict(outer_belts=2*np.sum(belt),radial_cables=2*np.sum(radial),
              torque_cables=2*np.sum(torque),rigid_hubs=2*np.sum(hub),
              motors_and_drives=np.sum(motor),bearings=np.sum(bearings),
              station_frames=np.sum(frame),
              temporary_startup_supports=2*len(u)*c['startup_support_kg_per_drum'],
              foundations=len(u)*c['foundation_kg_per_pair'],
              guides=k['installed_length_m']*c['guide_kg_per_m'],
              cooling_equipment=radiator_area*c['radiator_kg_m2'])
    arrays=dict(belt_area_m2=A,belt_thickness_m=A/c['belt_width'],belt_stress_Pa=T/A,
                free_ring_stress_Pa=rho*u*u,radial_tip_tension_N=radial_T,
                torque_member_tip_tension_N=torque_T,radial_root_area_m2=ar,
                torque_root_area_m2=at,normal_per_drum_N=normal,
                contact_pressure_Pa=normal/(c['belt_width']*c['contact_patch']),
                contacted_anchor_reaction_N=contacted_reaction,
                inertia_per_drum_kg_m2=inertia,storage_inertia_required_kg_m2=I_required,
                constant_mean_motor_droop_fraction=achieved_droop,
                additional_storage_belt_lower_bound_kg=storage_extra,
                rotor_mass_per_drum_kg=belt+radial+torque+hub,
                rotor_energy_per_drum_J=.5*inertia*omega**2,
                payload_contact_duty=st['contact_duration_s']*k['launch_frequency_hz'],
                startup_unloaded_gravity_rim_speed_m_s=np.sqrt(1.62*R)*np.ones(len(u)))
    result=dict(working_stress_Pa=allow,electrical_mean_W=electrical,
                machine_waste_heat_W=machine_heat,radiator_area_m2=radiator_area,
                conditional_installed_mass_kg=float(sum(mass.values())),
                extra_storage_mass_lower_bound_kg=float(2*np.sum(storage_extra)),
                maximum_belt_thickness_m=float(np.max(A/c['belt_width'])),
                maximum_contact_pressure_Pa=float(np.max(arrays['contact_pressure_Pa'])),
                final_free_ring_stress_Pa=float(rho*u[-1]**2),
                peak_installed_motor_power_W=float(np.sum(motor_rating)/c['motor_efficiency']),
                hub_rim_speed_final_m_s=float(omega[-1]*h),
                hub_free_ring_stress_benchmark_Pa=float(c['hub_density']*(omega[-1]*h)**2))
    return result, arrays, mass
