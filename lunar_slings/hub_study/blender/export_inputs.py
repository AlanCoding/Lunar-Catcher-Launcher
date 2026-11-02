"""Export numerical geometry for Blender's bundled Python (no scipy dependency)."""
from pathlib import Path
import json,hashlib
import numpy as np
from lunar_slings.hub_study.scenario_study import Scenario,geometry
from lunar_slings.hub_study.environment import LunarEnvironment
OUT=Path(__file__).resolve().parent
source=OUT.parent/'publication/candidate_50g.json'
r=json.loads(source.read_text());cable,branches,h,orbit=geometry(Scenario(acceleration_g=50,rover_mph=50,passes=1))
p=branches[0]['shapes'][-1]
assert abs(float(p['r'][-1])-r['release_radius_m'])<.02
points=[[float(x),0.,float(r['apex_height_m']-d)] for x,d in zip(p['r'],p['drop'])]
diameters=(np.sqrt(4*p['lam']/1450/np.pi)/np.sqrt(.65)).tolist()
moon=LunarEnvironment().reference_radius_m
clearance=[pt[2]-(np.sqrt(moon**2-pt[0]**2)-moon) for pt in points]
result=dict(candidate=r,moon_radius_m=moon,omega_rad_s=cable.omega,outward_points_m=points,outward_rope_diameter_m=diameters,
            loaded_centerline_min_clearance_m=float(min(clearance)),source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
            snapshot='Fully deployed loaded near-release equilibrium; not a dynamics animation')
(OUT/'scene_inputs.json').write_text(json.dumps(result,indent=2)+'\n')
print('Exported',len(points),'points;',points[0],points[-1],'; minimum centerline clearance',min(clearance))

# Companion diagram makes the small physical sag readable without distorting
# the actual Blender scene. Axes deliberately use km horizontally and m vertically.
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
fig,ax=plt.subplots(figsize=(11,4.6))
xx=np.array([pt[0] for pt in points]);zz=np.array([pt[2] for pt in points]);gg=np.sqrt(moon**2-xx**2)-moon
ax.plot(xx/1000,zz,color='#ad771b',lw=2.5,label='Solved loaded tether centerline')
ax.plot(xx/1000,gg,color='#606971',lw=2,label='Spherical lunar surface')
ax.fill_between(xx/1000,gg,-15,color='#e5e6e8')
ax.plot([xx[0]/1000]*2,[0,zz[0]],color='#417b95',lw=3,label='28.68 m apex')
ax.annotate('',xy=(xx[-1]/1000,zz[-1]),xytext=(xx[-1]/1000,gg[-1]),arrowprops=dict(arrowstyle='<->',color='#417b95'))
ax.text(4.7,-3.5,'10.51 m\ncenterline clearance',fontsize=10,color='#417b95')
ax.set(xlim=(0,6),ylim=(-15,35),xlabel='Distance from track center (km)',ylabel='Height above central datum (m)',title='50 g loaded near-release pose: calculated outward tether droop')
ax.grid(alpha=.2);ax.legend(loc='upper right',fontsize=9)
fig.text(.5,.02,'Axis scales differ to reveal droop. Blender geometry uses true physical scale.\nThe 3 m design clearance is controlled by another phase, not this loaded release pose.',ha='center',fontsize=9)
fig.tight_layout(rect=(0,.09,1,1));(OUT/'renders').mkdir(exist_ok=True)
for ext in ['png','svg']:
 target=OUT/'renders'/f'droop_diagram.{ext}';fig.savefig(target,dpi=180,bbox_inches='tight')
 if ext=='svg':target.write_text('\n'.join(line.rstrip() for line in target.read_text().splitlines())+'\n')
plt.close(fig)
