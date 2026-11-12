"""Conceptual top-down batch diagram. Departure arrows are local velocity directions."""
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Circle,Rectangle,FancyArrowPatch
P=Path(__file__).parent
INK='#354944';FIBER='#b77d46';RETURN='#547b91';GUIDE='#69806d';GROUND='#e1e2d7'
plt.rcParams.update({'font.size':12,'svg.fonttype':'none'})
def arrow(ax,a,b,color=INK,ls='-',lw=1.6):
 ax.add_patch(FancyArrowPatch(a,b,arrowstyle='-|>',mutation_scale=13,color=color,lw=lw,linestyle=ls))
def machine(ax,released):
 ax.set(xlim=(-6.8,6.8),ylim=(-3.4,3.4),aspect='equal');ax.axis('off')
 ax.add_patch(Circle((0,0),1.05,fc='#f7f7f1',ec=GROUND,lw=7));ax.add_patch(Circle((0,0),1.05,fill=False,ec=GUIDE,lw=1))
 ax.add_patch(Rectangle((-.95,-.32),1.9,.64,fc='#d3d8ce',ec=GUIDE))
 for x in [-.65,-.35,.35,.65]:
  for y in [-.21,.21]:ax.add_patch(Circle((x,y),.105,fc='white',ec=INK,lw=1))
 ax.add_patch(Circle((0,0),.07,color=INK))
 for sign in [-1,1]:
  ax.add_patch(Rectangle((.95 if sign==1 else -6.0,-.48),5.05,.96,fc='#edf1e8',ec=GUIDE,lw=1.4))
  for j,y in enumerate(np.linspace(-.16,.16,8)):
   x=sign*(5.0+.12*j)
   ax.plot([sign*.95,x],[y,y],color=FIBER,lw=.85,alpha=.85)
   if released:
    # At opposed arm ends, positive (CCW) rotation gives opposite tangential departures.
    end=(x,y+sign*2.05)
    arrow(ax,(x,y),end,FIBER,'--',1)
    ax.scatter([end[0]],[end[1]],s=24,c=FIBER,zorder=6)
    ax.scatter([x],[y],s=10,facecolors='white',edgecolors=FIBER,zorder=6)
   else:
    empty = j < 2 if sign == -1 else j >= 6
    ax.scatter([x],[y],s=24,facecolors='white' if empty else FIBER,edgecolors=RETURN if empty else FIBER,zorder=6)
  # Each moving end has its own lane and a cable terminating exactly at that end.
  # Full-length waiting lines occupy the central lanes; moving lines use the edges.
  for q,offset in [(2.3,.29),(3.9,.40)]:
   loaded_y=-sign*offset
   return_y=sign*offset
   ax.plot([sign*.95,sign*q],[loaded_y,loaded_y],color=FIBER,lw=1.3)
   ax.scatter([sign*q],[loaded_y],marker='o',s=24,facecolors=FIBER,edgecolors=FIBER,zorder=7)
   arrow(ax,(sign*(q-.20),-sign*.59),(sign*(q+.35),-sign*.59),FIBER,lw=1)
   ax.plot([sign*.95,sign*q],[return_y,return_y],color=RETURN,lw=1.3)
   ax.scatter([sign*q],[return_y],marker='o',s=24,facecolors='white',edgecolors=RETURN,zorder=7)
   arrow(ax,(sign*(q+.35),sign*.59),(sign*(q-.20),sign*.59),RETURN,lw=1)
 # Explicit CCW rotation arc, clear of the straight guide.
 th=np.linspace(np.radians(35),np.radians(145),60);ax.plot(1.45*np.cos(th),1.45*np.sin(th),color=INK,lw=1.5)
 arrow(ax,(1.45*np.cos(th[-3]),1.45*np.sin(th[-3])),(1.45*np.cos(th[-1]),1.45*np.sin(th[-1])),INK)
 ax.text(0,1.7,'Hub rotation',ha='center',fontsize=10,color=INK)
 ax.text(0,-1.2,'Paired drums',ha='center',fontsize=10,color=INK)
 ax.text(-3.1,-1.1,'Countermass-side straw',ha='center',fontsize=11,color=GUIDE)
 ax.text(3.1,-1.1,'Payload-side straw',ha='center',fontsize=11,color=GUIDE)
 if released:
  ax.text(5.25,2.8,'8 useful loads',ha='center',color=FIBER,fontsize=12)
  ax.text(-5.25,-2.8,'8 opposing loads',ha='center',color=FIBER,fontsize=12)
 else:
  ax.text(-5.25,1.1,'Hold the ready loads',ha='center',fontsize=11,color=INK)
  ax.text(5.25,1.1,'Build the batch',ha='center',fontsize=11,color=INK)
for released,name,title in [(False,'prepare_gradually','Prepare gradually'),(True,'release_batch','Release one batch at the catcher window')]:
 fig,ax=plt.subplots(figsize=(12,6.8),facecolor='white',layout='constrained')
 machine(ax,released)
 ax.set_title(title,fontsize=23,color=INK,pad=12)
 # Consistent symbols for both figures, including extended empty ends awaiting return.
 ax.scatter([-4.8],[-3.05],s=30,c=FIBER)
 ax.text(-4.5,-3.05,'Payload',va='center',fontsize=11,color=INK)
 ax.scatter([-2.1],[-3.05],s=30,facecolors='white',edgecolors=RETURN)
 ax.text(-1.8,-3.05,'Empty cable end',va='center',fontsize=11,color=INK)
 ax.text(1.5,-3.05,'Dashed arrows: release direction' if released else 'Ready loads wait; empty ends return in turn',va='center',fontsize=11,color=INK)
 fig.text(.5,.008,'Top-down concept · terminal spacing and hub size exaggerated · guide and cables remain attached',ha='center',fontsize=10,color='#65736b')
 for ext in ['svg','png']:fig.savefig(P/f'{name}.{ext}',dpi=180,facecolor='white',bbox_inches='tight')
 plt.close(fig)
