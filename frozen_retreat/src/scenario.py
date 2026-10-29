"""Scenario model and deterministic trade study runner."""

from __future__ import annotations

from dataclasses import asdict, dataclass
import math

from .ep import ep_power_for_thrust_W, mass_ratio, thrust_for_impulse, thrust_from_ep_power_N
from .orbital import (
    circular_speed_km_s,
    hohmann_delta_v_km_s,
    specific_energy_surface_rest_to_orbit_m2_s2,
    transfer_ellipse_from_rp_ra,
)
from .unit_helpers import days_to_seconds, hours_to_seconds, km_s_to_m_s, metric_tons_to_kg


@dataclass(frozen=True)
class Scenario:
    """Single source of truth assumptions for the lunar catcher analysis.

    All units are encoded in field names.
    """

    R_moon_km: float = 1737.4
    mu_km3_s2: float = 4902.800
    h_gauntlet_km: float = 30.0
    h_escape_km: float = 120.0
    dv_bridge_m_s: float = 800.0
    ve_m_s: float = 3000.0
    eta: float = 0.60
    f_sun: float = 0.71
    t_catch_hr: float = 50.0
    m_depart_gauntlet_t: float = 1000.0
    m_dry_t: float = 50.0
    sp_solar_W_per_kg: float = 100.0
    S_W_m2: float = 1361.6
    pv_net_fraction: float = 0.27
    g0_m_s2: float = 9.80665
    housekeeping_margin_MW: float = 0.03
    system_margin_factor: float = 1.2
    eff_driver: float = 0.5


def _bridge_budget_t(m_depart_t: float, dv_bridge_m_s: float, ve_m_s: float, m_dry_t: float) -> dict:
    mr = mass_ratio(dv_bridge_m_s, ve_m_s)
    m_arrive_t = m_depart_t / mr
    return {
        "MR": mr,
        "m_arrive_depot_t": m_arrive_t,
        "delivered_rocks_t": m_arrive_t - m_dry_t,
        "up_leg_prop_t": m_depart_t - m_arrive_t,
        "down_leg_prop_t": (mr - 1.0) * m_dry_t,
    }


def run_trade_study(s: Scenario) -> dict:
    """Run all sections of the trade study and return deterministic results.

    Input:
    - s: Scenario (all assumptions/units explicit)

    Output:
    - dict with assumptions and section-level results/tables
    """
    assert s.mu_km3_s2 > 0.0
    assert s.R_moon_km > 0.0
    assert s.ve_m_s > 0.0
    assert 0.0 < s.eta <= 1.0
    assert 0.0 < s.f_sun <= 1.0

    pv_net_W_m2 = s.S_W_m2 * s.pv_net_fraction

    # Section 1
    r30_km = s.R_moon_km + s.h_gauntlet_km
    v_c_30_km_s = circular_speed_km_s(s.mu_km3_s2, r30_km)

    # Section 2/3/4
    xfer = transfer_ellipse_from_rp_ra(s.mu_km3_s2, s.R_moon_km, r30_km)
    v_p_m_s = km_s_to_m_s(xfer["v_p_km_s"])
    v_a_m_s = km_s_to_m_s(xfer["v_a_km_s"])
    v_c_ra_m_s = km_s_to_m_s(v_c_30_km_s)
    dv1_m_s = v_p_m_s
    dv2_m_s = v_c_ra_m_s - v_a_m_s
    v_rel_catch_m_s = dv2_m_s
    v_impact_m_s = v_p_m_s

    # Section 5
    r1_km = s.R_moon_km + s.h_gauntlet_km
    r2_km = s.R_moon_km + s.h_escape_km
    hoh = hohmann_delta_v_km_s(s.mu_km3_s2, r1_km, r2_km)
    dv_30_to_120_m_s = km_s_to_m_s(hoh["dv_total_km_s"])

    # Section 8
    bridge = _bridge_budget_t(s.m_depart_gauntlet_t, s.dv_bridge_m_s, s.ve_m_s, s.m_dry_t)

    # Section 6
    captured_mass_kg = metric_tons_to_kg(bridge["delivered_rocks_t"])
    t_catch_s = hours_to_seconds(s.t_catch_hr)
    T_catch_N = captured_mass_kg * v_rel_catch_m_s / t_catch_s
    P_catch_W = ep_power_for_thrust_W(T_catch_N, s.ve_m_s, s.eta)

    escape_cases = []
    for days in (2.0, 3.0):
        t_escape_s = days_to_seconds(days)
        M_loaded_kg = metric_tons_to_kg(s.m_depart_gauntlet_t)
        T_avg_N = thrust_for_impulse(M_loaded_kg, dv_30_to_120_m_s, t_escape_s)
        T_sun_N = T_avg_N / s.f_sun
        P_sun_W = ep_power_for_thrust_W(T_sun_N, s.ve_m_s, s.eta)
        escape_cases.append(
            {
                "escape_days": days,
                "T_avg_N": T_avg_N,
                "T_sun_N": T_sun_N,
                "P_sun_W": P_sun_W,
                "T_catch_N": T_catch_N,
                "P_catch_W": P_catch_W,
            }
        )

    # Section 7
    arrays = []
    for e in escape_cases:
        P_total_W = (
            e["P_sun_W"] + e["P_catch_W"] + s.housekeeping_margin_MW * 1e6
        ) * s.system_margin_factor
        arrays.append(
            {
                "escape_days": e["escape_days"],
                "P_total_W": P_total_W,
                "array_mass_kg": P_total_W / s.sp_solar_W_per_kg,
                "array_area_m2": P_total_W / pv_net_W_m2,
                "P_sun_W": e["P_sun_W"],
            }
        )

    # Section 9 (2-day baseline)
    baseline = [a for a in arrays if abs(a["escape_days"] - 2.0) < 1e-9][0]
    T_sun_available_N = thrust_from_ep_power_N(baseline["P_sun_W"], s.ve_m_s, s.eta)
    T_avg_available_N = s.f_sun * T_sun_available_N
    m0_kg = metric_tons_to_kg(s.m_depart_gauntlet_t)
    m1_kg = metric_tons_to_kg(bridge["m_arrive_depot_t"])
    m_avg_kg = 0.5 * (m0_kg + m1_kg)
    t_up_leg_s = s.dv_bridge_m_s / (T_avg_available_N / m_avg_kg)

    # Section 10
    specific_energy_m2_s2 = specific_energy_surface_rest_to_orbit_m2_s2(
        s.mu_km3_s2, s.R_moon_km, s.R_moon_km + s.h_gauntlet_km
    )
    energy_total_J = specific_energy_m2_s2 * captured_mass_kg
    power_ideal_W = energy_total_J / t_catch_s
    power_elec_W = power_ideal_W / s.eff_driver
    pv_area_surface_m2 = power_elec_W / (s.S_W_m2 * s.pv_net_fraction)

    return {
        "assumptions": asdict(s) | {"pv_net_W_m2": pv_net_W_m2},
        "section_1": {
            "r30_km": r30_km,
            "v_c_30_km_s": v_c_30_km_s,
            "v_c_30_m_s": km_s_to_m_s(v_c_30_km_s),
        },
        "section_2": {
            "a_km": xfer["a_km"],
            "v_p_m_s": v_p_m_s,
            "v_a_m_s": v_a_m_s,
            "v_c_ra_m_s": v_c_ra_m_s,
            "dv1_m_s": dv1_m_s,
            "dv2_m_s": dv2_m_s,
            "dv_total_m_s": dv1_m_s + dv2_m_s,
        },
        "section_3": {"v_rel_catch_m_s": v_rel_catch_m_s},
        "section_4": {"v_impact_m_s": v_impact_m_s},
        "section_5": {
            "dv1_raise_m_s": km_s_to_m_s(hoh["dv1_km_s"]),
            "dv2_circ_m_s": km_s_to_m_s(hoh["dv2_km_s"]),
            "dv_30_to_120_m_s": dv_30_to_120_m_s,
        },
        "section_6": {"escape_cases": escape_cases},
        "section_7": {"array_cases": arrays},
        "section_8": bridge,
        "section_9": {
            "T_sun_available_N": T_sun_available_N,
            "T_avg_available_N": T_avg_available_N,
            "bridge_time_days": t_up_leg_s / 86400.0,
        },
        "section_10": {
            "specific_energy_MJ_per_kg": specific_energy_m2_s2 / 1e6,
            "energy_total_TJ": energy_total_J / 1e12,
            "power_ideal_MW": power_ideal_W / 1e6,
            "power_elec_MW": power_elec_W / 1e6,
            "surface_pv_area_m2": pv_area_surface_m2,
            "surface_pv_square_side_m": math.sqrt(pv_area_surface_m2),
        },
    }
