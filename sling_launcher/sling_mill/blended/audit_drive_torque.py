"""Expose payload-acceleration torque already present in the blended drum model."""
from pathlib import Path
import json,numpy as np
from model import solve,contact
P=Path(__file__).parent
c=json.loads((P/'search_results/iron_reference.json').read_text())['parameters']
r,a,m=solve(c);R=c['radius'];h=R*c['hub_ratio'];k=c['torque_members_effective'];mu=c['friction_coefficient'];rows=[]
for v in (100.,400.,800.,1200.,1600.):
 u=float(np.interp(v,a['v_m_s'],a['rim_speed_m_s']));N,T,dc,db,patch,lam,lower,upper=contact(u,c)
 Ft=mu*lower;tau=Ft*R;omega=u/R;Tc=Ft/(c['hub_ratio']*k)
 wall=float(np.interp(v,a['v_m_s'],a['hub_wall_m']));I=np.pi/4*(h**4-max(h-wall,0)**4)
 row=dict(payload_speed_m_s=v,rim_speed_m_s=u,lower_drum_normal_force_N=lower,
  lower_drum_forward_traction_N=Ft,lower_drum_contact_torque_Nm=tau,
  lower_drum_peak_mechanical_W=Ft*u,lower_drum_instant_payload_power_W=Ft*v,
  lower_drum_instant_slip_heat_W=Ft*(u-v),torque_member_tension_at_rim_N=Tc,
  torque_member_inward_component_N=Tc*np.sqrt(1-c['hub_ratio']**2),
  torque_member_tangential_component_N=Tc*c['hub_ratio'],
  shaft_torsional_shear_MPa=tau*h/(2*I)/1e6,
  hub_rotational_stress_benchmark_MPa=c['hub_density']*(u*c['hub_ratio'])**2/1e6)
 assert np.isclose(k*Tc*h,tau) and np.isclose(row['lower_drum_peak_mechanical_W']/omega,tau)
 rows.append(row)
out=dict(parameters=dict(roller_radius_m=R,hub_radius_m=h,torque_members_effective=k,attachments=c['attachments']),stages=rows,
 scope='Peak loaded contact for the lower drum. Motor mean rating is lower when occupancy is below one; rotor storage supplies the difference. Eight-way peak sharing is assumed rather than solved.')
(P/'search_results/drive_torque_audit.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(rows[-1],indent=2))
