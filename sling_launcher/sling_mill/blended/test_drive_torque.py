"""Check peak torque transmission and the additional belt stress envelope."""
import json
from pathlib import Path
import unittest
import numpy as np
from model import solve
from optimize import evaluate

class DriveTorqueTests(unittest.TestCase):
    def setUp(self):
        self.c=json.loads((Path(__file__).parent/'search_results/iron_reference.json').read_text())['parameters']

    def test_peak_torque_and_belt_envelope(self):
        c=self.c
        _,a,m=solve(dict(c,include_belt_traction_envelope=True))
        _,b,n=solve(dict(c,include_belt_traction_envelope=False))
        np.testing.assert_allclose(a['drive_torque_per_drum_Nm'],a['drive_force_per_drum_N']*c['radius'])
        np.testing.assert_allclose(a['torque_member_rim_tension_N']*c['torque_members_effective']*c['radius']*c['hub_ratio'],a['drive_torque_per_drum_Nm'])
        np.testing.assert_allclose(a['belt_stress_Pa']-b['belt_stress_Pa'],a['drive_force_per_drum_N']/(c['payload_width']*c['structural_belt_thickness_m']))
        np.testing.assert_allclose(a['member_taper_area_ratio'],b['member_taper_area_ratio'])
        self.assertEqual(m,n)
        self.assertLess(max(a['belt_stress_Pa']),c['working_stress_Pa'])

    def test_diagnostic_cannot_enter_optimizer(self):
        with self.assertRaises(ValueError):
            evaluate(dict(self.c,diagnostic_omit_drive_torque=True))

if __name__=='__main__':unittest.main()
