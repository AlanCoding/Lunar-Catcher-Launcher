"""Independent-resolution and nearby-start checks for the selected candidate."""
import json
from pathlib import Path
import numpy as np
from scipy.optimize import minimize
import optimize as opt
ROOT=Path(__file__).parent
source=json.loads((ROOT/'search_results/freehub_10gpa.json').read_text())
c=source['parameters']
checks=[]
for n in [161,321,641,1281]:
    r,a,m,q=opt.evaluate(dict(c,velocity_grid_points=n))
    checks.append(dict(points=n,payback_h=r['gross_operating_payback_hours'],mass_kg=r['conditional_machine_mass_kg'],max_residual=max(q.values())))
# Same expanded search bounds as the final global runs.
opt.VARIABLES[1]=('pitch_over_radius',2.01,5.,True)
opt.VARIABLES[3]=('payload_width',.015,.6,True)
base=dict(c,velocity_grid_points=81)
keys=list(opt.evaluate(base)[3]);rng=np.random.default_rng(501)
from functools import lru_cache
@lru_cache(maxsize=128)
def calculate(xx):
    try:
        r,a,m,q=opt.evaluate(opt.unpack(xx,base))
        return r['gross_operating_payback_hours'],np.array([q[key] for key in keys])
    except (ValueError,OverflowError):return 1e12,np.full(len(keys),1e6)
xx=opt.pack(base);bounds=np.array(opt.bounds());starts=[]
for j in range(4):
    trial=np.clip(xx+rng.normal(0,.015,len(xx)),bounds[:,0],bounds[:,1])
    local=minimize(lambda x:calculate(tuple(x))[0],trial,method='SLSQP',bounds=opt.bounds(),
        constraints={'type':'ineq','fun':lambda x:-calculate(tuple(x))[1]},options={'maxiter':160,'ftol':1e-8,'eps':2e-6})
    cc=opt.unpack(local.x,base);cc['velocity_grid_points']=641
    r,a,m,q=opt.evaluate(cc)
    starts.append(dict(start=j,payback_h=r['gross_operating_payback_hours'],max_residual=max(q.values()),message=str(local.message)))
    print(starts[-1],flush=True)
(ROOT/'search_results/verification.json').write_text(json.dumps(dict(resolution=checks,nearby_starts=starts),indent=2)+'\n')
