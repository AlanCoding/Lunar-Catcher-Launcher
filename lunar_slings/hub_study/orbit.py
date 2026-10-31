"""Ballistic transfers and exact finite horizontal-sling release geometry.

Moon-centered inertial axes: X is radial through the launcher center at release,
Y is east, Z is north (Moon spin axis). All public inputs/outputs use SI/radians.
No gravity harmonics, terrain, capture engineering, or assumed rocket burn.
"""

from dataclasses import dataclass
from math import acos, atan2, pi, sqrt

import numpy as np
from scipy.integrate import solve_ivp

from .environment import LunarEnvironment


def _positive(**values):
    for name, value in values.items():
        if not np.isfinite(value) or value <= 0:
            raise ValueError(f"{name} must be finite and positive")


def circular_period_s(mu_m3_s2: float, radius_m: float) -> float:
    """Circular inertial period [s] from mu [m³/s²] and radius [m]."""
    _positive(mu=mu_m3_s2, radius=radius_m)
    return 2 * pi * sqrt(radius_m**3 / mu_m3_s2)


def point_surface_reference(env: LunarEnvironment, catcher_altitude_m: float) -> dict:
    """Equatorial point-launch apoapsis reference, explicitly zero sling offset."""
    _positive(altitude=catcher_altitude_m)
    r0 = env.reference_radius_m
    rc = r0 + catcher_altitude_m
    a = (r0 + rc) / 2
    vp = sqrt(env.mu_m3_s2 * (2 / r0 - 1 / a))
    va = r0 * vp / rc
    vc = sqrt(env.mu_m3_s2 / rc)
    flight = pi * sqrt(a**3 / env.mu_m3_s2)
    n = vc / rc
    return dict(release_inertial_m_s=vp,
                prograde_site_m_s=vp-env.spin_rad_s*r0,
                retrograde_site_m_s=vp+env.spin_rad_s*r0,
                flight_s=flight, catch_relative_m_s=vc-va,
                catcher_phase_at_release_rad=pi-n*flight,
                orbit_period_s=2*pi/n,
                site_revisit_s=2*pi/(n-env.spin_rad_s))


@dataclass(frozen=True)
class NodeIntercept:
    """First equator-node intercept from a finite south-offset, eastward release.

    initial_state: X,Y,Z,VX,VY,VZ in m and m/s. 'tip_offset' is distance south
    of hub center, including apex radius, not just the outward sling length.
    Tip height is relative to the hub tangent plane; it is NOT pole height.
    """

    initial_state: np.ndarray
    intercept_state: np.ndarray
    flight_s: float
    site_tip_speed_m_s: float
    hub_rate_rad_s: float
    inclination_rad: float
    eccentricity: float
    apoapsis_radius_m: float
    catch_relative_vector_m_s: np.ndarray
    catcher_phase_at_release_rad: float


def finite_tip_node_intercept(env: LunarEnvironment, catcher_altitude_m: float,
                             tip_offset_m: float,
                             tip_tangent_height_m: float) -> NodeIntercept:
    """Solve an eastward horizontal release meeting the equatorial catcher.

    Both initial radial velocity and northward velocity are zero. The inclined
    plane first meets the equator 90 degrees downtrack; choose semilatus rectum
    p equal to catcher radius. Valid for a bound, below-catcher release.
    """
    _positive(altitude=catcher_altitude_m, tip_offset=tip_offset_m)
    if not np.isfinite(tip_tangent_height_m):
        raise ValueError("Tip tangent height must be finite")
    x = env.reference_radius_m + tip_tangent_height_m
    r0 = np.hypot(x, tip_offset_m)
    rc = env.reference_radius_m + catcher_altitude_m
    if not env.reference_radius_m < r0 < rc or x <= 0:
        raise ValueError("Release must be above reference surface and below catcher")
    e = rc/r0-1
    if not 0 < e < 1:
        raise ValueError("This branch needs a bound periapsis release")
    vi = sqrt(env.mu_m3_s2*rc)/r0
    u = vi-env.spin_rad_s*x
    vc = sqrt(env.mu_m3_s2/rc)
    rhat = np.array([x/r0, 0, -tip_offset_m/r0])
    final_velocity = vc*(-rhat + np.array([0, e, 0]))
    vc_catcher = np.array([-vc, 0, 0])
    a = rc/(1-e*e)
    eccentric_anomaly = acos(e)  # true anomaly = pi/2
    flight = (eccentric_anomaly-e*np.sin(eccentric_anomaly))*sqrt(a**3/env.mu_m3_s2)
    n = vc/rc
    return NodeIntercept(
        initial_state=np.array([x, 0, -tip_offset_m, 0, vi, 0]),
        intercept_state=np.r_[np.array([0, rc, 0]), final_velocity],
        flight_s=float(flight), site_tip_speed_m_s=u,
        hub_rate_rad_s=u/tip_offset_m,
        inclination_rad=atan2(tip_offset_m,x), eccentricity=e,
        apoapsis_radius_m=rc/(1-e),
        catch_relative_vector_m_s=final_velocity-vc_catcher,
        catcher_phase_at_release_rad=pi/2-n*flight)


def specific_invariants(state, mu_m3_s2: float) -> tuple[float, np.ndarray]:
    """Specific energy [J/kg] and angular momentum vector [m²/s]."""
    r, v = np.asarray(state[:3]), np.asarray(state[3:])
    return float(v@v/2-mu_m3_s2/np.linalg.norm(r)), np.cross(r,v)


def apsides_m(state, mu_m3_s2: float) -> tuple[float, float]:
    """Periapsis/apoapsis radii [m] for a nonradial bound state."""
    energy, h = specific_invariants(state, mu_m3_s2)
    if energy >= 0 or np.linalg.norm(h) == 0:
        raise ValueError("Apsides require a bound nonradial orbit")
    a = -mu_m3_s2/(2*energy)
    e = sqrt(max(0.0, 1+2*energy*(h@h)/mu_m3_s2**2))
    return a*(1-e), a*(1+e)


def propagate(env: LunarEnvironment, initial_state, duration_s: float,
              *, stop_at_surface: bool = False, samples: int = 401,
              rtol: float = 2e-11):
    """Independent Cartesian two-body propagation with spherical impact event.

    Returned scipy result contains SI states and, if present, impact time/state.
    Invalid integration is an error, not a missing impact or feasible result.
    """
    _positive(duration=duration_s, tolerance=rtol)
    state = np.asarray(initial_state, dtype=float)
    if state.shape != (6,) or not np.all(np.isfinite(state)):
        raise ValueError("Expected six finite initial state components")
    if np.linalg.norm(state[:3]) < env.reference_radius_m:
        raise ValueError("Initial position is below the reference surface")
    if samples < 2:
        raise ValueError("At least two samples required")

    def rhs(t, y):
        r = y[:3]
        return np.r_[y[3:], -env.mu_m3_s2*r/np.linalg.norm(r)**3]

    def impact(t, y):
        return np.linalg.norm(y[:3])-env.reference_radius_m
    impact.direction = -1
    impact.terminal = True
    result = solve_ivp(rhs, (0, duration_s), state, method="DOP853",
                       rtol=rtol, atol=np.array([1e-5]*3+[1e-8]*3),
                       t_eval=np.linspace(0,duration_s,samples), dense_output=True,
                       max_step=duration_s/200,
                       events=impact if stop_at_surface else None)
    if not result.success:
        raise RuntimeError(result.message)
    return result


def counter_release_state(env: LunarEnvironment, useful: NodeIntercept,
                          counter_tip_radius_fraction: float = 1.0) -> np.ndarray:
    """Opposite north tip with same hub omega, optional shorter rock-side radius.

    Fraction changes total hub-to-tip radius, not countermass mass. Both release
    tips are at the same tangent-plane height in this illustrative geometry.
    """
    _positive(radius_fraction=counter_tip_radius_fraction)
    x, _, z = useful.initial_state[:3]
    d = abs(z)
    dm = d*counter_tip_radius_fraction
    vy = env.spin_rad_s*x-useful.hub_rate_rad_s*dm
    return np.array([x,0,dm,0,vy,0])


def impact_report(env: LunarEnvironment, state) -> dict:
    """First spherical impact, or a proven two-body nonimpact apsis bound.

    Longitudes are relative to the hub meridian at release, rotating with Moon.
    No terrain, ejecta or safety certification is implied by these coordinates.
    """
    rp, ra = apsides_m(state, env.mu_m3_s2)
    out = dict(periapsis_altitude_m=rp-env.reference_radius_m,
               apoapsis_altitude_m=ra-env.reference_radius_m,
               impacts_reference_sphere=False)
    if rp > env.reference_radius_m:
        return out
    a = (rp+ra)/2
    result = propagate(env, state, circular_period_s(env.mu_m3_s2,a),
                       stop_at_surface=True)
    if not len(result.t_events[0]):
        raise RuntimeError("Orbit intersects reference surface but no impact was found")
    t = float(result.t_events[0][0])
    y = result.y_events[0][0]
    lon = (atan2(y[1],y[0])-env.spin_rad_s*t+pi)%(2*pi)-pi
    lat = atan2(y[2],np.hypot(y[0],y[1]))
    out.update(impacts_reference_sphere=True, impact_s=t,
               impact_longitude_rad=lon, impact_latitude_rad=lat,
               impact_inertial_m_s=float(np.linalg.norm(y[3:])),
               impact_ground_relative_m_s=float(np.linalg.norm(
                   y[3:]-np.cross([0,0,env.spin_rad_s],y[:3]))))
    return out
