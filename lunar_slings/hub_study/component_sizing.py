"""Best-effort mass curves: sourced terrestrial analogs + explicit beam sizing.

SI throughout. Analog hardware is NOT a selected lunar-qualified product.
Curve extrapolation and section fabrication limits remain visible outputs.
"""
from dataclasses import dataclass, asdict
import numpy as np
from scipy.optimize import brentq

# Manufacturer data transcribed with provenance in results/hardware_mass/SOURCES.md.
TIRES=[dict(name='Michelin XTRA LOAD PROTECT 18.00R33',diameter_m=1.888,width_m=.498,mass_kg=473.,load_earth_kg=13100.,tkph=194.),
       dict(name='Michelin XD GRIP 27.00R49',diameter_m=2.726,width_m=.733,mass_kg=1330.,load_earth_kg=32100.,tkph=720.),
       dict(name='Michelin XDR4 EXTRA LOAD 59/80R63',diameter_m=4.027,width_m=1.495,mass_kg=5350.,load_earth_kg=115000.,tkph=1840.)]
GEARS=[(480000.,2250.),(1050000.,4500.),(2260000.,11420.),(4010000.,20470.),(5450000.,29500.)]
MOTORS=[dict(name='Dana SUMO MD HV1800-3P',continuous_kw=100.,motor_kg=180.,inverter_kg=13.),
        dict(name='Dana SUMO MD HV2200-3P',continuous_kw=145.,motor_kg=225.,inverter_kg=13.),
        dict(name='Dana SUMO MD HV2200-6P',continuous_kw=190.,motor_kg=225.,inverter_kg=25.),
        dict(name='Dana SUMO HD HV3500-9P',continuous_kw=260.,motor_kg=340.,inverter_kg=38.)]

@dataclass(frozen=True)
class HardwareAssumptions:
    name: str = 'reference'
    steel_density: float = 7850.
    steel_E: float = 210e9
    steel_yield_pa: float = 650e6
    yield_factor: float = 2.
    buckling_factor: float = 2.
    euler_K: float = 2.
    diameter_wall_ratio: float = 30.
    min_wall_m: float = .004
    deflection_fraction: float = 1/150
    joint_fraction: float = .20
    bearing_pressure_pa: float = 100000.
    width_diameter: float = .35
    contact_length_diameter: float = .4
    wheel_install_factor: float = 2.1
    motor_kg_per_kw: float = 340/260
    motor_install_factor: float = 1.25
    inverter_kg_per_kw: float = 38/260
    motor_base_rad_s: float = 260000/1970
    gearbox_kg_per_nm: float = 2250/480000
    gearbox_kg_per_kw: float = 2.
    gearbox_service_factor: float = 1.5
    gearbox_install_factor: float = 1.4
    gear_efficiency: float = .96
    bend_D_over_d: float = 40.
    rope_fiber_fill: float = .65
    reel_pack_fill: float = .75
    radiator_temp_k: float = 330.
    radiator_sink_k: float = 250.
    radiator_kg_m2: float = 8.
    radiator_view_factor: float = .7
    radiator_emissivity: float = .85
    thermal_transport_fraction: float = .20
    controls_fraction: float = .02
    solar_w_kg: float = 100.
    recovery: float = .7


def variants():
    from dataclasses import replace
    base=HardwareAssumptions()
    return [replace(base,name='lighter',bearing_pressure_pa=250000.,wheel_install_factor=1.5,
                    motor_install_factor=1.,gearbox_kg_per_kw=1.,joint_fraction=.1,
                    bend_D_over_d=20.,radiator_temp_k=350.,radiator_kg_m2=6.),base,
            replace(base,name='heavier',bearing_pressure_pa=50000.,wheel_install_factor=3.,
                    motor_kg_per_kw=4.55,motor_base_rad_s=2990*2*np.pi/60,
                    motor_install_factor=1.3,gearbox_kg_per_kw=3.,joint_fraction=.35,
                    bend_D_over_d=50.,radiator_temp_k=315.,radiator_kg_m2=12.)]


def log_fit(x,y):
    exponent,intercept=np.polyfit(np.log(x),np.log(y),1)
    return float(np.exp(intercept)),float(exponent)

GEAR_MASS_FIT=log_fit([p[0] for p in GEARS],[p[1] for p in GEARS])
WHEEL_MASS_FIT=log_fit([t['diameter_m'] for t in TIRES],[t['mass_kg'] for t in TIRES])
WHEEL_LOAD_FIT=log_fit([t['diameter_m'] for t in TIRES],[t['load_earth_kg']*9.80665 for t in TIRES])


def wheel(normal_n,speed_m_s,c=HardwareAssumptions()):
    km,pm=WHEEL_MASS_FIT;kn,pn=WHEEL_LOAD_FIT
    pressure_d=np.sqrt(normal_n/(c.bearing_pressure_pa*c.width_diameter*c.contact_length_diameter))
    load_d=(normal_n/kn)**(1/pn)
    # Terrestrial tire heat-work proxy, explicitly extrapolated in D^2. Not a
    # lunar vacuum cooling law or a validation of 80-mph tire operation.
    thermal_d=4.027*np.sqrt((normal_n/9.80665/1000)*(speed_m_s*3.6)/1840.)
    d=max(.6,float(pressure_d),float(load_d),float(thermal_d))
    return dict(diameter_m=d,radius_m=d/2,width_m=c.width_diameter*d,
                mass_kg=c.wheel_install_factor*km*d**pm,normal_n=normal_n,
                contact_area_m2=c.width_diameter*c.contact_length_diameter*d*d,
                actual_pressure_pa=normal_n/(c.width_diameter*c.contact_length_diameter*d*d),
                sizing_diameters_m=dict(pressure=float(pressure_d),load=float(load_d),terrestrial_thermal=float(thermal_d)),
                extrapolated=bool(d>max(t['diameter_m'] for t in TIRES) or d<min(t['diameter_m'] for t in TIRES)))


def drive(peak_power_w,peak_torque_nm,max_shaft_rad_s,c=HardwareAssumptions()):
    # Four wheel drives and two reel drives are scaled custom machines, not
    # silently substituted banks of numerous commercial motors.
    ratio=max(1.,c.motor_base_rad_s/max(max_shaft_rad_s,1e-9))
    continuous_kw=max(peak_power_w/c.gear_efficiency,
                       peak_torque_nm/ratio/c.gear_efficiency*c.motor_base_rad_s)/1000
    motor=continuous_kw*c.motor_kg_per_kw*c.motor_install_factor
    inverter=continuous_kw*c.inverter_kg_per_kw
    gear=c.gearbox_install_factor*max(GEAR_MASS_FIT[0]*(peak_torque_nm*c.gearbox_service_factor)**GEAR_MASS_FIT[1],
                                    c.gearbox_kg_per_kw*peak_power_w/1000)
    return dict(motor_kg=motor,inverter_kg=inverter,gearbox_kg=gear,mass_kg=motor+inverter+gear,
                continuous_rating_kw=continuous_kw,shaft_peak_torque_nm=peak_torque_nm,
                ratio=ratio,motor_peak_torque_nm=peak_torque_nm/(ratio*c.gear_efficiency),
                extrapolation_from_260kw=continuous_kw/260.,
                gear_torque_extrapolation=peak_torque_nm*c.gearbox_service_factor/5450000.)


def pole(length_m,external_axial_n,radial_tip_force_n,radial_accel,angle_from_vertical,
         gravity,c=HardwareAssumptions(),radial_both_ends=False):
    """Minimum-diameter round member for a fixed D/t policy, including own mass.

    Out-of-plane beam-column: K=2; axial+amplified biaxial bending, Euler reserve
    and tip deflection. Fabrication-domain violations are marked, not hidden.
    """
    if length_m<=0:raise ValueError('Pole length must be positive')
    L=length_m;allow=c.steel_yield_pa/c.yield_factor
    def section(d,details=False):
        t=max(c.min_wall_m,d/c.diameter_wall_ratio);inner=max(0,d-2*t)
        A=np.pi/4*(d*d-inner*inner);I=np.pi/64*(d**4-inner**4);Z=2*I/d
        mass=c.steel_density*A*L
        axial=external_axial_n+mass*gravity*np.cos(angle_from_vertical)
        pcr=np.pi**2*c.steel_E*I/(c.euler_K*L)**2
        amp=1/max(1e-9,1-axial/pcr)
        mr=(radial_tip_force_n+(.125 if radial_both_ends else .5)*mass*radial_accel)*L
        mg=.5*mass*gravity*np.sin(angle_from_vertical)*L
        moment=np.hypot(mr,mg)
        stress=axial/A+amp*moment/Z
        dr=(radial_tip_force_n*L**3/3+mass*radial_accel*L**3*(5/384 if radial_both_ends else 1/8))/(c.steel_E*I)
        dg=mass*gravity*np.sin(angle_from_vertical)*L**3/(8*c.steel_E*I)
        deflection=amp*np.hypot(dr,dg)
        utilizations=dict(stress=stress/allow,buckling=c.buckling_factor*axial/pcr,
                          deflection=deflection/(c.deflection_fraction*L))
        u=max(utilizations.values())
        if not details:return u
        return dict(length_m=L,diameter_m=d,wall_m=t,bare_mass_kg=mass,
                    mass_with_joints_kg=mass*(1+c.joint_fraction),axial_n=axial,
                    bending_moment_nm=moment,stress_pa=stress,euler_n=pcr,deflection_m=deflection,
                    utilization=utilizations,plate_thickness_within_source=bool(t<=.160),
                    slender_beam=bool(d/L<=.2))
    lo=.03;hi=max(.1,L/10)
    while section(hi)>1 and hi<1e7:hi*=2
    if section(hi)>1:raise ValueError('No self-weight-consistent steel section')
    d=brentq(lambda x:section(x)-1,lo,hi,xtol=1e-8)
    return section(d,True)


def reel(cable_mass,root_solid_diameter,root_force,c=HardwareAssumptions()):
    diameter=root_solid_diameter/np.sqrt(c.rope_fiber_fill)
    core=c.bend_D_over_d*diameter/2
    width=max(1.,2*core)
    volume=cable_mass/(1450*c.rope_fiber_fill*c.reel_pack_fill)
    outer=np.sqrt(core*core+volume/(np.pi*width))
    # Tension-carrying capstan + low-tension storage, not an unanalysed many-layer
    # winding drum taking full line tension. Two bearings and rim/shaft included.
    torque=root_force*core;allow=c.steel_yield_pa/c.yield_factor
    shear_allow=allow/np.sqrt(3)
    shaft_d=(16*torque/(np.pi*shear_allow))**(1/3)
    shaft_mass=c.steel_density*np.pi*shaft_d**2/4*(width+.5)
    rim_section=max(.002,root_force/allow)
    rim_mass=c.steel_density*rim_section*2*np.pi*core
    storage_skin=.006*c.steel_density*(2*np.pi*outer*width+2*np.pi*(outer**2-core**2))
    mass=(shaft_mass+rim_mass+storage_skin)*1.3
    return dict(core_radius_m=core,outer_radius_m=outer,width_m=width,rope_outer_diameter_m=diameter,
                shaft_diameter_m=shaft_d,mass_kg=mass,holding_torque_nm=torque,
                rotor_inertia_kg_m2=.5*mass*(core*core+outer*outer),
                architecture='tension capstan plus low-tension storage; two such assemblies')
