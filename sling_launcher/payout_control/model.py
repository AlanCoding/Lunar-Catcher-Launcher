"""Point mass on a massless unilateral, prescribed-length cable.

Taut motion uses attachment-centered polar coordinates. Slack motion is free
Cartesian flight. No elasticity, segment shapes, gravity or drag are modeled.
"""
from dataclasses import dataclass,asdict
from pathlib import Path
import json
import numpy as np
from numpy.polynomial import Polynomial as Poly
from scipy.integrate import solve_ivp

@dataclass
class Config:
    anchor_radius_m:float=76.78937039996255
    anchor_speed_m_s:float=22.352
    mass_kg:float=1000.
    initial_length_m:float=100.
    final_length_m:float=5787.088393934127-76.78937039996255
    hold_revolutions:float=2.
    max_step_s:float=.2
    rtol:float=2e-10
    atol:float=2e-11
    @property
    def omega(self):return self.anchor_speed_m_s/self.anchor_radius_m

class Profile:
    """Analytic smooth-start/stop payout; linear speed bias across the run."""
    def __init__(self,cfg,mean_speed=5.,bias=0.,ramp=20.):
        self.l0=cfg.initial_length_m;self.l1=cfg.final_length_m
        self.duration=(self.l1-self.l0)/mean_speed+ramp
        self.mean_speed=mean_speed;self.bias=bias;self.ramp=ramp
        self.bounds=[0.,ramp,self.duration-ramp,self.duration]
        self.vel=[];self.pos=[];offset=self.l0
        for i,(a,b) in enumerate(zip(self.bounds[:-1],self.bounds[1:])):
            t=Poly([a,1.]);z=Poly([0.,1/ramp]) if i==0 else (self.duration-t)/ramp
            window=3*z*z-2*z*z*z if i!=1 else Poly([1.])
            v=mean_speed*(1+bias*(2*t/self.duration-1))*window
            integ=v.integ();integ=integ+(offset-integ(0))
            offset=float(integ(b-a));self.vel.append(v);self.pos.append(integ)
        assert abs(offset-self.l1)<1e-6
    def at(self,t):
        if t<=0:return self.l0,0.,0.
        if t>=self.duration:return self.l1,0.,0.
        i=int(np.searchsorted(self.bounds,t,side='right')-1);u=t-self.bounds[i]
        return float(self.pos[i](u)),float(self.vel[i](u)),float(self.vel[i].deriv()(u))
    def metadata(self):return dict(duration_s=self.duration,plateau_mean_speed_m_s=self.mean_speed,bias=self.bias,ramp_s=self.ramp)

def anchor(t,c):
    th=c.omega*t;e=np.array([np.cos(th),np.sin(th)])
    a=c.anchor_radius_m*e;v=c.omega*np.array([-a[1],a[0]])
    return a,v,-c.omega**2*a

def taut_values(t,z,c,p):
    phi,w=z[:2];L,u,udot=p.at(t);a,av,aa=anchor(t,c)
    n=np.array([np.cos(phi),np.sin(phi)]);q=np.array([-n[1],n[0]])
    x=a+L*n;v=av+u*n+L*w*q
    T=c.mass_kg*(L*w*w-n@aa-udot)
    return x,v,T,n,q,L,u,aa,av

def run(c,p):
    end=p.duration+c.hold_revolutions*2*np.pi/c.omega
    # phi, phi_dot, drive work, spool work, cumulative hub torque impulse
    z=np.array([0.,c.omega,0.,0.,0.]);mode='taut';now=0.;segments=[];events=[]
    lost=0.;impact_work=0.;impact_H=0.
    for iteration in range(1000):
        if now>=end-1e-8:break
        start=now
        if mode=='taut':
            def rhs(t,y):
                x,v,T,n,q,L,u,aa,av=taut_values(t,y,c,p)
                F=-T*n;torque=x[0]*F[1]-x[1]*F[0]
                return [y[1],(-aa@q-2*u*y[1])/L,F@av,-T*u,torque]
            def boundary(t,y):
                val=taut_values(t,y,c,p)[2]/c.mass_kg
                if t-start<1e-8:return max(val,1e-9)
                return val
            boundary.terminal=True;boundary.direction=-1
        else:
            # x,y,vx,vy,drive work,spool work,angular impulse integral
            def rhs(t,y):return [y[2],y[3],0.,0.,0.,0.,0.]
            def boundary(t,y):
                a,_,_=anchor(t,c);L,_,_=p.at(t);gap=np.linalg.norm(y[:2]-a)-L
                if t-start<1e-8:return min(gap,-1e-9)
                return gap
            boundary.terminal=True;boundary.direction=1
        sol=solve_ivp(rhs,(now,end),z,method='DOP853',events=boundary,dense_output=True,
                      rtol=c.rtol,atol=c.atol,max_step=c.max_step_s)
        if not sol.success:raise RuntimeError(sol.message)
        segments.append(dict(start=now,end=float(sol.t[-1]),mode=mode,sol=sol.sol,lost=lost,impact_work=impact_work,impact_H=impact_H))
        now=float(sol.t[-1]);z=sol.y[:,-1]
        if now>=end-1e-8:break
        if mode=='taut':
            x,v,T,n,q,L,u,aa,av=taut_values(now,z,c,p)
            events.append(dict(time_s=now,event='slack',tension_n=float(T)))
            z=np.r_[x,v,z[2:]];mode='slack'
        else:
            a,av,aa=anchor(now,c);L,u,_=p.at(now);n=(z[:2]-a)/L;n/=np.linalg.norm(n)
            q=np.array([-n[1],n[0]]);closing=float((z[2:4]-av)@n-u)
            assert closing>-1e-5
            closing=max(closing,0.);impulse=-c.mass_kg*closing*n
            v=z[2:4]+impulse/c.mass_kg
            diss=.5*c.mass_kg*closing**2
            drive_imp=float(impulse@av);spool_imp=float((impulse@n)*u)
            h_imp=float(z[0]*impulse[1]-z[1]*impulse[0])
            lost+=diss;impact_work+=drive_imp+spool_imp;impact_H+=h_imp
            events.append(dict(time_s=now,event='retension',relative_closing_speed_m_s=closing,
                               impulse_n_s=float(np.linalg.norm(impulse)),dissipated_j=diss,
                               drive_impulse_work_j=drive_imp,spool_impulse_work_j=spool_imp))
            phi=np.arctan2(n[1],n[0]);w=float((v-av)@q/L)
            z=np.r_[phi,w,z[4:]];mode='taut'
            if taut_values(now,z,c,p)[2]<0:
                z=np.r_[a+L*n,v,z[2:]];mode='slack'
    else:raise RuntimeError('Too many mode changes')
    return dict(config=c,profile=p,segments=segments,events=events,end=end)

def sample(result,times):
    c=result['config'];p=result['profile'];ends=np.array([s['end'] for s in result['segments']]);rows=[]
    for t in times:
        seg=result['segments'][min(np.searchsorted(ends,t,side='right'),len(ends)-1)]
        z=seg['sol'](t);a,av,aa=anchor(t,c);L,u,udot=p.at(t)
        if seg['mode']=='taut':
            x,v,T,n,q,_,_,_,_=taut_values(t,z,c,p);work=z[2:4];h_integral=z[4]
            T=max(0.,T)
        else:
            x,v=z[:2],z[2:4];T=0.;d=np.linalg.norm(x-a);n=(x-a)/d;work=z[4:6];h_integral=z[6]
        F=-T*n;r=np.linalg.norm(x);theta=np.arctan2(x[1],x[0]);d=np.linalg.norm(x-a)
        rd=x@v/r;w=(x[0]*v[1]-x[1]*v[0])/r**2;H=c.mass_kg*r*r*w
        tau=x[0]*F[1]-x[1]*F[0];K=.5*c.mass_kg*(v@v)
        rows.append([t,*x,*v,*a,L,u,d,r,theta,rd,w,T,tau,H,K,work[0],work[1],seg['lost'],seg['impact_work'],seg['impact_H'],h_integral,
                     float(seg['mode']=='taut'),max(0.,L-d),F@av,-T*u,np.arctan2(np.sin(c.omega*t-theta),np.cos(c.omega*t-theta))])
    return np.array(rows)
COLUMNS=['time_s','x_m','y_m','vx_m_s','vy_m_s','anchor_x_m','anchor_y_m','paid_length_m','payout_speed_m_s','distance_m','radius_m','theta_rad','radial_speed_m_s','angular_speed_rad_s','tension_n','torque_nm','angular_momentum','kinetic_j','drive_work_j','spool_work_j','retension_loss_j','impulse_work_j','angular_impulse','integrated_torque','taut','slack_m','drive_power_w','spool_power_w','lag_rad']

def scenarios(c):
    return dict(constant=Profile(c,5,0,20),slow_then_fast=Profile(c,5,.6,20),fast_then_slow=Profile(c,5,-.6,20),too_fast=Profile(c,40,0,1))
