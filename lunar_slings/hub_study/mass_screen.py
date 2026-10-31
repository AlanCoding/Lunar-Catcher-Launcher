"""Conditional mass screen, not complete launcher optimization. SI throughout."""
from pathlib import Path
import json
import numpy as np
from scipy.integrate import cumulative_trapezoid
from scipy.optimize import minimize_scalar
from .environment import LunarEnvironment
from .cycle import CycleInputs, ideal_cycle
from .orbit import point_surface_reference


def screen(payload_kg=1000., acceleration_g=100., allowable_pa=1e9,
           solar_specific_w_kg=100., recovery=0.):
    env=LunarEnvironment(); u=1684.52
    omega=acceleration_g*env.earth_g_m_s2/u
    tip=u/omega; apex=50.
    if omega*apex>35.76 or tip<=apex:
        return dict(acceleration_g=acceleration_g,status='wheel-speed limit',wheel_speed_m_s=omega*apex)
    r=np.linspace(apex,tip,10001)
    rho=1450.; g=env.surface_gravity_m_s2
    # Exact horizontal, constant-stress rotating tether solution; small-slope sag.
    tension=payload_kg*omega**2*tip*np.exp(rho*omega**2*(tip**2-r**2)/(2*allowable_pa))
    area=tension/allowable_pa
    linear=rho*area
    cumulative=cumulative_trapezoid(linear,r,initial=0)
    tether=cumulative[-1]
    vertical=g*(payload_kg+tether-cumulative)
    slope=vertical/tension
    sag=cumulative_trapezoid(slope,r,initial=0)
    terrain=np.sqrt(env.reference_radius_m**2-r**2)-env.reference_radius_m
    height=float(np.max(sag+terrain)+3)
    # Central tie has its own radial inertia and weight; approximate horizontal
    # stress sizing from endpoint force, with sag estimated by uniform-load cable.
    tie_area=tension[0]/allowable_pa
    tie_mass=2*apex*rho*tie_area
    tie_sag=rho*tie_area*g*(2*apex)**2/(8*tension[0])
    height=max(height,tie_sag+3)
    window=point_surface_reference(env,20000)['site_revisit_s']
    trip=(window-240)/2
    # Slowest rest-to-rest trapezoidal travel completing the chosen window.
    v=(trip-np.sqrt(trip**2-4*(tip-apex)))/2
    c=CycleInputs(apex,tip,omega,payload_kg,payload_kg,0.,v,1.,.85,.8,120.,120.)
    cycle=ideal_cycle(c,window,samples=10001)
    seg=cycle['segments'][0]
    electric=np.maximum(seg['wheel_mechanical_w'],0)/.85-recovery*np.maximum(-seg['radial_mechanical_w'],0)
    peak=float(max(electric)); pv=peak/solar_specific_w_kg
    tangential=2*payload_kg*omega*v*tip/apex
    vertical_apex=g*(payload_kg+tether)+tie_mass*g/2
    # Ideal truss load resolution for near-vertical + 45-degree trailing leg.
    loads=[abs(vertical_apex-tangential),np.sqrt(2)*tangential]
    # Tube diameter optimized, 2 mm minimum wall and t >= D/100, K=1,
    # Euler factor 2; 124 MPa allowable. Axial-only conditional lower bound.
    def poles(h):
        total=0.; dims=[]
        for length,load in zip([h,np.sqrt(2)*h],loads):
            def mass(d):
                wall=max(.002,d/100)
                a=np.pi/4*(d*d-(d-2*wall)**2)
                inertia=np.pi/64*(d**4-(d-2*wall)**4)
                if a*124e6<load or np.pi**2*68.3e9*inertia/length**2<2*load:
                    return 1e20
                return a*length*2710
            ds=np.geomspace(.01,5,10000)
            masses=np.array([mass(d) for d in ds]); idx=masses.argmin()
            total+=2*masses[idx]; dims.append(float(ds[idx]))
        return total,dims
    hs=np.linspace(height,height*2,41)
    pole_masses=[poles(h)[0] for h in hs]
    idx=int(np.argmin(pole_masses)); pole_mass,diameters=poles(hs[idx])
    subtotal=2*tether+tie_mass+pole_mass+pv
    return dict(status='conditional subtotal; hardware unsized',payload_kg=payload_kg,
        acceleration_g=acceleration_g,allowable_pa=allowable_pa,recovery_efficiency=recovery,
        solar_specific_w_kg=solar_specific_w_kg,tip_radius_m=tip,apex_radius_m=apex,
        wheel_speed_m_s=omega*apex,omega_rad_s=omega,payout_or_climber_speed_m_s=float(v),
        outward_sling_mass_kg=2*tether,main_tie_mass_kg=tie_mass,
        pole_mass_axial_only_kg=pole_mass,solar_mass_assumed_specific_power_kg=pv,
        subtotal_ratio=subtotal/payload_kg,height_optimum_m=float(hs[idx]),
        height_search_bounds_m=[height,2*height],tube_diameters_m=diameters,
        peak_solar_w=peak,one_way_travel_s=cycle['trip_s'],interval_s=window,
        max_small_slope=float(max(slope)),leading_leg_axial_n=float(vertical_apex-tangential),
        tangential_apex_n=float(tangential),vertical_apex_n=float(vertical_apex),
        unresolved_imported_mass_kg=None)


def main():
    results=[screen(acceleration_g=a,recovery=e) for a in [10,30,100,300] for e in [0,.7]]
    out=Path(__file__).parent/'results';out.mkdir(exist_ok=True)
    (out/'mass_screen.json').write_text(json.dumps(results,indent=2)+'\n')
    lines=['# Conditional mass screen — 1,000 kg useful payload','',
      'All ratios below omit unresolved hardware; they are NOT full launcher mass ratios.','',
      '| Acceleration (g) | Recovery | Height (m) | Poles (kg) | Slings (kg) | Main tie (kg) | Solar (kg) | Subtotal / payload |',
      '| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |']
    for r in results:
        if 'subtotal_ratio' not in r:
            lines.append(f"| {r['acceleration_g']} | — | wheel speed fails | — | — | — | — | — |")
        else:
            keys=['acceleration_g','recovery_efficiency','height_optimum_m','pole_mass_axial_only_kg','outward_sling_mass_kg','main_tie_mass_kg','solar_mass_assumed_specific_power_kg','subtotal_ratio']
            lines.append('| '+' | '.join(f'{r[k]:.3f}' for k in keys)+' |')
    (out/'mass_screen.md').write_text('\n'.join(lines)+'\n')
    print('\n'.join(lines))
if __name__=='__main__': main()
