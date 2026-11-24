"""Publication detail of one radial cable, using the reference taper profile."""
from pathlib import Path
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Rectangle
P=Path(__file__).parent
GREEN='#426e60';BLUE='#49677e';GRAY='#8c918e';INK='#293e39';LIGHT='#e8ede9'

def draw():
 d=json.loads((P/'blended/search_results/torque_reproduction.json').read_text())
 c=d['parameters'];v=d['cases']['torque_complete_envelope']['last_stage']
 R=c['radius'];h=R*c['hub_ratio'];omega=v['rim_speed_m_s']/R
 r=np.linspace(h,R,500)
 area=v['radial_tip_area_mm2']*np.exp(1560*omega**2*(R*R-r*r)/(2*c['working_stress_Pa']))
 diameter=2*np.sqrt(area/np.pi)
 ratio=area[0]/area[-1]
 plt.rcParams.update({'svg.fonttype':'none','font.family':'DejaVu Sans','font.size':12})
 fig=plt.figure(figsize=(12,6.3),facecolor='white')
 fig.text(.055,.92,'Taper carries the rotating cable’s own load',fontsize=23,weight='bold',color=GREEN)
 ax=fig.add_axes([.055,.40,.89,.42]);ax.set_aspect('equal');ax.set(xlim=(-50,420),ylim=(-60,65));ax.axis('off')
 ax.add_patch(Circle((0,0),h*1000,fc='#deded5',ec=GRAY,lw=1.5))
 ax.add_patch(Rectangle((R*1000,-42),8,84,fc=GREEN))
 ax.fill_between(r*1000,-diameter/2,diameter/2,color=BLUE,zorder=3)
 ax.plot(r*1000,diameter/2,color=INK,lw=.8)
 ax.plot(r*1000,-diameter/2,color=INK,lw=.8)
 ax.text(0,54,'Hub',ha='center',color=INK,fontsize=15)
 ax.text(R*1000,54,'Rim',ha='center',color=INK,fontsize=15)
 ax.annotate('',(R*1000,-49),(h*1000,-49),arrowprops=dict(arrowstyle='<->',color=GRAY))
 ax.text((h+R)*500,-57,f'{(R-h)*1000:.1f} mm radial span',ha='center',va='top',color=BLUE,fontsize=11)
 ax.text(160,35,'Thicker toward the hub',ha='center',color=BLUE,fontsize=14)
 # Same-scale cross sections make the area ratio visually explicit.
 ax2=fig.add_axes([.07,.08,.40,.27]);ax2.set_aspect('equal');ax2.axis('off');ax2.set(xlim=(-30,115),ylim=(-26,28))
 for x,diam,a,label in [(0,diameter[0],area[0],'Root'),(85,diameter[-1],area[-1],'Tip')]:
  ax2.add_patch(Circle((x,0),diam/2,fc=BLUE,ec=INK,lw=1))
  ax2.text(x,23,label,ha='center',color=INK,fontsize=13)
  ax2.text(x,-22,f'Ø {diam:.2f} mm',ha='center',color=BLUE,fontsize=12)
 fig.text(.55,.30,f'{ratio:.2f}:1 area taper',fontsize=24,weight='bold',color=GREEN)
 fig.text(.55,.235,f'{np.sqrt(ratio):.2f}:1 diameter ratio',fontsize=17,color=BLUE)
 fig.text(.55,.16,'Last-stage radial cable · 1.0 GPa working stress',fontsize=11,color=GRAY)
 fig.text(.055,.025,'Calculated single-cable profile. Dimensions shown to scale within each view.',fontsize=10,color=GRAY)
 for ext in ('svg','png'):fig.savefig(P/'figures'/f'09_radial_cable_taper.{ext}',dpi=180,facecolor='white')
 plt.close(fig)
if __name__=='__main__':draw()
