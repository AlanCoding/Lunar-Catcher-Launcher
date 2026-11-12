"""Accepted rigid opposed twin-drum design. Complete paired schedule and mass ledger."""
from pathlib import Path
import json,csv
import numpy as np
from scipy.integrate import cumulative_trapezoid
from scipy.optimize import brentq
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from ..staged_spool_bank.model import Model,Case
from ..component_sizing import GEAR_MASS_FIT
P=Path(__file__).parent;O=P/'results/reference';O.mkdir(parents=True,exist_ok=True)
m=Model(Case());T=m.c.period_s;D=T/2;slot=T/8;groups=12;modules=2*groups;lines=2*modules
# Twelve mirrored groups, each has two rigid modules. Stroke + paired hold = 1.5 T.
jobs=[]
for n in range(-36,72):
 start=n*slot;end=start+D;release=np.ceil(end/T-1e-10)*T;reuse=start+groups*slot
 assert release<=reuse+1e-8 and end+300<=reuse
 jobs.append(dict(group=n%groups,start_s=start,end_s=end,release_s=release,next_s=reuse))
for k in range(1,7):assert sum(abs(j['release_s']-k*T)<1e-6 for j in jobs)==8
# Actual rigid-angle winding mapped numerically, retaining the previous winding envelope.
rho=1450.;fill=.65;pack=.75;core=.6053152654289221;width=1.2106305308578442
qgrid=m.s;dep=m.mass-np.interp(m.L-qgrid,m.s,m.mom[0]);stored=m.mass-dep
radius=np.sqrt(core**2+stored/(rho*fill*pack*np.pi*width));theta=cumulative_trapezoid(1/radius,qgrid,initial=0);ws=theta[-1]/D
# Fixed gearing gives constant rotor angular velocity while in motion.
def motion(age,reverse=False):
 th=ws*age if not reverse else theta[-1]-ws*age
 q=np.interp(th,theta,qgrid);r=np.interp(q,qgrid,radius)
 dr=-np.interp(m.L-q,m.s,m.lam)/(2*r*rho*fill*pack*np.pi*width)
 v=ws*r*(-1 if reverse else 1);acc=ws**2*r*dr
 return q,v,acc,r
nt=24000;dt=slot/nt;t=(np.arange(nt)+.5)*dt
hub=np.zeros(nt);net=np.zeros(nt);heat_move=np.zeros(nt);recovered=np.zeros(nt);friction=np.zeros(nt)
module_powers=[];module_torques=[];max_force=0;max_tension=0
# Four active mirrored groups exactly at every phase. Each model.powers covers both geographic sides.
for k in range(4):
 age=t+k*slot;qo,vo,ao,ro=motion(age);qi,vi,ai,ri=motion(age,True)
 ho,so,_=m.powers(qo,vo,ao,1000);hi,si,_=m.powers(qi,vi,ai,0)
 h=ho+hi;s=so+si;gross=.5*(abs(so)+abs(si)) # individual module gross cable-shaft flow
 p=-s/2 # individual rigid module net generated power
 # 1% gross mechanical allowance (winding/bearings); net alone traverses wheel gearing.
 internal=.01*gross
 p_after=p-internal
 rail=np.where(p_after>=0,.96*p_after,p_after/.96)
 hm=internal+(p_after-rail)
 hub+=h;net+=h+s;recovered+=2*rail;heat_move+=2*hm
 mo=m.mass-np.interp(m.L-qo,m.s,m.mom[0]);mi=m.mass-np.interp(m.L-qi,m.s,m.mom[0])
 friction+=2*.1*(2*m.w*(mo+1000)*vo**2+2*m.w*mi*vi**2)
 module_powers.append(p);module_torques.append(p/ws)
 # F = (shaft power - radial inertia corrections)/v; direct centrifugal force expression
 def force(q,load):
  st=m.L-q;M=m.mass-np.interp(st,m.s,m.mom[0]);J=m.mom[1][-1]-np.interp(st,m.s,m.mom[1]);return m.w**2*((m.a-st)*M+J+load*(m.a+q))
 fo=force(qo,1000);fi=force(qi,0);max_force=max(max_force,float(np.max(abs(fo-fi))));max_tension=max(max_tension,float(max(fo.max(),fi.max())))
heat_move+=24000 # auxiliaries / all module bearings baseline
ring_load=hub-recovered+friction+24000+60000 # 60 kW rolling / rim allowance
# Stationary main motor, reduction, inverter; all loads remain positive in reference.
eta=.97*.96*.99*.985
assert ring_load.min()>0
motor=ring_load/(.96*.99);electric=ring_load/eta+40000
heat_station=electric-ring_load+60000
assert np.max(abs(electric-(net+friction+heat_move+heat_station)))<1e-5
# Constant source, 97% charge and 97% discharge inclusive battery converter efficiency.
eff=.97
def cellrate(source):
 diff=source-electric
 return np.where(diff>=0,eff*diff,diff/eff)
source=brentq(lambda p:np.mean(cellrate(p)),float(electric.min()),float(electric.max()))
crate=cellrate(source);energy=np.r_[0,np.cumsum(crate)*dt];swing=np.ptp(energy)/3.6e6
battery_power=max(abs(source-electric));energy_req=1.25*swing/.6
# Conservative high-power assumption: 2C discharge and charge, 100 Wh/kg installed pack.
nominal=np.ceil(max(energy_req,1.25*battery_power/1000/2)/100)*100
battery_mass=nominal/0.1;converter_mass=1.25*battery_power/1000*.5
battery_loss=source-electric-crate
# Separate 310 K battery circuit from 350 K motor/gear oil circuit.
def flux(temp):return .85*.7*5.670374419e-8*(temp**4-250**4)
Ahot=1.25*(heat_move.max()+heat_station.max())/flux(350)
Abat=1.25*battery_loss.max()/flux(310)
# Rotor shell + flanges + common shaft: direct high-tension winding, replacing old capstan/storage model.
outer=float(radius[0]);max_torque=max(float(np.max(abs(x))) for x in module_torques);max_power=max(float(np.max(abs(x))) for x in module_powers)
shaft_d=(16*1.5*max_torque/(np.pi*(325e6/np.sqrt(3))))**(1/3)
corewall=.08;flange=.025;flangeR=outer+.1
shell=2*np.pi*(core**2-(core-corewall)**2)*width*7850
flanges=4*np.pi*(flangeR**2-core**2)*flange*7850
shaft=7850*np.pi*shaft_d**2/4*3.4
rotor_each=1.5*(shell+flanges+shaft) # 50% stiffening, bearing/joint allowance
gear_each=1.4*max(GEAR_MASS_FIT[0]*(1.5*max_torque)**GEAR_MASS_FIT[1],2*max_power/1000)
positions=np.linspace(35,65,6);rail_length=sum(2*np.pi*np.hypot(positions,4));rails=rail_length*.012*7850*1.3
ring_A=.7*.5-(.7-.04)*(.5-.04);ring_mass=ring_A*2*np.pi*m.a*7850*1.3
unit_motor=np.ceil(1.2*motor.max()/8/250000)*250000
# New explicit bill; local production is allocated separately, never removed from total machine mass.
rows=[]
def add(name,mass,local,basis,production):rows.append(dict(component=name,mass_kg=float(mass),assumed_local_fraction=local,basis=basis,lunar_production=production))
add('48 tapered working tethers',lines*m.mass,0,'48 × 3 tonnes; paired holding schedule','Import Kevlar fiber, coatings and quality-critical terminations.')
add('Two straw guides',6000,0,'One 3 t fiber guide each side; provisional for new inventory','Import fiber; local assembly possible.')
add('Jackets, terminations, straw opening hardware',26000,0,'26 t allowance, including larger line inventory','Mixed polymers and precision contacts; imported initially.')
add('24 rigid twin-drum rotors',modules*rotor_each,.7,'80 mm core shells, 25 mm flanges, common shaft, 50% stiffening/bearings allowance','Bulk metal locally fabricated; bearings and qualified contact surfaces imported.')
add('24 module-to-ground reductions',modules*gear_each,0,'One per module, net torque and net power; no inter-drum gearbox','Precision gearing and heat treatment imported initially.')
add('Module clutches, brakes, reversers, levelwinds',modules*1500,0,'1.5 t per rigid module allowance','Precision mechanisms imported; no storage-follower drivetrain.')
add('Module ground wheels and suspension',modules*6000,.5,'Per module: four 1 t support/drive units + four 0.5 t capture rollers','Bulk wheel bodies local; bearings, dampers and wear surfaces imported.')
add('Six fixed circular ground reaction rails',rails,1,'12,000 mm² effective steel per path, six radii, 30% joints/base allowance','Locally refined/fabricated metal; precision alignment remains demanding.')
add('77 m moving drive rim',ring_mass,1,'0.70 × 0.50 m steel box, 20 mm wall, 30% teeth/joints allowance','Local structural metal; finish machining and alignment required.')
add('Rotating cross-structure and low machinery supports',100000,1,'100 t fabricated allowance; 24 suspended modules','Local bulk metal and fabrication.')
add('Opposed tension ties, anchors and lateral bracing',20000,.5,'20 t reserve for cable-force imbalance and radial machinery loads','Metal local; high-performance fiber and precision joints imported.')
add('Loading, retention and synchronized release hardware',45000,.25,'48 line positions and two terminal staging banks','Bulk structure local; release actuators and controls imported.')
add('Eight stationary rim-drive motors',8*unit_motor/1000*4.55*1.25,0,'Industrial 4.55 kg/kW anchor, 25% installation allowance','Electrical steel, windings, insulation and precision manufacture imported initially.')
add('Main reductions and drive wheels',8*unit_motor/1000*2*1.4+12000,.2,'2 kg/kW reduction floor ×1.4 plus 12 t wheels','Precision parts imported; wheel/frame metal partly local.')
add('Main inverters and protection',8*unit_motor/1000*.146*1.25,0,'Prior inverter curve','Imported electronics.')
add('Stationary buffer battery',battery_mass,0,f'{nominal:.0f} kWh at 100 Wh/kg; 2C power screen','Imported cells and battery management; installed pack allowance included.')
add('Battery bidirectional converter',converter_mass,0,'0.5 kg/kW at 125% peak buffer power; allowance','Imported power electronics.')
add('Radiators, rotary fluid transfer and manifolds',(Ahot+Abat)*9.6,.5,'8 kg/m² plus20% heat transport; two temperature circuits','Panel/pipe metal partly local; coatings, pumps and unions imported.')
add('Electrical distribution and controls',12000,.2,'12 t allowance; auxiliary slip rings only','Conductors partly local; controls imported.')
solar=1.2*source
add('External solar generation',solar/100,.2,'100 W/kg illuminated output;20% over battery-smoothed source','Support metal partly local; cells/electronics imported.')
add('Prepared local foundations',600000,1,'600 t local aggregate/anchors allowance, not an excavation estimate','Local feedstock, grading and foundations.')
netL1=8000/T*(np.exp(-900/(450*9.80665))-.1)
fabricated=sum(r['mass_kg'] for r in rows if r['component']!='Prepared local foundations')
imported=sum(r['mass_kg']*(1-r['assumed_local_fraction']) for r in rows)
mult=1.25*np.exp(2700/(450*9.80665));annual=netL1*365*86400*.5
summary=dict(schedule=dict(groups=groups,rigid_modules=modules,tethers=lines,stroke_s=D,paired_hold_s=T,exchange_repeat_s=1.5*T,tether_full_cycle_s=3*T,job_spacing_s=slot,batch_each_side=8,payload_kg=1000,min_groups_uniform_schedule=11,chosen_groups=12,working_fiber_kg=lines*m.mass,extra_fiber_vs_old_kg=(lines-32)*m.mass,useful_LLO_kg_s=8000/T),geometry=dict(core_radius_m=core,full_radius_m=outer,winding_width_m=width,rotor_rpm=ws*60/(2*np.pi),module_radii_m=positions.tolist(),max_line_tension_N=max_tension,max_module_radial_imbalance_N=max_force,max_module_net_torque_Nm=max_torque,max_module_net_power_W=max_power,rotor_mass_each_kg=rotor_each,reduction_each_kg=gear_each,common_shaft_diameter_m=shaft_d,module_ground_peak_force_at_35m_N=max_power/(m.w*35),module_ground_total_preload_mu_0p35_N=max_power/(m.w*35*.35)),power={name:dict(mean_W=float(v.mean()),max_W=float(v.max()),min_W=float(v.min())) for name,v in dict(ideal_net=net,electrical=electric,moving_heat=heat_move,stationary_heat=heat_station,battery_heat=battery_loss).items()},battery=dict(interval_s=slot,constant_source_W=source,energy_swing_kWh=float(swing),energy_only_nominal_kWh=float(energy_req),peak_bus_power_W=float(battery_power),selected_nominal_kWh=float(nominal),mass_kg=float(battery_mass),conversion_mass_kg=float(converter_mass),charge_efficiency=eff,discharge_efficiency=eff,energy_closure_J=float(energy[-1]),battery_soc_excursion_fraction=float(swing/nominal)),cooling=dict(hot_area_m2=float(Ahot),battery_area_m2=float(Abat),total_area_m2=float(Ahot+Abat),layout_area_with_2x_spacing_m2=float(2*(Ahot+Abat)),inner60m_area_m2=float(np.pi*60**2)),solar=dict(design_W=float(solar),area_at_250W_m2=float(solar/250)),motor_unit_rating_W=float(unit_motor),bill_of_materials=rows,totals=dict(fabricated_kg=fabricated,installed_with_local_foundations_kg=fabricated+600000,assumed_imported_kg=imported,assumed_locally_made_fabricated_kg=fabricated-imported),payback=dict(net_L1_kg_s=netL1,annual_L1_kg_at50pct=annual,imported_L1_investment_kg=imported*mult,annual_multiple_local_build=annual/(imported*mult),all_import_L1_investment_kg=fabricated*mult,annual_multiple_all_import=annual/(fabricated*mult),operating_hours_local_build=imported*mult/netL1/3600))
assert abs(energy[-1])<1 and abs(net.mean()/(8000/T*m.w**2*(m.R**2-m.a**2))-1)<2e-4
(O/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
with (O/'bill_of_materials.csv').open('w') as f:w=csv.DictWriter(f,fieldnames=rows[0].keys());w.writeheader();w.writerows(rows)
np.savez_compressed(O/'cycle.npz',time_s=t,electrical_W=electric,source_W=source,battery_energy_J=energy,ideal_net_W=net,moving_heat_W=heat_move,stationary_heat_W=heat_station)
plt.rcParams.update({'font.size':11,'svg.fonttype':'none'})
def save(fig,n):
 for e in ['png','svg']:fig.savefig(O/f'{n}.{e}',dpi=180)
 plt.close(fig)
fig,ax=plt.subplots(2,1,figsize=(10,7),layout='constrained')
for i in range(3):
 ax[0].plot((t+i*slot)/60,electric/1e6,color='#b67d45',label='Motor/auxiliary demand' if i==0 else None)
 ax[1].plot((np.arange(nt+1)*dt+i*slot)/60,(energy-energy.min())/3.6e6,color='#567b91')
ax[0].axhline(source/1e6,color='#567b60',label='Constant source including battery loss');ax[0].set(ylabel='Electrical power (MW)',title='Accepted rigid modules · stationary cycle-buffer battery');ax[0].legend()
ax[1].set(xlabel='Time (minutes)',ylabel='Stored energy above cycle minimum (kWh)',title=f'Installed {nominal:.0f} kWh · cycle excursion {swing:.1f} kWh')
for a in ax:a.grid(alpha=.2)
save(fig,'battery_buffer')
fig,ax=plt.subplots(figsize=(11,5),layout='constrained')
for g in range(groups):
 for k in range(-1,3):
  st=g*slot+k*groups*slot;en=st+D;hold=en+T
  for lo,hi,c in [(st,en,'#b67d45'),(en,hold,'#c4d5bf')]:
   lo=max(lo,0);hi=min(hi,3*T)
   if hi>lo:ax.broken_barh([(lo/T, (hi-lo)/T)],(g+.1,.75),facecolors=c)
ax.set(xlim=(0,3),ylim=(0,12),xlabel='Catcher orbits',ylabel='Mirrored four-tether group',title='12 groups · 24 rigid modules · 48 tethers: half-orbit motion, one-orbit paired hold')
for k in range(4):ax.axvline(k,color='#666',ls=':')
ax.text(.02,1.02,'Orange: exchange in progress    Green: one end held extended, mate held retracted',transform=ax.transAxes,fontsize=10)
save(fig,'paired_schedule')
print(json.dumps({k:v for k,v in summary.items() if k!='bill_of_materials'},indent=2))
