"""Publish conditional search checkpoint without changing accepted illustrations."""
import json,csv
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).parent;OUT=ROOT/'search_results'
rows=[json.loads((OUT/f'{name}.json').read_text()) for name in ['freehub_10gpa','freehub_15gpa','rounded_reference']]
labels=['1.0 GPa optimum','1.5 GPa optimum','Rounded 1.0 GPa candidate']
metrics=[]
for label,d in zip(labels,rows):
 c=d['parameters'];r=d['summary'];metrics.append(dict(case=label,radius_m=c['radius'],hub_radius_m=c['radius']*c['hub_ratio'],pitch_m=c['radius']*c['pitch_over_radius'],bar_length_m=c['payload_length'],bar_width_m=c['payload_width'],bar_depth_m=c['payload_depth'],gap_m=c['payload_depth']-c['total_squeeze_m'],squeeze_mm=c['total_squeeze_m']*1000,belt_thickness_mm=c['structural_belt_thickness_m']*1000,length_m=r['corridor_length_m'],pair_count=r['equivalent_pairs'],mass_t=r['conditional_machine_mass_kg']/1000,payback_h=r['gross_operating_payback_hours'],electrical_MW=r['electrical_mean_W']/1e6,sliding_heat_MW=r['slip_heat_W']/1e6))
with (OUT/'comparison.csv').open('w') as f:
 w=csv.DictWriter(f,fieldnames=list(metrics[0]));w.writeheader();w.writerows(metrics)
fig,ax=plt.subplots(figsize=(10,5))
parts={'Motors':['motors'],'Foundations':['foundations'],'Cooling':['motor_radiators'],'Fiber + contact layer':['structural_belts','contact_layers','radial_members','torque_members'],'Other machine parts':['hubs','bearings','frames','startup_supports','guides']}
bottom=np.zeros(3)
for color,(label,keys) in zip(['#49677e','#b5a17d','#80a3a8','#426e60','#a5a5a1'],parts.items()):
 values=np.array([sum(d['masses'][key] for key in keys)/1000 for d in rows]);ax.bar(labels,values,bottom=bottom,label=label,color=color);bottom+=values
ax.set(ylabel='Conditional accelerator mass (tonnes)',title='Working-stress margin has a small total-mass penalty')
ax.legend(bbox_to_anchor=(1.01,1),loc='upper left');fig.tight_layout()
for ext in ['svg','png']:fig.savefig(OUT/f'mass_comparison.{ext}',dpi=150,bbox_inches='tight')
plt.close(fig)
round_d=rows[-1];c=round_d['parameters'];r=round_d['summary']
feed_power=.5*r['mass_flow_kg_s']*c['v_entry']**2
power=r['electrical_mean_W']+feed_power
power_cases=[]
for intensity in [0,.001,.005,.01]:
 extra=power*intensity;total=r['conditional_machine_mass_kg']+extra
 power_cases.append(dict(power_specific_mass_kg_W=intensity,power_mass_t=extra/1000,total_t=total/1000,payback_h=total/r['mass_flow_kg_s']/3600))
with (OUT/'power_boundary_sensitivity.csv').open('w') as f:
 w=csv.DictWriter(f,fieldnames=list(power_cases[0]));w.writeheader();w.writerows(power_cases)
lines=['# Constrained search: first conditional system parameters','', '[Blended model](README.md) · [Comparison CSV](search_results/comparison.csv) · [Rounded configuration and results](search_results/rounded_reference.json)','',
'We now have numerical candidates from a constrained search over the connected blended model. The best 1.0 GPa candidate is about 1,665 tonnes, versus 1,645 tonnes at 1.5 GPa: **roughly 1.2% additional machine mass buys the lower Zylon working-stress ceiling**. These are conditional minima within the declared model and search domain.','',
'## Readable candidate','',
'The rounded candidate moves away from several tightly active limits at a modest mass cost. Its full precision inputs and constraint checks are saved separately; this table uses engineering display precision.','',
'| Quantity | Rounded candidate |','|---|---:|']
for label,value,unit in [('Drum diameter',2*c['radius'],'m'),('Hub radius',c['hub_ratio']*c['radius'],'m'),('Station pitch',c['radius']*c['pitch_over_radius'],'m'),('Clear gap between neighboring drums',c['radius']*c['pitch_over_radius']-2*c['radius'],'m'),('Bar length',c['payload_length'],'m'),('Bar width',c['payload_width']*1000,'mm'),('Bar depth',c['payload_depth']*1000,'mm'),('Imposed squeeze',c['total_squeeze_m']*1000,'mm'),('Roller surface gap',(c['payload_depth']-c['total_squeeze_m'])*1000,'mm'),('Structural Zylon thickness',c['structural_belt_thickness_m']*1000,'mm'),('Assumed contact-layer thickness',c['coating_thickness_m']*1000,'mm'),('Corridor length',r['corridor_length_m']/1000,'km'),('Equivalent station pairs',r['equivalent_pairs'],'pairs'),('Bar mass',r['payload_mass_kg'],'kg'),('Bar feed frequency',r['launch_frequency_Hz'],'Hz'),('Entry acceleration',r['acceleration_entry_m_s2'],'m/s²'),('Exit acceleration',r['acceleration_exit_m_s2'],'m/s²'),('Maximum structural-belt stress',r['maximum_belt_stress_Pa']/1e9,'GPa'),('Reserved rotor speed loss',c['speed_reserve_fraction']*100,'%'),('Mean mill electrical input',r['electrical_mean_W']/1e6,'MW'),('Total friction heat',r['slip_heat_W']/1e6,'MW'),('Maximum average roller temperature',r['maximum_average_roller_temperature_K'],'K'),('Conditional machine mass',r['conditional_machine_mass_kg']/1000,'tonnes'),('Machine-only mass payoff',r['gross_operating_payback_hours'],'operating hours')]:
 lines.append(f'| {label} | {value:,.3f} {unit} |')
lines+=['',
'Both search winners choose steady per-station motor input, with the rotor supplying contact-load energy. The averaged energy-budget calculation requires about 0.4% speed reserve. Thus the motor inventory is sized principally by mean power. This is a mechanical energy-storage result under the declared drive model; individual drives and controls still need design.','',
'## Search and checks','',
'Eleven continuous choices were searched: drum radius, hub fraction, pitch/radius, bar length/width/depth, squeeze, structural-belt thickness, hoop-support fraction, rotor speed reserve and fraction of contact pulse supplied directly by the motor. Attachment count (128), effective torque-sharing count (8), inlet speed (100 m/s), contact-layer thickness (0.5 mm), friction coefficient and other material properties stayed fixed.','',
'Constrained differential evolution was followed by SLSQP refinement. The initial search pushed width to its boundary; expanding the width limit from 0.15 to 0.60 m found an interior candidate. The initial pitch-ratio bound was also relaxed, allowing the explicit 20 mm drum-clearance requirement to govern. The final candidates were refined with 641 velocity points and checked with 1,281. Four nearby perturbed local starts returned payoff values within about 0.14% of the 1.0 GPa result; some have small discretization-scale reserve residuals and are retained as diagnostic checks rather than replacements for the refined candidate. This supports local stability, not a proof of global optimality.','',
'An added hub/shaft calculation sizes a hollow section for torsion and bending across the roller width. It uses a simply supported beam with a conservative concentrated load, 200 GPa modulus, and a 10 µm deflection limit. If even a solid hub of the chosen radius cannot meet the requirement, that candidate fails. A separate 250 MPa hoop-stress benchmark limits hub peripheral speed. These are explicit study assumptions.','',
'The final mathematical minima lie against several constraints: Zylon working stress, mean layer temperature, rotor speed reserve, bar buckling, minimum drum clearance, two-pitch bar engagement and the thin-string-panel thickness limit. The last two are reduced-model applicability conditions, so those selected dimensions require particular care. The raw optimum should not be presented as a fabrication drawing.','',
'## Where the mass goes','',
'![Mass comparison](search_results/mass_comparison.svg)','',
'| Component | Rounded candidate, tonnes |','|---|---:|']
for key,value in round_d['masses'].items():lines.append(f'| {key.replace("_"," ")} | {value/1000:,.2f} |')
lines+=['',
'The largest allowances remain motors at 2 kg/kW of rating, foundations at 200 kg per pair, and motor cooling at 5 kg/m² of effective radiator area. Real motor/drive, foundation and radiator designs could shift the optimum. Cable joints and attachment hardware are not yet separately sized; attachment topology was therefore held fixed.','',
'## The scope decision before a whole-system payoff','',
f'The optimized mill requires about {r["electrical_mean_W"]/1e6:.1f} MW continuously. Its inlet also assumes bars already moving at 100 m/s, which requires at least {feed_power/1e6:.2f} MW of kinetic power plus injector losses. The current inventory includes accelerator machinery, foundations, guides and motor radiators. **It excludes the generating/receiving power plant, low-speed injector, payload-processing plant and their infrastructure.**','',
'That is now the material boundary decision for the next design phase: use a dedicated continuous power plant and self-contained feed system, or treat power and preaccelerated bars as supplied industrial services. Dedicated nuclear generation and externally beamed/grid power imply different inventories. The distinction is needed before calling the short accelerator payoff a complete-system payoff.','',
'The following is an arithmetic sensitivity, with hypothetical power-system mass intensities. It makes the boundary visible; it does not select or estimate a real plant. Injector kinetic power is included in the power total, while injector/processing hardware and power losses are still omitted.','',
'| Assumed power-system mass intensity | Added power-system mass | Accelerator + that mass payoff |','|---:|---:|---:|']
for row in power_cases:lines.append(f'| {row["power_specific_mass_kg_W"]*1000:.1f} kg/kW | {row["power_mass_t"]:,.0f} t | {row["payback_h"]:.2f} h |')
lines+=['',
'## Evidence and remaining engineering limits','',
'The contact layer remains the hypothetical 1,400 kg/m³, 1 GPa compression-modulus material, with assumed 5 MPa tensile bond and 20 MPa shear limits and a 450 K mean-temperature ceiling. No named product has been qualified. The Zylon ceiling is kept fixed within each solve; lower stress is never obtained by changing fiber properties. The 1.0 GPa case is the preferred conservative candidate because its mass penalty is small.','',
'The model preserves the requested averaged treatment. It uses no bar-arrival or roller-angle event simulation. Conditional feasibility also depends on the string-panel approximation, the diagonal-cable mass approximation, available radiation view, friction and wear behavior. Passing the reduced checks is distinct from material qualification or a buildability finding.','',
'## Files and reproduction','',
'- [1.0 GPa optimum](search_results/freehub_10gpa.json) and [1.5 GPa optimum](search_results/freehub_15gpa.json).','- [Rounded reference](search_results/rounded_reference.json), [verification](search_results/verification.json), [power-boundary sensitivity](search_results/power_boundary_sensitivity.csv).','- Earlier `initial`, `expanded` and `shaft` outputs record successive search stages. The two `freehub` files are the final optimized comparison.','',
'```bash','MPLCONFIGDIR=/tmp/lunar-sling-mpl-cache OPENBLAS_NUM_THREADS=1 .env/hub/bin/python sling_launcher/sling_mill/blended/optimize.py --iterations 70 --seed 31 --ceiling 1000000000 --label repeat_10gpa --width-max .6 --pitch-min 2.01 --warmstart sling_launcher/sling_mill/blended/search_results/shaft_10gpa.json','.env/hub/bin/python sling_launcher/sling_mill/blended/verify_search.py','.env/hub/bin/python sling_launcher/sling_mill/blended/report_search.py','.env/hub/bin/python sling_launcher/sling_mill/blended/test_search.py','```','']
(ROOT/'OPTIMIZATION.md').write_text('\n'.join(lines))
