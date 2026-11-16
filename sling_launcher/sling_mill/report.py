"""Build the readable result checkpoint from generated JSON and CSV."""
from pathlib import Path
import json,csv
ROOT=Path(__file__).parent
r=json.loads((ROOT/'results/summary.json').read_text())
m=list(csv.DictReader((ROOT/'results/mass.csv').open()))
d=list(csv.DictReader((ROOT/'results/drive_cases.csv').open()))
s=list(csv.DictReader((ROOT/'results/stages.csv').open()))
sweeps=list(csv.DictReader((ROOT/'results/sweep.csv').open()))
lines=['# Sling mill: first engineering results','', '[Overview](README.md) · [Model and assumptions](MODEL.md) · [Figures](publication/README.md)','',
'The reference reaches the requested flow in the prescribed-motion calculation. Flexible-belt contact and rotating-member dynamics remain open feasibility gates. The mass figures below are conditional diagnostic inventories.','',
'## Flow, scale and energy','', '| Quantity | Result |','|---|---:|']
for label,value,unit in [
('Annual launched mass',10,'million tonnes'),('Operating days',365,'days/year'),
('Mass flow',r['mass_flow_kg_s'],'kg/s'),('Rod mass',r['payload_mass_kg'],'kg'),
('Launch rate',r['launch_frequency_hz'],'rods/s'),('Injection interval',r['interval_s']*1000,'ms'),
('Entrance occupancy',r['entry_occupancy']*100,'%'),('Entrance clear gap',r['entry_clear_gap_m'],'m'),
('Exit clear gap',r['exit_clear_gap_m'],'m'),('Acceleration distance',r['active_distance_m'],'m'),
('Installed contact corridor',r['installed_length_m'],'m'),('Installed drum pairs',r['installed_pairs'],'pairs'),
('Acceleration transit time',r['travel_time_s']*1000,'ms'),
('Final drum speed',float(s[-1]['rpm']),'RPM'),
('Peak pair traction, before dynamic factor',r['contact_peak_force_pair_N']/1000,'kN'),
('Payload kinetic power',r['ideal_power_W']/1e6,'MW'),('Sliding heat',r['slip_heat_W']/1e6,'MW'),
('Mean electrical power',r['electrical_mean_W']/1e6,'MW'),
('Whole-mill instantaneous electrical peak',r['simultaneous_contact_following_peak_electrical_W']/1e6,'MW'),
('Machine waste heat',r['machine_waste_heat_W']/1e6,'MW'),
('Radiator effective emitting area',r['radiator_area_m2'],'m²'),
('Bulk payload temperature rise',r['stability']['payload_bulk_temperature_rise_K'],'K')]:
    lines.append(f'| {label} | {value:,.3f} {unit} |')
lines+=['','The rod is 1 m × 60 mm × 40 mm. Each drum has 100 mm operating radius and 25 mm hub radius. The 100 m/s entrance injector adds at least 1.59 MW of kinetic power and needs separate hardware. The radiator assumes 400 K, ε=0.85, a 250 K equivalent sink and half the slip heat entering the machinery.','',
'![Station results](results/stage_results.svg)','',
'## What limits the example','',
f'- **Contact support at low speed:** the panel envelope asks for a maximum {r["maximum_belt_thickness_m"]*1000:.1f} mm belt thickness, exceeding the 100 mm drum radius. Its thin-belt assumptions fail. A coupled contact/rotating-string solution is the next decision point; this scalar screen alone cannot reject every flexible-drum configuration.',
f'- **Strength and load paths:** free-ring Zylon HM stress at the exit is {r["final_free_ring_stress_Pa"]/1e9:.3f} GPa, versus {r["working_stress_Pa"]/1e9:.3f} GPa assumed manufactured working stress. Radial support changes the belt load path, which the separate panel screen attempts to represent. Torque members also experience transverse centrifugal loading and will curve.',
f'- **Payload/contact:** dynamic-factor pressure reaches {r["maximum_contact_pressure_Pa"]/1e6:.2f} MPa. The conservative end-loaded rod stress is {r["stability"]["axial_end_loaded_stress_Pa"]/1e6:.2f} MPa. Surface heating, abrasion and flaw-sensitive strength require material-specific assessment.',
'- **Clearance:** 200 mm drums on 200 mm pitch leave zero clearance between adjacent drums. Real machinery needs a larger pitch or a revised layout.',
'- **Hub and bearings:** final hub speed is 400 m/s. High RPM, rotational stress and motor/shaft coupling need a dedicated design.',
'', '## Motor-supplied versus rotor-supplied contact pulses','',
'Each motor can supply its contact pulse or recharge the drum steadily while rotor energy supplies the pulse. The baseline sum of individual motor ratings greatly exceeds simultaneous whole-mill power because most stations are between rods. The following mass allowance uses 2 kg/kW throughout, making this assumption explicit.','',
'| Drive mode | Reserved speed drop | Mean electrical MW | Sum of drive ratings MW | Conditional total tonnes | Worst storage drop | Forward-slip energy screen |',
'|---|---:|---:|---:|---:|---:|---|']
for row in d:
    lines.append(f'| {row["mode"]} | {float(row["nominal_speed_headroom_fraction"])*100:.1f}% | {float(row["electrical_mean_MW"]):,.2f} | {float(row["aggregate_installed_drive_MW"]):,.2f} | {float(row["conditional_total_t"]):,.1f} | {float(row["largest_storage_droop_fraction"])*100:.2f}% | {"Pass" if row["forward_slip_headroom_sufficient"]=="True" else "Fails"} |')
lines+=['','The worst storage-drop column asks what the listed rotor inventory would do under constant-mean motor input, even in the contact-following row. Contact-following operation holds prescribed rim speed by supplying the pulse directly. Passing the energy screen is separate from passing the belt-contact and rotor-strength requirements. Added storage mass is recorded as an inertia lower bound in the CSV and excluded from the inventory until its support loads are re-sized.','',
'![Whole-mill power](results/whole_mill_power.svg)','',
'![Rotor energy screen](results/rotor_transient.svg)','',
'## Conditional baseline component inventory','',
'This is the contact-following drive case. The roughly 21,000-tonne total is dominated by the generic pulse-rated motor allowance. The alternative steady-drive inventory above is about an order of magnitude smaller. Neither should be used as a final system mass or a comparison winner.','',
'| Component | Tonnes | Sizing basis |','|---|---:|---|']
for row in m:
    name=row['component'];basis=('Conditional panel/cable forces and own rotating mass' if name in ['outer_belts','radial_cables','torque_cables'] else 'Torque-shell approximation' if name=='rigid_hubs' else 'Peak electrical rating × assumed kg/kW' if name=='motors_and_drives' else 'Declared load/unit/thermal allowance; see model')
    lines.append(f'| {name.replace("_"," ")} | {float(row["mass_kg"])/1000:,.3f} | {basis} |')
lines+=['', '## Sweeps and verification','',
f'The first {len(sweeps)} sampled cases vary radius with declared coupled dimensions, acceleration, hub fraction, rod depth and fiber material. {sum(row["basic_screens_pass"]=="True" for row in sweeps)} pass all basic screens. The conditional Pareto filter compares mass, length, heat and installed drive rating; it does not establish a physically feasible optimum.','',
'![Parameter screens](results/parameter_sweeps.svg)','',
'Energy closure is at floating-point roundoff. Twelve physics tests cover exact geometry and torque sign, the baseline, discrete-edge work closure, analytic sliding work, forward-slip scheduling, cable self-mass, flow feasibility, independent pitch and uncovered-contact rejection, and doubled-resolution heat convergence.','',
'Full numbers: [stage CSV](results/stages.csv), [mass CSV](results/mass.csv), [drive cases](results/drive_cases.csv), [sweep CSV](results/sweep.csv), [JSON summary](results/summary.json).','',
'## Next useful result','',
'Solve the contact-loaded flexible drum shape at several entrance and exit speeds. This will determine whether normal loads can be carried with practical belt geometry, how much torque-member curvature changes the leverage, and which mass estimates can be trusted. Payload recipes and drive design can then be selected against that resolved contact envelope.','']
(ROOT/'RESULTS.md').write_text('\n'.join(lines))
