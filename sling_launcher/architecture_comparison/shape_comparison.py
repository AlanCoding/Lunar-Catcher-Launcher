"""Matched hardware: moving loop and its zero-feed steady equilibrium."""
from pathlib import Path
from dataclasses import replace
import json,csv
import numpy as np
from scipy.integrate import solve_bvp
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from .compare import OUT
from ..conveyor_loop.steady.model import Inputs,solve,equations,evaluate
DEST=Path(__file__).parent/'publication'

def main():
    data=json.loads((OUT/'comparison.json').read_text()); rows=[]; histories=[]
    for u in [2,5,10]:
        old=next(r['conveyor'] for r in data['rows'] if r['material']=='zylon' and r['feed_m_s']==u)
        c=Inputs(**old['inputs']); sol,total=solve(c,tol=2e-8)
        moving,h=evaluate(c,sol,total); original=sol
        for speed in np.linspace(u,0,6)[1:]:
            stopped=replace(c,feed_speed=float(speed))
            fun,bc,_=equations(stopped,total,c.payload_per_m/c.bare_density)
            sol=solve_bvp(fun,bc,sol.x,sol.y,p=sol.p,tol=2e-8,max_nodes=40000)
            assert sol.success,sol.message
        rest,g=evaluate(stopped,sol,total)
        # Contact arc changes slightly: conserve total attached payload as well.
        for _ in range(4):
            stopped=replace(stopped,payload_per_m=stopped.payload_per_m*moving['payload_inventory_kg']/rest['payload_inventory_kg'])
            fun,bc,_=equations(stopped,total,stopped.payload_per_m/stopped.bare_density)
            sol=solve_bvp(fun,bc,sol.x,sol.y,p=sol.p,tol=2e-8,max_nodes=40000)
            assert sol.success
            rest,g=evaluate(stopped,sol,total)
        assert abs(rest['payload_inventory_kg']/moving['payload_inventory_kg']-1)<1e-9
        assert rest['boundary_residual']<1e-7 and rest['integrated_force_residual_scaled']<1e-5
        assert abs(moving['max_stress_GPa']/old['max_stress_GPa']-1)<1e-6
        row=dict(feed_m_s=u,tether_mass_kg=moving['bare_loop_mass_kg'],area_mm2=c.area*1e6,
            moving_peak_GPa=moving['max_stress_GPa'],stopped_peak_GPa=rest['max_stress_GPa'],
            moving_stress_increment_percent=100*(moving['max_stress_GPa']/rest['max_stress_GPa']-1),
            moving_width_m=moving['width_m'],stopped_width_m=rest['width_m'],
            moving_tip_radius_m=moving['radius_max_m'],stopped_tip_radius_m=rest['radius_max_m'],
            moving_payload_kg=moving['payload_inventory_kg'],stopped_payload_kg=rest['payload_inventory_kg'],
            moving_force_residual=moving['integrated_force_residual_scaled'],stopped_force_residual=rest['integrated_force_residual_scaled'])
        rows.append(row);histories.append((c,h,g))
        np.savez_compressed(DEST/f'shape_{u}m_s.npz',**{'moving_'+k:v for k,v in h.items()},**{'stopped_'+k:v for k,v in g.items()})
    (DEST/'shape_comparison.json').write_text(json.dumps(rows,indent=2)+'\n')
    with (DEST/'shape_comparison.csv').open('w') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    plt.rcParams.update({'font.size':11,'svg.fonttype':'none','axes.spines.top':False,'axes.spines.right':False})
    c,h,g=histories[1];fig,axs=plt.subplots(3,1,figsize=(11,8),layout='constrained',gridspec_kw={'height_ratios':[1,2,2]})
    for ax in axs[:2]:
        ax.plot(*g['xy_m'],color='#92958d',lw=2,ls='--',label='Feed stopped; hub still rotating')
        cut=h['s']<=c.release_center
        ax.plot(*h['xy_m'][:,cut],color='#9a6445',lw=2,label='5 m/s: loaded outbound')
        ax.plot(*h['xy_m'][:,~cut],color='#456f81',lw=2,label='5 m/s: unloaded return')
        ax.scatter([c.station_radius],[0],s=25,c='black',zorder=5)
        ax.grid(alpha=.15);ax.set(xlabel='Radial direction from hub (m)',ylabel='Transverse (m)')
    axs[0].set_aspect('equal',adjustable='datalim');axs[0].set_title('True geometric aspect ratio · 5 m/s reference loop')
    axs[1].set_title('Transverse detail · axes use different scales');axs[1].legend(fontsize=9)
    for z,col,label,ls in [(h,'#456f81','5 m/s','-'),(g,'#92958d','Feed stopped','--')]:
        axs[2].plot(z['s'],z['stress_Pa']/1e9,color=col,label=label,lw=2,ls=ls)
    axs[2].axvline(c.release_center,color='.5',ls=':',label='Payload unloading zone')
    axs[2].set(xlabel='Fraction along free loop: outbound → turn → return',ylabel='Tensile stress (GPa)',title='Stress from the solved two-dimensional force balance')
    axs[2].legend(fontsize=9);axs[2].grid(alpha=.15)
    for ext in ['png','svg']:fig.savefig(DEST/f'conveyor_shape_and_stress.{ext}',dpi=200)
    plt.close(fig)
    print(json.dumps(rows,indent=2))
if __name__=='__main__':main()
