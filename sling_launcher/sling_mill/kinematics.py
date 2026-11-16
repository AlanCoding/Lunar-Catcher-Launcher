"""Discrete contacts, edge overlap, prescribed constant-acceleration trajectory.
Each spatial midpoint carries exact m*a*dx kinetic work. Force shares sum to one.
Stations are extended through the exit so the entire rod remains supported.
"""
import numpy as np

def evaluate(c, histories=False):
    for key in ['acceleration','v_entry','pitch','payload_length','payload_width','payload_depth','payload_density','contact_patch','operating_days']:
        if c[key]<=0: raise ValueError(f'{key} must be positive')
    if c['v_exit']<=c['v_entry']: raise ValueError('Exit speed must exceed entrance speed')
    if not 0<=c['speed_droop']<1: raise ValueError('Reserved speed loss must be in [0,1)')
    if c['slip_margin']<0: raise ValueError('Forward-driving slip margin must be nonnegative')
    a, v0, ve = c['acceleration'], c['v_entry'], c['v_exit']
    L, s, patch = c['payload_length'], c['pitch'], c['contact_patch']
    mass = L*c['payload_width']*c['payload_depth']*c['payload_density']
    mdot = c['annual_mass_kg']/(c['operating_days']*86400)
    freq = mdot/mass
    S = (ve**2-v0**2)/(2*a)
    stations = np.arange(s/2, S+L+patch/2, s)
    n = len(stations)
    nx = int(np.ceil(S/s*c['integration_steps_per_pitch']))
    dx = S/nx
    x = (np.arange(nx)+.5)*dx
    v = np.sqrt(v0*v0+2*a*x)
    dt = dx/v
    # Rod occupies [x,x+L]; contact ends when its rear clears the patch.
    uend = np.sqrt(v0*v0+2*a*np.minimum(stations+patch/2, S))
    u = (uend+c['slip_margin'])/(1-c['speed_droop'])
    offsets = np.arange(int(np.ceil((L+patch)/s))+2)
    idx = np.floor((x-patch/2-s/2)/s).astype(int)[:,None]+offsets
    valid = (idx>=0)&(idx<n)
    idx = np.clip(idx,0,n-1)
    overlap = np.maximum(0, np.minimum((x+L)[:,None],stations[idx]+patch/2)
                         -np.maximum(x[:,None],stations[idx]-patch/2))/patch
    overlap *= valid
    if np.any(overlap.sum(axis=1)==0):
        raise ValueError('Unsupported rod: station spacing leaves a contact gap')
    force = mass*a*overlap/overlap.sum(axis=1)[:,None]
    slip = u[idx]-v[:,None]
    heat = force*slip*dt[:,None]
    work = force*dx
    eh = np.bincount(idx.ravel(),weights=heat.ravel(),minlength=n)
    ek = np.bincount(idx.ravel(),weights=work.ravel(),minlength=n)
    duration = np.bincount(idx.ravel(),weights=((force>0)*dt[:,None]).ravel(),minlength=n)
    fpeak = np.zeros(n); np.maximum.at(fpeak,idx.ravel(),force.ravel())
    slip_peak = np.zeros(n); np.maximum.at(slip_peak,idx[force>0],slip[force>0])
    ppeak = fpeak*u
    # Constant mean motor, cyclic energy deficit, then available recharge interval.
    swings = np.zeros(n)
    for j in range(n):
        rows, cols = np.where((idx==j)&(force>0))
        increments = force[rows,cols]*u[j]*dt[rows]-(eh[j]+ek[j])*freq*dt[rows]
        cum = np.r_[0,np.cumsum(increments)]
        swings[j] = np.ptp(cum)
    summary = dict(mass_flow_kg_s=mdot,payload_mass_kg=mass,launch_frequency_hz=freq,
                   interval_s=1/freq,entry_occupancy=freq*L/v0,
                   entry_clear_gap_m=v0/freq-L,exit_clear_gap_m=ve/freq-L,
                   active_distance_m=S,installed_length_m=S+L+patch,
                   travel_time_s=(ve-v0)/a,active_pairs_approx=int(np.ceil(S/s)),
                   installed_pairs=n,interior_pairs=L/s,
                   ideal_power_W=.5*mdot*(ve*ve-v0*v0),slip_heat_W=freq*eh.sum(),
                   contact_peak_force_pair_N=float(fpeak.max()),
                   minimum_slip_m_s=float(slip[force>0].min()),
                   energy_error_fraction=float((ek.sum()-.5*mass*(ve*ve-v0*v0))/(.5*mass*(ve*ve-v0*v0))))
    arrays=dict(position_m=stations,rim_speed_m_s=u,energy_payload_J=ek,energy_slip_J=eh,
                force_pair_peak_N=fpeak,contact_duration_s=duration,
                motor_pair_mean_W=(ek+eh)*freq,motor_pair_peak_W=ppeak,
                energy_swing_pair_J=swings,recharge_interval_s=1/freq-duration,
                rpm=u/c['radius']*60/(2*np.pi),peak_sliding_speed_m_s=slip_peak)
    if histories:
        arrays['_history']=(x,dt,idx,force,u)
    return summary, arrays
