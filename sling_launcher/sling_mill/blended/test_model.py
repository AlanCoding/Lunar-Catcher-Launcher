import json,unittest
from pathlib import Path
import numpy as np
from model import solve,contact

class BlendedTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.c=json.loads(Path(__file__).with_name('config.json').read_text())
        cls.r,cls.a,cls.m=solve(cls.c)
    def test_contact_gap_closes(self):
        self.assertLess(self.r['max_contact_residual_m'],1e-10)
    def test_gravity_balance(self):
        c=self.c;weight=c['payload_density']*c['payload_width']*c['payload_depth']*c['radius']*c['pitch_over_radius']*1.62
        np.testing.assert_allclose(self.a['lower_normal_force_N']-self.a['upper_normal_force_N'],weight,rtol=1e-11)
    def test_acceleration_is_derived(self):
        c=self.c
        expected=2*c['friction_coefficient']*self.a['normal_force_per_drum_N']/(c['payload_density']*c['payload_width']*c['payload_depth']*c['radius']*c['pitch_over_radius'])
        np.testing.assert_allclose(self.a['acceleration_m_s2'],expected)
        self.assertNotIn('acceleration',c)
    def test_rim_speed_closes(self):
        c=self.c
        expected=(np.sqrt(self.a['v_m_s']**2+self.a['acceleration_m_s2']*c['payload_length'])+c['slip_margin_m_s'])/(1-c['speed_reserve_fraction'])
        np.testing.assert_allclose(self.a['rim_speed_m_s'],expected)
    def test_energy_and_heat_partition(self):
        self.assertLess(abs(self.r['energy_error_fraction']),1e-10)
        self.assertAlmostEqual(self.r['bar_heating_W']+self.r['roller_heating_W'],self.r['slip_heat_W'])
        self.assertAlmostEqual(self.r['bar_heating_W'],self.r['roller_heating_W'])
    def test_loose_setting_rejected(self):
        with self.assertRaisesRegex(ValueError,'two-sided contact'):
            solve(dict(self.c,total_squeeze_m=.0001))
    def test_tighter_means_shorter_and_hotter(self):
        r,_,_=solve(dict(self.c,total_squeeze_m=.0008))
        self.assertLess(r['corridor_length_m'],self.r['corridor_length_m'])
        self.assertGreater(r['slip_heat_W'],self.r['slip_heat_W'])
        self.assertGreater(r['constraint_residuals']['bond_envelope'],0)
    def test_width_factorization(self):
        r,_,_=solve(dict(self.c,payload_width=self.c['payload_width']*2,annual_mass_kg=self.c['annual_mass_kg']*2))
        self.assertAlmostEqual(r['corridor_length_m']/self.r['corridor_length_m'],1,places=8)
        self.assertAlmostEqual(r['maximum_belt_stress_Pa']/self.r['maximum_belt_stress_Pa'],1,places=8)
        self.assertAlmostEqual(r['slip_heat_W']/self.r['slip_heat_W'],2,places=8)
    def test_stress_ceiling_rejects_stronger_demand(self):
        r,_,_=solve(dict(self.c,working_stress_Pa=1e9))
        self.assertGreater(r['constraint_residuals']['belt_stress'],0)
    def test_resolution(self):
        r,_,_=solve(dict(self.c,velocity_grid_points=321))
        self.assertLess(abs(r['corridor_length_m']/self.r['corridor_length_m']-1),.001)
        self.assertLess(abs(r['slip_heat_W']/self.r['slip_heat_W']-1),.001)
if __name__=='__main__':unittest.main()
