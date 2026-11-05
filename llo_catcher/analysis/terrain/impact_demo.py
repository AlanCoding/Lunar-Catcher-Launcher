"""Two-body, rotating-DEM missed-capture demo with finite sling offsets.

Run: MPLCONFIGDIR=/tmp/lunar-sling-mpl-cache .env/hub/bin/python -m
     llo_catcher.analysis.terrain.impact_demo
No GRAIL harmonics, external perturbations, libration or terrain uncertainty sweep.
"""
from dataclasses import dataclass,asdict
from pathlib import Path
import json
import numpy as np
from scipy.optimize import brentq
from .terrain_band import TerrainBand,RADIUS

MU=4.902800118e12
MOON_OMEGA=2*np.pi/(655.720*3600)
ROOT=Path(__file__).resolve().parent


@dataclass(frozen=True)
class Inputs:
    rpm: float=2.77962791161922
    prograde_catcher_altitude_m: float=25000.
    retrograde_catcher_altitude_m: float=35000.
    release_clearance_m: float=3.
    max_orbits: float=1.5


def release_solution(terrain,longitude,direction,inputs=Inputs()):
    """direction=+1 prograde/south release; -1 retrograde/north release.

    Both release velocities are horizontal east/west; payout speed at release=0.
    Solve p=catcher radius for the first equator node, plus local 3 m clearance.
    Frame is a fixed-axis approximation aligned to the DEM mean equator.
    """
    assert direction in [-1,1]
    if inputs.rpm<=0 or inputs.release_clearance_m<=0 or inputs.max_orbits<=0:
        raise ValueError('RPM, release clearance, and horizon must be positive')
    spin=inputs.rpm*2*np.pi/60
    alt=inputs.prograde_catcher_altitude_m if direction==1 else inputs.retrograde_catcher_altitude_m
    rc=RADIUS+alt

    def geometry(theta):
        lat=-direction*np.degrees(theta)
        h=float(terrain.height_m(lat,longitude))
        r=RADIUS+h+inputs.release_clearance_m
        d=r*np.sin(theta);x=r*np.cos(theta)
        vi=spin*d+direction*MOON_OMEGA*x
        return h,r,d,x,vi

    theta=brentq(lambda th: geometry(th)[1]**2*geometry(th)[4]**2/MU-rc,
                 np.radians(.10),np.radians(.24),xtol=1e-15)
    h,r,d,x,vi=geometry(theta)
    if not 0<rc/r-1<1 or vi<=0:
        raise ValueError('Demo requires a bound periapsis-to-first-node release')
    e=rc/r-1
    a=rc/(1-e*e)
    mean_motion=np.sqrt(MU/a**3)
    ec=np.arccos(e)
    tc=(ec-e*np.sin(ec))/mean_motion
    vc=np.sqrt(MU/rc)
    rhat=np.array([x/r,0.,-direction*d/r]);q=np.array([0.,float(direction),0.])
    v_at_catch=vc*(-rhat+e*q)
    delta=v_at_catch-np.array([-vc,0.,0.])
    return dict(longitude_deg_east=longitude%360,direction='prograde' if direction==1 else 'retrograde',
        sign=direction,catcher_altitude_m=alt,catcher_radius_m=rc,rpm=inputs.rpm,
        release_latitude_deg=-direction*np.degrees(theta),release_terrain_height_m=h,
        release_radius_from_moon_center_m=r,release_horizontal_offset_m=d,
        release_tangent_x_m=x,release_clearance_m=inputs.release_clearance_m,
        site_relative_release_speed_m_s=spin*d,inertial_release_speed_m_s=vi,
        payload_centripetal_g=spin*spin*d/9.80665,eccentricity=e,semimajor_axis_m=a,
        periapsis_radius_m=r,apoapsis_radius_m=rc/(1-e),period_s=2*np.pi/mean_motion,
        ideal_catch_time_s=tc,catch_relative_speed_m_s=float(np.linalg.norm(delta)),
        catch_radial_speed_m_s=e*vc,catch_out_of_plane_speed_m_s=float(delta[2]),
        catch_along_track_delta_m_s=float(delta[0]),
        required_catcher_phase_at_release_rad=float(direction*(np.pi/2-np.sqrt(MU/rc**3)*tc)),
        rhat=rhat.tolist(),q=q.tolist(),max_orbits=inputs.max_orbits)


def state(solution,t):
    """Analytic Kepler propagation; local inertial X is initial site radial axis."""
    t=np.asarray(t,dtype=float)
    a=solution['semimajor_axis_m'];e=solution['eccentricity']
    n=np.sqrt(MU/a**3);m=n*t;E=m.copy()
    for _ in range(8):E-=(E-e*np.sin(E)-m)/(1-e*np.cos(E))
    c=np.cos(E);s=np.sin(E);b=np.sqrt(1-e*e)
    p=np.asarray(solution['rhat']);q=np.asarray(solution['q'])
    position=a*((c-e)[...,None]*p+b*s[...,None]*q)
    velocity=(a*n/(1-e*c))[...,None]*(-s[...,None]*p+b*c[...,None]*q)
    return position,velocity


def ground_coordinates(solution,t):
    pos,_=state(solution,t)
    rr=np.linalg.norm(pos,axis=-1)
    lat=np.degrees(np.arcsin(pos[...,2]/rr))
    lon=(solution['longitude_deg_east']+np.degrees(np.arctan2(pos[...,1],pos[...,0])-MOON_OMEGA*np.asarray(t)))%360
    return lat,lon,rr


def clearance(solution,t,terrain):
    lat,lon,rr=ground_coordinates(solution,t)
    return rr-RADIUS-terrain.height_m(lat,lon)


def first_impact(solution,terrain,spatial_step_m=20.):
    """Sample <=spatial_step along the inertial orbit; bracket first DEM crossing.

    Repeat at half spacing for the demo. This is not a rigorous grazing-contact
    proof, nor resolution of features smaller than the source DEM.
    """
    duration=solution['max_orbits']*solution['period_s']
    dt=spatial_step_m/solution['inertial_release_speed_m_s']
    total=int(np.ceil(duration/dt))
    for start in range(0,total,8192):
        idx=np.arange(start,min(start+8192,total)+1)
        times=np.minimum(idx*dt,duration)
        lat,lon,rr=ground_coordinates(solution,times)
        # No DEM query needed if above the entire band maximum elevation.
        near=rr-RADIUS<=terrain.max_height_m+1
        gaps=rr-RADIUS-terrain.max_height_m
        gaps[near]=rr[near]-RADIUS-terrain.height_m(lat[near],lon[near])
        hit=np.flatnonzero(gaps<=0)
        if len(hit):
            k=int(hit[0])
            lo=times[max(0,k-1)];hi=times[k]
            if k==0:
                if start==0:raise ValueError('Release is not clear of terrain')
                lo=max(0.,lo-dt)
            ti=brentq(lambda t: float(clearance(solution,t,terrain)),lo,hi,xtol=1e-9)
            la,ln,ri=ground_coordinates(solution,ti)
            pos,vel=state(solution,ti)
            ground_vel=vel-np.cross([0.,0.,MOON_OMEGA],pos)
            arc_cos=(np.cos(np.radians(la))*np.cos(np.radians(float(ln)-solution['longitude_deg_east'])))
            distance=RADIUS*np.arccos(np.clip(arc_cos,-1,1))
            status='outbound_collision' if ti<solution['ideal_catch_time_s'] else 'arrested_after_missed_capture'
            return dict(status=status,impact_time_s=float(ti),impact_orbits=float(ti/solution['period_s']),
                impact_latitude_deg=float(la),impact_longitude_deg_east=float(ln),
                impact_ground_speed_m_s=float(np.linalg.norm(ground_vel)),
                impact_distance_from_hub_m=float(distance),horizon_s=duration,
                search_spatial_step_m=spatial_step_m)
    return dict(status='not_arrested',impact_time_s=None,horizon_s=duration,
                completed_orbits=solution['max_orbits'],search_spatial_step_m=spatial_step_m)


def run_demo():
    terrain=TerrainBand();inputs=Inputs();cases=[]
    for longitude in range(0,360,45):
        arms=[]
        for sign in [1,-1]:
            sol=release_solution(terrain,longitude,sign,inputs)
            coarse=first_impact(sol,terrain,.5)
            fine=first_impact(sol,terrain,.25)
            assert coarse['status']==fine['status'],(longitude,sign,coarse,fine)
            delta=None
            if fine['impact_time_s'] is not None:
                delta=abs(fine['impact_time_s']-coarse['impact_time_s'])
                assert delta<.001,(longitude,sign,delta)
            sol['outcome']=fine
            sol['refinement_05_to_025m_impact_time_change_s']=delta
            arms.append(sol)
        case=dict(longitude_deg_east=longitude,arms=arms,
            both_arrested_after_missed_capture=all(a['outcome']['status']=='arrested_after_missed_capture' for a in arms),
            payload_only_balance_mass_ratio_prograde_over_retrograde=arms[1]['release_horizontal_offset_m']/arms[0]['release_horizontal_offset_m'])
        cases.append(case)
        print(longitude,[(a['direction'],a['outcome']['status'],a['outcome'].get('impact_time_s')) for a in arms],flush=True)
    out=ROOT/'demo_results';out.mkdir(exist_ok=True)
    class ReferenceSphere:
        max_height_m=0.
        def height_m(self,lat,lon):
            return np.zeros(np.broadcast_arrays(lat,lon)[0].shape)
    sphere=ReferenceSphere()
    smooth=[]
    for sign in [1,-1]:
        sol=release_solution(sphere,0,sign,inputs)
        sol['outcome']=first_impact(sol,sphere,spatial_step_m=1000.)
        smooth.append(sol)
    result=dict(inputs=asdict(inputs),smooth_reference=smooth,reference_radius_m=RADIUS,mu_m3_s2=MU,
        moon_spin_rad_s=MOON_OMEGA,model='Central gravity; fixed-axis rotation aligned to SLDEM2015 mean equator; bilinear DEM',
        terrain_manifest='../band_manifest.json',catcher_altitude_datum='1737.4 km reference sphere',
        scenarios=cases)
    (out/'results.json').write_text(json.dumps(result,indent=2)+'\n')
    plot_results(result,terrain,out)
    write_report(result,out)
    return result


def plot_results(result,terrain,out):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig,axes=plt.subplots(4,2,figsize=(13,13),constrained_layout=True)
    for ax,case in zip(axes.flat,result['scenarios']):
        for arm,color in zip(case['arms'],['#336b92','#aa633b']):
            outcome=arm['outcome'];end=outcome.get('impact_time_s') or outcome['horizon_s']
            # Logarithmic time samples expose near-launch terrain encounters.
            t=np.r_[0.,np.geomspace(.001,end,1400)]
            gap=clearance(arm,t,terrain)
            ax.plot(t/60,gap/1000,color=color,label=f"{arm['direction']}: {outcome['status'].replace('_',' ')}")
            if outcome['impact_time_s'] is not None:ax.plot(end/60,0,'x',color=color,ms=8)
        ax.axhline(0,color='black',lw=.7)
        ax.set_title(f"Launcher {case['longitude_deg_east']}° E")
        ax.set_xlabel('Time since release (minutes)');ax.set_ylabel('Clearance above DEM (km)')
        ax.grid(alpha=.25);ax.legend(fontsize=7)
    fig.suptitle('Correct release, missed capture: first terrain contact or 1.5 payload orbits\n25 km prograde / 35 km retrograde catchers · 3 m release clearance',fontsize=13)
    fig.savefig(out/'clearance_cases.png',dpi=160);fig.savefig(out/'clearance_cases.svg');plt.close(fig)
    # First seconds are decisive where terrain rises immediately downrange.
    fig,axes=plt.subplots(4,2,figsize=(13,12),constrained_layout=True)
    for ax,case in zip(axes.flat,result['scenarios']):
        for arm,color in zip(case['arms'],['#336b92','#aa633b']):
            end=min(5.,arm['outcome'].get('impact_time_s') or 5.)
            t=np.linspace(0,end,501)
            ax.plot(t,clearance(arm,t,terrain),color=color,label=arm['direction'])
            if end<5.:ax.plot(end,0,'x',color=color,ms=8)
        ax.axhline(0,color='black',lw=.7);ax.set_title(f"Launcher {case['longitude_deg_east']}° E")
        ax.set_xlabel('Time since release (seconds)');ax.set_ylabel('Clearance above DEM (m)')
        ax.grid(alpha=.25);ax.legend(fontsize=8)
    fig.suptitle('First five seconds: local terrain can block nominal departures',fontsize=13)
    fig.savefig(out/'departure_clearance.png',dpi=160);fig.savefig(out/'departure_clearance.svg');plt.close(fig)


def write_report(result,out):
    lines=["# Initial 25/35 km catcher demo", "",
        "Eight demonstration longitudes, not a site-selection sweep. **No viable dual-direction site was found in this sample:** all 16 trajectories struck the interpolated terrain before their intended catch. These are rejected departures, not successful arrests after missed capture.", "",
        "## Inputs and scope", "",
        "- Prograde catcher: **25 km**; retrograde catcher: **35 km**, both circular and equatorial, relative to the **1,737.4 km DEM reference sphere**. This direction assignment is the stated demo interpretation and is adjustable.",
        "- Sling rotation: **2.7796279 RPM**, held common to both arms. Arm radii are solved, not fixed at 5.787 km.",
        "- Each release is **3 m above its local DEM surface**. Prograde leaves the southern arm; retrograde leaves the northern arm. East/west horizontal release, zero payout velocity at release, and an equatorial hub are assumed.",
        "- Propagate each uncaught payload only to **first terrain contact or 1.5 of its own orbital periods**. An uninterrupted 1.5-period trajectory is `not_arrested`. No subsequent-orbit fate is inferred.",
        "- Central gravity and uniform lunar rotation aligned with the DEM's mean-equator frame; no gravity harmonics, libration or third-body forces in this initial demo. Nominal catcher phase control is assumed.", "",
        "## Solved geometry and relative catch speed", "",
        "The finite north/south release offsets mean the payload meets the equator at a node, 90 degrees of orbital angle after release. We therefore solve semilatus rectum `p = catcher radius`, not an apoapsis-at-catcher condition. Relative catch speed is the full vector difference, including radial and north/south motion.", "",
        "For a smooth sphere at zero DEM elevation (a control case, not a selected launch site):", "",
        "| Quantity | Prograde | Retrograde |", "| --- | ---: | ---: |"]
    a,b=result['smooth_reference']
    for label,key,div in [('Catcher altitude (km)','catcher_altitude_m',1000),('Arm radius from hub center (m)','release_horizontal_offset_m',1),('Surface-relative release speed (m/s)','site_relative_release_speed_m_s',1),('Inertial release speed (m/s)','inertial_release_speed_m_s',1),('Payload centripetal acceleration (Earth g)','payload_centripetal_g',1),('Relative capture speed (m/s)','catch_relative_speed_m_s',1),('Radial component at capture (m/s)','catch_radial_speed_m_s',1),('Signed north component at capture (m/s)','catch_out_of_plane_speed_m_s',1),('Time to intended catch (min)','ideal_catch_time_s',60),('Payload orbital period (min)','period_s',60)]:
        lines.append(f"| {label} | {a[key]/div:.3f} | {b[key]/div:.3f} |")
    ratio=b['release_horizontal_offset_m']/a['release_horizontal_offset_m']
    lines += ["",f"Both smooth-sphere trajectories are **not arrested** at 1.5 periods, as expected: their periapses remain 3 m above that sphere. The payload-only radial-balance estimate is `m_pro / m_retro = R_retro / R_pro = {ratio:.6f}`, putting a slightly heavier payload on the shorter prograde arm. This is not a completed loading specification: tapered cable self-load, asymmetry and support reactions must also balance. Payload mass does not change a ballistic trajectory at a fixed release state.","",
        "The retrograde arm is longer because lunar rotation subtracts from its inertial launch speed, and this demo also assigns it the higher catcher. The revised accelerations are about 50.08 and 50.50 g, not exactly 50 g; the published launcher snapshot is unchanged.","",
        "## Actual terrain cases", "",
        "All coordinates below are DEM body-fixed coordinates with east-positive longitude. Arm dimensions and hypothetical capture speeds vary with local release elevation. Catch speeds are conditional on reaching the catcher; these particular shots do not.", "",
        "| Hub longitude E | Direction | Arm radius m | Relative catch m/s | First contact s | Impact latitude deg | Impact longitude E deg | Outcome |",
        "| ---: | --- | ---: | ---: | ---: | ---: | ---: | --- |"]
    for case in result['scenarios']:
        for arm in case['arms']:
            o=arm['outcome'];ti=o.get('impact_time_s')
            contact='—' if ti is None else f"{ti:.4f}"
            lat='—' if ti is None else f"{o['impact_latitude_deg']:.6f}"
            lon='—' if ti is None else f"{o['impact_longitude_deg_east']:.6f}"
            lines.append(f"| {case['longitude_deg_east']} | {arm['direction']} | {arm['release_horizontal_offset_m']:.2f} | {arm['catch_relative_speed_m_s']:.2f} | {contact} | {lat} | {lon} | {o['status']} |")
    lines += ["", "The coordinate digits describe the numerical result, not physical accuracy. A 3 m initial clearance is comparable to the DEM's typical vertical uncertainty; local features below its effective resolution are not resolved. These results do not qualify a launch site.", "",
        "![First five seconds](departure_clearance.png)","",
        "[Full pre-impact histories](clearance_cases.png) · [Vector figure](departure_clearance.svg) · [Machine-readable results](results.json)", "",
        "## What the demonstration establishes", "",
        "The chosen catcher altitudes and common RPM do close into distinct arm radii and vector catch speeds with only modest changes from the reference radius. Terrain access and first-contact evaluation also work. The first obstacle in this sample is the outgoing path: raising a nearly horizontal payload only 3 m above arbitrary local terrain does not make the neighboring terrain clear.", "",
        "A candidate passes the requested test only if **both nominal paths reach their catcher locations unobstructed and, after missed capture, both impact before 1.5 periods**. Immediate outbound crashes must not count as success. No claim about all longitudes follows from these eight trials. The next, separately scoped sweep can apply an outbound-clearance screen before evaluating the missed-capture returns.", "",
        "This is a release-state study, not a rebuilt sling design. It sets both endpoints relative to their own local terrain; common-apex packaging, intervening cable clearance and the full unequal-mass loading problem remain outside this calculation.", "",
        "## Reproduction and numerical checks", "", "```bash",
        ".env/hub/bin/python llo_catcher/analysis/terrain/terrain_band.py",
        ".env/hub/bin/python -m unittest llo_catcher.analysis.terrain.test_impact_demo -v",
        "MPLCONFIGDIR=/tmp/lunar-sling-mpl-cache .env/hub/bin/python -m llo_catcher.analysis.terrain.impact_demo", "```", "",
        "The downloaded ±0.25-degree corridor spans all longitudes, but only eight hub longitudes were simulated. Data are cached outside Git under `../data/`; [the manifest](../band_manifest.json) records all source URLs and byte checksums.", "",
        "Checks include release clearance and node intercept in both directions, agreement with independent Cartesian integration, longitude rotation after one orbit, a no-impact sphere, a synthetic outbound obstruction, and DEM seam/probe consistency. Every terrain case is run at 0.5 m and 0.25 m trajectory sampling; classifications agree and impact-time differences are below 0.001 s. Coarser 20 m/10 m sampling missed an earlier shallow intersection in the 315 E prograde case, illustrating why ordinary sample agreement alone can be misleading near grazing contact. Sampling convergence does not remove DEM uncertainty or prove absence of every possible grazing contact.", "",
        "[Terrain sources and frame conventions](../README.md) · [Work-item scope](../../../work_items/EQUATOR_TERRAIN_AND_FAILED_SHOTS.md)"]
    (out/'README.md').write_text('\n'.join(lines)+'\n')


if __name__=='__main__':run_demo()
