"""Physical limits and conservation for the cable-inventory payout model."""
import unittest
from dataclasses import replace
import numpy as np
from lunar_slings.hub_study.spooling_cycle import PayoutCase, run
from lunar_slings.hub_study.environment import LunarEnvironment

class SpoolingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.c=PayoutCase()
        cls.result=run(cls.c,include_history=True)

    def test_deployment_and_retraction_work_energy(self):
        r=self.result;g=LunarEnvironment().surface_gravity_m_s2
        for p in r['history'][1:3]:
            rolling=self.c.rolling_coefficient*g*(p['base_mass']+r['ballast_total_kg'])*self.c.track_radius_m*p['omega']
            work=np.trapezoid(p['wheel']-rolling+p['radial'],p['t'])
            energy=.5*p['inertia']*p['omega']**2+.5*p['radial_mass']*p['qd']**2
            change=energy[-1]-energy[0]
            self.assertLess(abs(work/change-1),2e-6)

    def test_phase_and_time_close(self):
        r=self.result
        angle=sum(np.trapezoid(p['omega'],p['t']) for p in r['history'])
        self.assertLess(abs(angle/(2*np.pi)-round(angle/(2*np.pi))),1e-8)
        self.assertAlmostEqual(sum(p['duration_s'] for p in r['phases']),r['interval_s'])

    def test_traction_peak_precedes_tip_and_ballast_satisfies_bound(self):
        r=self.result
        self.assertEqual(r['peak_traction_location']['phase'],'payout')
        self.assertTrue(.5<r['peak_traction_location']['deployed_fraction']<.99)
        self.assertGreaterEqual(r['minimum_traction_margin_n'],-1e-6)
        for p in r['history']:
            normal=LunarEnvironment().surface_gravity_m_s2*(p['base_mass']+r['ballast_total_kg'])
            self.assertTrue(np.all(abs(p['force'])<=self.c.friction*self.c.driven_normal_fraction*normal+1e-6))

    def test_two_passes_reduce_ballast_but_cannot_fix_release_speed(self):
        two=run(replace(self.c,passes=2))
        self.assertLess(two['ballast_total_kg'],self.result['ballast_total_kg'])
        for passes in [1,2]:
            self.assertEqual(run(replace(self.c,acceleration_g=300,passes=passes))['status'],'release wheel-speed constraint')
        smaller=run(replace(self.c,acceleration_g=300,track_radius_m=20))
        self.assertLess(smaller['wheel_release_speed_m_s'],35.76)

    def test_recovery_does_not_reduce_mechanical_traction_requirement(self):
        recovery=run(replace(self.c,recovery_efficiency=.7))
        self.assertEqual(recovery['ballast_total_kg'],self.result['ballast_total_kg'])
        self.assertLess(recovery['peak_solar_w'],self.result['peak_solar_w'])
        self.assertGreater(self.result['phases'][2]['peak_radial_input_w'],0)

    def test_spatial_and_time_refinement(self):
        fine=run(replace(self.c,nodes=20001,time_nodes=4001))
        for key in ['peak_solar_w','ballast_total_kg','solar_energy_j']:
            self.assertLess(abs(fine[key]/self.result[key]-1),2e-5)
