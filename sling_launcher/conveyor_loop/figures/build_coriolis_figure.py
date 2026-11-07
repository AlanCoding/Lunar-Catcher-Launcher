"""Additional qualitative diagram; does not regenerate figures 01–03."""
from pathlib import Path
import math
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyArrowPatch, PathPatch, FancyBboxPatch
from matplotlib.path import Path as MPath
plt.rcParams['svg.fonttype']='none'
plt.rcParams['font.family']='DejaVu Sans'
OUT=Path(__file__).parent
INK='#303c3c'; MUTED='#6f7771'; BROWN='#9a683d'; GREEN='#557c6a'; BLUE='#466e84'
f,ax=plt.subplots(figsize=(14,8));f.patch.set_facecolor('white')
ax.set_xlim(0,1200);ax.set_ylim(680,0);ax.set_aspect('equal');ax.axis('off');f.subplots_adjust(0,0,1,1)
def text(x,y,s,size=11,c=INK,ha='left'):ax.text(x,y,s,fontsize=size,color=c,ha=ha,va='center')
def arrow(a,b,c=BLUE,lw=2,rad=0):ax.add_patch(FancyArrowPatch(a,b,arrowstyle='-|>',mutation_scale=15,linewidth=lw,color=c,connectionstyle=f'arc3,rad={rad}'))
def line(xs,ys,c=MUTED,lw=1,**kw):ax.plot(xs,ys,color=c,lw=lw,**kw)
def clip(x,y):ax.add_patch(FancyBboxPatch((x-6,y-5),12,10,boxstyle='round,pad=0,rounding_size=2',facecolor=INK,edgecolor='white'))
text(50,52,'04  /  Why the loop may open sideways',23)
text(50,84,'Radial transport needs tangential force · oval is a placeholder, not a solved shape',11,MUTED)
line([50,1150],[108,108],c='#d3d6ce')
# Wheel, hub and a deliberately exaggerated free loop.
line([130,1075],[300,300],c='#c6cdc5',lw=1,linestyle='--')
ax.add_patch(Circle((130,300),10,facecolor=INK));text(130,350,'Hub',11,ha='center')
line([140,260],[300,300],INK,2)
ax.add_patch(Circle((260,300),32,facecolor='white',edgecolor=INK,lw=2))
for i in range(8):
 a=i*math.pi/4;line([260,260+26*math.cos(a)],[300,300+26*math.sin(a)],'#a5afa5',1)
ax.add_patch(Circle((260,300),5,facecolor=INK))
# Closed line: wheel contact on left, long bowed spans and no outer pulley.
verts=[(260,268),(450,168),(1060,140),(1060,300),(1060,460),(450,432),(260,332),(217,332),(217,268),(260,268)]
codes=[MPath.MOVETO]+[MPath.CURVE4]*9
ax.add_patch(PathPatch(MPath(verts,codes),facecolor='none',edgecolor=BROWN,lw=3))
arrow((640,197),(550,196),GREEN);arrow((550,404),(640,403),GREEN)
# positions on the cubic spans
p0=(260,268);p1=(450,168);p2=(1060,140);p3=(1060,300)
def point(t):return tuple((1-t)**3*p0[j]+3*(1-t)**2*t*p1[j]+3*(1-t)*t*t*p2[j]+t**3*p3[j] for j in range(2))
for t in [.23,.48,.73]:
 x,y=point(t);clip(x,y);clip(x,600-y)
 line([x,x],[606-y,618-y],INK,1.5)
 ax.add_patch(FancyBboxPatch((x-15,618-y),30,23,boxstyle='round,pad=0,rounding_size=3',facecolor=BLUE,edgecolor='white'))
arrow((173,262),(116,241),BLUE,2,rad=.35);text(78,207,'Rotation Ω',11,BLUE)
text(665,151,'Return strand · loses angular momentum',12,GREEN,ha='center')
text(665,467,'Outbound payloads · gain angular momentum',12,GREEN,ha='center')
text(1090,300,'r',12,MUTED);text(260,380,'Feed wheel',10,MUTED)
text(860,324,'Free turn',10,MUTED)
# Distinguish required real forces from rotating-frame apparent Coriolis forces.
for left,title,sgn in [(70,'OUTBOUND',-1),(640,'RETURN',1)]:
 ax.add_patch(FancyBboxPatch((left,505),490,109,boxstyle='round,pad=0,rounding_size=8',facecolor='#f3f5f1',edgecolor='#d7ded4'))
 x=left+155;y=560
 text(left+18,494,title,10,GREEN)
 ax.add_patch(Circle((x,y),4,facecolor=INK))
 arrow((x,y),(x-75,y),MUTED)
 arrow((x,y),(x,y+sgn*37),BLUE)
 arrow((x,y),(x-75,y+sgn*37),BROWN)
 text(left+205,539,'Inward + forward' if sgn<0 else 'Inward + backward',12)
 text(left+205,563,'Net tension force on moving mass',9,MUTED)
 text(left+205,589,'Angular momentum supplied' if sgn<0 else 'Angular momentum removed',10,BLUE)
text(50,638,'Local force sketches: inward ←, forward ↑. Radial-feed limit: aθ = 2Ω ṙ at fixed Ω.',10,MUTED)
text(1150,663,'Top view · no shape, stress or stability solution yet',9,MUTED,ha='right')
text(50,663,'CONVEYOR LUNAR SLING  /  CONCEPT STUDY',9,MUTED)
f.savefig(OUT/'04_coriolis_expansion.svg',facecolor='white')
p=OUT/'04_coriolis_expansion.svg';p.write_text('\n'.join(s.rstrip() for s in p.read_text().splitlines())+'\n')
f.savefig(OUT/'04_coriolis_expansion.png',dpi=140,facecolor='white')
