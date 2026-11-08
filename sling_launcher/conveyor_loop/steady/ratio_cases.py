"""Distinguish outbound line-density ratios from whole-loop inventory ratios."""
from dataclasses import replace
import json
import numpy as np
from scipy.optimize import brentq
from .model import Inputs, solve, evaluate
from .report import OUT


def run(q, tol=2e-6):
    base=Inputs(); c=replace(base,payload_per_m=q*base.bare_density)
    sol,length=solve(c,tol=tol)
    row,h=evaluate(c,sol,length)
    row['outbound_payload_to_tether_density_ratio']=q
    row['whole_loop_payload_to_tether_mass_ratio']=row['payload_inventory_kg']/row['bare_loop_mass_kg']
    row['working_stress_GPa']=2.9
    row['utilization']=row['max_stress_GPa']/2.9
    return row,h


def main():
    q=brentq(lambda q:run(q)[0]['whole_loop_payload_to_tether_mass_ratio']-1/3,.6,.8,xtol=1e-9)
    rows=[]
    for name,loading in [('outbound_density_1_to_3',1/3),('whole_loop_mass_1_to_3',q)]:
        row,h=run(loading);row['name']=name
        refined,_=run(loading,tol=2e-8)
        row['refinement_stress_relative_change']=abs(refined['max_stress_GPa']/row['max_stress_GPa']-1)
        assert row['refinement_stress_relative_change']<1e-6
        assert row['integrated_force_residual_scaled']<1e-5
        assert row['min_effective_tension_N']>0
        if name=='whole_loop_mass_1_to_3':
            assert abs(row['whole_loop_payload_to_tether_mass_ratio']-1/3)<1e-8
        rows.append(row);np.savez_compressed(OUT/f'{name}.npz',**h)
    (OUT/'ratio_cases.json').write_text(json.dumps(rows,indent=2)+'\n')
    for r in rows:
        print(r['name'],json.dumps({k:r[k] for k in ['outbound_payload_to_tether_density_ratio','whole_loop_payload_to_tether_mass_ratio','payload_inventory_kg','bare_loop_mass_kg','mass_flow_kg_s','max_stress_GPa','capstan_mu_proxy','width_m']}))

if __name__=='__main__':main()
