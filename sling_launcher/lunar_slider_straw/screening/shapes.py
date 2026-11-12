"""Frozen-inventory rotating common-centerline BVP, plus membrane/force screens.

All participating cables follow the same inextensible planar curve. End-device
masses are spread narrowly in arc length. This is a quasi-steady branch search,
not an elastic time integration or a unilateral-contact solution.
"""
from pathlib import Path
import json
import numpy as np
from scipy.integrate import solve_bvp,cumulative_trapezoid
from scipy.special import ndtr
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from .scalar import states
from ...staged_spool_bank.model import Model,Case
OUT=Path(__file__).parent/'results'/'shapes'

def inventory(B,K,time_s,engage_idle=True,nodes=1201,width=12.):
    m=Model(Case(payload_kg=1000,counterweight_kg=1000,minimum_hold_s=0))
    q,out,back,full,loaded,u=states(m,B,K,np.array([time_s]));q=q[:,0];out=out[:,0];back=back[:,0];full=full[:,0];loaded=loaded[:,0]
    # Gaussian contact representation; refine its width when checking near-tip cases.
    L=m.L;x=np.linspace(0,L,nodes)
    guide=np.interp(x,m.s,m.lam);mu=guide.copy();J=np.zeros(nodes);H=J.copy();moving=J.copy();payloads=[];parts=[]
    for j in range(16):
        if full[j] and not engage_idle:continue
        cable=np.where(x<q[j],np.interp(L-q[j]+x,m.s,m.lam),0.)
        if full[j]:cable=guide.copy()
        component=cable.copy()
        mu+=cable
        v=u if out[j] else -u if back[j] else 0.
        J+=cable*v;H+=cable*v*v;moving+=cable*(v!=0)
        if out[j]:
            center=q[j];norm=ndtr((L-center)/width)-ndtr(-center/width)
            blob=1000*np.exp(-.5*((x-center)/width)**2)/(np.sqrt(2*np.pi)*width*norm)
            mu+=blob;J+=v*blob;H+=v*v*blob;moving+=blob;component+=blob;payloads.append(float(center))
        parts.append((component,v,1000. if loaded[j] else 0.))
    # Tiny endpoint mass regularizes zero-tension singularity; test sensitivity.
    tipmass=1000*int(loaded.sum()) if engage_idle else 0.
    return dict(m=m,x=x,mu=mu,J=J,H=H,moving=moving,guide=guide,u=u,full=int(full.sum()),loaded=int(loaded.sum()),tipmass=tipmass,payloads=payloads,B=B,K=K,time_s=time_s,engage_idle=engage_idle,parts=parts)

def solve_shape(c,tip_regularization=.1,tol=2e-5,steps=8):
    m=c['m'];L=m.L;w=m.w;z=c['x']/L;scale=1000*w*w*L
    tipmass=c['tipmass']+tip_regularization
    mu=c['mu'];rr=m.a+c['x'];ax=tipmass*w*w*m.R+w*w*(np.trapezoid(mu*rr,c['x'])-cumulative_trapezoid(mu*rr,c['x'],initial=0))
    guess=np.array([rr/L,np.zeros(len(z)),ax/scale,np.zeros(len(z))])
    def bc(a,b):return np.array([a[0]-m.a/L,a[1],b[2]-tipmass/1000*b[0],b[3]-tipmass/1000*b[1]])
    previous=None
    for f in np.linspace(0,1,steps):
        def fun(s,y):
            mm=np.interp(s,z,c['mu'])*L/1000
            jj=np.interp(s,z,c['J'])*f/(1000*w)
            hh=np.interp(s,z,c['H'])*f*f/scale
            X,Y,Fx,Fy=y;T=np.hypot(Fx,Fy);tx=Fx/np.maximum(T,1e-12);ty=Fy/np.maximum(T,1e-12)
            normalR=-X*ty+Y*tx;tangentR=X*tx+Y*ty
            denom=T-hh
            denom=np.where(abs(denom)<1e-10,np.copysign(1e-10,denom),denom)
            curvature=(-mm*normalR+2*jj)/denom
            tangentF=-mm*tangentR
            return np.array([tx,ty,tangentF*tx-T*curvature*ty,tangentF*ty+T*curvature*tx])
        if previous is None:smesh=z;yg=guess
        else:smesh=previous.x;yg=previous.y
        sol=solve_bvp(fun,bc,smesh,yg,tol=tol,max_nodes=30000)
        if not sol.success:return None,dict(success=False,continuation_fraction=float(f),message=sol.message)
        previous=sol
    zz=np.linspace(0,1,3001);soly=sol.sol(zz);xy=soly[:2]*L;F=soly[2:]*scale;T=np.hypot(*F)
    H=np.interp(zz,z,c['H']);minimum=float(np.min(T-H))
    if minimum<=0:return None,dict(success=False,message='Nonpositive effective tension',minimum_effective_N=minimum)
    # Independent integrated force and torque balance of the solved branch.
    dy=sol.sol(zz,1);tx=soly[2]/np.hypot(*soly[2:]);ty=soly[3]/np.hypot(*soly[2:])
    kappa=(soly[2]*dy[3]-soly[3]*dy[2])/np.hypot(*soly[2:])**2/L
    mu=np.interp(zz,z,c['mu']);J=np.interp(zz,z,c['J'])
    force=-mu*w*w*xy+(2*w*J+H*kappa)*np.array([-ty,tx])
    forceerr=np.linalg.norm(F[:,-1]-F[:,0]-np.trapezoid(force,zz*L,axis=1))/np.linalg.norm(F[:,0])
    torque_density=xy[0]*force[1]-xy[1]*force[0]
    torqueerr=abs((xy[0,-1]*F[1,-1]-xy[1,-1]*F[0,-1])-(xy[0,0]*F[1,0]-xy[1,0]*F[0,0])-np.trapezoid(torque_density,zz*L))/max(1,abs(m.a*F[1,0]))
    # Guide's individual axial tension from its tangential equation on shared path.
    lam=np.interp(zz,z,c['guide']);guide_integrand=lam*w*w*(xy[0]*tx+xy[1]*ty)
    guideT=np.trapezoid(guide_integrand,zz*L)-cumulative_trapezoid(guide_integrand,zz*L,initial=0)
    guide_sigma=guideT/(lam/m.c.density_kg_m3)
    # Contact on guide from each separately tensioned strand, sharing this curve.
    rdot=xy[0]*tx+xy[1]*ty;rdotn=-xy[0]*ty+xy[1]*tx
    contact_plus=np.zeros(len(zz));contact_minus=contact_plus.copy();moving_normal=contact_plus.copy()
    for density,v,endpoint_mass in c['parts']:
        lam_i=np.interp(zz,z,density);g=lam_i*w*w*rdot
        ti=endpoint_mass*w*w*rdot[-1]+np.trapezoid(g,zz*L)-cumulative_trapezoid(g,zz*L,initial=0)
        reaction=(ti-lam_i*v*v)*kappa+lam_i*w*w*rdotn-2*w*lam_i*v
        contact_plus+=np.maximum(reaction,0);contact_minus+=np.maximum(-reaction,0)
        if v!=0:moving_normal+=abs(reaction)
    thickness=lam/m.c.density_kg_m3/(2*1.5)
    sigma_cross_30=np.maximum(contact_plus,contact_minus)/(2*thickness*np.sin(np.pi/6))
    # Point carrier result evaluated separately from its numerical smoothing kernel.
    carrier=[]
    for position in c['payloads']:
        f=1000*(w*w*np.interp(position,zz*L,rdotn)-2*w*c['u']-c['u']**2*np.interp(position,zz*L,kappa))
        hwall=np.interp(position,zz*L,thickness)
        carrier.append(dict(arc_m=position,normal_force_N=float(f),cross_stress_30deg_0p5m_MPa=float(abs(f)/(.5*2*hwall*.5)/1e6)))
    angle=np.arctan2(ty,tx);chord=np.arctan2(xy[1,-1]-xy[1,0],xy[0,-1]-xy[0,0])
    normal_chord=-(xy[0]-xy[0,0])*np.sin(chord)+(xy[1]-xy[1,0])*np.cos(chord)
    result=dict(success=True,carrier_contacts=carrier,
        moving_contact_friction_W_at_mu_0p1_both_sides=float(2*.1*c["u"]*np.trapezoid(moving_normal,zz*L)),
        gross_contact_max_N_m=float(np.max(contact_plus+contact_minus)),tip_x_m=float(xy[0,-1]),tip_y_m=float(xy[1,-1]),tip_radius_m=float(np.hypot(*xy[:,-1])),
        max_cross_track_m=float(np.max(abs(xy[1]))),chord_angle_deg=float(np.degrees(chord)),
        max_departure_from_chord_m=float(np.max(abs(normal_chord))),root_tension_N=float(T[0]),root_tangential_force_N=float(F[1,0]),
        guide_max_axial_stress_GPa=float(guide_sigma.max()/1e9),tangent_angle_range_deg=[float(np.degrees(angle.min())),float(np.degrees(angle.max()))],
        minimum_effective_tension_N=minimum,bvp_residual=float(sol.rms_residuals.max()),force_integral_error=float(forceerr),torque_integral_error=float(torqueerr))
    return dict(arc_m=zz*L,xy_m=xy,tension_N=T,guide_tension_N=guideT,guide_stress_Pa=guide_sigma,tangent_angle_rad=angle,contact_plus_N_m=contact_plus,contact_minus_N_m=contact_minus,cross_stress_30deg_Pa=sigma_cross_30,wall_fiber_thickness_m=thickness),result

def main():
    OUT.mkdir(parents=True,exist_ok=True);plt.rcParams.update({'font.size':10,'svg.fonttype':'none','axes.spines.top':False,'axes.spines.right':False})
    m=Model(Case(payload_kg=1000,counterweight_kg=1000));T=m.c.period_s
    configs=[('reference_after_release',8,4,T+1,True),('reference_before_release',8,4,T-1,True),('reference_midwindow',8,4,T/2,True),
        ('fast_two_in_transit',8,1,T+1,True),('larger_batch_fast',14,1,T+1,True),('idle_cables_disengaged',8,4,T+1,False),
        ('fast_near_tip',14,1,300-50/(m.L*14/T),True),
        ('fast_near_tip_idle_disengaged',14,1,300-50/(m.L*14/T),False)]
    rows=[];curves={}
    for name,B,K,time,engage in configs:
        c=inventory(B,K,time,engage);h,r=solve_shape(c)
        r.update(name=name,B=B,K=K,line_speed_m_s=c['u'],time_s=time,fully_extended=c['full'],held_payloads=c['loaded'],idle_engaged=engage)
        rows.append(r)
        if h is not None:curves[name]=h;np.savez_compressed(OUT/f'{name}.npz',**h)
        print(json.dumps(r),flush=True)
    (OUT/'summary.json').write_text(json.dumps(rows,indent=2)+'\n')
    fig,axs=plt.subplots(2,1,figsize=(11,7),layout='constrained')
    for r in rows:
        if not r['success']:continue
        h=curves[r['name']];label=r['name'].replace('_',' ')
        for ax in axs:ax.plot(h['xy_m'][0]/1000,h['xy_m'][1]/1000,label=label)
    axs[0].set_aspect('equal',adjustable='datalim');axs[0].set_title('True spatial aspect ratio')
    axs[1].set_title('Transverse detail; different axis scales')
    for ax in axs:ax.set(xlabel='Radial-axis coordinate (km)',ylabel='Spin-wise coordinate (km)');ax.grid(alpha=.15)
    axs[1].legend(fontsize=8);fig.suptitle('Shared-centerline quasi-steady shapes · one-tonne payloads')
    save(fig,'shared_shapes')
    fig,axs=plt.subplots(3,1,figsize=(11,8),layout='constrained',gridspec_kw={'height_ratios':[.7,1.5,1.5]})
    for r in rows[:3]:
        h=curves[r['name']];xy=h['xy_m'];label=r['name'].replace('reference_','').replace('_',' ')
        axs[0].plot(xy[0]/1000,xy[1]/1000,label=label)
        axs[1].plot(xy[0]/1000,xy[1],label=label)
        theta=np.radians(r['chord_angle_deg']);bow=-(xy[0]-xy[0,0])*np.sin(theta)+(xy[1]-xy[1,0])*np.cos(theta)
        axs[2].plot(h['arc_m']/1000,bow,label=label)
    axs[0].set_aspect('equal',adjustable='datalim');axs[0].set(xlabel='Radial-axis coordinate (km)',ylabel='Spin-wise (km)',title='True spatial scale')
    axs[1].set(xlabel='Radial-axis coordinate (km)',ylabel='Spin-wise offset (m)',title='Overall lean, transverse scale enlarged')
    axs[2].set(xlabel='Distance along guide (km)',ylabel='Bow from end-to-end chord (m)',title='Actual curvature after removing overall lean')
    for ax in axs:ax.grid(alpha=.15);ax.legend(fontsize=8)
    fig.suptitle('Reference shared guide · 16 tethers per side · 4 out + 4 back · 1 tonne per payload')
    save(fig,'reference_shapes')
    # Longitudinal guide stress on converged shapes.
    fig,ax=plt.subplots(figsize=(10,4),layout='constrained')
    for r in rows:
        if r['success']:
            h=curves[r['name']];ax.plot(h['arc_m']/1000,h['guide_stress_Pa']/1e9,label=r['name'].replace('_',' '))
    ax.set(xlabel='Distance along guide (km)',ylabel='Guide axial stress (GPa)',title='Guide lengthwise stress from its own rotational loading');ax.legend(fontsize=8);ax.grid(alpha=.15);save(fig,'axial_stress')
    if rows[0]['success']:
        c=inventory(8,4,T+1,True,nodes=2401,width=6.)
        h,check=solve_shape(c,tip_regularization=.01,tol=1e-5)
        assert check['success']
        assert abs(check['tip_y_m']-rows[0]['tip_y_m'])<.1
        assert abs(check['max_departure_from_chord_m']-rows[0]['max_departure_from_chord_m'])<.02
        for row in rows:
            if row['success']:
                assert row['force_integral_error']<1e-3 and row['torque_integral_error']<1e-3
        (OUT/'refinement.json').write_text(json.dumps(check,indent=2)+'\n')
        print('REFINEMENT',check,flush=True)

def save(fig,name):
    for ext in ['png','svg']:fig.savefig(OUT/f'{name}.{ext}',dpi=180)
    plt.close(fig)

if __name__=='__main__':main()
