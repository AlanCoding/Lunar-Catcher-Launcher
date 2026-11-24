"""Hypothesized compliant contact layer. No material product is qualified.
R is the operating outer radius; all formulas use the thin-layer limit.
"""
import numpy as np

def compliance(a):
    return a['coating_thickness_m']/a['coating_modulus_Pa']+a['backing_compliance_m_Pa']

def normal_force(delta,R,width,C):
    """Per-drum indentation delta; Winkler pressure over a parabolic gap."""
    delta=np.maximum(np.asarray(delta),0)
    return 4/3*width*np.sqrt(2*R)*delta**1.5/C

def indentation(N,R,width,C):
    return (3*np.asarray(N)*C/(4*width*np.sqrt(2*R)))**(2/3)

def screen(c,a,k,st):
    R,W,D=c['radius'],min(c['belt_width'],c['payload_width']),c['payload_depth']
    C=compliance(a); t=a['coating_thickness_m']; rho=a['coating_density_kg_m3']
    N=st['normal_per_drum_N']
    delta=indentation(N,R,W,C); patch=2*np.sqrt(2*R*delta)
    peak_pressure=delta/C
    # Free surface away from contact: no credit for payload contact compression.
    peel=rho*t*st['rim_speed_m_s']**2/R
    shear=c['mu']*peak_pressure
    bond_index=(peel/a['bond_tensile_allowable_Pa'])**2+(shear/a['bond_shear_allowable_Pa'])**2
    # Upper envelope combines maxima that can occur at different locations/phases.
    q=c['heat_to_belt_fraction']*shear*st['peak_sliding_speed_m_s']
    diffusivity=a['coating_conductivity_W_m_K']/(rho*a['coating_heat_capacity_J_kg_K'])
    residence=patch/st['rim_speed_m_s']
    depth=np.sqrt(diffusivity*residence)
    flash=2*q*np.sqrt(diffusivity*residence/np.pi)/a['coating_conductivity_W_m_K']
    heat_per_drum=st['energy_slip_J']*k['launch_frequency_hz']/2
    wear_volume_rate=a['wear_coefficient']*heat_per_drum/(c['mu']*a['wear_hardness_Pa'])
    wear_speed=wear_volume_rate/(2*np.pi*R*c['belt_width'])
    life=np.divide(t,wear_speed,out=np.full_like(wear_speed,np.inf),where=wear_speed>0)
    wear_mass_rate=2*rho*wear_volume_rate.sum()
    gap=D-2*delta
    tolerance=a['gap_setting_tolerance_m']
    dN_fraction=np.maximum(abs(normal_force(delta+tolerance/2,R,W,C)/N-1),abs(normal_force(delta-tolerance/2,R,W,C)/N-1))
    return dict(required_gap_m=gap,per_surface_indentation_m=delta,
                derived_contact_patch_m=patch,peak_pressure_Pa=peak_pressure,
                centrifugal_bond_traction_Pa=peel,sliding_shear_Pa=shear,
                mixed_bond_index=bond_index,flash_temperature_rise_K=flash,
                thermal_penetration_depth_m=depth,wear_life_s=life,
                traction_error_fraction=dN_fraction),dict(
                coating_mass_kg=2*len(N)*2*np.pi*R*c['belt_width']*rho*t,
                coating_bending_strain=t/(2*R),wear_mass_rate_kg_s=float(wear_mass_rate),
                minimum_wear_life_hours=float(life.min()/3600),
                minimum_required_gap_m=float(gap.min()),maximum_required_gap_m=float(gap.max()),
                maximum_peel_Pa=float(peel.max()),maximum_pressure_Pa=float(peak_pressure.max()),
                maximum_flash_rise_K=float(flash.max()),
                thermal_halfspace_applicable=bool(np.all(depth<t/3)))
