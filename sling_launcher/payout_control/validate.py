"""Analytic, independent-coordinate, conservation and refinement checks."""
from dataclasses import replace
import json
import numpy as np
from scipy.integrate import solve_ivp
from .model import Config,Profile,scenarios,run,sample,anchor
from .report import OUT,metric

def main():
    c=Config();checks={}
    class Fixed:
        duration=30.
        def at(self,t):return 100.,0.,0.
    r=run(c,Fixed());t=np.linspace(0,r['end'],301);a=sample(r,t)
    exact=(c.anchor_radius_m+100)*np.c_[np.cos(c.omega*t),np.sin(c.omega*t)]
    err=float(np.max(np.linalg.norm(a[:,1:3]-exact,axis=1)))
    assert err<1e-5 and np.all(a[:,24]==1)
    expected=c.mass_kg*c.omega**2*(c.anchor_radius_m+100)
    assert np.max(abs(a[:,14]-expected))<1e-4
    checks['fixed_length_corotation_position_error_m']=err
    # Independent Cartesian taut equation, without projection or stabilization.
    p=Profile(c);r=run(c,p);t=np.linspace(0,60,301);ref=sample(r,t)
    def rhs(t,y):
        aa,av,acc=anchor(t,c);L,u,udot=p.at(t);q=y[:2]-aa;vr=y[2:]-av
        factor=(vr@vr-u*u-q@acc-L*udot)/(L*L)
        return np.r_[y[2:],-factor*q]
    cart=solve_ivp(rhs,(0,60),ref[0,1:5],method='DOP853',t_eval=t,rtol=1e-11,atol=1e-11,max_step=.02)
    err=float(np.max(np.linalg.norm(cart.y[:2].T-ref[:,1:3],axis=1)))
    assert err<.001
    checks['independent_cartesian_position_error_m']=err
    results={}
    for name,p in scenarios(c).items():
        base=run(c,p);fine=run(replace(c,max_step_s=.1,rtol=5e-11,atol=5e-12),p)
        t=np.unique(np.r_[np.linspace(0,base['end'],1201),p.duration]);a=sample(base,t);b=sample(fine,t)
        err=float(np.max(np.linalg.norm(a[:,1:3]-b[:,1:3],axis=1)))
        assert err<.002
        m=metric(base,a,name)
        assert m['energy_relative_residual']<2e-7 and m['angular_momentum_relative_residual']<2e-7
        assert np.max(a[:,9]-a[:,7])<1e-5
        assert np.min(a[:,14])>=0
        taut=a[:,24]>0;slack=~taut
        assert np.max(abs(a[taut,9]-a[taut,7]))<1e-5
        if slack.any():assert np.max(abs(a[slack,14]))==0
        assert np.max(abs(a[:,26]-c.omega*a[:,15]))<1e-5
        loaded=a[:,14]>1e-5
        lever=np.abs(a[loaded,15]/a[loaded,14]);assert np.max(lever)<=c.anchor_radius_m+1e-6
        slack_ballistic_error=0.
        for seg in base['segments']:
            if seg['mode']=='slack':
                ts=np.linspace(seg['start'],seg['end'],20);y=seg['sol'](ts);dt=ts-ts[0]
                slack_ballistic_error=max(slack_ballistic_error,float(np.max(abs(y[:2]-(y[:2,0,None]+y[2:4,0,None]*dt)))))
        assert slack_ballistic_error<1e-6
        assert len(base['events'])==len(fine['events'])
        event_error=max([abs(x['time_s']-y['time_s']) for x,y in zip(base['events'],fine['events'])] or [0.])
        assert event_error<1e-5
        results[name]=dict(refined_position_difference_m=err,event_time_difference_s=event_error,
             relative_energy_residual=m['energy_relative_residual'],relative_angular_momentum_residual=m['angular_momentum_relative_residual'],
             slack_ballistic_error_m=slack_ballistic_error,max_torque_lever_m=float(np.max(lever)))
        print(name,'passed',flush=True)
    checks['scenarios']=results
    (OUT/'validation.json').write_text(json.dumps(checks,indent=2)+'\n')
    print('All checks passed',flush=True)
if __name__=='__main__':main()
