"""Plot accounted mass ratios and conditional feasibility screens, without inventing totals."""
from pathlib import Path
import json
import numpy as np
from scipy.optimize import brentq
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from .scenario_study import Scenario,geometry
from .environment import LunarEnvironment

ROOT=Path(__file__).parent
OUT=ROOT/'results/mass_ratio_trade'

def mass_ratios(r,recovery=True):
    """Keep unknown total separate from known subtotal; physical includes local rock."""
    key='accounted_imported_subtotal_recovery_kg' if recovery else 'accounted_imported_subtotal_no_recovery_kg'
    payload=r['inputs']['payload_kg'];imported=r[key]/payload
    return dict(accounted_imported=imported,accounted_permanent_physical=imported+r['ballast_total_kg']/payload,
                total_imported=None,total_permanent_physical=None)

def main():
    OUT.mkdir(exist_ok=True)
    rows=json.loads((ROOT/'results/speed_constrained/all_scenarios.json').read_text())
    upper=json.loads((ROOT/'results/speed_constrained/geometry_bounds.json').read_text())
    env=LunarEnvironment();limits={};summary=[]
    for mph in [50,80]:
        def fit(acc):
            cable,_,h,_=geometry(Scenario(acceleration_g=acc,rover_mph=mph,shape_fractions=121,shape_nodes=301))
            return h/(2*cable.radius)-1
        lower=float(brentq(fit,4,10,xtol=.001))
        # u variation is tiny here; solve it rather than silently freezing u.
        def road(acc):
            cable,_,_,_=geometry(Scenario(acceleration_g=acc,rover_mph=mph,shape_fractions=81,shape_nodes=201))
            return cable.omega*(mph*.44704)-.5*env.surface_gravity_m_s2
        lateral=float(brentq(road,3,8,xtol=.001))
        subset=[r for r in rows if r['inputs']['rover_mph']==mph and r['inputs']['passes']==1]
        limits[str(mph)]=dict(lower_45deg_fit_g=lower,upper_45deg_fit_g=upper[str(mph)]['upper_45deg_chord_boundary_g'],
            road_only_radial_friction_ceiling_g=lateral,
            min_sampled_compact_tipover_ratio=min(r['halfwidth_over_track_radius'] for r in subset),
            compact_tipover_passed_samples=0,scope='Tip-over assumes compact ballast at R, radial restraint at apex and support lever <= R. Road-only limit is an alternative radial load path, not an additional limit for the tie-supported model.')
        for passes in [1,2]:
            rs=[r for r in rows if r['inputs']['rover_mph']==mph and r['inputs']['passes']==passes]
            vals=[mass_ratios(r) for r in rs];v=np.array([p['accounted_permanent_physical'] for p in vals]);imp=np.array([p['accounted_imported'] for p in vals])
            summary.append(dict(rover_mph=mph,passes=passes,minimum_sampled_accounted_physical=float(min(v)),maximum_sampled_accounted_physical=float(max(v)),
                                physical_span_percent=float(100*(max(v)-min(v))/min(v)),
                                minimum_sampled_accounted_imported=float(min(imp)),maximum_sampled_accounted_imported=float(max(imp)),
                                total_mass_optimum=None))
    fig,axes=plt.subplots(3,2,figsize=(13,11),sharex=True,gridspec_kw={'height_ratios':[1,1,1.15]})
    colors={1:'#2066a8',2:'#22835a'}
    for col,mph in enumerate([50,80]):
        lim=limits[str(mph)]
        for passes in [1,2]:
            rs=[r for r in rows if r['inputs']['rover_mph']==mph and r['inputs']['passes']==passes];x=[r['inputs']['acceleration_g'] for r in rs]
            for row,key in [(0,'accounted_permanent_physical'),(1,'accounted_imported')]:
                y=[mass_ratios(r)[key] for r in rs];yn=[mass_ratios(r,False)[key] for r in rs]
                ax=axes[row,col];ax.plot(x,y,'o-',color=colors[passes],markersize=4,label=f'{passes} pass(es), 70% recovery')
                ax.plot(x,yn,'--',color=colors[passes],lw=1,label=f'{passes} pass(es), no recovery')
                ax.fill_between(x,y,yn,color=colors[passes],alpha=.07)
        rs=[r for r in rows if r['inputs']['rover_mph']==mph and r['inputs']['passes']==1];x=[r['inputs']['acceleration_g'] for r in rs]
        ax=axes[2,col]
        tip=np.array([r['halfwidth_over_track_radius'] for r in rs]);fitv=[r['pole_apex_height_m']/(2*r['track_radius_m']) for r in rs]
        ax.plot(x,tip,'s-',color='#b15d17',label='Required tipping lever / R')
        ax.fill_between(x,1,tip,color='#b15d17',alpha=.12)
        ax.plot(x,fitv,'o-',color='#74479a',label='45° leg span / track diameter')
        ax.axhline(1,color='black',lw=1,label='Screen limit: ratio <= 1')
        ax.set_yscale('log');ax.set_ylim(.025,2000)
        for row in range(3):
            ax=axes[row,col];ax.set_xscale('log');ax.set_xlim(3.5,4500);ax.grid(alpha=.2,which='both')
            ax.axvspan(3.5,lim['lower_45deg_fit_g'],color='#b24c5a',alpha=.12)
            ax.axvspan(lim['upper_45deg_fit_g'],4500,color='#b24c5a',alpha=.12)
            ax.axvline(lim['road_only_radial_friction_ceiling_g'],color='#444444',ls=':',lw=1.4)
            ax.axvline(lim['lower_45deg_fit_g'],color='#b24c5a',ls='--',lw=.9)
            ax.axvline(lim['upper_45deg_fit_g'],color='#b24c5a',ls='--',lw=.9)
        axes[0,col].set_title(f'{mph} mph; R = rover speed / angular speed',fontsize=12)
        axes[0,col].set_ylim(bottom=0);axes[1,col].set_ylim(bottom=0)
        axes[1,col].text(.98,.30,f"Road-only radial ceiling: {lim['road_only_radial_friction_ceiling_g']:.2f} g (dotted)\n45° fit: {lim['lower_45deg_fit_g']:.2f}–{lim['upper_45deg_fit_g']:.0f} g\nRed shading = frame chord cannot fit",transform=axes[1,col].transAxes,ha='right',va='top',fontsize=9,bbox=dict(facecolor='white',alpha=.9,edgecolor='none'))
        axes[2,col].set_xlabel('Payload release centripetal acceleration (Earth g)')
        axes[2,col].legend(loc='upper left',fontsize=8)
    axes[0,0].set_ylabel('Known permanent mass / payload\nWith ballast; incomplete')
    axes[1,0].set_ylabel('Known imported mass / payload\nWithout ballast; incomplete')
    axes[2,0].set_ylabel('Constraint ratio (log scale)\nAbove 1 fails the stated screen')
    axes[0,0].legend(loc='lower left',fontsize=8)
    fig.suptitle('Mass-ratio trade: known components and limits\nTotal system mass is UNSIZED; no feasible optimum demonstrated',fontsize=15,y=.99)
    fig.text(.5,.015,'Points are calculated scenarios; lines connect samples. Tipping screen fails across the sampled range.\nRoad-only traction is an alternative to apex radial restraint, not a universal cutoff. Loading: 5 min in all cases.',ha='center',fontsize=10)
    fig.tight_layout(rect=[0,.06,1,.94])
    for suffix in ['png','svg']:fig.savefig(OUT/f'mass_ratio_limits.{suffix}',dpi=160,bbox_inches='tight')
    plt.close(fig)
    svg=OUT/'mass_ratio_limits.svg';svg.write_text('\n'.join(line.rstrip() for line in svg.read_text().splitlines())+'\n')
    (OUT/'analysis.json').write_text(json.dumps(dict(limits=limits,summary=summary,
        ratios=[dict(acceleration_g=r['inputs']['acceleration_g'],rover_mph=r['inputs']['rover_mph'],passes=r['inputs']['passes'],**mass_ratios(r)) for r in rows]),indent=2)+'\n')
    print(json.dumps(dict(limits=limits,summary=summary),indent=2))

if __name__=='__main__':main()
