"""Check the selected iron search on progressively finer integration grids."""
import json
from pathlib import Path
import numpy as np
import optimize as opt
P=Path(__file__).parent
source=json.loads((P/'search_results/iron_thin_verified.json').read_text())
opt.VARIABLES[:]=[(d['name'],d['lower'],d['upper'],d['logarithmic']) for d in source['bounds']]
base=dict(source['parameters'],velocity_grid_points=1281)
_,_,_,q=opt.evaluate(base);keys=list(q)
# The existing 641-node SLSQP result already passes the finer grids.
# Preserve that solution; verification does not launch another optimization.
c=base;r,a,m,q=opt.evaluate(c)
checks=[]
for n in (641,1281,2561):
    rr,aa,mm,qq=opt.evaluate(dict(c,velocity_grid_points=n))
    checks.append(dict(nodes=n,mass_kg=rr['conditional_machine_mass_kg'],payoff_h=rr['gross_operating_payback_hours'],max_residual=max(qq.values())))
assert checks[-1]['max_residual']<1e-6,checks
out=dict(parameters=c,summary=r,masses=m,constraints=q,bounds=source['bounds'],verification=checks,
    refinement_message='Selected 641-node constrained refinement; independent 1281/2561-node verification',source='iron_thin_verified.json',verification_tolerance=1e-6,high_resolution_pass=True,
    hardware_notes='Continuous fabricated frame sections; prior audit used 5 mm section increments.',
    scope='Conditional optimum in expanded domain (0.10 mm thickness floor); full-sun solar included; 0-100 m/s injector excluded.')
(P/'search_results/iron_reference.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(dict(summary=r,verification=checks,parameters=c),indent=2))
