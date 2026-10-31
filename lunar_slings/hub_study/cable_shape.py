"""Finite-angle, quasi-static rotating string, with constant local lunar gravity.

One-dimensional force integrals, no continuum/FE model. Curvature enters terrain
clearance; gravity is the local parallel-field approximation. A flexible cable
is sized to constant TOTAL tensile stress in the fully loaded release state.
"""
from dataclasses import dataclass
import numpy as np
from scipy.integrate import solve_ivp, cumulative_trapezoid
from scipy.interpolate import PchipInterpolator

@dataclass
class Cable:
    radius: float
    tip_radius: float
    omega: float
    payload: float
    gravity: float
    density: float = 1450.
    stress: float = 1e9
    nodes: int = 1201

    def __post_init__(self):
        # Integrate inward in horizontal radius; tension components are positive.
        def rhs(r,y):
            tr,tv,_=y; T=np.hypot(tr,tv)
            return [-self.density*T*T/self.stress/tr*self.omega**2*r,
                    -self.density*T*T/self.stress/tr*self.gravity, T/tr]
        rs=np.linspace(self.tip_radius,self.radius,self.nodes)
        sol=solve_ivp(rhs,(self.tip_radius,self.radius),
                      [self.payload*self.omega**2*self.tip_radius,self.payload*self.gravity,0.],
                      t_eval=rs,rtol=2e-10,atol=1e-7)
        if not sol.success: raise RuntimeError(sol.message)
        self.length=-sol.y[2,-1]
        self.s=sol.y[2,::-1]+self.length
        self.lam=np.hypot(sol.y[0,::-1],sol.y[1,::-1])*self.density/self.stress
        self.linear=PchipInterpolator(self.s,self.lam)
        self.mass=float(self.linear.integrate(0,self.length))
        self.release_tension=float(np.hypot(sol.y[0,-1],sol.y[1,-1]))

    def shape(self,fraction,load,nodes=501):
        """Deployed material coordinate and radial/downward shape at given fraction."""
        q=self.length*fraction;x=np.linspace(0,1,nodes); s=self.length-q+q*x
        lam=self.linear(s);r=self.radius+q*x
        m=cumulative_trapezoid(lam,s,initial=0);tv=self.gravity*(load+m[-1]-m)
        for iteration in range(500):
            j=cumulative_trapezoid(lam*r,s,initial=0)
            tr=self.omega**2*(load*r[-1]+j[-1]-j)
            norm=np.hypot(tr,tv)
            cosine=np.divide(tr,norm,out=np.full_like(tr,1.),where=norm>0)
            if load==0: cosine[-1]=self.omega**2*r[-1]/np.hypot(self.omega**2*r[-1],self.gravity)
            new=self.radius+cumulative_trapezoid(cosine,s,initial=0)
            err=float(np.max(abs(new-r)));r=new
            if err < max(1e-7,q*1e-10):break
        else: raise RuntimeError('Cable shape did not converge')
        # Re-evaluate forces at converged radius.
        j=cumulative_trapezoid(lam*r,s,initial=0);tr=self.omega**2*(load*r[-1]+j[-1]-j)
        norm=np.hypot(tr,tv)
        sine=np.divide(tv,norm,out=np.zeros_like(tr),where=norm>0)
        if load==0:sine[-1]=self.gravity/np.hypot(self.omega**2*r[-1],self.gravity)
        drop=cumulative_trapezoid(sine,s,initial=0)
        return dict(x=x,s=s,lam=lam,r=r,drop=drop,tr=tr,tv=tv,
                    deployed_mass=float(m[-1]),iterations=iteration+1)

    def branch(self,load,moon_radius,fractions=241,nodes=501):
        fs=np.linspace(0,1,fractions);shapes=[self.shape(f,load,nodes) for f in fs]
        r=np.array([p['r'] for p in shapes]);z=-np.array([p['drop'] for p in shapes]);x=shapes[0]['x']
        # Material derivative at fixed s, not fixed normalized deployed coordinate x.
        rf=np.gradient(r,fs,axis=0,edge_order=2);zf=np.gradient(z,fs,axis=0,edge_order=2)
        for i,f in enumerate(fs):
            if f>0:
                rf[i]+=np.gradient(r[i],x,edge_order=2)*(1-x)/f
                zf[i]+=np.gradient(z[i],x,edge_order=2)*(1-x)/f
        # Tip position derivative at q=0 is the infinitesimal cable direction.
        records=[];height=3.;controlling=0.;root_stress=0.
        for i,(f,p) in enumerate(zip(fs,shapes)):
            mass=p['deployed_mass'];ss=p['s'];lam=p['lam']
            I=2*((self.mass-mass)*self.radius**2+np.trapezoid(lam*p['r']**2,ss)+load*p['r'][-1]**2)
            U=-2*self.gravity*(np.trapezoid(lam*p['drop'],ss)+load*p['drop'][-1])
            K=2*(np.trapezoid(lam*(rf[i]**2+zf[i]**2),ss)+load*(rf[i,-1]**2+zf[i,-1]**2))
            terrain=np.sqrt(moon_radius**2-p['r']**2)-moon_radius
            h=float(np.max(p['drop']+terrain)+3)
            if h>height:height=h;controlling=float(f)
            root_stress=max(root_stress,float(np.max(np.hypot(p['tr'],p['tv'])*self.density/lam)))
            records.append([I,U,K,p['r'][-1],p['drop'][-1],h])
        return dict(f=fs,values=np.array(records),height=height,controlling_fraction=controlling,
                    max_tensile_stress_pa=root_stress,shapes=shapes)
