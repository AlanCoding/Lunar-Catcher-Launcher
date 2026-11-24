"""Concept illustrations for branching tensile webs supporting the drum rim."""
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Circle,Rectangle
P=Path(__file__).parent
GREEN='#426e60'; BLUE='#49677e'; GRAY='#8c918e'; SAND='#c9bb98'; LIGHT='#a8bbc4'

def web(ax,slack=False,hub=.18,alpha=1):
    def point(r,t):return np.array([r*np.cos(t),r*np.sin(t)])
    for th in np.linspace(0,2*np.pi,16,endpoint=False):
        span=2*np.pi/16
        root=point(hub,th);fork=point(.66,th)
        if slack:
            from matplotlib.path import Path as MP
            from matplotlib.patches import PathPatch
            ctrl=(root+fork)/2+[0,-.10]
            ax.add_patch(PathPatch(MP([root,ctrl,fork],[MP.MOVETO,MP.CURVE3,MP.CURVE3]),fill=False,ec=BLUE,lw=1.5,alpha=alpha))
        else:ax.plot([root[0],fork[0]],[root[1],fork[1]],color=BLUE,lw=1.7,alpha=alpha)
        # Hub-tangent stay transmits drive torque into the shared rim web.
        ht=np.array([hub*hub/.66,hub*np.sqrt(1-(hub/.66)**2)])
        cs,sn=np.cos(th),np.sin(th);ht=np.array([[cs,-sn],[sn,cs]])@ht
        if slack:
            ctrl=(ht+fork)/2+[0,-.08]
            ax.add_patch(PathPatch(MP([ht,ctrl,fork],[MP.MOVETO,MP.CURVE3,MP.CURVE3]),fill=False,ec='#a25c43',lw=.9,alpha=alpha))
        else:ax.plot([ht[0],fork[0]],[ht[1],fork[1]],color='#a25c43',lw=.9,alpha=alpha)
        for j,sgn in enumerate((-1,1)):
            secondary=point(.84,th+sgn*span/4)
            ax.plot([fork[0],secondary[0]],[fork[1],secondary[1]],color=BLUE,lw=1.1,alpha=alpha)
            for k in range(4):
                tip=point(1,th-span/2+(j*4+k+.5)*span/8)
                ax.plot([secondary[0],tip[0]],[secondary[1],tip[1]],color=LIGHT,lw=.75,alpha=alpha)
    ax.add_patch(Circle((0,0),1,fill=False,ec=GREEN,lw=3))
    ax.add_patch(Circle((0,0),hub,fc='#deded5',ec=GRAY,zorder=6))

def draw():
    plt.rcParams.update({'svg.fonttype':'none','font.family':'DejaVu Sans','font.size':11})
    fig=plt.figure(figsize=(12,7),facecolor='white')
    fig.text(.04,.94,'A branching web supports the rim',fontsize=22,weight='bold',color=GREEN)
    ax=fig.add_axes([.03,.18,.48,.67]);ax.set(xlim=(-1.25,1.25),ylim=(-1.25,1.25),aspect='equal');ax.axis('off');web(ax)
    ax.text(0,-1.2,'Main spokes → branching web → closely spaced rim supports',ha='center',va='top',fontsize=10,color=BLUE)
    ax.text(0,-1.32,'Brown stays transmit drive torque',ha='center',va='top',fontsize=10,color='#a25c43')
    ax=fig.add_axes([.57,.43,.38,.39]);ax.axis('off');ax.set(xlim=(-.64,.64),ylim=(-.07,1.25))
    ax.plot([0,0],[0,.40],color=BLUE,lw=5)
    for sg in (-1,1):
        x=sg*.23;ax.plot([0,x],[.40,.68],color=BLUE,lw=3)
        for xx in np.linspace(sg*.05,sg*.46,4):
            yy=1-.10*xx**2
            ax.plot([x,xx],[.68,yy],color=BLUE,lw=1.5)
            ax.scatter([xx],[yy],s=20,color=GREEN,zorder=5)
    xx=np.linspace(-.56,.56,80);ax.plot(xx,1-.10*xx**2,color=GREEN,lw=6)
    # Circumferential links connect successive branch junctions.
    ax.plot([-.23,0,.23],[.68,.71,.68],color=LIGHT,lw=1.2,ls='--')
    ax.text(0,1.15,'Rim-sector detail',ha='center',color=BLUE,fontsize=14)
    ax.annotate('Main tapered spoke',(0,.12),(.34,.1),color=BLUE,fontsize=10,arrowprops=dict(arrowstyle='-',color=BLUE))
    ax.annotate('Branch junction',(-.23,.68),(-.57,.43),color=BLUE,fontsize=10,arrowprops=dict(arrowstyle='-',color=BLUE))
    ax=fig.add_axes([.57,.16,.38,.21]);ax.axis('off');ax.set(xlim=(-.8,.8),ylim=(-.1,1.1))
    ax.add_patch(Rectangle((-.65,.77),1.3,.13,facecolor=GREEN))
    for x in (-.48,0,.48):
        ax.plot([x,x],[.08,.5],color=BLUE,lw=2)
        for dx in (-.13,0,.13):ax.plot([x,x+dx],[.5,.77],color=LIGHT,lw=1.2)
    ax.plot([-.48,0,.48],[.5,.5,.5],color=BLUE,lw=1)
    ax.annotate('',(.65,-.01),(-.65,-.01),arrowprops=dict(arrowstyle='<->',color=GRAY))
    ax.text(0,-.09,'Across belt width: repeated webs + cross ties',ha='center',va='top',fontsize=10,color=BLUE)
    fig.text(.04,.055,'Concept: 16 main spokes branching to 128 rim points. Branch counts, joints and transverse ties require sizing.',fontsize=10,color=GRAY)
    for ext in ('svg','png'):fig.savefig(P/'figures'/f'08_rim_suspension_web.{ext}',dpi=170,facecolor='white')
    plt.close(fig)
if __name__=='__main__':draw()
