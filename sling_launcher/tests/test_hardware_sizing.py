import unittest
import numpy as np
from sling_launcher.component_sizing import wheel,drive,pole,HardwareAssumptions
from sling_launcher.scenario_study import Scenario,geometry,calculate
from sling_launcher.hardware_study import evaluate

class HardwareTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.case=Scenario(acceleration_g=100,rover_mph=50)
        cls.geo=geometry(cls.case);cls.base=calculate(cls.case,cls.geo,history=True)
        cls.r=evaluate(cls.base,cls.geo,radial_policy='upper_only')

    def test_wheels_grow_with_force_and_satisfy_footprint(self):
        small=wheel(1e5,22.352);large=wheel(6e5,22.352)
        self.assertGreater(large['diameter_m'],small['diameter_m'])
        self.assertGreater(large['mass_kg'],small['mass_kg'])
        self.assertLessEqual(large['actual_pressure_pa'],100000.+1e-8)

    def test_motor_and_gear_torque_cannot_hide_behind_zero_power(self):
        powered=drive(1e6,1e5,10.)
        holding=drive(0.,1e6,10.)
        self.assertGreater(holding['motor_kg'],0)
        self.assertGreater(holding['gearbox_kg'],powered['gearbox_kg'])
        self.assertGreater(drive(2e6,1e5,10.)['motor_kg'],powered['motor_kg'])

    def test_four_legs_and_selfweight_section_constraints(self):
        r=self.r;self.assertTrue(r['converged']);self.assertEqual(len(r['pole_legs']),4)
        for leg in r['pole_legs']:
            self.assertLessEqual(max(leg['utilization'].values()),1+1e-6)
            self.assertGreater(leg['mass_with_joints_kg'],leg['bare_mass_kg'])
        self.assertAlmostEqual(sum(p['mass_with_joints_kg'] for p in r['pole_legs']),r['masses_kg']['poles'])
        short=pole(5,1e6,1e6,10.,0.,1.6229)
        long=pole(10,1e6,1e6,10.,0.,1.6229)
        self.assertGreater(long['mass_with_joints_kg'],short['mass_with_joints_kg'])

    def test_coupled_budget_does_not_double_count_ballast(self):
        r=self.r;self.assertTrue(r['converged'])
        accounted=sum(v for k,v in r['masses_kg'].items() if k!='ballast_local')
        self.assertAlmostEqual(accounted,r['imported_total_kg'],places=6)
        self.assertAlmostEqual(accounted+r['ballast_kg'],r['permanent_physical_total_kg'])
        self.assertLess(r['ballast_kg'],self.base['ballast_total_kg'])
        self.assertLess(r['fixed_point_relative_residual'],2e-5)
        self.assertGreaterEqual(r['minimum_traction_margin_n'],-1e-5)
        self.assertEqual(r['masses_kg']['central_pivot_and_stabilizers'],0)
        self.assertFalse(r['feasible_design'])

    def test_failed_mass_feedback_never_becomes_a_total(self):
        r=evaluate(self.base,self.geo,max_iterations=1)
        self.assertFalse(r['converged'])
        self.assertIsNone(r['imported_ratio']);self.assertIsNone(r['imported_total_kg'])
        self.assertEqual(len(r['initial_load_pole_estimates']),4)


class SplitTieTests(unittest.TestCase):
    def test_low_tie_removes_ground_load_from_pole_and_keeps_budget_closed(self):
        c=Scenario(acceleration_g=75,rover_mph=50,passes=1);geo=geometry(c)
        r=evaluate(calculate(c,geo,history=True),geo,radial_policy='split')
        self.assertTrue(r['converged']);self.assertTrue(r['low_tie_used'])
        self.assertEqual(r['pole_ground_radial_force_each_n'],0)
        self.assertIsNone(r['missing_stabilizing_moment_nm'])
        self.assertGreater(r['masses_kg']['low_tie'],0)
        self.assertLess(r['low_tie']['sag_m'],r['low_tie_attachment_height_m'])
        self.assertAlmostEqual(sum(v for k,v in r['masses_kg'].items() if k!='ballast_local'),r['imported_total_kg'])
        self.assertGreaterEqual(r['minimum_traction_margin_n'],-1e-5)
        self.assertLess(r['masses_kg']['poles'],20000)
        self.assertAlmostEqual(r['road_only_radius_threshold_m'],616,delta=2)

    def test_large_track_has_no_low_tie_and_reserves_combined_grip(self):
        c=Scenario(acceleration_g=4,rover_mph=50,passes=1);geo=geometry(c)
        r=evaluate(calculate(c,geo,history=True),geo,radial_policy='split',max_iterations=1)
        self.assertFalse(r['low_tie_used']);self.assertEqual(r['masses_kg']['low_tie'],0)
        self.assertGreater(r['effective_tangential_friction'],0)
        self.assertLess(r['effective_tangential_friction'],.5)

    def test_cross_tie_accounts_for_distributed_inertia(self):
        from sling_launcher.hardware_study import cross_track_tie
        a=cross_track_tie(50,.4,1e6,1e9);b=cross_track_tie(50,.4,2e6,1e9)
        self.assertAlmostEqual(b['mass_kg'],2*a['mass_kg'])
        self.assertGreater(a['center_tension_n'],a['endpoint_force_n'])
        self.assertAlmostEqual(a['inertia_kg_m2']/(a['mass_kg']*50**2),1/3,delta=.001)

if __name__=='__main__':unittest.main()
