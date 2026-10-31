"""Single source for the Phase 4 illustrative sweep, NOT a candidate launcher.

No allowable stress, pole height, installed panel specific power or subsystem
mass is invented. Efficiencies/times below are declared sensitivities pending
hardware selection. Tip tangent height is release position, not pole height.
"""
from dataclasses import dataclass

from .config import MissionRequirements
from .environment import LunarEnvironment


@dataclass(frozen=True)
class OrbitCycleStudy:
    environment: LunarEnvironment = LunarEnvironment()
    mission: MissionRequirements = MissionRequirements()
    tip_offsets_m: tuple = (1000.0, 3000.0, 10000.0)
    illustrative_tip_offset_m: float = 3000.0
    tip_tangent_height_m: float = 3.0
    shorter_counter_radius_fraction: float = 0.99
    illustrative_apex_radius_m: float = 50.0
    illustrative_payload_kg: float = 100.0
    illustrative_countermass_kg: float = 100.0
    # A zero-mass comparison is a lower-bound device, not a physical climber.
    reference_climber_mass_ratio: float = 0.0
    climber_mass_ratio_sensitivities: tuple = (0.0, 0.01, 0.1)
    illustrative_travel_speeds_m_s: tuple = (0.5, 1.0, 5.0, 10.0)
    illustrative_radial_travel_accel_m_s2: float = 1.0
    illustrative_wheel_efficiency: float = 0.85
    illustrative_climber_efficiency: float = 0.80
    illustrative_loading_s: float = 60.0
    illustrative_settle_s: float = 60.0
    minimum_solar_elevation_deg: float = 10.0
