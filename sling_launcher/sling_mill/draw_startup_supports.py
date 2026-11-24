"""Hub-carried temporary struts extend at low speed and retract into the hub."""
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
from draw_rim_web import web,GREEN,BLUE,GRAY,SAND
P=Path(__file__).parent
plt.rcParams.update({'svg.fonttype':'none','font.family':'DejaVu Sans','font.size':11})
fig=plt.figure(figsize=(11,6.4),facecolor='white')
fig.text(.04,.93,'Hub-mounted startup supports',fontsize=23,weight='bold',color=GREEN)
for pos,running,title in [([.055,.22,.4,.6],False,'Stopped / low speed'),([.545,.22,.4,.6],True,'Operating speed')]:
 ax=fig.add_axes(pos);ax.set(xlim=(-1.2,1.2),ylim=(-1.2,1.2),aspect='equal');ax.axis('off');ax.set_title(title,color=BLUE,fontsize=15,pad=14)
 web(ax,slack=not running,hub=.22,alpha=.50 if not running else 1.)
 for th in np.arange(6)*2*np.pi/6:
  e=np.array([np.cos(th),np.sin(th)])
  if not running:
   for start,end,lw,color in [(.13,.52,8,SAND),(.47,.77,5.5,'#b3a37b'),(.72,.97,3.5,SAND)]:
    p=start*e;q=end*e;ax.plot([p[0],q[0]],[p[1],q[1]],lw=lw,color=color,zorder=7,solid_capstyle='butt')
   theta=np.linspace(th-.09,th+.09,15);ax.plot(.975*np.cos(theta),.975*np.sin(theta),color=SAND,lw=5,zorder=7)
   p=.80*e;q=.53*e;off=np.array([-e[1],e[0]])*.065
   ax.annotate('',q+off,p+off,arrowprops=dict(arrowstyle='->',color='#8d7950',lw=1.4),zorder=8)
  else:
   p=.07*e;q=.18*e;ax.plot([p[0],q[0]],[p[1],q[1]],color=SAND,lw=4,zorder=7)
 if running:
  ts=np.linspace(.2,1.0,35);ax.plot(.43*np.cos(ts),.43*np.sin(ts),color=BLUE,lw=1.5)
  ax.annotate('',(.43*np.cos(ts[-1]),.43*np.sin(ts[-1])),(.43*np.cos(ts[-3]),.43*np.sin(ts[-3])),arrowprops=dict(arrowstyle='->',color=BLUE,lw=1.5))
 ax.text(0,-1.18,'Supports extended from the hub' if not running else 'Supports retracted into the hub',ha='center',va='top',color=BLUE,fontsize=11)
fig.text(.04,.105,'Temporary struts rotate with the hub. The tensile web carries the rim as speed rises.',fontsize=11,color=BLUE)
fig.text(.04,.055,'Schematic deployment · hub proportions and telescoping stroke are illustrative',fontsize=10,color=GRAY)
for ext in ('svg','png'):fig.savefig(P/'figures'/f'07_startup_supports.{ext}',dpi=170,facecolor='white')
plt.close(fig)
