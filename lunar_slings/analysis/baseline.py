"""Ideal lunar surface-to-catcher geometry; Python 3 standard library only.

Use the original notebook's lunar radius and mass with an explicit G.
All internal quantities use SI units. This is a point-mass, two-body model
with a stationary launch site in the inertial frame and a circular catcher.
No rotating tether, terrain, or lunar rotation is included.
"""

from math import asin, degrees, isclose, pi, sin, sqrt


G_M3_KG_S2 = 6.67430e-11
MOON_MASS_KG = 7.34767309e22
MOON_RADIUS_M = 1_737_000.0
MU_M3_S2 = G_M3_KG_S2 * MOON_MASS_KG


def transfer(altitude_m: float) -> dict[str, float]:
    """Given catcher altitude [m], return ideal transfer metrics in SI units."""
    if altitude_m <= 0:
        raise ValueError("Catcher altitude must be positive.")
    rp = MOON_RADIUS_M
    ra = rp + altitude_m
    a = (rp + ra) / 2
    vp = sqrt(MU_M3_S2 * (2 / rp - 1 / a))
    va = sqrt(MU_M3_S2 * (2 / ra - 1 / a))
    vc = sqrt(MU_M3_S2 / ra)
    flight_s = pi * sqrt(a**3 / MU_M3_S2)
    catcher_period_s = 2 * pi * sqrt(ra**3 / MU_M3_S2)

    # Independent checks: angular momentum, energy, and original Hohmann form.
    assert isclose(rp * vp, ra * va, rel_tol=1e-12)
    assert isclose(vp**2 / 2 - MU_M3_S2 / rp,
                   va**2 / 2 - MU_M3_S2 / ra, rel_tol=1e-12)
    assert isclose(vp, sqrt(MU_M3_S2 / rp) * sqrt(2 * ra / (rp + ra)),
                   rel_tol=1e-12)

    def apoapsis_m(speed_m_s: float) -> float:
        """Apoapsis radius [m] for a tangential, bound surface launch [m/s]."""
        denominator = 2 * MU_M3_S2 / (rp * speed_m_s**2) - 1
        if denominator <= 0:
            raise ValueError("Launch is unbound; no finite apoapsis.")
        return rp / denominator

    assert isclose(apoapsis_m(vp), ra, rel_tol=1e-12)
    timing_s = catcher_period_s / 2 - flight_s
    return {
        "altitude_m": altitude_m,
        "launch_m_s": vp,
        "catch_mismatch_m_s": vc - va,
        "flight_s": flight_s,
        "catcher_lead_m": vc * timing_s,
        "apoapsis_error_plus_1_m_s_m": apoapsis_m(vp + 1) - ra,
        "cross_velocity_0_1_deg_m_s": va * sin(pi / 1800),
        "direction_error_for_equal_cross_deg": degrees(asin((vc - va) / va)),
        "launch_energy_j_kg": vp**2 / 2,
    }


def main() -> None:
    """Print comparison of the 30 km and original 100 km catcher cases."""
    cases = [transfer(30_000), transfer(100_000)]
    rows = [
        ("Surface launch speed (m/s)", "launch_m_s", 1),
        ("Tangential catch mismatch (m/s)", "catch_mismatch_m_s", 1),
        ("Launch-to-catch time (minutes)", "flight_s", 1 / 60),
        ("Catcher lead at firing (km of orbital arc)", "catcher_lead_m", 1 / 1000),
        ("Apoapsis error from +1 m/s launch error (km)", "apoapsis_error_plus_1_m_s_m", 1 / 1000),
        ("Cross velocity from 0.1 degree error (m/s)", "cross_velocity_0_1_deg_m_s", 1),
        ("Direction error giving equal cross/mismatch speed (degrees)", "direction_error_for_equal_cross_deg", 1),
        ("Ideal launch kinetic energy (MJ/kg)", "launch_energy_j_kg", 1e-6),
    ]
    print("| Quantity | 30 km catcher | 100 km catcher |")
    print("| --- | ---: | ---: |")
    for label, key, scale in rows:
        values = " | ".join(f"{case[key] * scale:.3f}" for case in cases)
        print(f"| {label} | {values} |")


if __name__ == "__main__":
    main()
