"""Planar elastic moving-domain string in a uniformly rotating frame.

A fixed computational mesh covers the deployed material interval [L-q, L].
Material-advection terms distinguish true spooling from stretching every link.
Finite-volume axial forces; lumped mass at nodes; prescribed rotating feed point.
"""
from dataclasses import dataclass,asdict
import numpy as np
from scipy.integrate import solve_ivp
from scipy.optimize import brentq
from scipy.sparse import lil_matrix
from ..architecture_comparison.compare import BASE,REF,OMEGA,PERIOD
from ..architecture_comparison.stress_frontier import taper_ratio

@dataclass
class Config:
    name: str='kevlar_1p5GPa'
    nodes: int=32
    density: float=1450.
    modulus: float=112.4e9
    nominal_strength: float=3e9
    design_stress: float=1.5e9
    target_tether_payload_ratio: float=0. # >0 overrides design stress
    payload: float=1000.
    retained_tip_mass: float=10.
    axial_relaxation_s: float=.02 # unmeasured sensitivity input, not supplier data
    initial_length: float=500.
    travel_s: float=PERIOD/5
    loaded_hold_s: float=300.
    release_settle_s: float=60.
    final_hold_s: float=120.
    rtol: float=2e-6
    atol: float=1e-5
    max_step: float=2.
    method: str="BDF"
    payout_profile: str="quintic"
    extension_only: bool=False

class Tether:
    def __init__(self,c=Config()):
        self.c=c;self.n=c.nodes;self.a=BASE.station_radius;self.R=REF['release_radius_m'];self.L=self.R-self.a;self.w=OMEGA
        self.k=c.design_stress/c.density
        if c.target_tether_payload_ratio>0:
            self.k=brentq(lambda k:taper_ratio(k)*(c.payload+c.retained_tip_mass)/c.payload-c.target_tether_payload_ratio,1e5,1e8)
        self.xi=np.linspace(0,1,self.n+1);self.dx=1/self.n
        sp=lil_matrix((4*self.n,4*self.n))
        for i in range(self.n):sp[4*i:4*i+4,4*max(0,i-3):4*min(self.n,i+4)]=1
        self.sparsity=sp.tocsr()
    def area(self,s):
        c=self.c
        return (c.payload+c.retained_tip_mass)*self.w**2*self.R/(self.k*c.density)*np.exp(self.w**2*(self.R**2-(self.a+s)**2)/(2*self.k))
    def geometry(self,q,load):
        mid=(self.xi[:-1]+self.xi[1:])/2
        area=self.area(self.L-q+q*mid);dm=self.c.density*area*q/self.n
        mass=.5*(dm+np.r_[dm[1:],0]);mass[-1]+=load
        return area,mass
    def initial(self,q,load):
        area,m=self.geometry(q,load);k=self.c.modulus*area*self.n/q;l=q/self.n
        mat=np.diag(k+np.r_[k[1:],0]-m*self.w**2)-np.diag(k[1:],1)-np.diag(k[1:],-1)
        rhs=(k-np.r_[k[1:],0])*l;rhs[0]+=k[0]*self.a
        x=np.linalg.solve(mat,rhs);z=np.zeros((self.n,4));z[:,0]=x
        return z.ravel()
    def motion(self,t,phase):
        if phase in ['extend','retract']:
            x=np.clip(t/self.c.travel_s,0,1);f=10*x**3-15*x**4+6*x**5
            fd=(30*x*x-60*x**3+30*x**4)/self.c.travel_s
            fdd=(60*x-180*x*x+120*x**3)/self.c.travel_s**2
            if phase=='extend' and self.c.payout_profile=='early_cruise':
                # Raised-cosine velocity ramp: 5% ramp up, 75% cruise, 20% down.
                a,b=.05,.20
                scale=1-(a+b)/2
                if x<a:
                    f=(x-a/np.pi*np.sin(np.pi*x/a))/(2*scale)
                    fd=(1-np.cos(np.pi*x/a))/(2*scale*self.c.travel_s)
                    fdd=np.pi*np.sin(np.pi*x/a)/(2*a*scale*self.c.travel_s**2)
                elif x<=1-b:
                    f=(x-a/2)/scale
                    fd=1/(scale*self.c.travel_s);fdd=0.
                else:
                    u=x-(1-b)
                    f=(1-b-a/2+(u+b/np.pi*np.sin(np.pi*u/b))/2)/scale
                    fd=(1+np.cos(np.pi*u/b))/(2*scale*self.c.travel_s)
                    fdd=-np.pi*np.sin(np.pi*u/b)/(2*b*scale*self.c.travel_s**2)
            elif phase=='extend' and self.c.payout_profile=='front_loaded':
                f=6*x*x-8*x**3+3*x**4
                fd=(12*x-24*x*x+12*x**3)/self.c.travel_s
                fdd=(12-48*x+36*x*x)/self.c.travel_s**2
            delta=self.L-self.c.initial_length
            if phase=='retract':return self.L-delta*f,-delta*fd,-delta*fdd
            return self.c.initial_length+delta*f,delta*fd,delta*fdd
        return (self.c.initial_length if phase=='final_hold' else self.L),0.,0.
    def fields(self,t,z,phase,load):
        q,qd,qdd=self.motion(t,phase);nodes=z.reshape(-1,4)
        X=np.vstack([[self.a,0],nodes[:,:2]]);V=np.vstack([[0,0],nodes[:,2:]])
        area,mass=self.geometry(q,load);D=np.diff(X,axis=0);length=np.linalg.norm(D,axis=1)
        tangent=D/np.maximum(length[:,None],1e-12);stretch=length/(q/self.n);strain=stretch-1
        rate=np.sum(tangent*np.diff(V,axis=0),axis=1)/(q/self.n)-stretch*qd/q
        wm=(1-(self.xi[:-1]+self.xi[1:])/2)*qd/q
        rate+=wm*np.gradient(strain,self.dx,edge_order=2)
        tension=np.where(strain>0,np.maximum(0,area*self.c.modulus*(strain+self.c.axial_relaxation_s*rate)),0.)
        Xx=np.gradient(X,self.dx,axis=0,edge_order=2);Vx=np.gradient(V,self.dx,axis=0,edge_order=2)
        Xxx=np.zeros_like(X);Xxx[1:-1]=(X[2:]-2*X[1:-1]+X[:-2])/self.dx**2
        w=(1-self.xi)*qd/q;beta=(1-self.xi)*(qdd/q-2*qd**2/q**2)
        material_velocity=V+w[:,None]*Xx
        return dict(q=q,qd=qd,qdd=qdd,X=X,V=V,area=area,mass=mass,tangent=tangent,
                    strain=strain,rate=rate,tension=tension,stress=tension/area,
                    Xx=Xx,Vx=Vx,Xxx=Xxx,w=w,beta=beta,material_velocity=material_velocity)
    def rhs(self,t,z,phase,load):
        f=self.fields(t,z,phase,load);F=f['tension'][:,None]*f['tangent'];force=np.vstack([F[1:]-F[:-1],-F[-1]])
        v=f['material_velocity'];cori=2*self.w*np.column_stack([-v[:,1],v[:,0]])
        acc=force/f['mass'][:,None]+self.w**2*f['X'][1:]-cori[1:]-2*f['w'][1:,None]*f['Vx'][1:]-f['w'][1:,None]**2*f['Xxx'][1:]-f['beta'][1:,None]*f['Xx'][1:]
        return np.column_stack([f['V'][1:],acc]).ravel()
    def run(self):
        c=self.c;z=self.initial(c.initial_length,c.payload+c.retained_tip_mass)
        phases=[('extend',c.travel_s,c.payload+c.retained_tip_mass),('loaded_hold',c.loaded_hold_s,c.payload+c.retained_tip_mass),
                ('release_settle',c.release_settle_s,c.retained_tip_mass),('retract',c.travel_s,c.retained_tip_mass),('final_hold',c.final_hold_s,c.retained_tip_mass)]
        if c.extension_only:phases=phases[:2]
        records=[];offset=0.;solver=[]
        for name,duration,load in phases:
            # Dense output at release captures fast waves; internal extrema also retained.
            sample=np.linspace(0,duration,int(np.ceil(duration/(.02 if name=='release_settle' else 2)))+1)
            progress=[-100.]
            def fun(t,z):
                if t-progress[0]>=200:
                    print(c.name,c.nodes,name,'time',round(t,1),flush=True);progress[0]=t
                return self.rhs(t,z,name,load)
            def strength_event(t,z):
                return c.nominal_strength-self.fields(t,z,name,load)['stress'].max()
            strength_event.terminal=True;strength_event.direction=-1
            sol=solve_ivp(fun,(0,duration),z,method=c.method,jac_sparsity=self.sparsity,events=strength_event,
                rtol=c.rtol,atol=c.atol,max_step=min(c.max_step,.1 if name=='release_settle' else c.max_step),dense_output=True)
            if not sol.success:raise RuntimeError(f'{name}: {sol.message}')
            sample=np.unique(np.r_[sample[sample<=sol.t[-1]],sol.t[-1]])
            # Stress extrema at accepted solver steps avoid hiding release spikes.
            stress_max=0.;strain_max=0.
            for t,y in zip(sol.t,sol.y.T):
                f=self.fields(t,y,name,load);stress_max=max(stress_max,float(f['stress'].max()));strain_max=max(strain_max,float(f['strain'].max()))
            solver.append(dict(phase=name,nfev=sol.nfev,steps=len(sol.t),accepted_step_peak_stress_Pa=stress_max,peak_strain=strain_max,completed=sol.status==0,end_phase_time_s=float(sol.t[-1]),stop_reason='nominal fiber strength reached' if sol.status==1 else None))
            for t,y in zip(sample,sol.sol(sample).T):
                f=self.fields(t,y,name,load)
                records.append((offset+t,name,f))
            z=sol.y[:,-1];offset+=duration
            print(c.name,c.nodes,name,'peak GPa',stress_max/1e9,flush=True)
            if sol.status==1:break
        return records,solver
    def metadata(self):
        return dict(config=asdict(self.c),station_radius_m=self.a,nominal_release_radius_m=self.R,
                    omega_rad_s=self.w,unstretched_full_length_m=self.L,
                    required_design_stress_Pa=self.k*self.c.density,
                    tether_mass_kg=taper_ratio(self.k)*(self.c.payload+self.c.retained_tip_mass),
                    tip_area_m2=float(self.area(self.L)),root_area_m2=float(self.area(0)))
