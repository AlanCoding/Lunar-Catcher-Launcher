"""Remove arbitrary plate thickness/feed caps; profile thickness with full-sun solar."""
import json
from pathlib import Path
from functools import lru_cache
import numpy as np
from scipy.optimize import minimize
import optimize as opt
P=Path(__file__).parent
source=json.loads((P/'search_results/iron_thin_solar.json').read_text())
base=dict(source['parameters'],velocity_grid_points=81,solar_full_sun=True,solar_W_per_kg=100.,solar_headroom=1.2,solar_output_W_m2=250.,maximum_occupancy=1.,maximum_feed_frequency_Hz=None)
new={'radius':(.1,3.),'pitch_over_radius':(2.0001,10.),'payload_length':(.1,20.),'payload_width':(.005,3.),'payload_depth':(.0001,.12),'total_squeeze_m':(1e-6,.005),'structural_belt_thickness_m':(1e-5,.02),'hoop_support_fraction':(.01,.95),'speed_reserve_fraction':(0.,.2),'hub_ratio':(.005,.4)}
opt.VARIABLES[:]=[(k,*new.get(k,(lo,hi)),log) for k,lo,hi,log in opt.VARIABLES]
keys=list(opt.evaluate(base)[3]); bounds=opt.bounds()
def search(seed,fixed_depth=None,maxiter=100):
    seed=dict(seed);bb=list(bounds)
    if fixed_depth is not None:
        ratio=seed['payload_depth']/fixed_depth
        seed['payload_width']*=ratio
        if ratio>1:
            seed['radius']*=ratio
            seed['payload_length']*=ratio
        seed['payload_depth']=fixed_depth
        seed['total_squeeze_m']=min(seed['total_squeeze_m'],fixed_depth*.3)
        j=[x[0] for x in opt.VARIABLES].index('payload_depth');bb[j]=(np.log(fixed_depth),np.log(fixed_depth))
    x0=np.clip(opt.pack(seed),np.array(bb)[:,0],np.array(bb)[:,1])
    @lru_cache(maxsize=1024)
    def ev(x):
        try:
            r,a,m,q=opt.evaluate(opt.unpack(x,base))
            return r['gross_operating_payback_hours'],np.array([q[k] for k in keys])
        except (ValueError,OverflowError,FloatingPointError):return 1e12,np.ones(len(keys))*1e6
    res=minimize(lambda x:ev(tuple(x))[0],x0,method='SLSQP',bounds=bb,
       constraints={'type':'ineq','fun':lambda x:-ev(tuple(x))[1]-2e-6},
       options={'maxiter':maxiter,'ftol':1e-8,'eps':2e-6})
    c=opt.unpack(res.x,base)
    try:r,a,m,q=opt.evaluate(c)
    except (ValueError,OverflowError,FloatingPointError):
        return dict(parameters=c,message=str(res.message),feasible=False)
    # Retain the feasible seed if SLSQP fails or makes the objective worse.
    if max(ev(tuple(x0))[1])<=1e-6 and (max(q.values())>1e-6 or ev(tuple(x0))[0]<r['gross_operating_payback_hours']):
        c=opt.unpack(x0,base);r,a,m,q=opt.evaluate(c)
    d=dict(parameters=c,summary=r,masses=m,constraints=q,message=str(res.message),feasible=max(q.values())<=1e-6)
    print('depth',c['payload_depth']*1000,'mm','payoff',r['gross_operating_payback_hours'],'residual',max(q.values()),res.message,flush=True)
    return d
r,a,m,q=opt.evaluate(base)
first=dict(parameters=base.copy(),summary=r,masses=m,constraints=q,feasible=max(q.values())<=1e-6)
rows=[]
for depth in (.0005,.001,.00125,.0015,.002,.003,.005):
    d=search(first['parameters'],fixed_depth=depth,maxiter=65);rows.append(d)
    (P/'search_results/thickness_profile.json').write_text(json.dumps(rows,indent=2)+'\n')
starts=[]
for factor in (.85,1.2):
    seed=dict(first['parameters']);seed['payload_depth']*=factor;seed['payload_width']/=factor
    starts.append(search(seed,maxiter=65))
(P/'search_results/iron_thickness_starts.json').write_text(json.dumps(starts,indent=2)+'\n')
valid=[d for d in [first,*rows,*starts] if d['feasible']]
for best in sorted(valid,key=lambda d:d['summary']['gross_operating_payback_hours']):
    checks=[]
    for n in (641,1281,2561):
        r,a,m,q=opt.evaluate(dict(best['parameters'],velocity_grid_points=n))
        checks.append(dict(nodes=n,mass_kg=r['conditional_machine_mass_kg'],payoff_h=r['gross_operating_payback_hours'],max_residual=max(q.values())))
    if checks[-1]['max_residual']<1e-6:break
else:raise ValueError('No candidate passes grid verification')
c=dict(best['parameters'],velocity_grid_points=1281);r,a,m,q=opt.evaluate(c)
best.update(parameters=c,summary=r,masses=m,constraints=q,verification=checks,bounds=[dict(name=k,lower=lo,upper=hi,logarithmic=log) for k,lo,hi,log in opt.VARIABLES],source='thickness_study.py',verification_tolerance=1e-6,high_resolution_pass=True)
(P/'search_results/iron_thin_verified.json').write_text(json.dumps(best,indent=2)+'\n')
print('VERIFIED',checks,flush=True)
