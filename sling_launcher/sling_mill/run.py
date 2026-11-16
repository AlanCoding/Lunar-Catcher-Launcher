"""Run from any working directory: python sling_launcher/sling_mill/run.py."""
import argparse, csv, json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from kinematics import evaluate
from structure import size
from stability import screen
from draw import diagrams
ROOT=Path(__file__).parent

def csvwrite(path, columns):
    keys=list(columns)
    with path.open('w') as f:
        w=csv.writer(f); w.writerow(keys);w.writerows(zip(*(columns[k] for k in keys)))

def compute(c):
    k,st=evaluate(c); b,extra,mass=size(c,k,st);st.update(extra)
    stability=screen(c,k,st)
    warnings=[]
    if k['entry_occupancy']>1: warnings.append('Single-lane entrance occupancy exceeds 1.')
    if c['pitch']<=2*c['radius']: warnings.append('Adjacent drums have zero or negative geometric clearance; shaft/frame and belt-motion clearance must be added.')
    if b['maximum_belt_thickness_m']>.05*c['radius']: warnings.append('Panel sizing requires a belt thicker than 5% of radius: thin flexible-belt approximation fails.')
    if not np.isfinite(b['conditional_installed_mass_kg']): warnings.append('No finite belt sizing under the configured panel geometry and allowable stress.')
    if np.any(st['contacted_anchor_reaction_N']<0): warnings.append('Contacted anchors require outward support: tension-only force path fails.')
    if stability['axial_end_loaded_stress_Pa']>c['payload_allowable']: warnings.append('Conservative end-loaded payload stress exceeds assumed allowable.')
    if stability['conservative_compression_N']>stability['buckling_load_N']: warnings.append('Conservative payload compression exceeds Euler buckling screen.')
    warnings += ['Coupled rotating belt/contact shape and fatigue life remain unvalidated.',
                 'Friction, wear, flash temperature, joint efficiency and payload properties are assumed.',
                 'Non-radial torque members curve under centrifugal load; straight-member sizing is conditional.',
                 'Startup gravity threshold is only a necessary lower bound; deployed supports and tension control remain to be solved.']
    return dict(**k,**b,stability=stability,warnings=warnings,feasible_demonstrated=False),st,mass

def figures(c,r,st,mass):
    x=st['position_m']
    fig,axs=plt.subplots(2,2,figsize=(12,8))
    axs[0,0].plot(x,st['rim_speed_m_s']);axs[0,0].set_ylabel('Fixed rim speed (m/s)')
    axs[0,1].plot(x,st['energy_slip_J']*r['launch_frequency_hz']/1000);axs[0,1].set_ylabel('Mean sliding heat per pair (kW)')
    axs[1,0].plot(x,st['motor_pair_peak_W']/1e6,label='Contact peak')
    axs[1,0].plot(x,st['motor_pair_mean_W']/1e6,label='Cycle mean');axs[1,0].legend();axs[1,0].set_ylabel('Mechanical drive per pair (MW)')
    axs[1,1].plot(x,st['free_ring_stress_Pa']/1e9,label='Free ring benchmark')
    axs[1,1].plot(x,st['belt_stress_Pa']/1e9,label='Supported-panel screen')
    axs[1,1].axhline(r['working_stress_Pa']/1e9,color='brown',ls='--',label='Working allowable')
    axs[1,1].set_ylabel('Stress (GPa)');axs[1,1].legend()
    for ax in axs.flat: ax.set_xlabel('Station position (m)');ax.grid(alpha=.2)
    fig.suptitle('Sling mill · 10 million tonnes/year · prescribed sliding contacts')
    fig.tight_layout();save(fig,'stage_results')
    fig,axs=plt.subplots(1,2,figsize=(12,4))
    axs[0].semilogy(x,st['belt_thickness_m']*1000);axs[0].set_ylabel('Required belt thickness (mm)')
    axs[1].semilogy(x,st['radial_tip_tension_N']/1000,label='Radial member tip')
    axs[1].semilogy(x,st['torque_member_tip_tension_N']/1000,label='Torque member tip');axs[1].legend();axs[1].set_ylabel('Peak tension (kN)')
    for ax in axs: ax.set_xlabel('Position (m)');ax.grid(alpha=.2)
    fig.suptitle('Conditional panel model: geometry failures remain visible');fig.tight_layout();save(fig,'structural_screen')

def save(fig,name):
    for ext in ['svg','png']:fig.savefig(ROOT/'results'/f'{name}.{ext}',dpi=150,bbox_inches='tight')
    plt.close(fig)

def transient(c,r,st):
    # Constant mean motor versus contact-following motor, last full interior stage.
    j=np.argmin(abs(st['position_m']-.9*r['active_distance_m']))
    _,raw=evaluate(c,True);x,dt,idx,forces,u=raw['_history']
    t=(np.sqrt(c['v_entry']**2+2*c['acceleration']*x)-c['v_entry'])/c['acceleration']
    ii,jj=np.where((idx==j)&(forces>0)); t=t[ii];p=forces[ii,jj]*u[j]/2
    period=r['interval_s']; local=t-t[0]; mean=st['motor_pair_mean_W'][j]/2
    # Aggregate contact-following drive demand includes all rods in the corridor.
    phase=np.linspace(0,period,2048,endpoint=False)
    trajectory_t=(np.sqrt(c['v_entry']**2+2*c['acceleration']*x)-c['v_entry'])/c['acceleration']
    power_one=np.sum(forces*u[idx],axis=1)
    total=np.zeros_like(phase)
    for shift in range(int(np.ceil(r['travel_time_s']/period))+1):
        total+=np.interp(phase+shift*period,trajectory_t,power_one,left=0,right=0)
    r['simultaneous_contact_following_peak_electrical_W']=float(total.max()/c['motor_efficiency'])
    fig,ax=plt.subplots(figsize=(9,4))
    ax.plot(np.r_[phase,phase+period]*1000,np.tile(total,2)/c['motor_efficiency']/1e6)
    ax.set(xlabel='Time (ms)',ylabel='Total electrical input (MW)',title='Whole mill · two injection periods · contact-following motors')
    ax.grid(alpha=.2);save(fig,'whole_mill_power')
    steps=np.r_[dt[ii],period-dt[ii].sum()]; loads=np.r_[p,0]
    energy=np.r_[0,np.cumsum((mean-loads)*steps)]
    I=st['inertia_per_drum_kg_m2'][j];nominal=u[j]/c['radius']
    E=.5*I*nominal**2+energy-energy.max()
    speed=np.where(E>=0,np.sqrt(np.maximum(0,2*E/I))*c['radius'],np.nan)
    times=np.r_[0,np.cumsum(steps)]
    csvwrite(ROOT/'results'/'rotor_transient.csv',{'time_s':times,'rim_speed_m_s':speed,'energy_J':E})
    fig,axs=plt.subplots(2,1,figsize=(9,6),sharex=True)
    for cycle in range(2):
        tt=np.r_[0,np.cumsum(steps)]+cycle*period
        axs[0].step(tt*1000,np.r_[loads,loads[-1]]/1e6,where='post',color='#426e60')
        axs[1].plot(tt*1000,speed,color='#49677e')
    axs[0].axhline(mean/1e6,color='brown',ls='--',label='Constant mean motor');axs[0].legend()
    axs[0].set_ylabel('Per-drum power (MW)');axs[1].set_ylabel('Rim speed (m/s)');axs[1].set_xlabel('Time (ms)')
    axs[0].set_title('Two launches at a late station · constant-mean motor energy screen')
    fig.tight_layout();save(fig,'rotor_transient')
    r['late_station_constant_motor_droop_fraction']=float(1-np.nanmin(speed)/u[j])
    r['late_station_transient_has_energy_deficit']=bool(np.any(E<0))
    r['late_station_rim_min_m_s']=float(np.nanmin(speed))
    r['late_station_forward_slip_end_required_m_s']=float(np.sqrt(c['v_entry']**2+2*c['acceleration']*min(st['position_m'][j]+c['contact_patch']/2,r['active_distance_m'])))

def main():
    p=argparse.ArgumentParser();p.add_argument('--config',type=Path,default=ROOT/'config.json');args=p.parse_args()
    c=json.loads(args.config.read_text());r,st,mass=compute(c)
    figures(c,r,st,mass)
    diagrams(c,r,system_config=json.loads((ROOT/'config_spaced.json').read_text()))
    transient(c,r,st)
    if r['late_station_rim_min_m_s'] < r['late_station_forward_slip_end_required_m_s']:
        r['warnings'].append('Constant-mean motor with baseline inertia loses the forward-slip margin; use speed headroom and re-size, or contact-following motors.')
    st['peak_contact_heat_flux_W_m2']=st['normal_per_drum_N']*c['mu']*st['peak_sliding_speed_m_s']/(c['belt_width']*c['contact_patch'])
    csvwrite(ROOT/'results'/'stages.csv',st)
    csvwrite(ROOT/'results'/'mass.csv',{'component':list(mass),'mass_kg':list(mass.values())})
    (ROOT/'results'/'summary.json').write_text(json.dumps(r,indent=2)+'\n')
    print(json.dumps(r,indent=2))
if __name__=='__main__':main()
