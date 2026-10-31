import unittest
from dataclasses import replace
import numpy as np
from lunar_slings.hub_study.scenario_study import Scenario,geometry,calculate
from lunar_slings.hub_study.environment import LunarEnvironment

class ScenarioTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.c=Scenario();cls.geo=geometry(cls.c);cls.r=calculate(cls.c,cls.geo,history=True)

    def test_dependent_radius_speed_and_phase(self):
        r=self.r;c=self.c
        self.assertAlmostEqual(r['track_radius_m']*r['omega_rad_s'],c.rover_mph*.44704)
        self.assertLessEqual(r['max_rover_speed_m_s'],c.rover_mph*.44704+1e-10)
        self.assertGreater(r['min_rover_speed_m_s'],0)
        angle=sum(np.trapezoid(p['omega'],p['t']) for p in r['history'])
        self.assertAlmostEqual(angle/(2*np.pi),round(angle/(2*np.pi)),places=8)

    def test_finite_angle_shape_and_sized_release(self):
        cable,branches,_,_=self.geo
        p=branches[0]['shapes'][-1]
        self.assertLess(abs(p['r'][-1]/cable.tip_radius-1),2e-5)
        for branch in branches:
            self.assertLess(branch['max_tensile_stress_pa']/self.c.stress_pa,1.0001)
            for p in branch['shapes'][1::20]:
                self.assertTrue(np.all(p['tr']>=-1e-6))
                self.assertTrue(np.all(p['tv']>=-1e-6))
                chord=np.hypot(np.diff(p['r']),np.diff(p['drop']))
                self.assertLess(np.max(abs(chord/np.diff(p['s'])-1)),.002)

    def test_shape_energy_balance_each_continuous_branch(self):
        g=LunarEnvironment().surface_gravity_m_s2
        for p in self.r['history'][1:3]:
            rolling=self.c.rolling*g*(p['base_mass']+self.r['ballast_total_kg'])*self.r['track_radius_m']*p['omega']
            work=np.trapezoid(p['wheel']-rolling+p['radial'],p['t'])
            change=(p['kinetic']+p['potential'])[-1]-(p['kinetic']+p['potential'])[0]
            self.assertLess(abs(work/change-1),3e-5)
        # The release jump must remain visible rather than included in this identity.
        self.assertGreater(abs(self.r['release_shape_energy_discontinuity_j']),1e6)

    def test_traction_and_timing(self):
        r=self.r;g=LunarEnvironment().surface_gravity_m_s2
        for p in r['history']:
            capacity=self.c.friction*self.c.driven_fraction*g*(p['base_mass']+r['ballast_total_kg'])
            self.assertTrue(np.all(abs(p['force'])<=capacity+1e-6))
        self.assertAlmostEqual(sum(p['duration_s'] for p in r['phases']),r['interval_s'])
        two=calculate(replace(self.c,passes=2),self.geo)
        self.assertLess(two['ballast_total_kg'],r['ballast_total_kg'])
        self.assertEqual(two['phases'][0]['duration_s'],r['phases'][0]['duration_s'])
        self.assertFalse(r['frame_45deg_same_track_fits'])
        self.assertIsNone(r['total_imported_mass_kg'])

    def test_refinement(self):
        fine=calculate(replace(self.c,shape_fractions=481,shape_nodes=1001,time_nodes=3201))
        for key in ['pole_apex_height_m','ballast_total_kg','peak_solar_no_recovery_w','peak_solar_recovery_w']:
            self.assertLess(abs(fine[key]/self.r[key]-1),.002,key)

if __name__=='__main__':unittest.main()
