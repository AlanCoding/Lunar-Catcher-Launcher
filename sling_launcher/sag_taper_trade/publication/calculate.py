"""Steady equal-total-stress Kevlar cable over P1's full-circle DEM envelope."""
from pathlib import Path
import json,csv
import numpy as np
from scipy.integrate import solve_ivp
from scipy.optimize import brentq
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from llo_catcher.site_selection.radial_terrain.calculate import profile_point
from llo_catcher.site_selection.global_hills.search import GlobalTerrain,RADIUS
from sling_launcher.staged_spool_bank.model import Model,Case
P=Path(__file__).parent
m=Model(Case());speed=m.w*m.R;stress=m.kappa*1450;rho=1450.;mass=1000.;height=5.;root=m.a;mu=4.9048695e12
site=json.loads((P.parents[2]/'llo_catcher/site_selection/featured_four/adjusted_hilltops/results.json').resolve().read_text())['sites'][0]
Rh=RADIUS+site['hub_elevation_m'];eq=Rh*np.sin(abs(np.radians(site['hub_latitude_deg'])))
def shape(acc,n=1601):
 tip=speed**2/(acc*9.80665);w=speed/tip
 def integrate(zt,dense=False):
  rr=np.hypot(tip,Rh+zt);H=mass*(w*w*tip-mu*tip/rr**3);V=mass*mu*(Rh+zt)/rr**3
  def rhs(r,y):
   z,h,v,M,s=y;T=np.hypot(h,v);ds=T/h;rad=np.hypot(r,Rh+z);lam=rho*T/stress
   return [-v/h,-lam*ds*(w*w*r-mu*r/rad**3),-lam*ds*mu*(Rh+z)/rad**3,-lam*ds,-ds]
  return solve_ivp(rhs,(tip,root),[zt,H,V,0,0],rtol=2e-9,atol=1e-7,dense_output=dense)
 zt=brentq(lambda z:integrate(z).y[0,-1]-height,-20000,height)
 sol=integrate(zt,True);r=np.linspace(root,tip,n);z,H,V,M,s=sol.sol(r);area=np.hypot(H,V)/stress
 return dict(r=r,z=z,area=area,H=H,V=V,acceleration_g=acc,tip_radius_m=tip,omega_rad_s=w,tip_z_m=zt,tether_mass_kg=float(M[0]),arc_length_m=float(s[0]),root_angle_deg=float(np.degrees(np.arctan2(V[0],H[0]))),tip_angle_deg=float(np.degrees(np.arctan2(V[-1],H[-1]))),taper_area_ratio=float(area[0]/area[-1]))
class PatchTerrain:
 def __init__(self):self.a=np.load(P/'p1_dem_patch.npy')
 def height(self,lat,lon):
  lat,lon=np.broadcast_arrays(lat,lon);y=1535.5-lat*512;x=(lon-13)*512-.5
  assert np.all((x>=0)&(x<3327)&(y>=0)&(y<3071))
  yi=np.floor(y).astype(int);xi=np.floor(x).astype(int);wy=y-yi;wx=x-xi
  return 1000*((1-wy)*((1-wx)*self.a[yi,xi]+wx*self.a[yi,xi+1])+wy*((1-wx)*self.a[yi+1,xi]+wx*self.a[yi+1,xi+1]))
def main():
 cache=P/'terrain_envelope.csv'
 if cache.exists() and np.genfromtxt(cache,delimiter=',',names=True)['radius_m'][-1]>=70000:a=np.genfromtxt(cache,delimiter=',',names=True)
 else:
  terrain=PatchTerrain();radii=np.unique(np.r_[np.r_[np.arange(0,22000.1,12.5),np.arange(22025,70000.1,25)],root,eq]);rows=[]
  old=np.genfromtxt(cache,delimiter=',',names=True) if cache.exists() else None
  lookup={float(v['radius_m']):{n:float(v[n]) for n in old.dtype.names} for v in old} if old is not None else {}
  for r in radii:rows.append(lookup[r] if r in lookup else profile_point(terrain,site,r,30))
  with cache.open('w') as f:
   w=csv.DictWriter(f,fieldnames=rows[0]);w.writeheader();w.writerows(rows)
  a=np.genfromtxt(cache,delimiter=',',names=True)
 def gap(s):
  # Combine profile nodes with every terrain radial node to resolve narrow terrain peaks.
  r=np.unique(np.r_[s['r'],a['radius_m'][(a['radius_m']>=root)&(a['radius_m']<=s['tip_radius_m'])]])
  z=np.interp(r,s['r'],s['z']);terrain=np.interp(r,a['radius_m'],a['max_tangent_height_m']);g=z-terrain;j=np.argmin(g)
  return float(g[j]),float(r[j])
 scan=[]
 for acc in np.r_[np.linspace(100,15,86),np.linspace(14.5,4.2,104)]:
  s=shape(acc);g,r=gap(s);scan.append((acc,g))
  if g<0:break
 brackets=[(x[0],y[0]) for x,y in zip(scan,scan[1:]) if x[1]>0 and y[1]<=0]
 assert brackets,'Extend the DEM band: no terrain contact found in current range'
 threshold=brentq(lambda acc:gap(shape(acc))[0],*sorted(brackets[0]),xtol=1e-7)
 cases=[100,50,25,15,threshold,threshold*.96];results=[]
 plt.rcParams.update({'font.size':12,'svg.fonttype':'none','axes.spines.top':False,'axes.spines.right':False})
 extent=max(shape(c)['tip_radius_m'] for c in cases)/1000*1.04
 fig,axs=plt.subplots(3,2,figsize=(14,12),sharex=True,sharey=True,layout='constrained')
 for i,(acc,ax) in enumerate(zip(cases,axs.flat)):
  s=shape(acc);g,where=gap(s);tipgap=s['tip_z_m']-np.interp(s['tip_radius_m'],a['radius_m'],a['max_tangent_height_m'])
  terrain=a['max_tangent_height_m'];ax.fill_between(a['radius_m']/1000,-1400,terrain,color='#ddd6c7');ax.plot(a['radius_m']/1000,terrain,color='#8a826d',lw=1,label='Highest terrain around each circle')
  ax.plot(s['r']/1000,s['z'],color='#426d7e',lw=2.2,label='Loaded tapered Kevlar tether');ax.plot([root/1000]*2,[0,height],color='#4b5149',lw=4)
  ax.scatter([s['tip_radius_m']/1000],[s['tip_z_m']],s=65,c='#b56f39',zorder=5,label='Payload')
  ax.axvline(eq/1000,ls=':',color='#627b55',label='Nearest equator crossing radius')
  if g<-.01:ax.scatter([where/1000],[np.interp(where,s['r'],s['z'])],marker='x',c='#a3312e',s=100,zorder=6)
  ax.axhline(0,color='.5',ls='--',lw=.7)
  ax.set_title(f'{acc:.2f} g · reach {s["tip_radius_m"]/1000:.2f} km\nminimum clearance {g:.1f} m · tip {tipgap:.1f} m',fontsize=12)
  ax.set(xlim=(0,extent),ylim=(min(-1100,min(shape(c)["tip_z_m"] for c in cases)-100),80));ax.grid(alpha=.15)
  if i>=4:ax.set_xlabel('Horizontal radius from hub (km)')
  if i%2==0:ax.set_ylabel('Height above hub tangent plane (m)')
  row={k:v for k,v in s.items() if np.isscalar(v)};row.update(minimum_clearance_m=g,controlling_radius_m=where,payload_point_clearance_m=float(tipgap));results.append(row)
  np.savez_compressed(P/f'case_{i+1}.npz',**s)
  # Individual publication panel with its own legend.
  f,b=plt.subplots(figsize=(10,4.8),layout='constrained');b.fill_between(a['radius_m']/1000,-1400,terrain,color='#ddd6c7');b.plot(a['radius_m']/1000,terrain,color='#8a826d',label='Full-circle maximum terrain');b.plot(s['r']/1000,s['z'],color='#426d7e',lw=2.5,label='Tapered Kevlar tether');b.scatter([s['tip_radius_m']/1000],[s['tip_z_m']],c='#b56f39',s=70,label='1 tonne payload');b.axvline(eq/1000,ls=':',color='#627b55',label='Nearest equator crossing');b.axhline(0,color='.5',ls='--',lw=.7)
  if g<-.01:b.scatter([where/1000],[np.interp(where,s['r'],s['z'])],marker='x',c='#a3312e',s=100,label='Terrain penetration')
  zoom=max(6,s['tip_radius_m']/1000*1.08);bottom=min(float(np.min(terrain[a['radius_m']<=zoom*1000])),s['tip_z_m'])-80
  b.set(xlim=(0,zoom),ylim=(bottom,60),xlabel='Horizontal radius from hub (km)',ylabel='Height above hub tangent plane (m)',title=ax.get_title());b.legend(fontsize=9,loc='lower left');b.grid(alpha=.15)
  for ext in ['png','svg']:f.savefig(P/f'case_{i+1}.{ext}',dpi=180)
  plt.close(f)
 fig.legend(*axs.flat[0].get_legend_handles_labels(),loc='outside lower center',ncol=2,fontsize=11)
 fig.suptitle('P1 hill · fixed release speed · longer tethers sag into the surrounding terrain\n5 m support datum; vertically exaggerated; maximum terrain over all azimuths',fontsize=16)
 for ext in ['png','svg']:fig.savefig(P/f'p1_tether_series.{ext}',dpi=180)
 plt.close(fig)
 terrain_check=profile_point(PatchTerrain(),site,shape(threshold)['tip_radius_m'],10)['max_tangent_height_m']
 validation=dict(direct_tip_terrain_clearance_m=shape(threshold)['tip_z_m']-terrain_check,root_height_max_error_m=max(abs(shape(c)['z'][0]-height) for c in cases),threshold_clearance_m=gap(shape(threshold))[0],fine_grid_threshold_clearance_m=gap(shape(threshold,6401))[0])
 # Independent quadrature of distributed force, plus source-patch overlap check.
 fine=shape(50,6401);r=fine['r'];z=fine['z'];h=fine['H'];v=fine['V'];ds=np.hypot(h,v)/h;rad=np.hypot(r,Rh+z);lam=rho*fine['area']
 errors=[abs((h[0]-h[-1])/np.trapezoid(lam*ds*(fine['omega_rad_s']**2*r-mu*r/rad**3),r)-1),abs((v[0]-v[-1])/np.trapezoid(lam*ds*mu*(Rh+z)/rad**3,r)-1)]
 assert max(errors)<1e-6
 lat=np.linspace(-.4,.4,40);lon=np.linspace(15.5,17,40);overlap=float(np.max(abs(PatchTerrain().height(lat,lon)-GlobalTerrain().height(lat,lon))))
 assert overlap<1e-6
 validation.update(force_integral_relative_errors_50g=errors,overlap_dem_match_max_m=overlap)
 output=dict(speed_m_s=speed,working_stress_Pa=stress,density_kg_m3=rho,support_radius_m=root,support_height_m=height,equator_nearest_radius_m=eq,first_contact_acceleration_g=threshold,site=site,cases=results,validation=validation)
 (P/'results.json').write_text(json.dumps(output,indent=2)+'\n')
 with (P/'scenarios.csv').open('w') as f:w=csv.DictWriter(f,fieldnames=results[0]);w.writeheader();w.writerows(results)
 print(json.dumps({'threshold':threshold,'cases':results,'validation':validation},indent=2))
if __name__=='__main__':main()
