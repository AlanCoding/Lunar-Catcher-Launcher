"""Reproduce the reference and isolate drive torque; no web model or reoptimization."""
import json,sys
from pathlib import Path
import numpy as np
from model import solve,RHO
from hardware import update
P=Path(__file__).parent
ref=json.loads((P/'search_results/iron_reference.json').read_text());base=ref['parameters']
results={}
for name,changes in [('published_nominal_belt',dict(include_belt_traction_envelope=False)),
                     ('torque_complete_envelope',dict(include_belt_traction_envelope=True)),
                     ('omit_structural_drive_load_DIAGNOSTIC',dict(include_belt_traction_envelope=True,diagnostic_omit_drive_torque=True))]:
 c=dict(base,**changes);r,a,m=solve(c);r,a,m=update(c,r,a,m)
 results[name]=dict(summary=r,masses=m,last_stage=dict(
  payload_speed_m_s=float(a['v_m_s'][-1]),rim_speed_m_s=float(a['rim_speed_m_s'][-1]),
  nominal_belt_stress_GPa=float(a['nominal_belt_stress_Pa'][-1]/1e9),peak_belt_stress_GPa=float(a['belt_stress_Pa'][-1]/1e9),
  peak_belt_specific_stress_MJ_kg=float(a['belt_stress_Pa'][-1]/RHO/1e6),
  member_working_stress_GPa=c['working_stress_Pa']/1e9,member_specific_working_stress_MJ_kg=c['working_stress_Pa']/RHO/1e6,
  taper_area_ratio=float(a['member_taper_area_ratio'][-1]),torque_Nm=float(a['drive_torque_per_drum_Nm'][-1]),
  torque_member_rim_N=float(a['torque_member_rim_tension_N'][-1]),
  radial_tip_area_mm2=float(a['radial_member_tip_area_m2'][-1]*1e6),radial_root_area_mm2=float(a['radial_member_root_area_m2'][-1]*1e6),
  torque_tip_area_mm2=float(a['torque_member_tip_area_m2'][-1]*1e6),torque_root_area_mm2=float(a['torque_member_root_area_m2'][-1]*1e6)))
# Read each architecture's own sizing method/record for an area-ratio comparison.
sys.path.insert(0,str(P.parents[2]))
from sling_launcher.staged_spool_bank.model import Model,Case
straw=Model(Case())
from sling_launcher.architecture_comparison.compare import spool
kart=spool(1450.,1e9)
comparison=dict(definition='Root/loaded-tip material cross-sectional area ratio; constant-section loop=1. Mill reports largest stage cable ratio; its outer belt is constant-section.',
 sling_mill=dict(stress_GPa=base['working_stress_Pa']/1e9,density_kg_m3=RHO,specific_stress_MJ_kg=base['working_stress_Pa']/RHO/1e6,taper_area_ratio=results['torque_complete_envelope']['last_stage']['taper_area_ratio'],outer_belt_area_ratio=1.),
 go_kart=dict(stress_GPa=1.,density_kg_m3=1450.,specific_stress_MJ_kg=1e9/1450/1e6,taper_area_ratio=kart['taper_area_ratio']),
 slider_straw=dict(stress_GPa=straw.kappa*straw.c.density_kg_m3/1e9,density_kg_m3=straw.c.density_kg_m3,specific_stress_MJ_kg=straw.kappa/1e6,taper_area_ratio=float(straw.lam[0]/straw.lam[-1])),
 conveyor=dict(stress_GPa=2.9,density_kg_m3=1560.,specific_stress_MJ_kg=2.9e9/1560/1e6,taper_area_ratio=1.))
out=dict(parameters=base,cases=results,architecture_comparison=comparison,
 interpretation='Geometry and throughput held fixed. Drive torque was already included in cable and hub sizing. Added one-sided belt traction stress envelope; omission diagnostic keeps the physical power/traction demand and removes only its internal structural torque path.')
(P/'search_results/torque_reproduction.json').write_text(json.dumps(out,indent=2)+'\n')
(P/'search_results/architecture_taper_comparison.json').write_text(json.dumps(comparison,indent=2)+'\n')
print(json.dumps({k:v['last_stage'] for k,v in results.items()},indent=2));print(json.dumps(comparison,indent=2))
