"""Fixed-geometry iron payload and height-aware hardware audit; no optimization."""
import json
from pathlib import Path
import numpy as np
from model import solve
ROOT=Path(__file__).parent
c=json.loads((ROOT/'search_results/rounded_reference.json').read_text())['parameters']
c.update(payload_density=7860.,payload_heat_capacity=450.)
s,a,m=solve(c)
v=a['v_m_s']; acc=a['acceleration_m_s2']; R=c['radius']; W=c['payload_width']; D=c['payload_depth']
pitch=R*c['pitch_over_radius']; density=v/acc/pitch
integrate=lambda z:float(np.trapezoid(z*density,v))
# Four uprights, two side portals; axial clamping and fore/aft traction load.
# Conservative cantilever columns; cross beams use same section, gusset allowance25%.
height=3*R+D+.2; span=W+.4; E=200e9; allowable=100e6; load_factor=1.5
horizontal=load_factor*2*c['friction_coefficient']*a['normal_force_per_drum_N']/4
axial=load_factor*a['lower_normal_force_N']/2
chosen=[]
for H,P0 in zip(horizontal,axial):
    P=P0
    for b in np.arange(.05,.801,.005):
        t=max(.004,b/30); A=b*b-(b-2*t)**2; I=(b**4-(b-2*t)**4)/12
        P=P0+1.25*(height+span/2)*A*7800*1.62
        if (P/A+H*height*b/(2*I)<=allowable and H*height**3/(3*E*I)<=.0001
                and P<=np.pi**2*E*I/(2*height)**2 and P0*span**3/(48*E*I)<=.00005):
            chosen.append((b,1.25*(4*height+2*span)*A*7800));break
    else:raise ValueError('No section fits audit sizing grid')
sections=np.array(chosen)
m['frames']=integrate(sections[:,1])
# Reuse straw industrial anchor. 25% installed allowance is separate from20% rating headroom.
pair_rating=2*c['friction_coefficient']*a['normal_force_per_drum_N']*a['rim_speed_m_s']*a['occupancy']/c['motor_efficiency']*1.2
m['motors']=integrate(pair_rating)/1000*4.55*1.25
# Explicit converter/cabling allowance; capacity sized to motor headroom.
m['power_electronics']=integrate(pair_rating)/1000*.5
summary=dict(s)
summary.update(conditional_machine_mass_kg=sum(m.values()),gross_operating_payback_hours=sum(m.values())/s['mass_flow_kg_s']/3600)
extra=dict(peak_acceleration_g=float(acc.max()/9.80665),payload_modulus_Pa=207e9,payload_working_allowable_Pa=70e6,
    end_load_stress_envelope_Pa=float(c['payload_density']*c['payload_length']*acc.max()),
    peak_contact_pressure_Pa=float(a['peak_contact_pressure_Pa'].max()),upper_axis_height_m=height,
    payload_axis_height_m=2*R+.2+D/2,frame_section_min_m=float(sections[:,0].min()),frame_section_max_m=float(sections[:,0].max()),
    motor_pair_rating_min_W=float(pair_rating.min()),motor_pair_rating_max_W=float(pair_rating.max()),
    motor_total_installed_rating_W=integrate(pair_rating),motor_per_drum_rating_max_W=float(pair_rating.max()/2),
    power_plant_mass_sensitivity_kg_per_kW={str(q):{'mass_kg':sum(m.values())+q*s['electrical_mean_W']/1000,'payoff_hours':(sum(m.values())+q*s['electrical_mean_W']/1000)/s['mass_flow_kg_s']/3600} for q in (0,1,5,10)})
output=dict(parameters=c,summary=summary,audit=extra,masses=m)
(ROOT/'search_results/iron_hardware_audit.json').write_text(json.dumps(output,indent=2)+'\n')
print(json.dumps({'summary':summary,'audit':extra,'masses':m},indent=2))
