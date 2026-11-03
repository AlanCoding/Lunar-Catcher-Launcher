"""Regenerate Phase 4 numerical results, figures and a concise Markdown report.

Run from repo root: .env/hub/bin/python -m sling_launcher.run_orbit_cycle
Creates files only in this study's results/ directory. No optimization.
"""
from dataclasses import asdict, replace
import json
from math import ceil, degrees, pi, radians, sqrt
from pathlib import Path
import platform
import os
import tempfile

os.environ.setdefault('MPLCONFIGDIR',str(Path(tempfile.gettempdir())/'lunar-sling-mpl-cache'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import scipy

from .cycle import (CycleInputs, ideal_cycle, minimum_solar_elevation_window,
                    count_catches_in_window)
from .orbit import (finite_tip_node_intercept, point_surface_reference, propagate,
                    counter_release_state, impact_report, circular_period_s,
                    specific_invariants)
from .study_inputs import OrbitCycleStudy


def run(study: OrbitCycleStudy = OrbitCycleStudy()) -> dict:
    """Return SI results with explicit approximation labels and source config."""
    e, m = study.environment, study.mission
    reference=point_surface_reference(e,m.catcher_altitude_m)
    cases=[]
    for d in study.tip_offsets_m:
        node=finite_tip_node_intercept(e,m.catcher_altitude_m,d,study.tip_tangent_height_m)
        numerical=propagate(e,node.initial_state,node.flight_s)
        error=numerical.y[:,-1]-node.intercept_state
        en0,h0=specific_invariants(node.initial_state,e.mu_m3_s2)
        enf,hf=specific_invariants(numerical.y[:,-1],e.mu_m3_s2)
        cases.append(dict(tip_offset_m=d,
            release_radius_m=float(np.linalg.norm(node.initial_state[:3])),
            inclination_deg=degrees(node.inclination_rad),
            site_tip_speed_m_s=node.site_tip_speed_m_s,
            hub_rate_rad_s=node.hub_rate_rad_s,
            actual_centripetal_earth_g=node.hub_rate_rad_s**2*d/e.earth_g_m_s2,
            max_wheel_path_radius_m=m.proposed_max_wheel_speed_m_s/node.hub_rate_rad_s,
            flight_s=node.flight_s,
            catch_relative_m_s=float(np.linalg.norm(node.catch_relative_vector_m_s)),
            catch_relative_vector_m_s=node.catch_relative_vector_m_s.tolist(),
            catcher_phase_at_release_deg=degrees(node.catcher_phase_at_release_rad),
            transfer_apoapsis_altitude_m=node.apoapsis_radius_m-e.reference_radius_m,
            numerical_position_error_m=float(np.linalg.norm(error[:3])),
            numerical_velocity_error_m_s=float(np.linalg.norm(error[3:])),
            relative_energy_error=abs((enf-en0)/en0),
            relative_angular_momentum_error=float(np.linalg.norm(hf-h0)/np.linalg.norm(h0)),
            equal_radius_counter=impact_report(e,counter_release_state(e,node)),
            shorter_radius_counter=impact_report(e,counter_release_state(
                e,node,study.shorter_counter_radius_fraction))))
    node=finite_tip_node_intercept(e,m.catcher_altitude_m,
                                  study.illustrative_tip_offset_m,study.tip_tangent_height_m)
    cycles=[]
    for speed in study.illustrative_travel_speeds_m_s:
        inputs=CycleInputs(study.illustrative_apex_radius_m,
                           study.illustrative_tip_offset_m,node.hub_rate_rad_s,
                           study.illustrative_payload_kg,study.illustrative_countermass_kg,
                           study.reference_climber_mass_ratio*study.illustrative_payload_kg,speed,
                           study.illustrative_radial_travel_accel_m_s2,
                           study.illustrative_wheel_efficiency,
                           study.illustrative_climber_efficiency,
                           study.illustrative_loading_s,study.illustrative_settle_s)
        cycle=ideal_cycle(inputs,reference['site_revisit_s'])
        cycles.append(dict(travel_speed_m_s=speed,**{
            k:v for k,v in cycle.items() if k!='segments'}))
    sun=minimum_solar_elevation_window(e,radians(study.minimum_solar_elevation_deg))
    best_cycle=cycles[-1]
    sensitivity=[]
    for ratio in study.climber_mass_ratio_sensitivities:
        c=replace(inputs,climber_mass_kg=ratio*study.illustrative_payload_kg)
        cycle=ideal_cycle(c,reference['site_revisit_s'])
        sensitivity.append(dict(each_climber_to_payload_ratio=ratio,
            each_climber_kg=c.climber_mass_kg,
            peak_electrical_w=cycle['peak_electrical_w'],
            electrical_energy_j=cycle['electrical_energy_j'],
            outbound={k:v for k,v in cycle['segments'][0].items()
                      if k.startswith('peak_') or k.endswith('energy_j')},
            returning={k:v for k,v in cycle['segments'][1].items()
                       if k.startswith('peak_') or k.endswith('energy_j')}))
    # Fixed-speed phase mismatch over one site/catcher repeat; correction must
    # be supplied by a later control profile that restores release speed.
    turn=node.hub_rate_rad_s*reference['site_revisit_s']
    mismatch=(turn+pi)%(2*pi)-pi
    sun['ideal_complete_cycles_per_solar_day']=count_catches_in_window(
        sun['operating_window_s'],best_cycle['launch_interval_s'])
    sun['conditional_catches_per_year']=sun['ideal_complete_cycles_per_solar_day']*e.year_s/e.solar_day_s
    sun['conditional_payload_kg_year']=sun['conditional_catches_per_year']*study.illustrative_payload_kg
    return dict(configuration=asdict(study),
                approximation='two-body node intercept; illustrative constant-spin straight-sling cycle',
                versions=dict(python=platform.python_version(),numpy=np.__version__,
                              scipy=scipy.__version__,matplotlib=matplotlib.__version__),
                environment_derived=dict(surface_spin_m_s=e.spin_rad_s*e.reference_radius_m,
                                         surface_gravity_m_s2=e.surface_gravity_m_s2),
                point_reference=reference,finite_tip_cases=cases,cycles=cycles,sun=sun,
                climber_mass_sensitivity=sensitivity,
                constant_spin_phase_mismatch_rad=mismatch,
                required_phase_integral_correction_rad=-mismatch,
                ideal_phase_correction_mean_rad_s=-mismatch/best_cycle['phase_wait_budget_s'],
                illustrative_wheel_speed_m_s=node.hub_rate_rad_s*study.illustrative_apex_radius_m)


def figures(study, out):
    """Plot only computed trajectories and ideal cycle power, with units."""
    e,m=study.environment,study.mission
    node=finite_tip_node_intercept(e,m.catcher_altitude_m,
                                  study.illustrative_tip_offset_m,study.tip_tangent_height_m)
    useful=propagate(e,node.initial_state,node.flight_s,samples=601)
    fig,axes=plt.subplots(1,2,figsize=(12,4.5),layout='constrained')
    angle=np.linspace(0,2*pi,600)
    ax=axes[0]
    ax.fill(e.reference_radius_m*np.cos(angle)/1000,e.reference_radius_m*np.sin(angle)/1000,
            color='#e7e9ed',label='reference Moon')
    ax.plot(useful.y[0]/1000,useful.y[1]/1000,color='#1967a3',label='useful payload, 3-D propagated')
    rc=e.reference_radius_m+m.catcher_altitude_m
    ax.plot(rc*np.cos(angle)/1000,rc*np.sin(angle)/1000,'--',color='#687887',label='catcher circle')
    ax.scatter([0],[rc/1000],color='#c03932',zorder=4,label='first equator-node catch')
    ax.set(xlabel='Inertial X [km]',ylabel='Inertial Y [km]',aspect='equal',title='Quarter-orbit node intercept (XY projection)')
    ax.legend(fontsize=8,loc='lower left')
    ax=axes[1]
    ax.plot(useful.t/60,useful.y[2],color='#1967a3')
    ax.axhline(0,color='#687887',lw=1)
    ax.set(xlabel='Time after release [min]',ylabel='North offset Z [m]',title='Finite sling tip begins off the equator')
    fig.savefig(out/'orbit_node.png',dpi=160);plt.close(fig)

    fig,axs=plt.subplots(1,2,figsize=(12,4.5),layout='constrained')
    for fraction,label in [(1.0,'equal radius: no impact'),
                           (study.shorter_counter_radius_fraction,'shorter rock side: spherical impact')]:
        state=counter_release_state(e,node,fraction)
        period=circular_period_s(e.mu_m3_s2,np.linalg.norm(state[:3]))
        sol=propagate(e,state,period,stop_at_surface=True,samples=3001)
        times=sol.t
        states=sol.y
        if len(sol.t_events[0]):
            times=np.r_[times,sol.t_events[0]]
            states=np.column_stack((states,sol.y_events[0].T))
        alt=np.linalg.norm(states[:3],axis=0)-e.reference_radius_m
        for ax in axs:
            ax.plot(times/60,alt,label=label)
            if len(sol.t_events[0]):
                ax.scatter(sol.t_events[0]/60,[0],s=30,zorder=5)
    for ax in axs:
        ax.axhline(0,color='black',lw=1)
        ax.set(xlabel='Time after rock release [min]',ylabel='Altitude above reference sphere [m]')
    axs[0].set_title('One full near-surface rock orbit')
    axs[0].legend(fontsize=8)
    axs[1].set(xlim=(0,1),ylim=(-1,12),title='First minute: shorter-side impact')
    fig.suptitle('Equal radius stays aloft in two-body model; shorter rock side intersects reference surface')
    fig.savefig(out/'countermass_altitude.png',dpi=160);plt.close(fig)

    c=CycleInputs(study.illustrative_apex_radius_m,study.illustrative_tip_offset_m,
                  node.hub_rate_rad_s,study.illustrative_payload_kg,study.illustrative_countermass_kg,
                  study.reference_climber_mass_ratio*study.illustrative_payload_kg,study.illustrative_travel_speeds_m_s[-1],
                  study.illustrative_radial_travel_accel_m_s2,study.illustrative_wheel_efficiency,
                  study.illustrative_climber_efficiency,study.illustrative_loading_s,
                  study.illustrative_settle_s)
    result=ideal_cycle(c,point_surface_reference(e,m.catcher_altitude_m)['site_revisit_s'])
    fig,axes=plt.subplots(1,2,figsize=(12,4),layout='constrained')
    for ax,seg in zip(axes,result['segments']):
        t=seg['time_s']
        ax.plot(t,np.maximum(seg['wheel_mechanical_w'],0)/c.wheel_efficiency/1e6,label='wheel electrical input')
        ax.plot(t,np.maximum(seg['radial_mechanical_w'],0)/c.climber_efficiency/1e6,label='radial-drive electrical input')
        ax.plot(t,np.maximum(-seg['radial_mechanical_w'],0)/1e6,'--',label='radial braking available (mechanical)')
        ax.set(xlabel='Trip elapsed time [s]',ylabel='Power [MW]',title=seg['name'])
        ax.legend(fontsize=8)
    fig.suptitle('Constant-spin comparison: zero climber mass limit; wheel input and radial output separated')
    fig.savefig(out/'cycle_power_bound.png',dpi=160);plt.close(fig)


def write_results(study=OrbitCycleStudy()):
    out=Path(__file__).resolve().parent/'results'
    out.mkdir(exist_ok=True)
    result=run(study)
    (out/'orbit_cycle.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    figures(study,out)
    ref=result['point_reference']
    lines=['# Phase 4 generated numerical tables','',
           'Illustrative two-body and straight-sling bounds; **not a feasible launcher design**.','',
           '| Point-equatorial reference quantity | Value |','| --- | ---: |']
    for label,key,scale in [('Catcher orbit period [min]','orbit_period_s',1/60),
                            ('Site-relative revisit [min]','site_revisit_s',1/60),
                            ('Prograde site release speed [m/s]','prograde_site_m_s',1),
                            ('Retrograde site release speed [m/s]','retrograde_site_m_s',1),
                            ('Surface-to-apoapsis flight [min]','flight_s',1/60),
                            ('Apoapsis mismatch [m/s]','catch_relative_m_s',1)]:
        lines.append(f'| {label} | {ref[key]*scale:.6f} |')
    lines+=['','| Tip offset [km] | Inclination [deg] | Site tip speed [m/s] | Flight [min] | Catch mismatch [m/s] | Actual centripetal Earth-g | Max wheel radius [m] |',
            '| ---: | ---: | ---: | ---: | ---: | ---: | ---: |']
    for c in result['finite_tip_cases']:
        lines.append(f"| {c['tip_offset_m']/1000:.1f} | {c['inclination_deg']:.6f} | {c['site_tip_speed_m_s']:.6f} | {c['flight_s']/60:.6f} | {c['catch_relative_m_s']:.6f} | {c['actual_centripetal_earth_g']:.3f} | {c['max_wheel_path_radius_m']:.3f} |")
    lines+=['','| Tip offset [km] | Equal-radius rock minimum altitude [m] | Equal-radius impact? | Shorter-side impact time [s] | Impact latitude [deg] | Relative longitude [deg] | Impact ground speed [m/s] |',
            '| ---: | ---: | --- | ---: | ---: | ---: | ---: |']
    for c in result['finite_tip_cases']:
        eq,sh=c['equal_radius_counter'],c['shorter_radius_counter']
        vals=[c['tip_offset_m']/1000,eq['periapsis_altitude_m'],eq['impacts_reference_sphere'],
              sh.get('impact_s'),degrees(sh['impact_latitude_rad']) if sh.get('impact_s') else None,
              degrees(sh['impact_longitude_rad']) if sh.get('impact_s') else None,
              sh.get('impact_ground_relative_m_s')]
        lines.append('| '+' | '.join(f'{v:.4f}' if isinstance(v,float) else str(v) for v in vals)+' |')
    lines+=['','Counter radius fraction = '+str(study.shorter_counter_radius_fraction)+
            '; this changes geometry, not just rock mass. Impact safety remains unverified.','',
            '| Radial speed [m/s] | One trip [s] | Minimum full cycle [s] | Catcher passes skipped | Peak electric bound [MW] | Cycle electric energy [MJ] |',
            '| ---: | ---: | ---: | ---: | ---: | ---: |']
    for c in result['cycles']:
        lines.append(f"| {c['travel_speed_m_s']:.1f} | {c['trip_s']:.3f} | {c['minimum_cycle_s']:.3f} | {c['passes_skipped']} | {c['peak_electrical_w']/1e6:.4f} | {c['electrical_energy_j']/1e6:.3f} |")
    lines+=['', 'Main cycle table uses zero climber mass as a comparison limit, not a sized climber.',
            '', '| Each climber / payload mass | Each climber [kg] | Outbound wheel peak [MW electric] | Outbound radial braking peak [MW mechanical] | Return radial-drive peak [MW electric] | Cycle electric [MJ, no recovery] |',
            '| ---: | ---: | ---: | ---: | ---: | ---: |']
    for c in result['climber_mass_sensitivity']:
        lines.append(f"| {c['each_climber_to_payload_ratio']:.2f} | {c['each_climber_kg']:.1f} | {c['outbound']['peak_wheel_input_w']/1e6:.4f} | {c['outbound']['peak_radial_braking_available_w']/1e6:.4f} | {c['returning']['peak_radial_drive_input_w']/1e6:.4f} | {c['electrical_energy_j']/1e6:.3f} |")
    lines+=['',f"10° sun-elevation availability: {result['sun']['available_fraction']:.6f} of solar day.",
            f"Illustrative conditional catches/year: {result['sun']['conditional_catches_per_year']:.3f}.",
            f"Fixed-spin phase mismatch each site revisit: {result['constant_spin_phase_mismatch_rad']:.6f} rad.",
            '', 'See [interpretation and limitations](../docs/orbit_cycle_review.md).']
    (out/'orbit_cycle_tables.md').write_text('\n'.join(lines)+'\n')
    return result


if __name__=='__main__':
    result=write_results()
    print((Path(__file__).resolve().parent/'results/orbit_cycle_tables.md').read_text())
