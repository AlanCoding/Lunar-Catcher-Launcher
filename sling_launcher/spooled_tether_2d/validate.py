"""Local mechanics checks and convergence comparison for saved shape histories."""
from dataclasses import replace
import json
import numpy as np
from scipy.integrate import solve_ivp,quad
from .model import Config,Tether
from .run import OUT

def main():
    c=Config(nodes=24,axial_relaxation_s=0.,rtol=2e-8,atol=1e-5)
    m=Tether(c);load=c.payload+c.retained_tip_mass;z=m.initial(m.L,load)
    accel=float(np.max(abs(m.rhs(0,z,'loaded_hold',load))))
    assert accel<1e-5
    z=z.reshape(-1,4);z[:,1]=5*np.sin(np.pi*m.xi[1:]);z=z.ravel()
    sol=solve_ivp(lambda t,z:m.rhs(t,z,'loaded_hold',load),[0,20],z,method='Radau',jac_sparsity=m.sparsity,rtol=c.rtol,atol=c.atol,max_step=.1,t_eval=np.linspace(0,20,401))
    assert sol.success
    energies=[]
    for t,y in zip(sol.t,sol.y.T):
        f=m.fields(t,y,'loaded_hold',load)
        E=.5*np.sum(f['mass']*(np.sum(f['V'][1:]**2,axis=1)-m.w**2*np.sum(f['X'][1:]**2,axis=1)))
        E+=.5*np.sum(m.c.modulus*f['area']*np.maximum(f['strain'],0)**2)*m.L/m.n
        energies.append(E)
    drift=float(np.ptp(energies)/abs(energies[0]));assert drift<1e-5
    checks=dict(static_discrete_equilibrium_max_acceleration=accel,fixed_length_undamped_rotating_energy_relative_drift=drift)
    # Manufactured advection patch: X(s)=s is stationary in material coordinates.
    xi=np.linspace(0,1,20);q=2345.;qd=3.;qdd=.01
    w=(1-xi)*qd/q;beta=(1-xi)*(qdd/q-2*qd**2/q**2)
    error=float(np.max(abs((xi-1)*qdd+2*w*qd+beta*q)))
    assert error<1e-12;checks['moving_coordinate_acceleration_patch_error']=error
    profile_checks={}
    for profile in ['quintic','early_cruise','front_loaded']:
        model=Tether(Config(payout_profile=profile))
        T=model.c.travel_s
        assert abs(model.motion(0,'extend')[0]-model.c.initial_length)<1e-9
        assert abs(model.motion(T,'extend')[0]-model.L)<1e-8
        assert abs(model.motion(T,'extend')[1])<1e-10
        for t in [10.,100.,500.,1200.]:
            h=.001;q,v,a=model.motion(t,'extend')
            qm,vm,_=model.motion(t-h,'extend');qp,vp,_=model.motion(t+h,'extend')
            assert abs((qp-qm)/(2*h)-v)<1e-5
            assert abs((vp-vm)/(2*h)-a)<1e-7
        profile_checks[profile]='endpoint and finite-difference derivative checks passed'
    checks['payout_profiles']=profile_checks
    for name in ['kevlar_1p5GPa','kevlar_ratio3','kevlar_early_cruise','kevlar_front_loaded']:
        path=OUT/f'{name}_n32.npz'
        if not path.exists():continue
        data=np.load(path);assert np.isfinite(data['xy_m']).all() and np.isfinite(data['stress_Pa']).all()
    a=OUT/'kevlar_1p5GPa_n32.npz';b=OUT/'kevlar_1p5GPa_n64.npz'
    if a.exists() and b.exists():
        lo=np.load(a);hi=np.load(b);values=[]
        for phase in ['extend','loaded_hold','release_settle','retract','final_hold']:
            il=lo['phase']==phase;ih=hi['phase']==phase
            if not il.any() or not ih.any():continue
            t=lo['time_s'][il];valid=t<=hi['time_s'][ih][-1];t=t[valid]
            # Physical-node tip comparison at identical times, independent of mesh count.
            tiplo=lo['xy_m'][il,-1][valid];tiphi=np.column_stack([np.interp(t,hi['time_s'][ih],hi['xy_m'][ih,-1,k]) for k in range(2)])
            alo=lo['tip_angle_deg'][il][valid];ahi=np.interp(t,hi['time_s'][ih],hi['tip_angle_deg'][ih])
            values.append(dict(phase=phase,max_tip_position_difference_m=float(np.linalg.norm(tiplo-tiphi,axis=1).max()),
                              max_tip_angle_difference_deg=float(np.max(abs(alo-ahi))),
                              coarse_peak_stress_GPa=float(lo['stress_Pa'][il].max()/1e9),fine_peak_stress_GPa=float(hi['stress_Pa'][ih].max()/1e9)))
        checks['mesh_and_integrator_comparison']=values
    (OUT/'validation.json').write_text(json.dumps(checks,indent=2)+'\n');print(json.dumps(checks,indent=2))
if __name__=='__main__':main()
