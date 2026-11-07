"""Concept schematics, not dimensioned engineering drawings. Run from repo root."""
from pathlib import Path
import math
import argparse
parser = argparse.ArgumentParser()
parser.add_argument("--only", help="Output basename to regenerate; default: all three")
ONLY = parser.parse_args().only
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Rectangle, FancyBboxPatch, FancyArrowPatch, Arc
from matplotlib import rcParams
rcParams['svg.fonttype']='none'
rcParams['font.family']='DejaVu Sans'
OUT=Path(__file__).parent
BG='#ffffff'; INK='#303c3c'; MUTED='#6f7771'; LINE='#9a683d'; GREEN='#557c6a'; BLUE='#466e84'; PALE='#d9dfd6'

def start(title,sub):
 f,ax=plt.subplots(figsize=(14,8));f.patch.set_facecolor(BG);ax.set_facecolor(BG)
 ax.set_xlim(0,1200);ax.set_ylim(680,0);ax.set_aspect('equal');ax.axis('off');f.subplots_adjust(0,0,1,1)
 ax.text(50,52,title,fontsize=23,color=INK,weight='bold');ax.text(50,84,sub,fontsize=11,color=MUTED)
 ax.plot([50,1150],[108,108],color='#d3d6ce',lw=1)
 ax.text(50,650,'CONVEYOR LUNAR SLING  /  CONCEPT STUDY',fontsize=9,color=MUTED)
 ax.text(1150,650,'Top view · not to scale',ha='right',fontsize=9,color=MUTED)
 return f,ax

def txt(ax,x,y,s,size=11,c=INK,ha='left'):ax.text(x,y,s,fontsize=size,color=c,ha=ha,va='center')
def line(ax,x,y,color=LINE,lw=3,**kw):ax.plot(x,y,color=color,lw=lw,solid_capstyle='round',**kw)
def arrow(ax,a,b,c=GREEN,lw=2,curve=0):
 ax.add_patch(FancyArrowPatch(a,b,arrowstyle='-|>',mutation_scale=15,linewidth=lw,color=c,connectionstyle=f'arc3,rad={curve}'))
def wheel(ax,x,y,r,c=INK):
 ax.add_patch(Circle((x,y),r,facecolor=BG,edgecolor=c,lw=2))
 ax.add_patch(Circle((x,y),r*.79,fill=False,edgecolor='#bcc3b9',lw=1.5))
 for i in range(8):
  a=i*math.pi/4;line(ax,[x,x+r*.78*math.cos(a)],[y,y+r*.78*math.sin(a)],'#a5afa5',1.4)
 ax.add_patch(Circle((x,y),max(4,r*.14),facecolor=c,edgecolor=BG,lw=1))
def loop(ax,a,b,y,r,width=3,left_wheel=True,right_wheel=False):
 if left_wheel: wheel(ax,a,y,r)
 if right_wheel: wheel(ax,b,y,r)
 line(ax,[a,b],[y+r,y+r],lw=width);line(ax,[a,b],[y-r,y-r],lw=width)
 ax.add_patch(Arc((a,y),2*r,2*r,theta1=90,theta2=270,color=LINE,lw=width))
 ax.add_patch(Arc((b,y),2*r,2*r,theta1=-90,theta2=90,color=LINE,lw=width))
 d=45
 arrow(ax,((a+b)/2-d,y+r),((a+b)/2+d,y+r))
 arrow(ax,((a+b)/2+d,y-r),((a+b)/2-d,y-r))
def clip(ax,x,y,scale=1):
 ax.add_patch(FancyBboxPatch((x-6*scale,y-5*scale),12*scale,10*scale,boxstyle='round,pad=0,rounding_size=2',facecolor=INK,edgecolor=BG,lw=.7))
def turn(ax,x,y,r):
 # Counterclockwise quarter-circle, matching hub rotation.
 ax.add_patch(Arc((x,y),2*r,2*r,theta1=270,theta2=360,color=GREEN,lw=2))
 arrow(ax,(x+10,y-r+1),(x-2,y-r),GREEN)
def payload(ax,x,y,scale=1,c=BLUE,side=1):
 ax.add_patch(FancyBboxPatch((x-6*scale,y-5*scale),12*scale,10*scale,boxstyle='round,pad=0,rounding_size=2',facecolor=INK,edgecolor=BG,lw=.7))
 line(ax,[x,x],[y+side*5*scale,y+side*18*scale],INK,1.4)
 ax.add_patch(FancyBboxPatch((x-16*scale,y+(18 if side==1 else -43)*scale),32*scale,25*scale,boxstyle='round,pad=0,rounding_size=3',facecolor=c,edgecolor=BG,lw=1.3))
 line(ax,[x-9*scale,x+9*scale],[y+side*25*scale,y+side*25*scale],BG,.8)
def badge(ax,x,y,n):
 ax.add_patch(Circle((x,y),13,facecolor=INK,edgecolor=BG,lw=1));txt(ax,x,y,str(n),10,BG,'center')
def save(f,name):
 if ONLY and name != ONLY:
  plt.close(f)
  return
 f.savefig(OUT/(name+'.svg'),facecolor=BG)
 svg=OUT/(name+'.svg')
 svg.write_text('\n'.join(row.rstrip() for row in svg.read_text().splitlines())+'\n')
 f.savefig(OUT/(name+'.png'),dpi=140,facecolor=BG);plt.close(f)

f,ax=start('01  /  One sling, two motions','Zyling · one circulating loop on each opposing arm')
# track and rotating frames, deliberately enlarged
ax.add_patch(Circle((600,340),145,fill=False,edgecolor='#d6d6ca',lw=15))
ax.add_patch(Circle((600,340),145,fill=False,edgecolor=MUTED,lw=1,linestyle=(0,(4,5))))
line(ax,[455,745],[340,340],MUTED,2)
for x in [455,745]:
 ax.add_patch(Rectangle((x-27,303),54,74,facecolor=PALE,edgecolor=INK,lw=1.5))
 for yy in [295,374]:
  for xx in [x-26,x+13]: ax.add_patch(Rectangle((xx,yy),13,12,facecolor=INK))
 # wheel at apex in top view
 wheel(ax,x,340,24)
# outward right loop
loop(ax,745,1070,340,24)
# left loop, mirror only artwork
loop(ax,130,455,340,24,left_wheel=False,right_wheel=True)
for x in [820,915,1005]:payload(ax,x,364)
for x in [205,300,390]:payload(ax,x,316,c='#8b8374',side=-1)
for x in [205,300,390]:clip(ax,x,364)
for x in [820,915,1005]:clip(ax,x,316)
for x in [455,745]:turn(ax,x,340,49)
ax.add_patch(Circle((600,340),10,facecolor=INK));badge(ax,600,301,1)
badge(ax,730,406,2);badge(ax,780,289,3);badge(ax,1026,425,4);badge(ax,1115,340,5)
arrow(ax,(710,231),(485,222),BLUE,3,curve=.5);txt(ax,600,164,'Whole machine rotates · Ω',13,BLUE,'center')
arrow(ax,(1092,307),(1092,205),BLUE,3);txt(ax,1113,221,'Release',11,BLUE)
arrow(ax,(108,375),(108,474),BLUE,3);txt(ax,70,502,'Paired release',11,BLUE)
txt(ax,895,453,'Slow line circulation · u',12,GREEN,'center')
txt(ax,291,223,'Countermass stream',12,MUTED,'center')
txt(ax,600,526,'1  Hub / pivot     2  Rover + A-frame     3  Feed / brake wheel',11,INK,'center')
txt(ax,600,555,'4  Payload + reusable attachment     5  Free loop turn',11,INK,'center')
txt(ax,600,590,'Radial loads close through ties; rover wheels supply tangential drive.',10,MUTED,'center')
save(f,'01_system_overview')

f,ax=start('02  /  Feed, carry, release','One arm enlarged · attachment and grip details are conceptual')
loop(ax,225,1020,300,76)
for x in [420,625,825]:payload(ax,x,376,1.25)
for x in [420,625,825]:clip(ax,x,224,1.25)
badge(ax,164,203,3);txt(ax,187,202,'Feed / brake wheel',12)
badge(ax,1020,300,5)
# Loader meets the returning device halfway around the inboard contact arc.
clip(ax,149,300,1.25)
ax.add_patch(FancyBboxPatch((65,286),32,28,boxstyle='round,pad=0,rounding_size=3',facecolor=BLUE,edgecolor=BG,lw=1.3))
arrow(ax,(101,300),(141,300),INK)
line(ax,[81,81],[321,351],MUTED,1)
txt(ax,50,377,'Reload returning\ndevice',11)

arrow(ax,(1095,337),(1132,232),BLUE,3);txt(ax,1090,201,'Release',12,BLUE,'center')
txt(ax,690,177,'Reusable attachment devices return inward',12,GREEN,'center')
txt(ax,700,461,'Payloads move outward with the line',12,GREEN,'center')
# brake / generator below inner wheel
ax.add_patch(FancyBboxPatch((173,425),104,46,boxstyle='round,pad=0,rounding_size=6',facecolor=PALE,edgecolor=INK,lw=1.5))
line(ax,[225,225],[309,425],INK,2);txt(ax,225,448,'Brake / drive',10,INK,'center')
arrow(ax,(278,447),(320,447),GREEN);txt(ax,225,493,'Energy recovery',11,GREEN,'center')
# Soft-release inset: device retains a controlled payout link before separation.
ax.add_patch(FancyBboxPatch((555,485),585,132,boxstyle='round,pad=0,rounding_size=9',facecolor='#e7e9e1',edgecolor='#d0d6cb'))
badge(ax,579,505,4);txt(ax,601,505,'Gentle release · controlled unloading',12)
txt(ax,601,526,"For Rüdiger’s wave concern",10,MUTED)
line(ax,[580,730],[547,547],lw=3);clip(ax,652,547,1.3)
line(ax,[652,652,775],[553,571,571],INK,1.5)
ax.add_patch(FancyBboxPatch((775,559),30,24,boxstyle='round,pad=0,rounding_size=3',facecolor=BLUE,edgecolor=BG))
arrow(ax,(682,590),(792,590),BLUE);txt(ax,738,607,'~10 m travel? To size.',9,MUTED,'center')
# Conceptual force ramp inset (not simulated data).
line(ax,[850,850,1110],[548,593,593],MUTED,1)
xx=[850+i*2.5 for i in range(101)]
yy=[551+42*(3*(i/100)**2-2*(i/100)**3) for i in range(101)]
line(ax,xx,yy,GREEN,2)
txt(ax,980,543,'Support force → zero',9,GREEN,'center')
txt(ax,980,607,'Then detach; device returns',9,MUTED,'center')
txt(ax,60,562,'Grip must transmit the braking load.',12)
txt(ax,60,587,'Extra wraps / separate holding device',10,MUTED)
save(f,'02_feed_and_attachment')

f,ax=start('03  /  Two loops, one step in thickness','One arm shown · thicker inner loop + thinner outer loop')
# Both loops contact one shared rigid pulley / common shaft.
# Inner loop wraps its right half; outer loop wraps its left half.
loop(ax,155,600,300,42,width=6,right_wheel=True)
loop(ax,600,1085,300,42,width=2.7,left_wheel=False)
ax.add_patch(Circle((600,300),55,facecolor='none',edgecolor=BLUE,lw=1.5,linestyle='--'))
for x in [270,420,810,965]:payload(ax,x,342,1.1)
for x in [270,420,810,965]:clip(ax,x,258,1.1)
arrow(ax,(1117,342),(1140,240),BLUE)
txt(ax,1000,198,'Gentle release; devices return',10,BLUE,'center')
arrow(ax,(665,375),(535,375),GREEN,2)
txt(ax,600,395,'Power passes through the shared pulley',10,GREEN,'center')
badge(ax,600,220,6);txt(ax,600,180,'Shared intermediate pulley',13,BLUE,'center')
txt(ax,330,427,'Thicker inner loop',13,INK,'center');txt(ax,875,427,'Thinner outer loop',13,INK,'center')
badge(ax,96,300,3);badge(ax,1143,300,5)
# transfer inset restrained graphic
ax.add_patch(FancyBboxPatch((200,476),800,123,boxstyle='round,pad=0,rounding_size=10',facecolor='#e7e9e1',edgecolor='#d0d6cb'))
txt(ax,228,505,'6  Payload handoff',12,BLUE)
line(ax,[240,400],[539,539],lw=6);line(ax,[490,650],[539,539],lw=2.7)
payload(ax,373,539,.95);payload(ax,516,539,.95)
arrow(ax,(407,555),(481,555),BLUE)
txt(ax,704,530,'One pulley · common shaft.',11);txt(ax,704,555,'Transfer payload support.',11);txt(ax,704,579,'Handoff mechanism to design.',10,MUTED)
txt(ax,600,132,'No rigid arm to the hub: the intermediate assembly must balance tether forces.',10,MUTED,'center')
save(f,'03_two_stage_loop')
