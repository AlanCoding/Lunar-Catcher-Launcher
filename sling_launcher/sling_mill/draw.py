"""Coordinate-generated technical SVGs and PNG previews."""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Rectangle, Arc
from geometry import geometry, rotate
from pathlib import Path
ROOT=Path(__file__).parent
GREEN='#426e60'; BLUE='#49677e'; RED='#a25c43'; GRAY='#8c918e'

def save(fig,name):
    fig.savefig(ROOT/'figures'/f'{name}.svg',bbox_inches='tight',facecolor='white')
    fig.savefig(ROOT/'figures'/f'{name}.png',dpi=160,bbox_inches='tight',facecolor='white')
    plt.close(fig)

def arrow(ax,p,q,color=BLUE,label=None,offset=(0,0)):
    ax.annotate('',q,p,arrowprops=dict(arrowstyle='->',color=color,lw=1.8))
    if label:
        mid=(np.array(p)+q)/2+offset
        ax.text(*mid,label,color=color,fontsize=10,ha='center')

def drum(ax,center,R,h,direction=1,cables=12):
    center=np.array(center)
    ax.add_patch(Circle(center,R,fill=False,ec=GREEN,lw=2))
    ax.add_patch(Circle(center,h,fc='#dfdfd6',ec=GRAY,lw=1))
    _,P,Q,H=geometry(R,h); H[1]*=direction
    for angle in np.linspace(0,2*np.pi,cables,endpoint=False):
        p,q,hh=rotate([P,Q,H],angle)+center
        ax.plot([q[0],p[0]],[q[1],p[1]],color='#bbc4bf',lw=.7)
        ax.plot([hh[0],p[0]],[hh[1],p[1]],color='#9eb0b9',lw=.65)

def diagrams(c,k,system_config=None):
    R=c['radius']; h=R*c['hub_ratio']; D=c['payload_depth']; L=c['payload_length']
    plt.rcParams.update({'font.size':11,'svg.fonttype':'none'})
    fig,ax=plt.subplots(figsize=(10,7)); drum(ax,(0,0),R,h)
    O,P,Q,H=geometry(R,h)
    ax.plot(*np.array([Q,P]).T,color=GREEN,lw=3,label='Radial member Q–P')
    ax.plot(*np.array([H,P]).T,color=BLUE,lw=3,label='Hub-tangent member H–P')
    ax.plot(*np.array([O,H]).T,color=GRAY,ls='--')
    e1=-H/np.linalg.norm(H); e2=(P-H)/np.linalg.norm(P-H); d=.08*R
    corner=np.array([H+d*e1,H+d*(e1+e2),H+d*e2])
    ax.plot(*corner.T,color='black',lw=1)
    for name,p in [('O',O),('P',P),('Q',Q),('H',H)]:
        ax.scatter(*p,s=16,c='black'); ax.text(p[0]+.025*R,p[1]+.04*R,name)
    arrow(ax,P,P+.45*(H-P),BLUE,'T',(.0,.01))
    arrow(ax,P,P+np.array([0,.4*R]),RED,'T rₕ / R',(.025,0))
    arrow(ax,P,P-np.array([.45*R,0]),RED,'inward component',(0,-.02))
    ax.annotate('',(R,-1.16*R),(0,-1.16*R),arrowprops=dict(arrowstyle='<->',color=GRAY))
    ax.text(R/2,-1.27*R,f'R = {R:.3f} m',ha='center')
    ax.text(-.95*R,-.8*R,f'rₕ = {h:.3f} m\nθ = {np.degrees(np.arcsin(h/R)):.2f}°')
    ax.text(-1.15*R,1.28*R,'Hub-tangent cable geometry',fontsize=17,weight='bold')
    ax.set(aspect='equal',xlim=(-1.2*R,1.6*R),ylim=(-1.4*R,1.4*R)); ax.axis('off')
    ax.legend(loc='upper center',bbox_to_anchor=(.5,-.02),frameon=False,fontsize=10,ncol=2); save(fig,'01_drum_geometry')

    fig,ax=plt.subplots(figsize=(11,7))
    for y,sgn in [(R+D/2,1),(-R-D/2,-1)]:
        drum(ax,(0,y),R,h,sgn)
        ts=np.linspace(.1,1.6,30)*sgn
        ax.plot(.65*R*np.cos(ts),y+.65*R*np.sin(ts),color=RED,lw=2)
        arrow(ax,(.65*R*np.cos(ts[-2]),y+.65*R*np.sin(ts[-2])),
              (.65*R*np.cos(ts[-1]),y+.65*R*np.sin(ts[-1])),RED)
    ax.add_patch(Rectangle((-.3,-D/2),.6,D,fc='#c9bb98',ec='#665c43'))
    for y in [-D/2,D/2]: arrow(ax,(-.03,y),(.07,y),BLUE)
    arrow(ax,(0,D/2+.045),(0,D/2),RED)
    arrow(ax,(0,-D/2-.045),(0,-D/2),RED)
    ax.text(.14,.17,'Upper surface moves forward\nLower surface moves forward',fontsize=11)
    ax.text(.14,.095,'Blue: traction on payload\nBrown: compression on payload')
    ax.text(-.29,-.31,f'Payload depth {D*1000:.0f} mm • belt diameter {2*R*1000:.0f} mm\nContact reactions on each belt point toward its hub.')
    ax.set(aspect='equal',xlim=(-.32,.45),ylim=(-.34,.31));ax.axis('off')
    ax.set_title('Opposed drum pair • side elevation • equal horizontal and vertical scale',fontsize=15)
    save(fig,'02_opposed_pair')

    if system_config is not None:
        from kinematics import evaluate
        c=system_config
        k,_=evaluate(c)
    system_pattern(c,k)

def system_pattern(c,k):
    R=c['radius']; h=R*c['hub_ratio']; D=c['payload_depth']; L=c['payload_length']
    plt.rcParams.update({'font.size':11,'svg.fonttype':'none'})
    fig,(ax,overview)=plt.subplots(2,1,figsize=(14,7),gridspec_kw={'height_ratios':[3,1]})
    # True-scale repeated pattern, two rods at entrance cadence.
    pitch=c['pitch']; first=.04
    age=(np.sqrt(c['v_entry']**2+2*c['acceleration']*first)-c['v_entry'])/c['acceleration']+k['interval_s']
    second=c['v_entry']*age+.5*c['acceleration']*age**2
    end=second+L+.15
    for x in np.arange(pitch/2,end,pitch):
        drum(ax,(x,R+D/2),R,h,1,8);drum(ax,(x,-R-D/2),R,h,-1,8)
    for x in [first,second]:
        ax.add_patch(Rectangle((x,-D/2),L,D,fc='#c9bb98',ec='#665c43'))
        arrow(ax,(x+.15,0),(x+.45,0),RED)
    ax.annotate('',(.04,-.34),(.04+L,-.34),arrowprops=dict(arrowstyle='<->'))
    ax.text(.04+L/2,-.41,f'{L:.2f} m rod · {c["payload_width"]*1000:.0f} mm wide × {D*1000:.0f} mm deep',ha='center')
    ax.text(.04,.36,f'{2*R:.2f} m drums · {pitch:.2f} m pitch · {pitch-2*R:.2f} m clear gap · L/pitch = {k["interior_pairs"]:.2f}')
    ax.set(aspect='equal',xlim=(-.03,end+.1),ylim=(-.46,.45));ax.axis('off')
    ax.set_title('Sling mill • the payload bridges successive drum pairs',loc='left',fontsize=18)
    S=k['active_distance_m']
    overview.plot([0,S],[0,0],lw=14,color='#e2e4df')
    for x in np.linspace(0,S,32):
        overview.plot([x,x],[-.08,.08],color=GREEN,lw=2)
    arrow(overview,(0,.2),(S,.2),BLUE)
    overview.text(0,.38,f'Feed {c["v_entry"]:.0f} m/s',ha='left')
    overview.text(S,.38,f'Exit {c["v_exit"]:.0f} m/s',ha='right')
    overview.text(S/2,-.32,f'{S:.1f} m active acceleration • {k["installed_pairs"]} installed pairs • {k["launch_frequency_hz"]:.1f} rods/s',ha='center')
    overview.text(S/2,-.58,'Overview compresses the longitudinal scale; the repeated pattern above is to scale.',ha='center',fontsize=10)
    overview.set(xlim=(-2,S+2),ylim=(-.7,.6));overview.axis('off')
    fig.tight_layout();save(fig,'03_system_pattern')
