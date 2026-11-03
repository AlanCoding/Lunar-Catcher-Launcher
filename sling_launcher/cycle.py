"""Kinematic cadence and ideal direct-drive power bounds, not hardware sizing.

Constant hub speed, straight rigid radial slings, no sag/elastic transient or
rolling loss. Positive mechanical power is charged; negative power is dumped,
never credited. These are explicit comparison limits, not a feasible design.
"""

from dataclasses import dataclass
from math import acos, ceil, pi, sqrt
import numpy as np

from .environment import LunarEnvironment


@dataclass(frozen=True)
class CycleInputs:
    """Illustrative inputs [SI], not selected engineering defaults.

    Acceleration here is radial travel acceleration, not total payload tolerance.
    Set separately chosen efficiency values explicitly. 'settle' is a reserved
    time allowance, not a calculated guarantee that the machine is restored.
    """

    apex_radius_m: float
    tip_radius_m: float
    hub_rate_rad_s: float
    payload_mass_kg: float
    countermass_mass_kg: float
    climber_mass_kg: float
    travel_speed_m_s: float
    travel_accel_m_s2: float
    wheel_efficiency: float
    climber_efficiency: float
    loading_s: float
    settle_s: float

    def __post_init__(self):
        for name,value in vars(self).items():
            if not np.isfinite(value) or value < 0:
                raise ValueError(f"{name} must be finite and nonnegative")
        for name in ("apex_radius_m", "hub_rate_rad_s", "payload_mass_kg",
                     "travel_speed_m_s", "travel_accel_m_s2"):
            if getattr(self,name) <= 0:
                raise ValueError(f"{name} must be positive")
        if self.tip_radius_m <= self.apex_radius_m:
            raise ValueError("Tip radius must exceed apex radius")
        for eta in (self.wheel_efficiency,self.climber_efficiency):
            if not 0 < eta <= 1:
                raise ValueError("Efficiency must be in (0,1]")


def travel_duration_s(distance_m: float, vmax_m_s: float, accel_m_s2: float) -> float:
    """Rest-to-rest minimum travel time [s], symmetric triangular/trapezoid speed."""
    if not all(np.isfinite(v) and v > 0 for v in (distance_m,vmax_m_s,accel_m_s2)):
        raise ValueError("Travel inputs must be finite and positive")
    if distance_m <= vmax_m_s**2/accel_m_s2:
        return 2*sqrt(distance_m/accel_m_s2)
    return distance_m/vmax_m_s+vmax_m_s/accel_m_s2


def travel_state(t, distance_m: float, vmax_m_s: float, accel_m_s2: float):
    """Outward rest-to-rest displacement, speed, acceleration [m, m/s, m/s²]."""
    total = travel_duration_s(distance_m,vmax_m_s,accel_m_s2)
    tt = np.asarray(t,dtype=float)
    if np.any(tt<0) or np.any(tt>total):
        raise ValueError("Travel time outside motion interval")
    peak = min(vmax_m_s,sqrt(distance_m*accel_m_s2))
    ta = peak/accel_m_s2
    accel = np.where(tt<ta,accel_m_s2,
                     np.where(tt>total-ta,-accel_m_s2,0.0))
    speed = np.where(tt<ta,accel_m_s2*tt,
                     np.where(tt>total-ta,accel_m_s2*(total-tt),peak))
    position = np.where(tt<ta,0.5*accel_m_s2*tt**2,
                        np.where(tt>total-ta,distance_m-0.5*accel_m_s2*(total-tt)**2,
                                 0.5*accel_m_s2*ta**2+peak*(tt-ta)))
    return position,speed,accel


def ideal_cycle(inputs: CycleInputs, site_revisit_s: float, samples: int = 4001) -> dict:
    """Full time allocation and positive-power bounds for both climbers combined.

    Each trip starts/ends with zero radial speed; rotation never stops. For one
    moving mass, F_r=m(rddot-omega²r), F_t=2m omega rdot. The hub pays
    F_t*omega*r; the radial drive pays F_r*rdot. Negative work is dissipated.
    The elastic, structural, wheel rolling and auxiliary budgets are not modeled.
    """
    if not np.isfinite(site_revisit_s) or site_revisit_s <= 0 or samples < 101:
        raise ValueError("Invalid cadence or sampling")
    c = inputs
    length = c.tip_radius_m-c.apex_radius_m
    trip = travel_duration_s(length,c.travel_speed_m_s,c.travel_accel_m_s2)
    t = np.linspace(0,trip,samples)
    dx,v,a = travel_state(t,length,c.travel_speed_m_s,c.travel_accel_m_s2)
    w = c.hub_rate_rad_s
    segments=[]
    for name, mass, r, rd, rdd in (
        ("outbound",c.payload_mass_kg+c.countermass_mass_kg+2*c.climber_mass_kg,
         c.apex_radius_m+dx,v,a),
        ("return",2*c.climber_mass_kg,c.tip_radius_m-dx,-v,-a)):
        pr = mass*(rdd-w*w*r)*rd
        pw = 2*mass*w*w*r*rd
        pelec = np.maximum(pw,0)/c.wheel_efficiency+np.maximum(pr,0)/c.climber_efficiency
        dumped = np.maximum(-pw,0)+np.maximum(-pr,0)
        mechanical_work = float(np.trapezoid(pw+pr,t))
        kinetic_change = 0.5*mass*w*w*(r[-1]**2-r[0]**2)
        segments.append(dict(name=name, time_s=t, radius_m=r,
                             wheel_mechanical_w=pw, radial_mechanical_w=pr,
                             electrical_w=pelec,dumped_mechanical_w=dumped,
                             electrical_energy_j=float(np.trapezoid(pelec,t)),
                             dumped_energy_j=float(np.trapezoid(dumped,t)),
                             peak_electrical_w=float(max(pelec)),
                             peak_wheel_input_w=float(max(np.maximum(pw,0)/c.wheel_efficiency)),
                             peak_radial_drive_input_w=float(max(np.maximum(pr,0)/c.climber_efficiency)),
                             peak_radial_braking_available_w=float(max(np.maximum(-pr,0))),
                             wheel_input_energy_j=float(np.trapezoid(np.maximum(pw,0)/c.wheel_efficiency,t)),
                             radial_input_energy_j=float(np.trapezoid(np.maximum(pr,0)/c.climber_efficiency,t)),
                             radial_braking_energy_j=float(np.trapezoid(np.maximum(-pr,0),t)),
                             work_energy_residual_j=mechanical_work-kinetic_change))
    minimum = c.loading_s+2*trip+c.settle_s
    passes = max(1,ceil(minimum/site_revisit_s))
    interval=passes*site_revisit_s
    return dict(trip_s=trip,minimum_cycle_s=minimum,passes_skipped=passes-1,
                launch_interval_s=interval,phase_wait_budget_s=interval-minimum,
                peak_electrical_w=max(s['peak_electrical_w'] for s in segments),
                electrical_energy_j=sum(s['electrical_energy_j'] for s in segments),
                dumped_energy_j=sum(s['dumped_energy_j'] for s in segments),
                segments=segments)


def radial_rotation_power(mass_kg, radius_m, radial_speed_m_s,
                          radial_accel_m_s2, omega_rad_s, alpha_rad_s2,
                          fixed_inertia_kg_m2=0.0):
    """General straight-radial energy identity, including variable spin.

    Sum point masses into equal-radius mass_kg; fixed inertia is all components
    with unchanging radius. Returns torque [N m] and mechanical powers [W].
    Radial power is positive when the radial actuator supplies work, negative
    when it can extract work. No electrical regeneration or storage is assumed.
    This computes power for a prescribed motion; it does not solve that motion.
    """
    m,r,rd,rdd,w,alpha,I0=np.broadcast_arrays(
        mass_kg,radius_m,radial_speed_m_s,radial_accel_m_s2,
        omega_rad_s,alpha_rad_s2,fixed_inertia_kg_m2)
    if not all(np.all(np.isfinite(v)) for v in (m,r,rd,rdd,w,alpha,I0)):
        raise ValueError("Power inputs must be finite")
    if np.any(m<0) or np.any(r<=0) or np.any(I0<0):
        raise ValueError("Invalid mass, radius or fixed inertia")
    inertia=I0+m*r*r
    inertia_rate=2*m*r*rd
    torque=inertia*alpha+inertia_rate*w
    wheel_power=torque*w
    radial_power=m*(rdd-w*w*r)*rd
    kinetic_rate=inertia*w*alpha+0.5*inertia_rate*w*w+m*rd*rdd
    return dict(torque_n_m=torque,wheel_mechanical_w=wheel_power,
                radial_mechanical_w=radial_power,kinetic_rate_w=kinetic_rate,
                residual_w=wheel_power+radial_power-kinetic_rate)


def minimum_solar_elevation_window(env: LunarEnvironment, minimum_elevation_rad: float) -> dict:
    """Zero-declination, flat-horizon equatorial sunlight bound; tracking optional.

    Availability only, no panel performance assumption. Operate within the given
    positive elevation threshold to avoid claiming power at the horizon.
    """
    if not np.isfinite(minimum_elevation_rad) or not 0 <= minimum_elevation_rad < pi/2:
        raise ValueError("Minimum elevation must be in [0,pi/2)")
    fraction=(pi-2*minimum_elevation_rad)/(2*pi)
    return dict(available_fraction=fraction,
                operating_window_s=env.solar_day_s*fraction,
                night_or_low_sun_s=env.solar_day_s*(1-fraction))


def count_catches_in_window(window_s: float, launch_interval_s: float,
                            full_cycle_before_first: bool = True) -> int:
    """Conservative complete-cycle count in one uninterrupted sun window.

    Requiring the first full interval avoids silently precharging/preloading at
    night; actual phase can cost one additional opportunity per window.
    """
    if window_s < 0 or launch_interval_s <= 0:
        raise ValueError("Invalid window or launch interval")
    return int(window_s//launch_interval_s)+(0 if full_cycle_before_first else 1)
