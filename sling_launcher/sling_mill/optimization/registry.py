"""Machine-readable classification of every baseline and contact input."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
BASE=json.loads((ROOT/'config.json').read_text())
CONTACT=json.loads((ROOT/'optimization/assumptions.json').read_text())
# Search bounds define initial experiments, rather than manufactured limits.
DESIGN={
 'radius':('m',.1,10.), 'hub_ratio':('1',.05,.6),
 'payload_length':('m',.2,10.),'payload_width':('m',.02,1.),'payload_depth':('m',.01,.2),
 'acceleration':('m/s²',980.665,29419.95),'v_entry':('m/s',50.,500.),
 'belt_deflection_fraction':('1',.002,.02),'attachments':('integer',16,256),
 'torque_members_effective':('integer',2,256),'slip_margin':('m/s',0.,50.),
 'speed_droop':('1',0.,.1),'storage_design_droop':('1',.005,.1),
 'radiator_temperature':('K',300.,450.),
 'coating_thickness_m':('m',.00005,.002),
 'pitch_over_radius':('1',2.2,10.),'belt_width_over_payload_width':('1',1.,1.25)}
TARGET={'annual_mass_kg','operating_days','v_exit','successful_delivery_fraction'}
DERIVED={'pitch':'radius × pitch_over_radius',
         'belt_width':'payload_width × belt_width_over_payload_width',
         'contact_patch':'contact-pressure/gap solution; legacy prescribed value retained only for closure audit',
         'contact_modulus':'legacy unused value; replaced by coating modulus plus backing compliance'}
CATEGORIES={'material':['Kevlar 49','Zylon AS','Zylon HM'],
            'motor_supply_mode':['contact_following','constant_mean']}

def entries():
    result=[]
    for source,values in [('baseline',BASE),('contact_assumptions',CONTACT)]:
        for name,value in values.items():
            category='assumption_or_requirement'
            if name in DESIGN:category='independent_design'
            elif name in TARGET:category='mission_fixed'
            elif name in DERIVED:category='derived_or_superseded'
            elif name in CATEGORIES:category='categorical_design'
            elif name=='integration_steps_per_pitch':category='numerical'
            row=dict(name=name,source=source,classification=category,reference=value)
            if name in DESIGN:row.update(unit=DESIGN[name][0],exploration_bounds=list(DESIGN[name][1:]))
            if name in DERIVED:row['relationship']=DERIVED[name]
            if name in CATEGORIES:row['choices']=CATEGORIES[name]
            result.append(row)
    for name,default in [('pitch_over_radius',3.),('belt_width_over_payload_width',1.)]:
        result.append(dict(name=name,source='solver_parameterization',classification='independent_design',reference=default,unit=DESIGN[name][0],exploration_bounds=list(DESIGN[name][1:])))
    return result

if __name__=='__main__':
    rows=entries()
    (ROOT/'optimization/variables.json').write_text(json.dumps(rows,indent=2)+'\n')
    lines=['# Complete input classification','', '[Optimizer design](README.md) · [Machine-readable register](variables.json)','',
           'Every key in the baseline and new contact assumptions is classified below. Mission requirements and uncertain material properties stay fixed within a solve; sensitivity studies vary them between solves. Exploration bounds appear in the JSON.','',
           '| Input | Classification | Reference |','|---|---|---|']
    for row in rows:lines.append(f'| `{row["name"]}` | {row["classification"]} | {row["reference"]} |')
    (ROOT/'optimization/VARIABLES.md').write_text('\n'.join(lines)+'\n')
