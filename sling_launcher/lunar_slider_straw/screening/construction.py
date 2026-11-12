"""One-tonne payload sizing screens; conditional sheet construction and radiation."""
from pathlib import Path
import json,csv
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from ...staged_spool_bank.model import Model,Case
OUT=Path(__file__).parent/'results'/'shapes'

def main():
    m=Model(Case(payload_kg=1000,counterweight_kg=1000));w=m.w;u=m.L/(m.c.period_s/2);rho=1450.;W=1.5
    x=m.s;r=m.a+x;lam=m.lam;area=lam/rho;h=area/(2*W)
    T=w*w*(m.a*(m.mom[0][-1]-m.mom[0])+m.mom[1][-1]-m.mom[1]);sigma=T/area
    rows=[]
    for f in [0,.25,.5,.75,.9,.99,1]:
        xx=m.L*f;aa=float(np.interp(xx,x,area));tt=float(np.interp(xx,x,T));hh=float(np.interp(xx,x,h))
        # Reference Coriolis-only moving payload force, distributed across a 0.5 m shoe.
        normal=2*w*u*1000
        rows.append(dict(length_fraction=f,radius_m=m.a+xx,axial_force_N=tt,axial_stress_GPa=tt/aa/1e9,
            equivalent_fiber_wall_mm=hh*1000,transverse_30deg_MPa=normal/(.5*2*hh*np.sin(np.pi/6))/1e6,
            transverse_5deg_MPa=normal/(.5*2*hh*np.sin(np.radians(5)))/1e6))
    spool=[]
    for f in [.25,.5,.75,1.]:
        q=m.L*f;start=m.L-q;m0=m.mass-np.interp(start,x,m.mom[0]);m1=m.mom[1][-1]-np.interp(start,x,m.mom[1]);j=(m.a-start)*m0+m1
        cable=w*w*j;payload=w*w*(m.a+q)*1000
        spool.append(dict(deployed_fraction=f,deployed_mass_kg=float(m0),empty_hold_N=float(cable),loaded_hold_N=float(cable+payload),
            outward_friction_N_mu_0p1=float(.1*2*w*u*(m0+1000)),return_friction_N_mu_0p1=float(.1*2*w*u*m0),
            one_second_speed_ramp_force_N=float((m0+1000)*u),generalized_mass_feed_correction_N=float(.5*np.interp(start,x,lam)*u*u)))
    old=json.loads((OUT.parent/'summary.json').read_text())['fixed_delivery'][-1]
    heat=4*old['friction_both_sides_W_per_mu']*.1
    eps=.8;sb=5.670374419e-8;exposed=2*2*W*m.L
    thermal=dict(total_sliding_heat_W=heat,two_faces_both_straws_m2=exposed,mean_W_m2=heat/exposed,
        ideal_cold_sky_area_at_300K_m2=heat/(eps*sb*300**4),incremental_temperature_at_300K_if_uniform_K=heat/exposed/(4*eps*sb*300**3),assumed_emissivity=eps)
    packaging=[dict(bulk_density_kg_m3=d,cubic_payload_side_m=(1000/d)**(1/3),clear_square_side_m=(1000/d)**(1/3)+.3,
        round_bore_for_square_envelope_m=np.sqrt(2)*((1000/d)**(1/3)+.3)) for d in [1000,2000,3000]]
    mid_tension=float(np.interp(.5*m.L,x,T))
    opening=[]
    for transition in [1.,10.,100.]:
        normal=2*mid_tension*np.sin(np.arctan(.5/transition))
        opening.append(dict(transition_length_m=transition,midspan_guide_tension_N=mid_tension,
            total_normal_on_one_payload_N=float(normal),friction_W_per_payload_mu_0p1=float(.1*normal*u)))
    summary=dict(opening_sensitivity=opening,payload_kg=1000,guide_kg_per_side=m.mass,tether_and_straw_total_kg=34*m.mass,delivered_kg_s=8000/m.c.period_s,
        assumed_flat_face_width_m=W,equivalent_fiber_wall_range_mm=[float(h.min()*1000),float(h.max()*1000)],
        axial_profiles=rows,spool_forces=spool,thermal=thermal,packaging=packaging,
        sheet_model='Two 1.5 m faces; transverse membrane strip carried at edge angle alpha; footprint length 0.5 m. Edge support is assumed, not designed.')
    (OUT/'construction.json').write_text(json.dumps(summary,indent=2)+'\n')
    for name,data in [('material_stress',rows),('spool_forces',spool)]:
        with (OUT/f'{name}.csv').open('w') as file:
            out=csv.DictWriter(file,fieldnames=list(data[0]));out.writeheader();out.writerows(data)
    plt.rcParams.update({'font.size':10,'svg.fonttype':'none','axes.spines.top':False,'axes.spines.right':False})
    fig,axs=plt.subplots(2,1,figsize=(10,7),sharex=True,layout='constrained')
    axs[0].plot(x/1000,sigma/1e9,color='#527e68',label='Axial stress per total fiber area')
    axs[0].plot(x/1000,sigma/.8/1e9,color='#476d86',ls='--',label='If 80% of fiber carries axial tension')
    axs[0].set(ylabel='Axial stress (GPa)',title='Lengthwise load from rotation');axs[0].legend()
    normal=2*w*u*1000
    for alpha,color in [(30,'#a2673d'),(5,'#476d86')]:
        transverse=normal/(.5*2*h*np.sin(np.radians(alpha)))/1e6
        axs[1].plot(x/1000,transverse,color=color,label=f'Local one-tonne carrier; edge angle {alpha}°')
    axs[1].set(ylabel='Transverse membrane demand (MPa)',xlabel='Distance along guide (km)',title='Conditional local strip model · 0.5 m contact length · 1.5 m face width');axs[1].legend()
    for ax in axs:ax.grid(alpha=.15)
    save(fig,'material_stress')
    # Actual reference shared-shape contact: numerical kernel vs resolved carrier footprint.
    solved=json.loads((OUT/'summary.json').read_text())
    fig,ax=plt.subplots(figsize=(10,4),layout='constrained')
    for row in solved[:3]:
        data=np.load(OUT/f"{row['name']}.npz");label=row['name'].replace('reference_','').replace('_',' ')
        ax.plot(data['arc_m']/1000,data['cross_stress_30deg_Pa']/1e6,alpha=.7,label=label+'; smoothed density')
        contacts=row['carrier_contacts'];ax.scatter([v['arc_m']/1000 for v in contacts],[v['cross_stress_30deg_0p5m_MPa'] for v in contacts],marker='x',s=45)
    ax.set(xlabel='Distance along guide (km)',ylabel='Transverse membrane demand (MPa)',title='Shared-shape contact loads · crosses: individual 0.5 m carrier footprints')
    ax.legend(fontsize=8);ax.grid(alpha=.15);save(fig,'transverse_contacts')
    from matplotlib.patches import Rectangle,Circle
    fig,axs=plt.subplots(1,2,figsize=(12,4),layout='constrained')
    ax=axs[0]
    ax.plot([-.75,.75],[.65,.65],color='#527e68',lw=4);ax.plot([-.75,.75],[-.65,-.65],color='#527e68',lw=4)
    ax.plot([-.75,-.75],[-.65,.65],color='.6',ls='--');ax.plot([.75,.75],[-.65,.65],color='.6',ls='--')
    ax.add_patch(Rectangle((-.5,-.5),1,1,facecolor='#e7d7c9',edgecolor='#a2673d'))
    ax.text(0,0,'Example 1 m cargo envelope\n1 tonne at 1,000 kg/m³',ha='center',va='center',fontsize=9)
    for i in range(4):
        for j in range(4):ax.add_patch(Circle((.59+j*.031,-.06+i*.031),.0122,color='#476d86'))
    ax.annotate('Tether bundle',xy=(.64,0),xytext=(.5,-.83),ha='center',arrowprops=dict(arrowstyle='->'),fontsize=9)
    ax.set(xlim=(-1,1),ylim=(-1,1),title='Illustrative clear passage: 1.5 × 1.3 m');ax.set_aspect('equal');ax.axis('off')
    ax=axs[1];ax.plot([-2,-.7, .7,2],[0,.5,.5,0],color='#527e68',lw=2);ax.plot([-2,-.7,.7,2],[0,-.5,-.5,0],color='#527e68',lw=2)
    ax.add_patch(Rectangle((-.7,-.5),1.4,1,facecolor='#e7d7c9',edgecolor='#a2673d'))
    for sign in [-1,1]:ax.annotate('',xy=(0,sign*.15),xytext=(0,sign*.8),arrowprops=dict(arrowstyle='->',lw=2,color='#a2673d'))
    ax.text(0,-1,'A collapsed sleeve also squeezes the cargo\nthrough its much larger longitudinal tension.',ha='center',fontsize=10)
    ax.set(xlim=(-2.3,2.3),ylim=(-1.3,1.2),title='Opening a tensioned sleeve adds normal load');ax.axis('off')
    save(fig,'passage_and_opening')
    print(json.dumps(summary,indent=2))

def save(fig,name):
    for ext in ['png','svg']:fig.savefig(OUT/f'{name}.{ext}',dpi=180)
    plt.close(fig)
if __name__=='__main__':main()
