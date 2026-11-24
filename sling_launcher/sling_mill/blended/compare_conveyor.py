"""Matched speed, loaded acceleration and useful flow; structural fiber only.

Retain the conveyor study's geometrically similar feed-wheel/hub proportions.
Scale all lengths and omega inversely to match the loaded acceleration limit.
"""
from pathlib import Path
import sys,json
from dataclasses import replace
import numpy as np
from scipy.optimize import root
P=Path(__file__).resolve().parent
sys.path.insert(0,str(P.parents[2]))
from sling_launcher.conveyor_loop.steady.model import Inputs,solve,evaluate
ref=json.loads((P/'search_results/iron_reference.json').read_text())
vtarget=ref['parameters']['v_exit'];atarget=ref['summary']['acceleration_exit_m_s2'];mdot=ref['summary']['mass_flow_kg_s']
base=Inputs();rho=1560.;allow=2.9e9

def run(q,speed_scale,u,tol=2e-6):
 c=replace(base,track_speed=speed_scale*base.station_radius/base.radius_scale,feed_speed=u,payload_per_m=q*rho*base.area)
 sol,L=solve(c,tol=tol);r,h=evaluate(c,sol,L)
 return c,sol,L,r,h

rows=[]
for u in [1.,5.,10.,20.]:
 def residual(z):
  q,V=np.exp(z);_,_,_,r,_=run(q,V,u)
  return [np.log(r['max_stress_GPa']*1e9/allow),np.log(r['release_center_speed_m_s']/vtarget)]
 fit=root(residual,np.log([.15,1600.]),tol=1e-7)
 if not fit.success:raise RuntimeError(fit.message)
 q,V=np.exp(fit.x);c,sol,L,r,h=run(q,V,u,tol=2e-8)
 # Inertial acceleration for steady flow: -omega^2 r + 2 omega u n + u^2 kappa n.
 s=h['s'];ph=h['tangent_angle'];normal=np.array([-np.sin(ph),np.cos(ph)])
 free_arc=h['arc_m'][-1];curvature=sol.sol(s,1)[2]/free_arc
 acc=-c.omega**2*h['xy_m']+2*c.omega*u*normal+u*u*curvature*normal
 # Same smooth unloading convention as source; include release until >99.995% unloaded.
 loaded=s<=c.release_center+5*c.release_width
 peak=float(np.linalg.norm(acc[:,loaded],axis=0).max())
 scale=peak/atarget
 area=mdot/(q*rho*u)
 scaled=replace(c,radius_scale=c.radius_scale*scale,station_radius=c.station_radius*scale,
  wheel_radius=c.wheel_radius*scale,area=area,payload_per_m=mdot/u)
 rr,hh=evaluate(scaled,sol,L)
 normal2=np.array([-np.sin(hh['tangent_angle']),np.cos(hh['tangent_angle'])])
 aa=-scaled.omega**2*hh['xy_m']+2*scaled.omega*u*normal2+u*u*sol.sol(s,1)[2]/hh['arc_m'][-1]*normal2
 actual_peak=float(np.linalg.norm(aa[:,loaded],axis=0).max())
 assert abs(actual_peak/atarget-1)<1e-10
 assert abs(rr['mass_flow_kg_s']/mdot-1)<1e-10
 assert abs(rr['max_stress_GPa']/r['max_stress_GPa']-1)<1e-10
 mass=rr['bare_loop_mass_kg']
 row=dict(feed_speed_m_s=u,area_m2=area,outbound_payload_to_line_density=float(q),
  release_speed_m_s=r['release_center_speed_m_s'],maximum_loaded_acceleration_m_s2=actual_peak,
  release_radius_m=r['release_center_radius_m']*scale,maximum_radius_m=r['radius_max_m']*scale,
  station_radius_m=c.station_radius*scale,wheel_radius_m=c.wheel_radius*scale,
  omega_rad_s=c.omega/scale,loop_length_m=r['length_m']*scale,
  working_stress_GPa=r['max_stress_GPa'],taper_area_ratio=1.,
  useful_arm_fiber_mass_kg=mass,opposed_pair_fiber_mass_kg=2*mass,
  useful_arm_payoff_s=mass/mdot,opposed_pair_payoff_s=2*mass/mdot,
  bvp_residual=r['bvp_residual'],force_residual=r['integrated_force_residual_scaled'])
 assert abs(row['release_speed_m_s']/vtarget-1)<2e-5
 assert abs(row['working_stress_GPa']/2.9-1)<2e-5
 rows.append(row);print(json.dumps(row),flush=True)
m=ref['masses'];fiber=sum(m[k] for k in ['structural_belts','radial_members','torque_members'])
out=dict(matched_release_speed_m_s=vtarget,matched_maximum_loaded_acceleration_m_s2=atarget,
 useful_mass_flow_kg_s=mdot,conveyor_allowable_GPa=2.9,conveyor_density_kg_m3=rho,
 mill=dict(structural_fiber_mass_kg=fiber,fiber_payoff_s=fiber/mdot,
 working_allowable_GPa=1.,peak_belt_stress_GPa=ref['summary']['maximum_belt_stress_Pa']/1e9,
 total_included_mass_kg=sum(m.values()),whole_system_payoff_s=sum(m.values())/mdot),
 cases=rows,scope='Conveyor opposed pair: useful arm plus equally loaded disposable-countermass arm; useful flow counts one arm. Mill counts all structural belts, radial and torque members in both rollers at every stage. Contact coatings and hardware excluded from both fiber totals.',
 limitations='Steady 2D similarity screen, independent of width scale; continuous loading and smoothed release. Maximum acceleration evaluated through release_center+5*release_width. No conveyor hardware, support, feed, slip, batching or catcher logistics sizing. Geometric similarity retains source feed-wheel/hub proportions; these are not optimized.')
(P/'search_results/conveyor_matched_acceleration.json').write_text(json.dumps(out,indent=2)+'\n')
