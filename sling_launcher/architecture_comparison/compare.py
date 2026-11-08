"""Matched-throughput, matched-release-speed tether-material screen.

Reuses conveyor free-turn BVP and original tapered Cable sizing, in a common
horizontal, quasi-static comparison. This is not complete machinery sizing.
"""
from pathlib import Path
from dataclasses import replace
import json
import numpy as np
from scipy.optimize import root, brentq
from ..conveyor_loop.steady.model import Inputs, solve, evaluate
from ..cable_shape import Cable
from ..environment import LunarEnvironment
from ..orbit import point_surface_reference

OUT=Path(__file__).parent/'results'
REFERENCE=Path(__file__).parents[1]/'publication/candidate_50g.json'
REF=json.loads(REFERENCE.read_text())
BASE=Inputs()
OMEGA=BASE.omega
SPEED=OMEGA*REF['release_radius_m']
PERIOD=point_surface_reference(LunarEnvironment(),20000)['site_revisit_s']
MDOT=1000/PERIOD


def geometry(q,radius,u,rho,tol=2e-6):
    c=replace(BASE,radius_scale=radius,feed_speed=u,density=rho,payload_per_m=q*rho*BASE.area)
    sol,L=solve(c,tol=tol)
    row,h=evaluate(c,sol,L)
    return c,sol,L,row,h


def conveyor(u,rho,allow):
    # First measure the matched-speed unloaded floor, independent of cross-section.
    rad=REF['release_radius_m']
    for _ in range(4):
        *_,r,h=geometry(0,rad,u,rho)
        rad*=SPEED/r['release_center_speed_m_s']
    *_,empty,h=geometry(0,rad,u,rho)
    floor=empty['max_stress_GPa']*1e9
    if floor>=allow:
        return dict(status='no finite area below self-stress floor',feed_m_s=u,density_kg_m3=rho,
                    allowance_Pa=allow,unloaded_stress_Pa=floor),None
    def residual(z):
        q=np.exp(z[0]);R=np.exp(z[1]); *_,r,h=geometry(q,R,u,rho)
        return [np.log(r['max_stress_GPa']*1e9/allow),np.log(r['release_center_speed_m_s']/SPEED)]
    fit=root(residual,np.log([max(.01,(allow/floor-1)),rad]),tol=2e-7)
    assert fit.success,fit.message
    q,R=np.exp(fit.x);c,sol,L,r,h=geometry(q,R,u,rho)
    # Linear scaling: fixed q preserves shape; select area to match mean flow.
    factor=MDOT/r['mass_flow_kg_s']
    c=replace(c,area=c.area*factor,payload_per_m=c.payload_per_m*factor)
    r,h=evaluate(c,sol,L)
    assert abs(r['mass_flow_kg_s']/MDOT-1)<1e-10
    assert abs(r['release_center_speed_m_s']/SPEED-1)<1e-6
    assert abs(r['max_stress_GPa']*1e9/allow-1)<1e-6
    r.update(status='strength-sized steady screen',feed_m_s=u,density_kg_m3=rho,allowance_Pa=allow,
         unloaded_stress_Pa=floor,outbound_payload_to_line_density=q,
         material_mass_kg=r['bare_loop_mass_kg'],mass_per_throughput_s=r['bare_loop_mass_kg']/MDOT,
         fiber_volume_m3=r['bare_loop_mass_kg']/rho,area_mm2=c.area*1e6)
    return r,h


def spool(rho,allow):
    cable=Cable(BASE.station_radius,REF['release_radius_m'],OMEGA,1000,0.,rho,allow,nodes=4001)
    # Direct force integration at release, independent of taper ODE.
    s=cable.s;r=BASE.station_radius+s;lam=cable.lam
    from scipy.integrate import cumulative_trapezoid
    j=cumulative_trapezoid(lam*r,s,initial=0)
    stress=(1000*OMEGA**2*r[-1]+OMEGA**2*(j[-1]-j))*rho/lam
    residual=float(np.max(np.abs(stress/allow-1)))
    assert residual<1e-6
    return dict(material_mass_kg=cable.mass,fiber_volume_m3=cable.mass/rho,
        payload_batch_kg=1000,mean_flow_kg_s=MDOT,cycle_s=PERIOD,release_speed_m_s=SPEED,
        allowance_Pa=allow,peak_quasistatic_stress_Pa=allow,
        mass_per_throughput_s=cable.mass/MDOT,tether_to_batch_mass_ratio=cable.mass/1000,
        root_area_mm2=float(lam[0]/rho*1e6),tip_area_mm2=float(lam[-1]/rho*1e6),
        taper_area_ratio=float(lam[0]/lam[-1]),force_integral_relative_error=residual)


def main():
    OUT.mkdir(exist_ok=True)
    cases=[('zylon',1560.,2.9e9,u) for u in [1.,2.,5.,10.,20.]]
    cases += [('zylon_low_allowance',1560.,2.5e9,5.),('zylon_high_allowance',1560.,3.5e9,5.),
              ('kevlar',1450.,1.5e9,5.),('legacy_kevlar',1450.,1e9,5.)]
    rows=[]
    for material,rho,allow,u in cases:
        conv,h=conveyor(u,rho,allow);sp=spool(rho,allow)
        row=dict(name=f'{material}_{u:g}',material=material,density_kg_m3=rho,allowance_Pa=allow,feed_m_s=u,spool=sp,conveyor=conv)
        if h is not None:
            row['conveyor_over_spool_mass']=conv['material_mass_kg']/sp['material_mass_kg']
            row['crossover_spool_cycle_s']=conv['mass_per_throughput_s']/sp['tether_to_batch_mass_ratio']
            np.savez_compressed(OUT/f'{row["name"]}.npz',**h)
        rows.append(row)
        print(row['name'],sp['material_mass_kg'],conv.get('material_mass_kg',conv['status']),flush=True)
    # Independent comparison with the frozen finite-gravity published cable mass.
    legacy=Cable(BASE.station_radius,REF['release_radius_m'],OMEGA,1000,LunarEnvironment().surface_gravity_m_s2,1450,1e9)
    regression=abs(2*legacy.mass/REF['masses_kg']['outward_cables']-1)
    assert regression<1e-4
    ref=rows[2]['conveyor'];q=ref['outbound_payload_to_line_density'];R=ref['inputs']['radius_scale']
    _,_,_,fine,_=geometry(q,R,5,1560,tol=2e-8)
    refinement=abs(fine['max_stress_GPa']/ref['max_stress_GPa']-1)
    assert refinement<1e-6
    report=dict(scope='per useful-payload arm; active-operation mean transport, not catcher delivery',
                matched_mean_flow_kg_s=MDOT,matched_release_speed_m_s=SPEED,omega_rad_s=OMEGA,
                spool_cycle_s=PERIOD,spool_loading_s=300,spool_buffer_s=300,
                spool_payout_s=(PERIOD-600)/2,spool_retraction_s=(PERIOD-600)/2,
                rows=rows,checks=dict(published_cable_mass_relative_difference=regression,
                    conveyor_reference_stress_refinement_relative_difference=refinement),
                sources=['../publication/candidate_50g.json','../cable_shape.py','../spooling_cycle.py',
                         '../conveyor_loop/steady/model.py','../conveyor_loop/steady/README.md'])
    (OUT/'comparison.json').write_text(json.dumps(report,indent=2)+'\n')
    # A same-mass check avoids making stress comparison solely allowance-by-construction.
    budget=rows[2]['spool']['material_mass_kg']
    def same_mass_at_q(q,final=False):
        R=REF['release_radius_m']
        for _ in range(4):
            *_,r,h=geometry(q,R,5,1560);R*=SPEED/r['release_center_speed_m_s']
        c,sol,L,r,h=geometry(q,R,5,1560)
        c=replace(c,area=MDOT/(q*1560*5),payload_per_m=MDOT/5)
        r,h=evaluate(c,sol,L)
        return r if final else r['bare_loop_mass_kg']-budget
    qmass=brentq(same_mass_at_q,.03,1.,xtol=1e-8)
    matched=same_mass_at_q(qmass,True)
    (OUT/'same_mass.json').write_text(json.dumps(dict(material='Zylon HM',spool_peak_Pa=2.9e9,
        common_material_mass_kg=budget,conveyor=matched),indent=2)+'\n')
    print('same mass conveyor stress',matched['max_stress_GPa'],flush=True)

if __name__=='__main__':main()
