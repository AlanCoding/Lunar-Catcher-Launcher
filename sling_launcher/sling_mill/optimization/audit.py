"""Solver-facing objective/residual contract; no feasible optimum is asserted.
Run this local audit before enabling optimization over the incomplete model.
"""
import sys,json,csv
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from run import compute
from contact import screen

def audit(c,a):
    c=dict(c,coating_density=a['coating_density_kg_m3'],coating_thickness=a['coating_thickness_m'])
    r,st,mass=compute(c)
    arrays,contact=screen(c,a,r,st)
    residuals={
        'entrance_occupancy':r['entry_occupancy']/.8-1,
        'launch_frequency':r['launch_frequency_hz']/a['maximum_launch_frequency_Hz']-1,
        'drum_clearance':(2*c['radius']+a['minimum_drum_clearance_m'])/c['pitch']-1,
        'station_count':r['installed_pairs']/a['maximum_station_count']-1,
        'corridor_length':r['installed_length_m']/a['maximum_corridor_length_m']-1,
        'rpm':float(st['rpm'].max()/a['maximum_rpm']-1),
        'thin_belt_model':r['maximum_belt_thickness_m']/(a['maximum_belt_thickness_radius_ratio']*c['radius'])-1,
        'belt_strength':float(np.max(st['belt_stress_Pa'])/r['working_stress_Pa']-1),
        'contact_compression':contact['maximum_pressure_Pa']/a['coating_compressive_allowable_Pa']-1,
        'adhesive_load_envelope':float(np.sqrt(arrays['mixed_bond_index'].max())-1),
        'coating_bending':contact['coating_bending_strain']/a['coating_cyclic_strain_allowable']-1,
        'total_interference':float(2*arrays['per_surface_indentation_m'].max()/(c['payload_depth']*a['maximum_total_interference_fraction'])-1),
        'gap_tolerance':float(arrays['traction_error_fraction'].max()/a['allowable_traction_error_fraction']-1),
        'thermal_flash_screen':(a['belt_bulk_temperature_K']+contact['maximum_flash_rise_K'])/a['coating_temperature_limit_K']-1,
        'wear_service_interval':a['replacement_interval_hours']/contact['minimum_wear_life_hours']-1,
        'payload_axial':r['stability']['axial_end_loaded_stress_Pa']/c['payload_allowable']-1,
        'payload_buckling':r['stability']['conservative_compression_N']/r['stability']['buckling_load_N']-1,
        # The old prescribed patch and new derived patch must be reconciled first.
        'contact_patch_closure':float(np.max(np.abs(arrays['derived_contact_patch_m']/c['contact_patch']-1))/.05-1),
    }
    radial=st['contacted_anchor_reaction_N']
    residuals['inward_only_support']=float(-radial.min()/max(1,st['normal_per_drum_N'].max()))
    if c['motor_supply_mode']=='constant_mean':
        residuals['rotor_speed_headroom']=float(np.max(st['constant_mean_motor_droop_fraction'])-c['speed_droop'])
    mass['contact_layer_spares']=contact['wear_mass_rate_kg_s']*a['wear_stock_hours']*3600
    machine=sum(mass.values())
    duty=c['operating_days']/365
    useful_rate=a['successful_delivery_fraction']*r['mass_flow_kg_s']
    net=useful_rate-contact['wear_mass_rate_kg_s']
    extended=None
    if a['power_system_specific_mass_kg_W'] is not None and a['injector_and_processing_mass_kg'] is not None:
        # Power source includes a lower-bound ideal injector energy; its losses need their own budget.
        extended=machine+(r['electrical_mean_W']+r['stability']['injection_kinetic_power_W'])*a['power_system_specific_mass_kg_W']+a['injector_and_processing_mass_kg']
    return dict(machine_mass_kg=float(machine),delivered_rate_kg_s=float(useful_rate),
        gross_mass_payback_operating_hours=float(machine/useful_rate/3600),
        replacement_adjusted_payback_calendar_hours=float(machine/(net*duty)/3600) if net>0 else None,
        complete_site_mass_kg=extended,
        complete_site_payback_calendar_hours=extended/(net*duty)/3600 if extended is not None and net>0 else None,
        mass_per_width_kg_m=float(machine/c['payload_width']),
        delivery_per_width_kg_s_m=float(useful_rate/c['payload_width']),
        contact=contact,constraint_residuals=residuals,
        all_screen_constraints_pass=bool(all(np.isfinite(v) and v<=0 for v in residuals.values())),
        solver_ready=False,
        closure_tasks=['Recompute finite contact engagement and slip with the pressure-derived, time-varying patch.',
                       'Resolve contact-loaded belt and curved torque-member shapes.',
                       'Qualify coating/bond/thermal/wear properties and hardware allowances.',
                       'Choose site power, injector and processing mass boundary.']),arrays,mass

if __name__=='__main__':
    c=json.loads((ROOT/'config_spaced.json').read_text())
    a=json.loads((ROOT/'optimization/assumptions.json').read_text())
    result,arrays,mass=audit(c,a)
    out=ROOT/'optimization/results'
    (out/'audit.json').write_text(json.dumps(result,indent=2)+'\n')
    with (out/'contact_stages.csv').open('w') as f:
        w=csv.writer(f);w.writerow(arrays);w.writerows(zip(*arrays.values()))
    with (out/'mass_with_layer.csv').open('w') as f:
        w=csv.writer(f);w.writerow(['component','mass_kg']);w.writerows(mass.items())
    print(json.dumps(result,indent=2))
