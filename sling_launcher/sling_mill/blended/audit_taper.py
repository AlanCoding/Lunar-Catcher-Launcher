"""Expose the tapered drum cables already assumed by the selected calculation."""
import json,csv
from pathlib import Path
import numpy as np
from model import solve,contact,RHO
P=Path(__file__).parent
c=json.loads((P/'search_results/iron_reference.json').read_text())['parameters']
s,a,m=solve(c);R=c['radius'];h=R*c['hub_ratio'];W=c['payload_width'];n=c['attachments'];sigma=c['working_stress_Pa']
ell=2*R*np.sin(np.pi/n);rows=[]
for v in (100.,400.,800.,1200.,1600.):
    u=float(np.interp(v,a['v_m_s'],a['rim_speed_m_s']))
    N,T,dc,db,patch,lam,lower,upper=contact(u,c)
    radial=lam*u*u*ell/R-2*T*np.sin(np.pi/n)
    torque=c['friction_coefficient']*lower/c['hub_ratio']/c['torque_members_effective']
    floor=RHO*u*u*(1-(h/R)**2)/2;ratio=np.exp(floor/sigma)
    rt=radial/sigma;rr=rt*ratio;tt=torque/sigma;tr=tt*ratio
    rows.append(dict(payload_speed_m_s=v,rim_speed_m_s=u,rpm=u/R*60/(2*np.pi),
        belt_stress_GPa=T/(W*c['structural_belt_thickness_m'])/1e9,
        self_stress_uniform_GPa=floor/1e9,root_tip_area_ratio=ratio,root_tip_diameter_ratio=np.sqrt(ratio),
        radial_tip_load_N=radial,radial_tip_area_mm2=rt*1e6,radial_root_area_mm2=rr*1e6,
        radial_tip_diameter_mm=1000*np.sqrt(4*rt/np.pi),radial_root_diameter_mm=1000*np.sqrt(4*rr/np.pi),
        torque_tip_load_N=torque,torque_tip_area_mm2=tt*1e6,torque_root_area_mm2=tr*1e6,
        torque_tip_diameter_mm=1000*np.sqrt(4*tt/np.pi),torque_root_diameter_mm=1000*np.sqrt(4*tr/np.pi),
        radial_root_area_fraction=n*rr/(2*np.pi*h*W),minimum_radial_root_band_width_m=n*rr/(2*np.pi*h)))
out=dict(parameters=dict(radius_m=R,hub_radius_m=h,belt_width_m=W,attachments=n,working_stress_Pa=sigma,density_kg_m3=RHO),stages=rows,
        taper_law='A(r)/A(R)=exp[rho*omega^2*(R^2-r^2)/(2*sigma)]',
        limitations=['Straight radial cable self-mass integration; non-radial torque cables require transverse support/shape closure.',
        'Equivalent circular diameters describe area only; packed ribbon/termination design unresolved.',
        'Radial root packing fraction is an ideal solid-area lower bound; torque cables and terminations need additional space.'])
(P/'search_results/drum_taper_audit.json').write_text(json.dumps(out,indent=2)+'\n')
with (P/'search_results/drum_taper_audit.csv').open('w') as f:
    w=csv.DictWriter(f,fieldnames=rows[0].keys());w.writeheader();w.writerows(rows)
print(json.dumps(out,indent=2))
