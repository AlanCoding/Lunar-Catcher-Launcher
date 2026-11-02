"""Run with Blender --background --python this_file -- [--draft] [--views name,...]."""
import bpy, math, json, sys, argparse, random
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parent
parser=argparse.ArgumentParser();parser.add_argument('--draft',action='store_true');parser.add_argument('--views',default='hub,frame,pivot,site,span,profile');args=parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
D=json.loads((P/'scene_inputs.json').read_text());C=D['candidate'];R=C['track_radius_m'];H=C['apex_height_m'];MOON=D['moon_radius_m'];OUT=P/'renders';OUT.mkdir(exist_ok=True)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
for c in list(bpy.data.collections):
 if c.name!='Collection' and c.users==0:bpy.data.collections.remove(c)
bpy.context.preferences.filepaths.save_version=0
scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1
scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=16 if args.draft else 48;scene.cycles.use_denoising=True
scene.render.image_settings.file_format='PNG';scene.render.resolution_percentage=100
scene.render.film_transparent=False
try:scene.view_settings.view_transform='Standard';scene.view_settings.look='None'
except Exception:pass
scene.world.color=(.035,.035,.035)
COL={}
for name in ['Surface','Rotating hardware','Upper payload tie','Low rover ties','Pivot and stabilizing stays','Outward slings','Payloads','Stationary utilities','Cameras','Render annotations']:
 c=bpy.data.collections.new(name);scene.collection.children.link(c);COL[name]=c

def put(o,group):
 for co in list(o.users_collection):co.objects.unlink(o)
 COL[group].objects.link(o);return o

def mat(name,color,metal=0,rough=.6):
 m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True
 bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(*color,1);bs.inputs['Metallic'].default_value=metal;bs.inputs['Roughness'].default_value=rough
 return m
steel=mat('Fabricated steel',(.42,.48,.51),.65,.32);lightsteel=mat('Joints',(.65,.68,.65),.65,.35)
tire=mat('Lunar wheel analog / schematic tread',(.095,.11,.12),.2,.8);gold=mat('Aramid ropes',(.9,.57,.10),.15,.5)
blue=mat('Wheel electric drives',(.10,.32,.42),.4,.4);orange=mat('Reel drives',(.65,.24,.09),.3,.45)
binmat=mat('Ballast retention',(.28,.36,.32),.3,.6);rock=mat('Local regolith',(.26,.25,.23),0,.95)
solar=mat('Solar panels',(.025,.07,.16),.4,.28);white=mat('Radiator emitting panels',(.72,.76,.73),.12,.45)
trackmat=mat('Compacted lunar track',(.14,.145,.15),0,.9);moonmat=mat('Lunar surface',(.27,.275,.28),0,.95)
nt=moonmat.node_tree;bs=nt.nodes.get('Principled BSDF');noise=nt.nodes.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=2.7;noise.inputs['Detail'].default_value=3
coords=nt.nodes.new('ShaderNodeTexCoord');nt.links.new(coords.outputs['Object'],noise.inputs['Vector'])
bump=nt.nodes.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.35;bump.inputs['Distance'].default_value=.15;nt.links.new(noise.outputs['Fac'],bump.inputs['Height']);nt.links.new(bump.outputs['Normal'],bs.inputs['Normal'])

def finish(o,name,material,group):
 o.name=name;o.data.materials.append(material);put(o,group);return o

def cube(name,loc,scale,material,group='Rotating hardware',angle=0):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.dimensions=scale;o.rotation_euler.z=angle
 bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 return finish(o,name,material,group)

def rod(name,a,b,radius,material,group='Rotating hardware',vertices=24):
 a,b=Vector(a),Vector(b);delta=b-a
 bpy.ops.mesh.primitive_cylinder_add(vertices=vertices,radius=radius,depth=delta.length,location=(a+b)/2)
 o=bpy.context.object;o.rotation_euler=delta.to_track_quat('Z','Y').to_euler()
 for p in o.data.polygons:p.use_smooth=True
 o['axis_length_m']=delta.length
 return finish(o,name,material,group)

def rope(name,points,radii,material,group):
 cu=bpy.data.curves.new(name,'CURVE');cu.dimensions='3D';cu.resolution_u=1;cu.bevel_resolution=2;cu.bevel_depth=1
 sp=cu.splines.new('POLY');sp.points.add(len(points)-1)
 for p,co,r in zip(sp.points,points,radii):p.co=(*co,1);p.radius=float(r)
 ob=bpy.data.objects.new(name,cu);COL[group].objects.link(ob);cu.materials.append(material);return ob

def ground(x,y):return math.sqrt(MOON*MOON-x*x-y*y)-MOON

def polar(theta,z,rad=R):return Vector((rad*math.cos(theta),rad*math.sin(theta),z))

# Spherical ground. Low relief stays below the loaded cable clearance.
rng=random.Random(50);craters=[]
for i in range(42):
 x=rng.uniform(-7200,7200);y=rng.uniform(-6500,6500)
 if abs(y)<900 and abs(x)<1300:continue
 craters.append((x,y,rng.uniform(100,420)))
def terrain(x,y):
 base=ground(x,y)
 if abs(x)<1300 and abs(y)<1000:return base
 val=.45*math.sin(x*.013)*math.cos(y*.017)
 for cx,cy,r in craters:
  u=math.hypot(x-cx,y-cy)/r
  if u<1.5:val+=-.12*r*max(0,1-u*u)**2+2*math.exp(-((u-1)/.16)**2)
 return base+min(0.,val) if math.hypot(x,y)<6200 else base+val
n=280;extent=8500;vs=[];fs=[]
for j in range(n+1):
 y=-extent+2*extent*j/n
 for i in range(n+1):
  x=-extent+2*extent*i/n;vs.append((x,y,terrain(x,y)))
for j in range(n):
 for i in range(n):a=j*(n+1)+i;fs.append((a,a+1,a+n+2,a+n+1))
mesh=bpy.data.meshes.new('Spherical lunar ground mesh');mesh.from_pydata(vs,[],fs);mesh.update();ob=bpy.data.objects.new('Lunar surface • 17 km tile',mesh);COL['Surface'].objects.link(ob);mesh.materials.append(moonmat)
for p in mesh.polygons:p.use_smooth=True
# Local high-resolution pad prevents coarse-mesh curvature interpolation at wheels.
N=256;vs=[];fs=[]
for rad in [R-11,R+11]:
 for i in range(N):t=2*math.pi*i/N;vs.append((rad*math.cos(t),rad*math.sin(t),0.0))
for i in range(N):j=(i+1)%N;fs.append((i,j,N+j,N+i))
me=bpy.data.meshes.new('Unbanked annulus');me.from_pydata(vs,[],fs);ob=bpy.data.objects.new('Flat circular track • 76.789 m centerline radius',me);COL['Surface'].objects.link(ob);me.materials.append(trackmat)
# Wheel and foot geometry, exactly eight wheels.
def wheel(theta,spec,name):
 rad=Vector((math.cos(theta),math.sin(theta),0));center=polar(theta,spec['radius_m']+0.0);w=spec['width_m'];r=spec['radius_m']
 ob=rod(name,center-rad*w/2,center+rad*w/2,r,tire,vertices=64);ob['diameter_m']=2*r;ob['installed_mass_kg']=spec['mass_kg']
 for sign in [-1,1]:rod(name+' rim '+str(sign),center+rad*(sign*w/2),center+rad*(sign*w/2+.025*sign),r*.60,lightsteel,vertices=48)
 # Thin tread bars contained within the nominal outside diameter.
 tangent=Vector((-math.sin(theta),math.cos(theta),0))
 for k in range(32):
  ph=2*math.pi*k/32;rr=tangent*math.cos(ph)+Vector((0,0,math.sin(ph)))
  rod(name+f' tread {k:02}',center+rr*(r-.045)-rad*w*.48,center+rr*(r-.045)+rad*w*.48,.045,steel,vertices=6)
 return center,rad
powered=C['powered_wheel'];passive=C['passive_wheel'];L=C['pole_legs'][0]['length_m'];lag=2*math.asin(L/(2*R));gap=2*math.asin((powered['radius_m']+passive['radius_m']+.65)/(2*R))
foot_angles=[]
for f,theta in enumerate([0,math.pi]):
 apex=polar(theta,H);feet=[]
 for leg_idx,t in enumerate([theta,theta-lag]):
  tag=f'Frame {"AB"[f]} / {"vertical" if leg_idx==0 else "trailing"}'
  pc,rad=wheel(t,powered,tag+' POWERED wheel');qc,_=wheel(t-gap,passive,tag+' passive wheel');feet.append(pc);foot_angles.append(t)
  # Fore/aft coupling offset to the side of the tire, not a second radial wheel.
  off=rad*(powered['width_m']/2+.25)
  rod(tag+' tandem coupling',pc+off,qc+off,.16,steel)
  spec=C['pole_legs'][f*2+leg_idx]
  rod(tag+' pole',pc,apex,spec['diameter_m']/2,steel)
  rod(tag+' axle',pc-rad*3.7,pc+rad*3.7,.23,lightsteel)
  for sign in [-1,1]:
   # Two balanced ballast boxes per foot, bulk density 1800 kg/m³.
   boxheight=(C['ballast_kg']/8/1800)/(10*4)
   loc=pc+rad*sign*6;loc.z=C['low_tie_attachment_height_m']
   box=cube(tag+f' ballast bin {sign}',loc,(4,10,boxheight),binmat,angle=t)
   box['rock_mass_kg']=C['ballast_kg']/8
   cube(tag+f' exposed regolith {sign}',loc+Vector((0,0,boxheight/2)),(3.7,9.7,.08),rock,angle=t)
  # Mass-based visual packaging envelopes, not supplier CAD dimensions.
  motor_len=C['wheel_drive']['motor_kg']/2000/(math.pi*.9**2)
  rod(tag+' electric motor',pc+rad*(powered['width_m']/2+.1),pc+rad*(powered['width_m']/2+.1+motor_len),.9,blue,vertices=40)
  gear_len=C['wheel_drive']['gearbox_kg']/3000/(math.pi*1.1**2)
  rod(tag+' fixed reduction',pc-rad*(powered['width_m']/2+.1),pc-rad*(powered['width_m']/2+.1+gear_len),1.1,blue,vertices=40)
 rod(f'Frame {f} base brace',feet[0]+Vector((0,0,.5)),feet[1]+Vector((0,0,.5)),.18,steel)
 # Apex platform and a capstan plus storage assembly in the available envelope.
 def local(x,y,z):return apex+Vector((math.cos(theta)*x-math.sin(theta)*y,math.sin(theta)*x+math.cos(theta)*y,z))
 cube(f'Frame {f} apex platform',local(-2,0,-1.4),(9,10,.3),steel,angle=theta)
 core=C['reel']['core_radius_m'];outer=C['reel']['outer_radius_m'];width=C['reel']['width_m'];axis=Vector((-math.sin(theta),math.cos(theta),0))
 for nm,x,y in [('capstan',-2.8,2.5),('empty storage',-4.7,-2.5)]:
  center=local(x,y,core-1.1)
  rod(f'Frame {f} {nm} barrel',center-axis*width/2,center+axis*width/2,core,orange,vertices=48)
  for sign in [-1,1]:rod(f'Frame {f} {nm} flange {sign}',center+axis*(sign*width/2),center+axis*(sign*(width/2+.12)),outer,steel,vertices=48)
 # Reel-drive package mass envelopes (one drive per apex).
 gearvol=C['reel_drive']['gearbox_kg']/3000
 cube(f'Frame {f} reel gearbox',local(1,2,-.9+gearvol/(3*3)/2),(3,3,gearvol/9),orange,angle=theta)
 motorvol=C['reel_drive']['motor_kg']/2000
 cube(f'Frame {f} reel motor',local(1,-2,-.9+motorvol/(2.5*2.5)/2),(2.5,2.5,motorvol/6.25),blue,angle=theta)
 # Schematic guide routes solved exterior centerline to the capstan.
 rope(f'Frame {f} guide', [tuple(local(-2.8,2.5,core-1.1)),tuple(local(-1,1,0)),tuple(apex)], [.045]*3,gold,'Rotating hardware')

# Upper cross-tie and separate low cross-ties. The low crossing node floats;
# it does not terminate the radial forces on the ground pivot.
sag=C['low_tie']['sag_m'];rho=1450;stress=.999e9
for theta,nm,height,T,group in [(0,'Upper apex-to-apex tie',H,C['upper_tie_endpoint_force_n'],'Upper payload tie'),(0,'Low tie / leading feet',C['low_tie_attachment_height_m'],C['low_tie']['endpoint_force_n']/2,'Low rover ties'),(-lag,'Low tie / trailing feet',C['low_tie_attachment_height_m'],C['low_tie']['endpoint_force_n']/2,'Low rover ties')]:
 points=[];rads=[]
 for i in range(201):
  x=-R+2*R*i/200;points.append((x*math.cos(theta),x*math.sin(theta),height-sag*(1-(x/R)**2)))
  tension=T*math.exp(rho*D['omega_rad_s']**2*(R*R-x*x)/(2*stress));rads.append(math.sqrt(tension/stress/math.pi/.65))
 rope(nm,points,rads,gold,group)
rod('Floating low-tie crossing junction',(0,0,C['low_tie_attachment_height_m']-.12),(0,0,C['low_tie_attachment_height_m']+.12),.4,steel,'Low rover ties')
# Ground-mounted pivot/swivel is independent of the floating low-tie junction.
# These dimensions and stay diameters are illustration assumptions, not sizing.
staymat=mat('Center-pivot stays / cyan',(.04,.65,.85),.25,.35)
bs=staymat.node_tree.nodes.get('Principled BSDF');bs.inputs['Emission Color'].default_value=(.04,.65,.85,1);bs.inputs['Emission Strength'].default_value=.35
pivot=(0,0,1.05)
rod('Ground pivot foundation (schematic)',(0,0,0),(0,0,.18),1.8,steel,'Pivot and stabilizing stays',vertices=48)
rod('Ground pivot post',(0,0,.18),pivot,.35,lightsteel,'Pivot and stabilizing stays')
rod('Rotating stay swivel',(0,0,.85),(0,0,1.1),.62,staymat,'Pivot and stabilizing stays',vertices=40)
stay_highlights=[]
for sign in [-1,1]:
 pts=[(sign*R,0,H),pivot]
 ob=rope(f'Apex-to-ground-pivot stay {sign}',pts,[.012,.012],staymat,'Pivot and stabilizing stays')
 ob['diameter_is_illustrative']=True;ob['ground_attachment_m']=list(pivot)
 ob=rope(f'STAY VISIBILITY highlight {sign}',pts,[.12,.12],staymat,'Render annotations')
 ob['display_only']=True;ob.visible_shadow=False;stay_highlights.append(ob)

# Physical outward ropes: exact exported centerline and mass-derived taper.
for sign,nm in [(1,'Useful payload'),(-1,'Rock countermass')]:
 points=[(sign*p[0],sign*p[1],p[2]) for p in D['outward_points_m']]
 ob=rope(nm+' sling',points,[d/2 for d in D['outward_rope_diameter_m']],gold,'Outward slings');ob['shape_source']='scene_inputs.json / solved fully deployed loaded branch'
 end=Vector(points[-1]);payload=cube(nm+' 1000 kg envelope',end-Vector((0,0,.65)),(1.5,1.2,1.3),blue if sign==1 else rock,'Payloads');payload['mass_kg']=1000;payload['geometry_assumed']=True

# Stationary arrays. Solar 200 W/m² is an illustration assumption, thermal
# area is a model output. Dimensions imply no detailed mounting design.
solar_area=C['peak_solar_w']/200;sw=40;sl=solar_area/(80*sw)
for j in range(8):
 for i in range(10):
  x=-600+i*(sw+8)+sw/2;y=300+j*(sl+8)+sl/2;z=ground(x,y)+1.3
  cube(f'Solar module {j}_{i}',(x,y,z),(sw,sl,.12),solar,'Stationary utilities')
  for k in range(1,8):cube(f'Solar cell row {j}_{i}_{k}',(x-sw/2+k*sw/8,y,z+.07),(.035,sl,.015),steel,'Stationary utilities')
rw=20;rl=C['radiator_area_m2']/(64*rw)
for j in range(8):
 for i in range(8):
  x=400+i*(rw+4)+rw/2;y=300+j*(rl+5)+rl/2;z=ground(x,y)+1.5
  cube(f'Radiator module {j}_{i}',(x,y,z),(rw,rl,.15),white,'Stationary utilities')
# Actual sun shadows; no atmosphere or invented Earth in the sky.
bpy.ops.object.light_add(type='SUN',location=(0,0,100));sun=bpy.context.object;sun.name='Sun';sun.data.energy=2.3;sun.data.angle=.0093;sun.rotation_euler=Vector((.4,.6,-1.2)).to_track_quat('-Z','Y').to_euler()

# Render-only visibility overlays are separated and labelled in the images.
highlights=[]
for sign in [-1,1]:
 pts=[(sign*p[0],0,p[2]+.05) for p in D['outward_points_m']]
 highlights.append(rope('SPAN ONLY • rope visibility highlight',pts,[4.]*len(pts),gold,'Render annotations'))
for o in highlights:o.hide_render=True;o.hide_viewport=True

cameras={}
def camera(name,pos,target,scale,res):
 bpy.ops.object.camera_add(location=pos);o=bpy.context.object;o.name='Camera / '+name;put(o,'Cameras');o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();o.data.type='ORTHO';o.data.ortho_scale=scale;o.data.clip_start=.1;o.data.clip_end=50000;cameras[name]=(o,res);return o
camera('hub',(215,-270,175),(0,0,11),320,(1800,1200))
camera('pivot',(30,-42,27),(0,0,3),35,(1800,1200))
camera('frame',(145,-100,65),(R-3,-12,13),105,(1800,1400))
camera('site',(900,-1000,1050),(0,270,0),1450,(2000,1400))
camera('span',(0,-11500,8500),(0,0,-2),13000,(2400,1100))
camera('profile',(3000,-7500,0),(3000,0,0),6500,(2400,650))
# Camera-aligned text: exact pixel-relative titles independent of scene scale.
annotation_objects=[]
textmat=mat('Annotation ivory',(.9,.92,.93),0,1)
bs=textmat.node_tree.nodes.get('Principled BSDF');bs.inputs['Emission Color'].default_value=(.9,.92,.93,1);bs.inputs['Emission Strength'].default_value=1
captions={
 'hub':('THE 50 g LUNAR SLING','76.79 m track radius  /  28.68 m apex  /  4 powered + 4 passive wheels','Cyan: apex-to-ground-pivot stays (highlighted). Gold: upper and low cross-ties.'),
 'pivot':('GROUND PIVOT + STAY CONNECTIONS','Cyan stays terminate on the ground-mounted swivel','Gold low ties cross above it; their center junction is not the ground pivot.'),
 'frame':('ONE A-FRAME / FOUR WHEELS','25.44 m vertical leg  /  35.97 m trailing leg  /  50 mph','Sized parts; ballast boxes and drive packaging are illustrative.'),
 'site':('STATIONARY POWER + HEAT REJECTION','21.97 MW solar peak  /  33,123 m² radiator area','Solar area assumes 200 W/m². Heat-transfer interfaces not designed.'),
 'span':('11.57 km TIP-TO-TIP','1,000 kg useful payload + 1,000 kg rock countermass','Physical positions to scale. Gold rope highlights widened for visibility.'),
 'profile':('LOADED OUTWARD TETHER / TRUE-SCALE PROFILE','28.68 m apex  /  5,787 m release radius  /  10.51 m minimum cable-center clearance','No vertical exaggeration. Ropes highlighted; loaded equilibrium, not release dynamics.')}
def titles(name):
 for o in annotation_objects:bpy.data.objects.remove(o,do_unlink=True)
 annotation_objects.clear();cam,res=cameras[name];width=cam.data.ortho_scale;height=width*res[1]/res[0]
 for idx,(txt,y,size) in enumerate([(captions[name][0],.44,.024),(captions[name][1],.365,.012),(captions[name][2],-.455,.011)]):
  cu=bpy.data.curves.new('Render caption','FONT');cu.body=txt;cu.size=min(width*size,height*(.047 if idx==0 else .025));cu.align_x='CENTER';cu.align_y='CENTER';cu.extrude=0;cu.materials.append(textmat)
  ob=bpy.data.objects.new('Caption '+str(idx),cu);COL['Render annotations'].objects.link(ob);ob.parent=cam;ob.location=(0,height*y,-5);ob.rotation_euler=(0,0,0);ob.visible_shadow=False;annotation_objects.append(ob)
 if name in ['hub','pivot']:
  bpy.context.view_layer.update()
  target=cam.matrix_world.inverted() @ Vector(pivot)
  end=(target.x,target.y,-4.5)
  start=(target.x-width*.20,target.y-height*.12,-4.5)
  a,b=Vector(start),Vector(end);direction=(b-a).normalized();side=Vector((-direction.y,direction.x,0));arrow=width*.006
  segments=[(a.lerp(b,i/12),a.lerp(b,(i+.55)/12)) for i in range(12)]
  segments += [(b-direction*arrow+side*arrow*.4,b),(b-direction*arrow-side*arrow*.4,b)]
  for a1,b1 in segments:
   line=rope('Annotation only / pivot leader',[a1,b1],[width*.00022]*2,textmat,'Render annotations');line.parent=cam;line.visible_shadow=False;annotation_objects.append(line)
  cu=bpy.data.curves.new('Pivot label','FONT');cu.body='GROUND PIVOT';cu.size=width*.011;cu.align_x='CENTER';cu.materials.append(textmat)
  ob=bpy.data.objects.new('Ground pivot label',cu);COL['Render annotations'].objects.link(ob);ob.parent=cam;ob.location=(start[0],start[1]-height*.024,-4.5);ob.visible_shadow=False;annotation_objects.append(ob)
# Save with hub selected; camera list and physical ropes retained in the file.
scene['geometry_source']='publication/candidate_50g.json + scene_inputs.json'
scene['pose']='Fully deployed loaded equilibrium; static engineering illustration'
scene['track_radius_m']=R;scene['release_acceleration_earth_g']=50
scene.camera=cameras['hub'][0];scene.render.resolution_x=1800;scene.render.resolution_y=1200
titles('hub')
for screen in bpy.data.screens:
 for area in screen.areas:
  if area.type=='VIEW_3D':
   area.spaces.active.region_3d.view_perspective='CAMERA'
   area.spaces.active.shading.color_type='MATERIAL'
# Structural checks against the frozen candidate.
wp=[o for o in bpy.data.objects if o.name.endswith('POWERED wheel')]
wq=[o for o in bpy.data.objects if o.name.endswith('passive wheel')]
legs=[o for o in bpy.data.objects if o.name.endswith(' pole')]
assert len(wp)==4 and len(wq)==4 and len(legs)==4
assert all(abs(math.hypot(o.location.x,o.location.y)-R)<1e-4 for o in wp+wq)
assert all(abs(a-b)<1e-4 for a,b in zip(sorted(o['axis_length_m'] for o in legs),sorted(p['length_m'] for p in C['pole_legs'])))
assert abs(sum(o.get('rock_mass_kg',0) for o in bpy.data.objects)-C['ballast_kg'])<1e-5
scene['validated_powered_wheel_count']=len(wp);scene['validated_passive_wheel_count']=len(wq)
bpy.ops.wm.save_as_mainfile(filepath=str(P/'lunar_sling_50g.blend'))
prior_views=json.loads((P/'render_manifest.json').read_text()).get('views',{}) if (P/'render_manifest.json').exists() else {}
manifest={'blender_version':bpy.app.version_string,'views':prior_views,'true_rope_geometry':True,'illustration_assumptions':{'regolith_bulk_density_kg_m3':1800,'motor_packaging_density_kg_m3':2000,'gear_packaging_density_kg_m3':3000,'solar_installed_w_m2':200,'ballast_bins':8,'span_highlight_radius_m':4,'stay_highlight_radius_m':.12,'schematic_stay_radius_m':.012,'schematic_pivot_height_m':1.05,'payload_envelope_m':[1.5,1.2,1.3]}}
for name in args.views.split(','):
 cam,res=cameras[name];scene.camera=cam;factor=.6 if args.draft else 1
 scene.render.resolution_x=int(res[0]*factor);scene.render.resolution_y=int(res[1]*factor)
 for o in highlights:o.hide_render=name not in ['span','profile']
 for o in stay_highlights:o.hide_render=name not in ['hub','frame','pivot','site']
 titles(name);scene.render.filepath=str(OUT/f'{name}.png');bpy.ops.render.render(write_still=True)
 manifest['views'][name]={'file':str(OUT/f'{name}.png'),'position':list(cam.location),'ortho_width_m':cam.data.ortho_scale,'resolution':[scene.render.resolution_x,scene.render.resolution_y],'rope_highlights':name in ['span','profile']}
(P/'render_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
# Leave the hub view with labeled stay highlights; long-span highlights off.
for o in highlights:o.hide_render=True
for o in stay_highlights:o.hide_render=False
titles('hub');scene.camera=cameras['hub'][0];scene.render.resolution_x=1800;scene.render.resolution_y=1200
bpy.ops.wm.save_as_mainfile(filepath=str(P/'lunar_sling_50g.blend'))
print('SCENE_AND_RENDERS_COMPLETE',P)
