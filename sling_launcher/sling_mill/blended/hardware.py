"""Height-aware frame and drive mass model shared by the iron search.
Continuous fabricated hollow sections; fixed assumptions from hardware_audit.py.
"""
import numpy as np

def update(c,r,a,m):
    v=a['v_m_s'];R=c['radius'];W=c['payload_width'];D=c['payload_depth']
    density=v/a['acceleration_m_s2']/(R*c['pitch_over_radius'])
    total=lambda z:float(np.trapezoid(z*density,v))
    height=3*R+D+.2;span=W+.4;E=200e9
    H=1.5*2*c['friction_coefficient']*a['normal_force_per_drum_N']/4
    P0=1.5*a['lower_normal_force_N']/2
    def section(b):
        wall=np.maximum(.004,b/30);area=b*b-(b-2*wall)**2;I=(b**4-(b-2*wall)**4)/12
        P=P0+1.25*(height+span/2)*area*7800*1.62
        demand=np.maximum.reduce([(P/area+H*height*b/(2*I))/100e6,
            H*height**3/(3*E*I)/.0001,P/(np.pi**2*E*I/(2*height)**2),
            P0*span**3/(48*E*I)/.00005])
        return demand,area
    lo=np.full_like(v,.05);hi=np.full_like(v,8.)
    if np.max(section(hi)[0])>1:raise ValueError('Frame section exceeds 8 m numerical bracket')
    for _ in range(30):
        mid=(lo+hi)/2;bad=section(mid)[0]>1
        lo=np.where(bad,mid,lo);hi=np.where(bad,hi,mid)
    m=dict(m);m['frames']=total(1.25*(4*height+2*span)*section(hi)[1]*7800)
    peak=2*c['friction_coefficient']*a['normal_force_per_drum_N']*a['rim_speed_m_s']
    mean=peak*a['occupancy']
    rating=(mean+c['motor_pulse_fraction']*(peak-mean))/c['motor_efficiency']*1.2
    m['motors']=total(rating)/1000*4.55*1.25
    m['power_electronics']=total(rating)/1000*.5
    if c.get('solar_full_sun',False):
        m['solar_array']=r['electrical_mean_W']*c.get('solar_headroom',1.2)/c.get('solar_W_per_kg',100.)
    r=dict(r);r.update(conditional_machine_mass_kg=sum(m.values()),gross_operating_payback_hours=sum(m.values())/r['mass_flow_kg_s']/3600)
    a.update(frame_section_width_m=hi,motor_pair_rating_W=rating)
    return r,a,m
