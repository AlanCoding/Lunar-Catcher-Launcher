"""Steady moving, inextensible string with a free turn and circular feed wheel.

Lengths scaled by radius_scale; speeds by omega*radius_scale; tensions by
bare_density*(omega*radius_scale)**2. Payloads are a continuous mass stream.
No distant anchor, prescribed outer shape, elastic dynamics or slip law.
"""
from dataclasses import dataclass, asdict
import numpy as np
from scipy.integrate import cumulative_trapezoid, solve_bvp
from scipy.optimize import root
from numpy.polynomial.legendre import leggauss

@dataclass
class Inputs:
    radius_scale: float = 5787.088393934127
    station_radius: float = 76.78937039996255
    track_speed: float = 22.352
    wheel_radius: float = 25.0
    feed_speed: float = 5.0
    area: float = .001
    density: float = 1560.0
    payload_per_m: float = .312
    release_center: float = .49
    release_width: float = .001

    @property
    def omega(self): return self.track_speed/self.station_radius
    @property
    def bare_density(self): return self.area*self.density


def seed(c):
    """Unloaded first-integral solution; select cable length to give R=scale."""
    A=c.station_radius/c.radius_scale; b=c.wheel_radius/c.radius_scale
    v=c.feed_speed/(c.omega*c.radius_scale)
    nodes, weights=leggauss(300); ts=(nodes+1)/2; ws=weights/2
    def params(delta):
        al=-np.pi/2+delta
        xy=np.array([A+b*np.cos(al),b*np.sin(al)])
        r0=np.linalg.norm(xy); th0=-np.arctan2(xy[1],xy[0]); psi=delta+th0
        st=(1-r0*r0)*(v+.5*r0*np.sin(psi))/(1-r0*np.sin(psi))
        return r0,th0,st
    def integrands(delta,t):
        r0,th,st=params(delta); d=1-r0; r=1-d*t*t; S=st+.5*(1-r*r)
        q=(st-v+v*r*r)/(r*S)
        common=2*d*t/np.sqrt(1-q*q)
        return r,S,q,common,common*q/r
    def residual(z):
        *_,aa=integrands(z[0],ts)
        return [np.sum(aa*ws)-params(z[0])[1]]
    answer=root(residual,[-.03])
    if not answer.success: raise RuntimeError(answer.message)
    delta=answer.x[0]; *_,ss0,aa=integrands(delta,ts)
    total=2*np.sum(ss0*ws)+b*(np.pi+2*delta)
    t=np.linspace(1e-5,1,3001)
    r,S,q,ds,da=integrands(delta,t)
    arc=cumulative_trapezoid(ds,t,initial=0)
    theta=-cumulative_trapezoid(da,t,initial=0)
    x=r*np.cos(theta); y=r*np.sin(theta); phi=theta+np.arcsin(q)
    z=np.array([np.r_[x[::-1],x[1:]],np.r_[y[::-1],-y[1:]],
                np.r_[phi[::-1],np.pi-phi[1:]],
                np.log(np.r_[S[::-1],S[1:]]+v*v)])
    s=np.r_[arc[-1]-arc[::-1],arc[-1]+arc[1:]]; s/=s[-1]
    return s,z,np.array([-np.pi/2+delta,np.pi/2-delta]),total


def equations(c,total,loading):
    A=c.station_radius/c.radius_scale; b=c.wheel_radius/c.radius_scale
    v=c.feed_speed/(c.omega*c.radius_scale)
    def mass(s):
        return 1+loading*.5*(1-np.tanh((s-c.release_center)/c.release_width))
    def fun(s,z,p):
        al,be=p; L=total-b*(al+2*np.pi-be)
        x,y,ph,h=z; T=np.exp(np.clip(h,-30,30)); m=mass(s); S=T-m*v*v
        return L*np.array([np.cos(ph),np.sin(ph),
                    m*(2*v+x*np.sin(ph)-y*np.cos(ph))/S,
                    -m*(x*np.cos(ph)+y*np.sin(ph))/T])
    def bc(l,r,p):
        al,be=p
        return np.array([l[0]-A-b*np.cos(al),l[1]-b*np.sin(al),
                r[0]-A-b*np.cos(be),r[1]-b*np.sin(be),
                l[2]-al-np.pi/2,r[2]-be-np.pi/2])
    return fun,bc,mass


def solve(c,tol=2e-6):
    s,z,p,total=seed(c)
    target=c.payload_per_m/c.bare_density
    for loading in np.linspace(0,target,max(2,int(target/.08)+2)):
        fun,bc,mass=equations(c,total,loading)
        sol=solve_bvp(fun,bc,s,z,p=p,tol=tol,max_nodes=40000)
        if not sol.success: raise RuntimeError(f'load={loading}: {sol.message}')
        s,z,p=sol.x,sol.y,sol.p
    return sol,total


def evaluate(c,sol,total,n=10001):
    s=np.linspace(0,1,n); z=sol.sol(s); x,y,phi,h=z
    fun,bc,mass=equations(c,total,c.payload_per_m/c.bare_density)
    m=mass(s); v=c.feed_speed/(c.omega*c.radius_scale)
    T=np.exp(h); wrap=sol.p[0]+2*np.pi-sol.p[1]
    free=total-c.wheel_radius/c.radius_scale*wrap
    scale=c.bare_density*(c.omega*c.radius_scale)**2
    tension=T*scale; xy=z[:2]*c.radius_scale
    velocity=c.omega*np.array([-xy[1],xy[0]])+c.feed_speed*np.array([np.cos(phi),np.sin(phi)])
    # Independent dense-grid integral of the vector force balance.
    dz=sol.sol(s,1); t=np.array([np.cos(phi),np.sin(phi)]); normal=np.array([-np.sin(phi),np.cos(phi)])
    integrand=m*(v*v*normal*dz[2]/free+2*v*normal-z[:2])*free
    force_error=np.max(np.abs(T[-1]*t[:,-1]-T[0]*t[:,0]-np.trapezoid(integrand,s,axis=1)))
    invariant=T+.5*(x*x+y*y)  # constant only for unloaded cable
    summary=dict(inputs=asdict(c),omega_rad_s=c.omega,rpm=c.omega*60/(2*np.pi),
        length_m=total*c.radius_scale,bare_loop_mass_kg=total*c.radius_scale*c.bare_density,
        payload_inventory_kg=float(np.trapezoid(m-1,s)*free*c.radius_scale*c.bare_density),
        mass_flow_kg_s=c.payload_per_m*c.feed_speed,
        release_center_radius_m=float(np.interp(c.release_center,s,np.hypot(*xy))),
        release_center_speed_m_s=float(np.interp(c.release_center,s,np.hypot(*velocity))),
        radius_max_m=float(np.hypot(*xy).max()),width_m=float(np.ptp(xy[1])),
        max_stress_GPa=float(tension.max()/c.area/1e9),min_tension_N=float(tension.min()),
        departure_tension_N=float(tension[0]),return_tension_N=float(tension[-1]),
        wheel_wrap_rad=float(wrap),capstan_mu_proxy=float(np.log(tension[0]/tension[-1])/wrap),
        ideal_feed_brake_power_W=float((tension[0]-tension[-1])*c.feed_speed),
        min_effective_tension_N=float(np.min(T-m*v*v)*scale),
        bvp_residual=float(sol.rms_residuals.max()),boundary_residual=float(np.max(np.abs(bc(sol.y[:,0],sol.y[:,-1],sol.p)))),
        integrated_force_residual_scaled=float(force_error),
        unloaded_first_integral_range=float(np.ptp(invariant)) if c.payload_per_m==0 else None)
    return summary,dict(s=s,arc_m=s*free*c.radius_scale,xy_m=xy,tension_N=tension,
         stress_Pa=tension/c.area,mass_per_m=m*c.bare_density,velocity_m_s=velocity,
         tangent_angle=phi,contact_angles=sol.p)
