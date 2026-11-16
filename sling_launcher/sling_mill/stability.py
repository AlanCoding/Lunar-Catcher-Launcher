"""Load-path and rigid-body perturbation screens, not closed-loop validation."""
import numpy as np

def screen(c,k,st):
    L,W,D,s=c['payload_length'],c['payload_width'],c['payload_depth'],c['pitch']
    m=k['payload_mass_kg']; E=c['payload_modulus']; a=c['acceleration']
    Iv=W*D**3/12; Il=D*W**3/12
    # Conservative acceleration transmitted from a single end.
    axial=m*a/(W*D)
    buckling=np.pi**2*E*min(Iv,Il)/s**2
    imbalance=st['normal_per_drum_N'].max()*c['normal_mismatch_fraction']
    bend_stress=imbalance*s/4*(D/2)/Iv
    gravity_deflection=5*(m/L*1.62)*s**4/(384*E*Iv)
    Ix=m*(W*W+D*D)/12
    Iz=m*(L*L+W*W)/12; Iy=m*(L*L+D*D)/12
    tau_pitch=m*a*c['traction_mismatch_fraction']*D/2
    tau_yaw=m*a*c['misalignment_radians']*L/2
    time=s/c['v_entry']
    return dict(payload_roll_inertia_kg_m2=Ix,payload_pitch_inertia_kg_m2=Iy,payload_yaw_inertia_kg_m2=Iz,
                uncontrolled_roll_one_entry_pitch_rad=.5*(imbalance*W/2)/Ix*time*time,
                axial_end_loaded_stress_Pa=axial,payload_allowable_Pa=c['payload_allowable'],
                buckling_load_N=buckling,conservative_compression_N=m*a,
                payload_bending_stress_from_mismatch_Pa=bend_stress,
                gravity_span_deflection_m=gravity_deflection,
                vertical_acceleration_from_one_pair_mismatch_m_s2=imbalance/m,
                vertical_drift_one_entry_pitch_m=.5*imbalance/m*time*time,
                uncontrolled_pitch_one_entry_pitch_rad=.5*tau_pitch/Iy*time*time,
                uncontrolled_yaw_one_entry_pitch_rad=.5*tau_yaw/Iz*time*time,
                lateral_guide_force_N=m*a*c['misalignment_radians'],
                injection_kinetic_power_W=.5*k['mass_flow_kg_s']*c['v_entry']**2,
                payload_bulk_temperature_rise_K=(1-c['heat_to_belt_fraction'])*k['slip_heat_W']/k['mass_flow_kg_s']/c['payload_heat_capacity'])
