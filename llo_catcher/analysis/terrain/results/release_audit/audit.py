"""Read-only audit of saved sweep states; does not rerun the site sweep."""
from pathlib import Path
import hashlib,json
import numpy as np
from scipy.integrate import solve_ivp
from llo_catcher.analysis.terrain.impact_demo import state,ground_coordinates,MU
from llo_catcher.analysis.terrain.terrain_band import TerrainBand,RADIUS
OUT=Path(__file__).resolve().parent
ROOT=OUT.parent.parent

def main():
    saved=json.loads((ROOT/'results/sweep_1deg/results.json').read_text())
    for name,digest in saved['code_sha256'].items():
        assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==digest
    terrain=TerrainBand();arms=[a for s in saved['scenarios'] for a in s['arms']]
    vr=[];peri_errors=[];speed_ratios=[];examples=[]
    for a in arms:
        r,v=state(a,0.);rr=np.linalg.norm(r);h=np.cross(r,v)
        ev=np.cross(v,h)/MU-r/rr
        rp=np.dot(h,h)/MU/(1+np.linalg.norm(ev))
        vr.append(float(r@v/rr));peri_errors.append(float(rp-rr))
        speed_ratios.append(float(np.linalg.norm(v)/np.sqrt(MU/rr)))
    assert max(abs(x) for x in vr)<1e-9
    assert max(abs(x) for x in peri_errors)<1e-6
    assert min(speed_ratios)>1
    for a in arms[:2]:
        t=a['outcome']['impact_time_s'];lat,lon,r=ground_coordinates(a,t)
        dh=float(terrain.height_m(lat,lon))-a['release_terrain_height_m']
        dr=float(r)-a['release_radius_from_moon_center_m']
        r0,v0=state(a,0.)
        def rhs(t,y):return np.r_[y[3:],-MU*y[:3]/np.linalg.norm(y[:3])**3]
        sol=solve_ivp(rhs,(0,t),np.r_[r0,v0],rtol=1e-12,atol=1e-9,method='DOP853',max_step=.01)
        r_direct=np.linalg.norm(sol.y[:3,-1]);err=float(abs(r_direct-r))
        assert err<1e-6 and dr>0 and abs(3+dr-dh)<1e-6
        # Arc distance from release, not distance from hub's equatorial location.
        lat0=np.radians(a['release_latitude_deg']);lat1=np.radians(lat)
        dl=np.radians(((lon-a['longitude_deg_east']+180)%360)-180)
        dist=2*RADIUS*np.arcsin(np.sqrt(np.sin((lat1-lat0)/2)**2+np.cos(lat0)*np.cos(lat1)*np.sin(dl/2)**2))
        examples.append(dict(direction=a['direction'],longitude_deg_east=0,impact_time_s=t,
            ground_distance_from_release_m=float(dist),payload_radial_rise_m=dr,terrain_rise_m=dh,
            initial_radial_acceleration_m_s2=float(v0@v0/np.linalg.norm(r0)-MU/np.linalg.norm(r0)**2),
            direct_integration_radius_error_m=err,mean_ground_rise_angle_deg=float(np.degrees(np.arctan2(dh,dist)))))
    result=dict(checked_saved_states=len(arms),max_abs_initial_radial_speed_m_s=max(abs(x) for x in vr),
        max_abs_periapsis_minus_release_radius_m=max(abs(x) for x in peri_errors),
        release_speed_over_local_circular_range=[min(speed_ratios),max(speed_ratios)],
        examples=examples,source_hashes_match_saved_sweep=True)
    (OUT/'results.json').write_text(json.dumps(result,indent=2)+'\n')
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig,axs=plt.subplots(1,2,figsize=(11,4.5),layout='constrained')
    for ax,a,ex in zip(axs,arms[:2],examples):
        ts=np.linspace(0,ex['impact_time_s']*1.15,250)
        lat,lon,rr=ground_coordinates(a,ts)
        rise=rr-a['release_radius_from_moon_center_m']
        th=terrain.height_m(lat,lon)-a['release_terrain_height_m']
        ax.plot(ts,3+rise,label='Payload height above initial ground radius',color='#265e80')
        ax.plot(ts,th,label='Terrain rise along ground track',color='#a47742')
        ax.axvline(ex['impact_time_s'],ls=':',color='black');ax.set_title('0° E hub: '+a['direction']);ax.set_xlabel('Seconds after release');ax.grid(alpha=.2)
    axs[0].set_ylabel('Metres relative to ground radius at release');axs[0].legend(fontsize=8)
    fig.suptitle('Saved trajectories: payload radius rises, but terrain rises faster')
    fig.savefig(OUT/'first_impact.png',dpi=160);fig.savefig(OUT/'first_impact.svg');plt.close(fig)
    print(json.dumps(result,indent=2))

if __name__=='__main__':main()
