"""Orbital mechanics helpers for the frozen retreat trade study."""

from __future__ import annotations

import math


def circular_speed_km_s(mu_km3_s2: float, r_km: float) -> float:
    """Return circular speed in km/s.

    Inputs:
    - mu_km3_s2: gravitational parameter [km^3/s^2]
    - r_km: orbital radius [km]

    Output:
    - circular speed [km/s]
    """
    assert mu_km3_s2 > 0.0
    assert r_km > 0.0
    return math.sqrt(mu_km3_s2 / r_km)


def vis_viva_speed_km_s(mu_km3_s2: float, r_km: float, a_km: float) -> float:
    """Return speed at radius r for orbit semi-major axis a, in km/s.

    Inputs:
    - mu_km3_s2: gravitational parameter [km^3/s^2]
    - r_km: instantaneous radius [km]
    - a_km: semi-major axis [km]

    Output:
    - speed [km/s]
    """
    assert mu_km3_s2 > 0.0
    assert r_km > 0.0
    assert a_km > 0.0
    term = 2.0 / r_km - 1.0 / a_km
    assert term > 0.0
    return math.sqrt(mu_km3_s2 * term)


def transfer_ellipse_from_rp_ra(mu_km3_s2: float, rp_km: float, ra_km: float) -> dict:
    """Return transfer ellipse metrics for periapsis/apoapsis radii.

    Inputs:
    - mu_km3_s2 [km^3/s^2]
    - rp_km [km]
    - ra_km [km]

    Output dict:
    - a_km: semi-major axis [km]
    - v_p_km_s: speed at periapsis [km/s]
    - v_a_km_s: speed at apoapsis [km/s]
    """
    assert ra_km >= rp_km > 0.0
    a_km = 0.5 * (rp_km + ra_km)
    return {
        "a_km": a_km,
        "v_p_km_s": vis_viva_speed_km_s(mu_km3_s2, rp_km, a_km),
        "v_a_km_s": vis_viva_speed_km_s(mu_km3_s2, ra_km, a_km),
    }


def hohmann_delta_v_km_s(mu_km3_s2: float, r1_km: float, r2_km: float) -> dict:
    """Return Hohmann transfer burn components and total in km/s.

    Inputs:
    - mu_km3_s2 [km^3/s^2]
    - r1_km: initial circular radius [km]
    - r2_km: final circular radius [km]

    Output dict:
    - dv1_km_s
    - dv2_km_s
    - dv_total_km_s
    """
    assert r1_km > 0.0 and r2_km > 0.0
    v1 = circular_speed_km_s(mu_km3_s2, r1_km)
    v2 = circular_speed_km_s(mu_km3_s2, r2_km)
    dv1 = v1 * (math.sqrt((2.0 * r2_km) / (r1_km + r2_km)) - 1.0)
    dv2 = v2 * (1.0 - math.sqrt((2.0 * r1_km) / (r1_km + r2_km)))
    return {
        "dv1_km_s": dv1,
        "dv2_km_s": dv2,
        "dv_total_km_s": dv1 + dv2,
    }


def specific_energy_surface_rest_to_orbit_m2_s2(
    mu_km3_s2: float, r_surface_km: float, r_orbit_km: float
) -> float:
    """Return ideal specific energy to reach orbit from rest at surface.

    Uses delta-epsilon = mu*(1/R - 1/(2r_orbit)).

    Inputs:
    - mu_km3_s2 [km^3/s^2]
    - r_surface_km [km]
    - r_orbit_km [km]

    Output:
    - specific energy [m^2/s^2] (= J/kg)
    """
    assert r_orbit_km >= r_surface_km > 0.0
    delta_eps_km2_s2 = mu_km3_s2 * (1.0 / r_surface_km - 1.0 / (2.0 * r_orbit_km))
    return delta_eps_km2_s2 * 1e6
