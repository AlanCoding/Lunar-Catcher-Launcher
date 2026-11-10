"""Ideal signed shaft powers for radial payout and return of a tapered pair.

Rigid co-rotation is imposed, not dynamically demonstrated. Opposed 1000 kg
loads release together. This module does not simulate cable angles or waves.
"""
from dataclasses import dataclass,asdict
import numpy as np
from scipy.integrate import cumulative_trapezoid,quad
from scipy.optimize import brentq
from ..architecture_comparison.compare import BASE,REF,OMEGA,PERIOD,SPEED

@dataclass
class Case:
    payload_kg: float=1000.
    counterweight_kg: float=1000.
    tether_to_payload_mass: float=3.
    density_kg_m3: float=1450.
    period_s: float=PERIOD
    travel_s: float=PERIOD/5
    loading_s: float=300.
    minimum_hold_s: float=300.
    count: int=15

class Model:
    def __init__(self,c=Case(),nodes=30001):
        self.c=c;self.a=BASE.station_radius;self.R=REF['release_radius_m'];self.L=self.R-self.a;self.w=OMEGA
        def ratio(k):return self.w**2*self.R/k*quad(lambda r:np.exp(self.w**2*(self.R**2-r*r)/(2*k)),self.a,self.R)[0]
        self.kappa=brentq(lambda k:ratio(k)-c.tether_to_payload_mass,1e5,1e8)
        self.s=np.linspace(0,self.L,nodes)
        self.lam=c.payload_kg*self.w**2*self.R/self.kappa*np.exp(self.w**2*(self.R**2-(self.a+self.s)**2)/(2*self.kappa))
        self.mom=[cumulative_trapezoid(self.lam*self.s**k,self.s,initial=0) for k in range(3)]
        self.mass=self.mom[0][-1]
        assert c.counterweight_kg==c.payload_kg,'This first model assumes an exactly symmetric pair.'
    def motion(self,t,start,duration,reverse=False):
        x=np.clip((t-start)/duration,0,1)
        f=10*x**3-15*x**4+6*x**5
        fd=(30*x*x-60*x**3+30*x**4)/duration
        fdd=(60*x-180*x*x+120*x**3)/duration**2
        if reverse:return self.L*(1-f),-self.L*fd,-self.L*fdd
        return self.L*f,self.L*fd,self.L*fdd
    def powers(self,q,qd,qdd,load):
        start=self.L-q
        m0,m1,m2=[f[-1]-np.interp(start,self.s,f) for f in self.mom]
        shift=self.a-start;J1=shift*m0+m1
        I=2*((self.mass-m0)*self.a**2+shift**2*m0+2*shift*m1+m2+load*(self.a+q)**2)
        Ip=4*(J1+load*(self.a+q));Mr=2*(m0+load)
        Mrp=2*np.interp(start,self.s,self.lam)
        hub=Ip*qd*self.w**2
        spool=(Mr*qdd+.5*Mrp*qd**2-.5*Ip*self.w**2)*qd
        energy=.5*I*self.w**2+.5*Mr*qd**2
        return hub,spool,energy
    def single(self,t):
        c=self.c;t=np.asarray(t)%c.period_s
        out=c.loading_s;release=out+c.travel_s+c.minimum_hold_s;ret=release
        q,qd,qdd=self.motion(t,out,c.travel_s)
        after=t>=ret
        qr,vr,ar=self.motion(t,ret,c.travel_s,True)
        q=np.where(after,qr,q);qd=np.where(after,vr,qd);qdd=np.where(after,ar,qdd)
        load=np.where((t>=out)&(t<release),c.payload_kg,0.)
        h,s,e=self.powers(q,qd,qdd,load)
        return dict(q_m=q,qdot_m_s=qd,hub_W=h,spool_W=s,energy_J=e,loaded=load>0)
    def synchronized(self,t,j):
        """Four-window spool cycle; 15 jobs/window, with 60 reusable pairs.

        Retraction and extension each take one window. Completed payloads wait
        for a common release; empty extended cables wait for their return slot.
        """
        c=self.c; T=c.period_s; cycle=4*T; start=j*T/c.count
        phase=(np.asarray(t)-start)%cycle
        out=T+c.loading_s; end=out+T
        release=np.ceil((start+end+c.minimum_hold_s)/T)*T-start
        assert end <= release < cycle
        q,qd,qdd=self.motion(phase,0,T,True)
        qo,vo,ao=self.motion(phase,out,T)
        after=phase>=out
        q=np.where(after,qo,q);qd=np.where(after,vo,qd);qdd=np.where(after,ao,qdd)
        load=np.where(after & (phase<release),c.payload_kg,0.)
        h,s,e=self.powers(q,qd,qdd,load)
        return dict(q_m=q,qdot_m_s=qd,hub_W=h,spool_W=s,energy_J=e,loaded=load>0,
                    retract_start_s=start,payout_start_s=start+out,
                    release_s=start+release,loaded_hold_s=release-end,
                    empty_hold_s=cycle-release)
    def metadata(self):
        return dict(inputs=asdict(self.c),omega_rad_s=self.w,track_radius_m=self.a,tip_radius_m=self.R,
           release_speed_m_s=SPEED,tether_mass_per_arm_kg=self.mass,tether_mass_per_pair_kg=2*self.mass,
           specific_working_stress_J_kg=self.kappa,working_stress_Pa=self.kappa*self.c.density_kg_m3,
           taper_root_to_tip_area=float(self.lam[0]/self.lam[-1]),
           loading_energy_per_pair_J=self.c.payload_kg*(self.w*self.a)**2,
           released_energy_per_pair_J=self.c.payload_kg*(self.w*self.R)**2)
