"""Spherical two-body environment; SI constants and source IDs live here once."""

from dataclasses import dataclass
from math import isfinite, pi


@dataclass(frozen=True)
class LunarEnvironment:
    """Equatorial spherical reference, not a lunar terrain or gravity-harmonic model.

    Sources: S5 NASA Moon Fact Sheet (equatorial radius, rotation, solar day,
    irradiance), S8 JPL DE440 parameters (mu, Julian year). Rounded rotation
    and solar-day values follow S5; precision is adequate only for this study.
    """

    reference_radius_m: float = 1_738_100.0
    mu_m3_s2: float = 4.902800118e12
    sidereal_rotation_s: float = 655.720 * 3600.0
    solar_day_s: float = 29.53 * 86400.0
    solar_irradiance_w_m2: float = 1361.0
    earth_g_m_s2: float = 9.80665
    year_s: float = 365.25 * 86400.0

    def __post_init__(self):
        for name, value in vars(self).items():
            if not isfinite(value) or value <= 0:
                raise ValueError(f"{name} must be finite and positive")

    @property
    def spin_rad_s(self) -> float:
        return 2 * pi / self.sidereal_rotation_s

    @property
    def surface_gravity_m_s2(self) -> float:
        return self.mu_m3_s2 / self.reference_radius_m**2
