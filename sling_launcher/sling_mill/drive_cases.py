"""Separate motor-supplied transients from rotor-supplied transients."""
import json,csv
import numpy as np
from run import ROOT,compute
c0=json.loads((ROOT/'config.json').read_text())
rows=[]
for mode,headroom in [('contact_following',0),('constant_mean',0),('constant_mean',.03),('constant_mean',.04)]:
    c=c0.copy();c.update(motor_supply_mode=mode,speed_droop=headroom)
    r,st,mass=compute(c)
    rows.append(dict(mode=mode,nominal_speed_headroom_fraction=headroom,
        electrical_mean_MW=r['electrical_mean_W']/1e6,
        aggregate_installed_drive_MW=r['peak_installed_motor_power_W']/1e6,
        motor_allowance_t=mass['motors_and_drives']/1000,
        conditional_total_t=r['conditional_installed_mass_kg']/1000,
        largest_storage_droop_fraction=float(np.nanmax(st['constant_mean_motor_droop_fraction'])),
        storage_shortfall_present=bool(np.any(~np.isfinite(st['constant_mean_motor_droop_fraction']))),
        forward_slip_headroom_sufficient=bool(mode=='contact_following' or np.all(st['constant_mean_motor_droop_fraction']<=headroom)),
        additional_1percent_storage_mass_lower_bound_t=r['extra_storage_mass_lower_bound_kg']/1000,
        demonstrated_feasible=False))
with (ROOT/'results'/'drive_cases.csv').open('w') as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
print(rows)
