"""Angular histories and publication summary for constant-cruise free cables."""
from pathlib import Path
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
P=Path(__file__).parent
COL={'extend':'#a2673d','retract':'#547b91'}
def main():
 ds={n:dict(np.load(P/f'constant_speed_n{n}.npz')) for n in [32,64]};ms={n:json.loads((P/f'constant_speed_n{n}.json').read_text()) for n in ds};m=ms[64];d=ds[64]
 # Keep endpoint orientation continuous in time; shift the spatial band to its branch.
 for a in ds.values():
  continuous=np.degrees(np.unwrap(np.arctan2(a['xy_m'][:,-1,1],a['xy_m'][:,-1,0])))
  shift=continuous-a['tip_angle_deg'];a['tip_angle_deg']=continuous
  a['angle_min_deg']=a['angle_min_deg']+shift;a['angle_max_deg']=a['angle_max_deg']+shift
 plt.rcParams.update({'font.size':12,'svg.fonttype':'none','axes.spines.top':False,'axes.spines.right':False})
 fig,axs=plt.subplots(2,2,figsize=(13,8),layout='constrained',sharex='col')
 rows=[]
 for col,phase in enumerate(['extend','retract']):
  for n in [32,64]:
   a=ds[n];mask=a['phase']==phase
   if not mask.any():continue
   t=a['time_s'][mask];elapsed=t-t[0];angles=a['tip_angle_deg'][mask];color=COL[phase]
   axs[0,col].plot(elapsed/60,angles,color=color,lw=1.8 if n==64 else 1,ls='-' if n==64 else '--',alpha=1 if n==64 else .55,label=f'Tip, {n} cells')
   axs[1,col].plot(elapsed/60,a['stress_Pa'][mask].max(axis=1)/1e9,color=color,ls='-' if n==64 else '--',alpha=1 if n==64 else .55)
   if n==64:
    axs[0,col].fill_between(elapsed/60,a['angle_min_deg'][mask],a['angle_max_deg'][mask],color=color,alpha=.2,label='Cable span outside 500 m radius')
    row=dict(phase=phase,tip_min_deg=float(angles.min()),tip_max_deg=float(angles.max()),max_lateral_tip_m=float(abs(a['xy_m'][mask,-1,1]).max()),duration_minutes=float(elapsed[-1]/60),completed=next(v['completed'] for v in m['solver'] if v['phase']==phase),peak_stress_GPa=next(v['accepted_step_peak_stress_Pa']/1e9 for v in m['solver'] if v['phase']==phase),samples=[])
    for f in [.25,.5,.75]:
     k=int(np.argmin(abs(elapsed-f*m['config']['travel_s'])));row['samples'].append(dict(stroke_time_fraction=f,elapsed_min=float(elapsed[k]/60),tip_angle_deg=float(angles[k]),tip_radius_m=float(np.linalg.norm(a['xy_m'][mask][k,-1]))))
    early=elapsed<=.8*m['config']['travel_s']
    cruise=(elapsed>=60)&(elapsed<=m['config']['travel_s']-60)
    row['cruise_mean_tip_angle_deg']=float(angles[cruise].mean())
    row['first80pct_tip_min_deg']=float(angles[early].min());row['first80pct_tip_max_deg']=float(angles[early].max())
    rows.append(row)
  if phase=='retract':
   for ax in axs[:,col]:ax.axvspan(.8*m['config']['travel_s']/60,m['config']['travel_s']/60,color='.7',alpha=.15)
  axs[0,col].set_title('Loaded extension' if phase=='extend' else 'Empty retraction · shaded tail is provisional');axs[0,col].axhline(0,color='.5',lw=.8);axs[0,col].legend(fontsize=9)
  axs[1,col].set_xlabel('Time since stroke start (minutes)');axs[1,col].axhline(3,color='#a3312e',ls=':',label='3 GPa stop threshold')
  for ax in axs[:,col]:ax.grid(alpha=.18)
 axs[0,0].set_ylabel('Angle from rotating hub radial line (°)');axs[1,0].set_ylabel('Maximum cable stress (GPa)')
 fig.suptitle('Independent tapered cable · constant 1.72 m/s cruise\n1 t payload · 3 t cable · 10 kg retained end device · 30 s start/stop ramps',fontsize=16)
 save(fig,'angular_deviation')
 for phase in ['extend','retract']:
  fig,ax=plt.subplots(figsize=(8,4.8),layout='constrained')
  mask=d['phase']==phase;elapsed=d['time_s'][mask]-d['time_s'][mask][0]
  selected=np.ones(len(elapsed),dtype=bool) if phase=='extend' else elapsed<=.8*m['config']['travel_s']
  ax.plot(elapsed[selected]/60,d['tip_angle_deg'][mask][selected],color=COL[phase],label='Endpoint angle')
  ax.fill_between(elapsed[selected]/60,d['angle_min_deg'][mask][selected],d['angle_max_deg'][mask][selected],color=COL[phase],alpha=.2,label='Cable span outside 500 m')
  ax.axhline(0,color='.5',lw=.8);ax.set(xlabel='Time since stroke start (minutes)',ylabel='Angle from rotating radial line (°)',title='Loaded extension' if phase=='extend' else 'Empty return · first 80% of stroke');ax.grid(alpha=.18);ax.legend(fontsize=9)
  save(fig,'extension_angles' if phase=='extend' else 'retraction_angles')
 fig,ax=plt.subplots(figsize=(12,4.7),layout='constrained')
 for phase in dict.fromkeys(d['phase']):
  mask=d['phase']==phase
  ax.plot(d['time_s'][mask]/60,d['tip_angle_deg'][mask],label=phase.replace('_',' '))
  ax.fill_between(d['time_s'][mask]/60,d['angle_min_deg'][mask],d['angle_max_deg'][mask],alpha=.12)
 ax.axhline(0,color='.5',lw=.8);ax.set(xlabel='Time from extension start (minutes)',ylabel='Angle from hub radial line (°)',title='Continuous state through hold, release and return');ax.legend(fontsize=9,ncol=3);ax.grid(alpha=.18);save(fig,'full_cycle_angles')
 fig,axs=plt.subplots(1,2,figsize=(12,5),layout='constrained')
 for ax,phase in zip(axs,['extend','retract']):
  mask=d['phase']==phase
  if not mask.any():continue
  t=d['time_s'][mask];X=d['xy_m'][mask];elapsed=t-t[0]
  for f in [.1,.25,.5,.75,.95]:
   if f*m['config']['travel_s']>elapsed[-1]:continue
   k=np.argmin(abs(elapsed-f*m['config']['travel_s']));ax.plot(X[k,:,0]/1000,X[k,:,1]/1000,label=f'{elapsed[k]/60:.1f} min');ax.scatter(X[k,-1,0]/1000,X[k,-1,1]/1000,s=15)
  ax.axhline(0,color='.6',lw=.8);ax.set_aspect('equal',adjustable='datalim');ax.set(xlabel='Rotating radial coordinate (km)',ylabel='Tangential displacement (km)',title=phase.capitalize());ax.legend(fontsize=9);ax.grid(alpha=.15)
 fig.suptitle('Free-cable shapes at constant cruise · equal distance scales');save(fig,'free_cable_shapes')
 checks=[]
 for phase in ['extend','retract']:
  a,b=ds[32],ds[64];ma=a['phase']==phase;mb=b['phase']==phase
  if ma.any() and mb.any():
   ta=a['time_s'][ma]-a['time_s'][ma][0];tb=b['time_s'][mb]-b['time_s'][mb][0];valid=tb<=ta[-1]
   err=np.abs(b['tip_angle_deg'][mb][valid]-np.interp(tb[valid],ta,a['tip_angle_deg'][ma]));checks.append(dict(phase=phase,max_tip_angle_difference_deg=float(err.max()),median_tip_angle_difference_deg=float(np.median(err)),first80pct_max_difference_deg=float(err[tb[valid]<=.8*m['config']['travel_s']].max())))
 result=dict(reference=m,phase_results=rows,mesh_comparison=checks);(P/'summary.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(dict(phase_results=rows,mesh_comparison=checks),indent=2))
def save(fig,name):
 for ext in ['svg','png']:fig.savefig(P/f'{name}.{ext}',dpi=180)
 plt.close(fig)
if __name__=='__main__':main()
