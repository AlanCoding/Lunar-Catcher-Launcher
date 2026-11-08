"""Material-independent stress/mass frontier at fixed flow and release speed."""
import json
import numpy as np
from scipy.integrate import quad
from scipy.interpolate import PchipInterpolator
from scipy.optimize import brentq
from .compare import OUT,BASE,REF,OMEGA,SPEED,PERIOD,MDOT,geometry

def taper_ratio(kappa):
    a=BASE.station_radius;R=REF['release_radius_m']
    return OMEGA**2*R/kappa*quad(lambda r:np.exp(OMEGA**2*(R*R-r*r)/(2*kappa)),a,R,epsabs=1e-7)[0]

def main():
    curves=[]
    for u in [2.,5.,10.]:
        rows=[];R=REF['release_radius_m']
        for q in [0,.003,.007,.015,.03,.06,.1,.18,.3,.5,.8,1.2,1.6]:
            for it in range(7):
                *_,r,h=geometry(q,R,u,1560.)
                err=r['release_center_speed_m_s']/SPEED-1
                if abs(err)<2e-8:break
                R/=1+err
            assert abs(err)<2e-8
            assert r['integrated_force_residual_scaled']<1e-5
            k=r['max_stress_GPa']*1e9/1560
            # C/(u*q) has units seconds, and is independent of density.
            weight=None if q==0 else r['length_m']/(u*q)
            rows.append(dict(q=q,specific_stress_J_kg=k,mass_per_flow_s=weight,
                tether_mass_kg=None if q==0 else MDOT*weight,
                spool_tether_mass_kg=MDOT*PERIOD*taper_ratio(k),
                equal_mass_spool_cycle_s=None if q==0 else weight/taper_ratio(k),
                radius_scale_m=R,release_speed_m_s=r['release_center_speed_m_s']))
        finite=rows[1:];xs=[x['specific_stress_J_kg'] for x in finite]
        # Interpolate q and length-related coefficient separately, resolving pole at q=0.
        qi=PchipInterpolator([x['specific_stress_J_kg'] for x in rows],[x['q'] for x in rows])
        ci=PchipInterpolator([x['specific_stress_J_kg'] for x in rows],
            [r['mass_per_flow_s']*r['q'] if r['q'] else rows[1]['mass_per_flow_s']*rows[1]['q'] for r in rows])
        def massweight(k): return float(ci(k)/qi(k))
        crossings=[]
        for period in [1800.,3600.,PERIOD]:
            lo=xs[0];hi=xs[-1]
            f=lambda k:massweight(k)-period*taper_ratio(k)
            k=brentq(f,lo,hi) if f(lo)*f(hi)<0 else None
            crossings.append(dict(spool_cycle_s=period,specific_stress_J_kg=k))
        curves.append(dict(feed_m_s=u,rows=rows,crossings=crossings))
        (OUT/'stress_frontier.json').write_text(json.dumps(dict(mdot_kg_s=MDOT,release_speed_m_s=SPEED,
            reference_cycle_s=PERIOD,curves=curves),indent=2)+'\n')
        print(u,'floor',rows[0]['specific_stress_J_kg']/1e6,'crossings',crossings,flush=True)
    # Compare interpolation against the independently solved prior 2.9 GPa cases.
    old=json.loads((OUT/'comparison.json').read_text())
    checks=[]
    for c in curves:
        rows=c['rows'];qi=PchipInterpolator([r['specific_stress_J_kg'] for r in rows],[r['q'] for r in rows])
        prior=next(r['conveyor'] for r in old['rows'] if r['material']=='zylon' and r['feed_m_s']==c['feed_m_s'])
        error=abs(float(qi(2.9e9/1560))/prior['outbound_payload_to_line_density']-1)
        assert error<.002
        checks.append(dict(feed_m_s=c['feed_m_s'],interpolated_q_relative_error=error))
    assert abs(taper_ratio(2.9e9/1560)-old['rows'][2]['spool']['tether_to_batch_mass_ratio'])<1e-7
    # Directly verify the interpolated 5 m/s, reference-cadence crossing.
    curve=curves[1];r=curve['rows'];k=curve['crossings'][-1]['specific_stress_J_kg']
    q=float(PchipInterpolator([v['specific_stress_J_kg'] for v in r],[v['q'] for v in r])(k))
    R=r[0]['radius_scale_m']
    for _ in range(4):
        *_,v,h=geometry(q,R,5.,1560.);R*=SPEED/v['release_center_speed_m_s']
    actualk=v['max_stress_GPa']*1e9/1560
    ratio=(v['length_m']/(5*q))/(PERIOD*taper_ratio(actualk))
    assert abs(ratio-1)<.002 and abs(actualk/k-1)<.002
    checks.append(dict(crossover_check_feed_m_s=5,computed_specific_stress_J_kg=actualk,
                       conveyor_over_spool_mass=float(ratio)))
    (OUT/'frontier_validation.json').write_text(json.dumps(checks,indent=2)+'\n')

if __name__=='__main__':main()
