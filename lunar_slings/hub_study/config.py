"""Mission requirements from the user handoff; SI units, no material assumptions."""

from dataclasses import dataclass
from math import isfinite


@dataclass(frozen=True)
class MissionRequirements:
    """Fixed architecture and initial targets, not a feasible design assertion.

    Altitude is initially relative to the eventual reference Moon surface.
    Wheel speed is a proposed upper bound to validate, not a commanded speed.
    """

    catcher_altitude_m: float = 20_000.0
    proposed_max_wheel_speed_m_s: float = 35.76
    site_latitude_rad: float = 0.0
    assembly_count: int = 2
    powered_wheel_count: int = 4
    passive_wheel_count: int = 4
    climber_count: int = 2
    simultaneous_useful_payload_count: int = 1
    maximum_catches_per_orbit: int = 1
    sling_material: str = "Kevlar"
    electrical_storage_allowed: bool = False
    flywheel_buffer_allowed: bool = False

    def __post_init__(self) -> None:
        for name in ("catcher_altitude_m", "proposed_max_wheel_speed_m_s"):
            value = getattr(self, name)
            if not isfinite(value) or value <= 0:
                raise ValueError(f"{name} must be finite and positive")
        if self.site_latitude_rad != 0:
            raise ValueError("This study requires an equatorial launch site")
        if (self.assembly_count, self.powered_wheel_count, self.passive_wheel_count, self.climber_count,
            self.simultaneous_useful_payload_count, self.maximum_catches_per_orbit
        ) != (2, 4, 4, 2, 1, 1):
            raise ValueError("Configuration changes the specified architecture")
        if self.sling_material != "Kevlar":
            raise ValueError("The specified sling material is Kevlar")
        if self.electrical_storage_allowed or self.flywheel_buffer_allowed:
            raise ValueError("The specified architecture excludes energy buffers")
