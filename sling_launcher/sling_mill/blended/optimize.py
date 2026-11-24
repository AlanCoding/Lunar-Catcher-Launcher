"""Conditional constrained search over the blended model; fixed material scenario.
No material property or mass-cost coefficient is adjustable by the optimizer.
"""
import argparse,csv,json
from pathlib import Path
from functools import lru_cache
import numpy as np
from scipy.optimize import differential_evolution,NonlinearConstraint,minimize
from model import solve
ROOT=Path(__file__).parent
# Log coordinates for positive geometric dimensions, linear fractions for controls.
VARIABLES=[('radius',.38,2.0,True),('pitch_over_radius',2.1,5.,True),
 ('payload_length',.8,8.,True),('payload_width',.015,.15,True),
 ('payload_depth',.015,.12,True),('total_squeeze_m',.0001,.002,True),
 ('structural_belt_thickness_m',.0005,.008,True),
 ('hoop_support_fraction',.12,.38,False),
 ('speed_reserve_fraction',0.,.05,False),('motor_pulse_fraction',0.,1.,False),
 ('hub_ratio',.05,.15,True)]

def unpack(x,base):
    c=base.copy()
    for val,(key,lo,hi,log) in zip(x,VARIABLES):c[key]=float(np.exp(val) if log else val)
    return c

def pack(c):return np.array([np.log(c[key]) if log else c[key] for key,lo,hi,log in VARIABLES])
def bounds():return [(np.log(lo),np.log(hi)) if log else (lo,hi) for key,lo,hi,log in VARIABLES]

def evaluate(c):
    if c.get('diagnostic_omit_drive_torque',False):raise ValueError('Torque-omission diagnostic cannot be optimized as a design')
    r,a,m=solve(c);q=r['constraint_residuals'].copy()
    if c.get('hardware_audit_enabled',False):
        from hardware import update
        r,a,m=update(c,r,a,m)
    # Normalize the energy-reserve difference for diagnostics and search scaling.
    q['speed_reserve']/=.01
    pitch=c['radius']*c['pitch_over_radius']
    W,D,L=c['payload_width'],c['payload_depth'],c['payload_length']
    peak_a=float(np.max(a['acceleration_m_s2']))
    payload_mass=c['payload_density']*W*D*L
    beam_I=min(W*D**3,D*W**3)/12
    euler=np.pi**2*70e9*beam_I/pitch**2
    q.update(blended_engagement=2*pitch/L-1,
        feed_frequency=(r['launch_frequency_Hz']/c.get('maximum_feed_frequency_Hz',100.)-1 if c.get('maximum_feed_frequency_Hz',100.) else -1.),
        payload_end_load=c['payload_density']*L*peak_a/c.get('payload_working_allowable_Pa',100e6)-1,
        payload_buckling=(-1. if c.get('front_pulling',False) else payload_mass*peak_a/euler-1),
        hub_rotational_stress=c['hub_density']*float(a['rim_speed_m_s'].max()*c['hub_ratio'])**2/250e6-1)
    if c.get('front_pulling',False):
        # Conservative scalar contact-pressure screen, pending combined local stress.
        q['payload_contact_pressure']=float(a['peak_contact_pressure_Pa'].max())/c['payload_working_allowable_Pa']-1
    # Report all assumptions alongside the result. This is an accelerator-only objective.
    return r,a,m,q

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--iterations',type=int,default=120)
    parser.add_argument('--seed',type=int,default=7);parser.add_argument('--ceiling',type=float,default=1.5e9)
    parser.add_argument('--label',default='search')
    parser.add_argument('--width-max',type=float,default=.15)
    parser.add_argument('--pitch-min',type=float,default=2.1)
    parser.add_argument('--depth-min',type=float,default=.015)
    parser.add_argument('--warmstart',type=Path)
    parser.add_argument('--solar',action='store_true',help='Include full-sun solar at 100 W/kg plus 20% headroom')
    parser.add_argument('--review-domain',action='store_true',help='Broaden arbitrary bounds and remove arbitrary feed utilization caps')
    parser.add_argument('--iron',action='store_true',help='Iron, front pulling and height-aware hardware budget')
    args=parser.parse_args()
    VARIABLES[1]=('pitch_over_radius',args.pitch_min,5.,True)
    VARIABLES[3]=('payload_width',.015,args.width_max,True)
    VARIABLES[4]=('payload_depth',args.depth_min,.12,True)
    if args.review_domain:
        broader={'radius':(.1,3.),'pitch_over_radius':(2.0001,10.),'payload_length':(.1,20.),
          'payload_width':(.005,3.),'payload_depth':(args.depth_min,.12),
          'total_squeeze_m':(1e-6,.005),'structural_belt_thickness_m':(1e-5,.02),
          'hoop_support_fraction':(.01,.95),'speed_reserve_fraction':(0.,.2),'hub_ratio':(.005,.4)}
        VARIABLES[:]=[(k,*broader.get(k,(lo,hi)),log) for k,lo,hi,log in VARIABLES]
    base=json.loads((ROOT/'config.json').read_text())
    base.update(hub_ratio=.10,working_stress_Pa=args.ceiling,velocity_grid_points=41,
        hub_bending_enabled=True,hub_modulus_Pa=200e9,hub_deflection_limit_m=10e-6)
    if args.iron:
        base.update(payload_density=7860.,payload_heat_capacity=450.,payload_modulus_Pa=207e9,
            payload_working_allowable_Pa=70e6,front_pulling=True,hardware_audit_enabled=True,include_belt_traction_envelope=True)
    if args.solar:base.update(solar_full_sun=True,solar_W_per_kg=100.,solar_headroom=1.2,solar_output_W_m2=250.)
    if args.review_domain:base.update(maximum_occupancy=1.,maximum_feed_frequency_Hz=None)
    # Only unpack geometric variables from a warmstart; material assumptions stay fixed.
    initial=base.copy()
    if args.warmstart:
        warm=json.loads(args.warmstart.read_text())['parameters']
        initial.update({k:warm[k] for k,_,_,_ in VARIABLES})
    r0,a0,m0,q0=evaluate(initial);keys=list(q0)
    count=0
    @lru_cache(maxsize=1024)
    def run_cached(xx):
        nonlocal count
        count+=1
        try:
            c=unpack(xx,base);r,a,m,q=evaluate(c)
            vals=np.array([q[key] for key in keys])
            if not np.all(np.isfinite(vals)) or not np.isfinite(r['conditional_machine_mass_kg']):raise ValueError('Nonfinite model output')
            return r['gross_operating_payback_hours'],vals
        except (ValueError,OverflowError,FloatingPointError):return 1e12,np.full(len(keys),1e6)
    fun=lambda x:run_cached(tuple(x))[0]
    con=lambda x:run_cached(tuple(x))[1]
    rng=np.random.default_rng(args.seed);bb=np.array(bounds())
    pop=rng.uniform(bb[:,0],bb[:,1],(80,len(VARIABLES)))
    # Seed the search with a known nearby low-squeeze feasible neighborhood.
    seed=base.copy();seed.update(total_squeeze_m=.0002)
    if args.warmstart:seed.update(json.loads(args.warmstart.read_text())['parameters'])
    pop[0]=pack(seed)
    for j in range(1,16):pop[j]=np.clip(pop[0]+rng.normal(0,.04,len(VARIABLES)),bb[:,0],bb[:,1])
    history=[]
    def callback(xk,convergence):
        val=fun(xk);viol=float(np.max(con(xk)));history.append(dict(iteration=len(history),payback_h=val,max_residual=viol))
        if len(history)%20==0:print(f'{args.label} generation {len(history)}: {val:.4f} h, residual {viol:.3g}, {count} evaluations',flush=True)
    result=differential_evolution(fun,bounds(),constraints=(NonlinearConstraint(con,-np.inf,0),),
        init=pop,maxiter=args.iterations,seed=args.seed,polish=False,tol=1e-5,callback=callback)
    # Explicit constrained local refinement, never accept a failed/infeasible improvement.
    local=minimize(fun,result.x,method='SLSQP',bounds=bounds(),
        constraints={'type':'ineq','fun':lambda x:-con(x)},options={'maxiter':180,'ftol':1e-8,'eps':1e-5})
    xx=result.x
    if np.max(con(local.x))<=1e-6 and fun(local.x)<fun(xx):xx=local.x
    fine_base=dict(base,velocity_grid_points=641)
    @lru_cache(maxsize=128)
    def fine_cached(zz):
        try:
            rr,aa,mm,qq=evaluate(unpack(zz,fine_base))
            return rr['gross_operating_payback_hours'],np.array([qq[key] for key in keys])
        except (ValueError,FloatingPointError,OverflowError):return 1e12,np.full(len(keys),1e6)
    fine=minimize(lambda z:fine_cached(tuple(z))[0],xx,method='SLSQP',bounds=bounds(),
        constraints={'type':'ineq','fun':lambda z:-fine_cached(tuple(z))[1]},
        options={'maxiter':100,'ftol':1e-8,'eps':2e-6})
    if np.max(fine_cached(tuple(fine.x))[1])<=1e-6:xx=fine.x
    c=unpack(xx,fine_base)
    r,a,m,q=evaluate(c)
    output=dict(parameters=c,summary=r,masses=m,constraints=q,evaluations=count,
        global_search_message=str(result.message),local_search_message=str(local.message),
        high_resolution_pass=bool(max(q.values())<=1e-6),
        bounds=[dict(name=key,lower=lo,upper=hi,logarithmic=log) for key,lo,hi,log in VARIABLES],
        limitations=['Conditional blended-model accelerator mass objective.',
          'Hypothetical layer/bond properties and generic hardware mass allowances remain fixed.',
          'Attachment count, inlet speed, material and coating thickness are fixed.',
          '250 MPa hub hoop screen, 200 GPa shaft modulus/10 micrometre deflection; payload assumptions are recorded in parameters (historical default 100 MPa/70 GPa).',
          'No global-optimality or buildability certification.'])
    (ROOT/'search_results'/f'{args.label}.json').write_text(json.dumps(output,indent=2)+'\n')
    with (ROOT/'search_results'/f'{args.label}_history.csv').open('w') as f:
        w=csv.DictWriter(f,fieldnames=list(history[0]));w.writeheader();w.writerows(history)
    print(json.dumps(dict(parameters={k:c[k] for k,_,_,_ in VARIABLES},payback_h=r['gross_operating_payback_hours'],mass_t=r['conditional_machine_mass_kg']/1000,length_m=r['corridor_length_m'],constraints=q),indent=2),flush=True)
if __name__=='__main__':main()
