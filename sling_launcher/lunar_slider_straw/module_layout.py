"""Rigid twin-drum modules: each joins payload-side and countermass-side cable."""
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Circle,Rectangle,Ellipse,FancyArrowPatch,FancyBboxPatch
P=Path(__file__).parent/'figures'
plt.rcParams.update({'font.size':11,'svg.fonttype':'none'})
ink='#354944';out='#b77d46';back='#547b91';steel='#8b978d';tie='#74685b'
def arrow(ax,a,b,c=ink,both=False):ax.add_patch(FancyArrowPatch(a,b,arrowstyle='<->' if both else '-|>',color=c,lw=1.7,mutation_scale=14))
def save(fig,n):
 for ext in ['svg','png']:fig.savefig(P/f'{n}.{ext}',dpi=180,facecolor='white')
 plt.close(fig)
fig,axs=plt.subplots(2,1,figsize=(15,10),layout='constrained',gridspec_kw={'height_ratios':[1,1]})
ax=axs[0];ax.set_aspect('equal');ax.set(xlim=(-91,91),ylim=(-81,84));ax.axis('off')
ax.add_patch(Circle((0,0),76.789,fc='#fafbf7',ec=steel,lw=1.5))
ax.add_patch(Rectangle((-77,-9),154,18,fc='#eef2e9',ec=steel,lw=1.5))
# two cable corridors at inner tangencies; drum pairs above and below corridor
for y in [-2,2]:ax.plot([-88,88],[y,y],color=tie,lw=2)
for y in [-4,4]:
 for sign in [-1,1]:
  for x in [35,41,47,53,59,65]:
   ax.add_patch(Circle((sign*x,y),1.3,fc='#e6d9c6',ec=ink,lw=.8))
for sign in [-1,1]:
 ax.add_patch(Rectangle((77 if sign==1 else -89,-5),12,10,fc='#edf1e8',ec='#69806d',lw=1.5))
 ax.text(sign*53,17,'Payload straw' if sign==1 else 'Countermass straw',ha='center',color=ink)
ax.add_patch(Circle((0,0),1.5,fc=ink));ax.text(0,41,'24 rigid twin-drum modules · 48 spools\nEvery module connects BOTH sides',ha='center',fontsize=13,color=ink)
arrow(ax,(37,33),(44,7));ax.text(0,-32,'Two rows flank the radial cable corridor\nGround wheels support each module directly',ha='center',fontsize=12,color=ink)
ax.text(0,-66,'77 m outer reference radius · module centers placed at 35–65 m for this sketch',ha='center',fontsize=10,color=ink)
ax.set_title('A · Top-down view of the hub and rotating cross-structure',fontsize=16,color=ink)
ax=axs[1];ax.set(xlim=(-87,87),ylim=(-17,20));ax.axis('off')
ax.add_patch(Rectangle((-72,-9),144,18,fc='#f0f3ec',ec=steel,lw=1.2))
for row,y in enumerate([-5,5]):
 for side,sign in enumerate([-1,1]):
  for j,x in enumerate([35,41,47,53,59,65]):
   xx=sign*x;idx=row*12+side*6+j+1
   ax.add_patch(Ellipse((xx,y),5,3,fc='#f9faf6',ec=ink,lw=1.2));ax.add_patch(Ellipse((xx,y),4.2,2.3,fill=False,ec=out,lw=1.6));ax.add_patch(Ellipse((xx,y),3.4,1.6,fill=False,ec=back,lw=1.5))
   ax.text(xx,y,str(idx),ha='center',va='center',fontsize=8,color=ink)
   # wheels projected beneath, symbolic footprints
   ax.add_patch(Rectangle((xx-2.2,y+(-3 if y<0 else 2.2)),1.2,.8,fc=steel));ax.add_patch(Rectangle((xx+1,y+(-3 if y<0 else 2.2)),1.2,.8,fc=steel))
# Show one representative pair per row through the corridor, at two different heights.
for y,sgn in [(-3.4,1),(3.4,-1)]:
 ax.plot([-85,85],[y,y],color=tie,lw=1)
 x=44 if sgn==1 else -44
 ax.plot([-85,x],[y+.26,y+.26],color=back,lw=2)
 ax.plot([x,85],[y-.26,y-.26],color=out,lw=2)
 arrow(ax,(-27,y+.26),(-15,y+.26),back);arrow(ax,(14,y-.26),(26,y-.26),out)
ax.text(0,14,'Each numbered position = two coaxial drums rigidly joined\nOpposed cable leads occupy different vertical levels',ha='center',fontsize=12,color=ink)
ax.text(0,-14,'Representative cable routes shown; the remaining lines run in parallel lanes.\nPositions and lateral dimensions are schematic. The central corridor remains open.',ha='center',fontsize=11,color=ink)
ax.text(-80,0,'← C',ha='center',color=ink);ax.text(80,0,'P →',ha='center',color=ink)
ax.set_title('B · Two-row plan enlarged vertically · wheels directly beneath the modules',fontsize=16,color=ink)
fig.suptitle('Opposed-cable twin drums · rigid pair, local ground drive',fontsize=21,color=ink)
save(fig,'04_paired_bank_layout')
fig,axs=plt.subplots(1,2,figsize=(15,7),layout='constrained',gridspec_kw={'width_ratios':[1.2,1]})
ax=axs[0];ax.set(xlim=(-6,8),ylim=(-1,8));ax.axis('off')
for y,col in [(2.2,out),(3.65,back)]:
 ax.add_patch(Rectangle((-.2,y),2.6,1.2,fc='#edf0e8',ec=col,lw=2));ax.add_patch(Ellipse((1.1,y+1.2),2.6,.25,fc='#fafbf8',ec=col,lw=1.5))
ax.plot([1.1,1.1],[1.3,5.15],color=ink,lw=5)
ax.plot([2.4,7.4],[2.8,2.8],color=out,lw=2);arrow(ax,(4,2.8),(6,2.8),out)
ax.plot([-5.4,-.2],[4.25,4.25],color=back,lw=2);arrow(ax,(-4.4,4.25),(-2.4,4.25),back)
ax.text(5,3.3,'Payload side\npaying out →',ha='center',color=out)
ax.text(-3,4.9,'Countermass side\nreturning →',ha='center',color=back)
ax.text(1.1,5.65,'Rigid common rotor\nBoth drums turn together',ha='center',fontsize=12,color=ink)
ax.add_patch(Rectangle((-.7,1),3.6,.35,fc=steel))
ax.add_patch(FancyBboxPatch((3.2,.7),3.4,1.1,boxstyle='round,pad=.08',fc='#f3f4ed',ec=ink));ax.text(4.9,1.25,'Fixed gearing\n+ forward / reverse clutch',ha='center',va='center',fontsize=10,color=ink)
ax.plot([1.1,1.1,3.1],[2,1.5,1.5],color=ink,lw=2);ax.plot([4.9,4.9,2],[.62,.4,.4],color=ink,lw=2)
for x in [-.1,2]:ax.add_patch(Circle((x,.2),.45,fc='#d8dfd3',ec=ink,lw=1.5))
ax.plot([-5.7,7.5],[-.25,-.25],color=tie,lw=3)
ax.text(1,-.85,'Supporting wheels free-roll during hold; rotor brake holds cable length.',ha='center',fontsize=10,color=ink)
ax.text(1,7.1,'C · Side view of one opposed-cable module',ha='center',fontsize=16,color=ink)
ax.text(1,6.55,'Stacked winding envelope ≈ 2.6 m, plus bearings and frame',ha='center',fontsize=11,color=ink)
ax=axs[1];ax.set(xlim=(0,10),ylim=(0,8));ax.axis('off')
def box(x,y,w,h,txt,col=ink):
 ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=.1',fc='#f4f5ee',ec=col,lw=1.6));ax.text(x+w/2,y+h/2,txt,ha='center',va='center',fontsize=11,color=ink)
box(.4,5.7,4,1.2,'Payload-side drum',out);box(5.6,5.7,4,1.2,'Countermass-side drum',back)
ax.plot([4.5,5.5],[6.3,6.3],color=ink,lw=5);ax.text(5,7.25,'Rigid mechanical connection',ha='center',fontsize=12,color=ink)
box(2.4,3.3,5.2,1.25,'Fixed-ratio ground drive\nforward / reverse engagement\n+ disconnect for holding');arrow(ax,(5,5.6),(5,4.7),both=True)
box(2.4,1,5.2,1.15,'Ground wheel reaction\n↔ rotating structure');arrow(ax,(5,3.15),(5,2.3),both=True)
ax.text(5,.25,'Early stroke: may draw energy. Later: returns energy.\nRadial tension imbalance transfers through the frame/ties.',ha='center',fontsize=10,color=ink)
ax.set_title('Power and reaction paths',fontsize=16,color=ink)
fig.suptitle('One rigid twin-drum rotor · gearing only between rotor and ground wheels',fontsize=20,color=ink)
save(fig,'05_stacked_module')
