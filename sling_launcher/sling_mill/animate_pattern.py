"""Publication motion schematic, using the established SVG palette and drum geometry.
Speeds and bar thickness are illustrative; this is not a dynamics result.
"""
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Rectangle
from matplotlib.collections import LineCollection
from PIL import Image
from geometry import geometry, rotate
ROOT=Path(__file__).parent
plt.rcParams.update({'svg.fonttype':'none','font.family':'DejaVu Sans'})
GREEN='#426e60'; BLUE='#49677e'; GRAY='#8c918e'; SAND='#c9bb98'
fig,ax=plt.subplots(figsize=(11,4.5),dpi=100)
fig.subplots_adjust(left=.035,right=.985,bottom=.16,top=.8)
R=.56; h=.11*R; depth=.10; length=2.30
centers=np.arange(.9,8.1,1.4); v0=.9; accel=.30
entry_gap=.05; interval=(length+entry_gap)/v0; period=4*interval
acceleration_rear=centers[0]-length; frame_count=160
ax.set(xlim=(-4,9),ylim=(-1.35,1.35),aspect='equal');ax.axis('off')
fig.text(.045,.92,'Sling mill',size=22,weight='bold',color=GREEN)
rotors=[]
_,P,Q,H=geometry(R,h)
for x in centers:
 for sign in (1,-1):
  y=sign*(R+depth/2)
  ax.add_patch(Circle((x,y),R,fc='#f5f7f4',ec=GREEN,lw=1.6))
  ax.add_patch(Circle((x,y),h,fc='#dfdfd6',ec=GRAY,lw=.8))
  lc=LineCollection([],colors=['#bbc4bf','#9eb0b9']*10,linewidths=.7);ax.add_collection(lc)
  marker,=ax.plot([],[],color=GREEN,lw=2.8)
  rotors.append((x,y,sign,lc,marker))
  # Contact surface direction remains forward for both opposed drums.
  ax.annotate('',(x+.17,sign*.20),(x-.17,sign*.20),arrowprops=dict(arrowstyle='->',color=BLUE,lw=1.1))
bars=[]
for _ in range(8):
 p=Rectangle((0,-depth/2),length,depth,fc=SAND,ec='#665c43',lw=1.0,zorder=5);ax.add_patch(p);bars.append(p)
ax.annotate('',(8.9,0),(8.25,0),arrowprops=dict(arrowstyle='->',color=BLUE,lw=2))
frames=[]
for i in range(frame_count):
 t=period*i/frame_count
 for x,y,sign,lc,marker in rotors:
  # Integer revolutions per loop make GIF seam exact; monotonic stage speeds.
  turns=round((1.08*np.sqrt(v0*v0+2*accel*x)/R)*period/(2*np.pi))
  angle=sign*2*np.pi*turns*t/period
  seg=[]
  for phi in np.linspace(0,2*np.pi,10,endpoint=False)+angle:
   pp,qq,hh=rotate([P,Q,H*np.array([1,sign])],phi)+[x,y]
   seg.extend([[qq,pp],[hh,pp]])
  lc.set_segments(seg)
  theta=np.linspace(angle,angle+.18,12)
  marker.set_data(x+R*np.cos(theta),y+R*np.sin(theta))
 # Infinite periodic feed; bars enter from outside camera and accelerate through it.
 positions=[]
 for k in range(-12,12):
  age=t-k*interval
  # Constant entry velocity until the leading end reaches the first rollers.
  rear=acceleration_rear+v0*age+.5*accel*max(age,0)**2
  if rear<9.5 and rear+length>-4.1:positions.append(rear)
 # Rigid bars have identical time-shifted motion and never overlap.
 ordered=sorted(positions)
 assert all(q-p>=length-1e-9 for p,q in zip(ordered,ordered[1:]))
 for j,b in enumerate(bars):
  b.set_visible(j<len(positions))
  if j<len(positions):b.set_x(positions[j])
 if i==48:
  fig.savefig(ROOT/'figures/05_mill_motion.svg',facecolor='white')
  fig.savefig(ROOT/'figures/05_mill_motion.png',facecolor='white',dpi=150)
 fig.canvas.draw()
 frames.append(Image.fromarray(np.asarray(fig.canvas.buffer_rgba())[:,:,:3].copy()))
frames[0].save(ROOT/'figures/05_mill_motion.gif',save_all=True,append_images=frames[1:],duration=60,loop=0,optimize=True)
plt.close(fig)
print(f'Saved {frame_count}-frame GIF; incoming gap {entry_gap/length:.2%} of bar length')
