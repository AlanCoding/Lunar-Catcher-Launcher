"""Check the mission and mass-accounting rules before any physics is approved."""

import unittest

from lunar_slings.hub_study.accounting import (
    MassCategory as C, MassItem, category_total_kg, imported_mass_ratio,
)
from lunar_slings.hub_study.config import MissionRequirements


class FoundationTests(unittest.TestCase):
    def test_mass_origins_and_normalization(self):
        items = [MassItem("hardware", C.PERMANENT_IMPORTED, 200),
                 MassItem("ballast", C.PERMANENT_LOCAL, 800),
                 MassItem("countermass", C.EXPENDABLE_LOCAL_PER_LAUNCH, 100),
                 MassItem("captured payload", C.PAYLOAD, 100)]
        self.assertEqual(imported_mass_ratio(items), 2)
        self.assertEqual(category_total_kg(items, C.PERMANENT_LOCAL), 800)

    def test_incomplete_budget_is_not_a_zero_mass_design(self):
        items = [MassItem("unsized panels", C.PERMANENT_IMPORTED, None),
                 MassItem("captured payload", C.PAYLOAD, 100)]
        with self.assertRaisesRegex(ValueError, "unsized panels"):
            imported_mass_ratio(items)
        with self.assertRaises(ValueError):
            imported_mass_ratio([])

    def test_invalid_masses_and_changed_architecture_are_rejected(self):
        for value in (-1, float("nan"), float("inf")):
            with self.assertRaises(ValueError):
                MassItem("invalid", C.PERMANENT_IMPORTED, value)
        for override in ({"electrical_storage_allowed": True},
                         {"flywheel_buffer_allowed": True},
                         {"powered_wheel_count": 6},
                         {"catcher_altitude_m": float("nan")}):
            with self.assertRaises(ValueError):
                MissionRequirements(**override)
        self.assertEqual(MissionRequirements().powered_wheel_count, 4)
