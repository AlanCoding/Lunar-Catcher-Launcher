"""Physical invariants and independent trajectory checks, not implementation copies."""
import unittest
from math import pi
import numpy as np

from sling_launcher.environment import LunarEnvironment
from sling_launcher.orbit import (
    apsides_m, counter_release_state, finite_tip_node_intercept, impact_report,
    point_surface_reference, propagate, specific_invariants,
)
from sling_launcher.cycle import (
    CycleInputs, ideal_cycle, minimum_solar_elevation_window,
    travel_duration_s, travel_state, radial_rotation_power,
)


class OrbitTests(unittest.TestCase):
    def setUp(self):
        self.env=LunarEnvironment()

    def test_analytic_node_matches_independent_cartesian_integration(self):
        for d in [1000,3000,10000]:
            node=finite_tip_node_intercept(self.env,20000,d,3)
            result=propagate(self.env,node.initial_state,node.flight_s)
            np.testing.assert_allclose(result.y[:3,-1],node.intercept_state[:3],atol=0.002,rtol=0)
            np.testing.assert_allclose(result.y[3:,-1],node.intercept_state[3:],atol=2e-6,rtol=0)
            e0,h0=specific_invariants(node.initial_state,self.env.mu_m3_s2)
            energies=[]
            for state in result.y.T:
                energy,h=specific_invariants(state,self.env.mu_m3_s2)
                energies.append(energy)
                self.assertLess(np.linalg.norm(h-h0)/np.linalg.norm(h0),1e-9)
            self.assertLess(max(abs(np.array(energies)-e0))/abs(e0),1e-9)
            # Catcher phase must place it at the computed node at intercept time.
            n=(self.env.mu_m3_s2/(self.env.reference_radius_m+20000)**3)**0.5
            self.assertAlmostEqual(node.catcher_phase_at_release_rad+n*node.flight_s,pi/2,places=12)

    def test_integrator_tolerance_refinement(self):
        node=finite_tip_node_intercept(self.env,20000,3000,3)
        for rtol in [1e-8,1e-11]:
            result=propagate(self.env,node.initial_state,node.flight_s,rtol=rtol)
            self.assertLess(np.linalg.norm(result.y[:3,-1]-node.intercept_state[:3]),.01)

    def test_retrograde_direction_does_not_imply_impact(self):
        node=finite_tip_node_intercept(self.env,20000,3000,3)
        equal=counter_release_state(self.env,node)
        self.assertLess(equal[4],0)
        self.assertFalse(impact_report(self.env,equal)['impacts_reference_sphere'])
        short=counter_release_state(self.env,node,.99)
        report=impact_report(self.env,short)
        self.assertTrue(report['impacts_reference_sphere'])
        result=propagate(self.env,short,report['impact_s']*1.1,stop_at_surface=True)
        hit=result.y_events[0][0]
        self.assertAlmostEqual(np.linalg.norm(hit[:3]),self.env.reference_radius_m,places=5)

    def test_site_repeat_not_inertial_orbit_period(self):
        r=point_surface_reference(self.env,20000)
        n=2*pi/r['orbit_period_s']
        self.assertAlmostEqual((n-self.env.spin_rad_s)*r['site_revisit_s'],2*pi,places=12)
        self.assertGreater(r['site_revisit_s'],r['orbit_period_s'])
        self.assertAlmostEqual(r['retrograde_site_m_s']-r['prograde_site_m_s'],
                               2*self.env.spin_rad_s*self.env.reference_radius_m,places=9)

    def test_invalid_geometry_does_not_produce_feasible_state(self):
        for d,height in [(0,3),(3000,-100),(1e6,3)]:
            with self.assertRaises(ValueError):
                finite_tip_node_intercept(self.env,20000,d,height)


class CycleTests(unittest.TestCase):
    def test_massless_climber_limit_has_no_return_power(self):
        c=CycleInputs(50,3000,.56,100,100,0,10,1,.85,.8,60,60)
        result=ideal_cycle(c,6600)
        outgoing,returning=result['segments']
        self.assertGreater(outgoing['radial_braking_energy_j'],0)
        self.assertEqual(returning['electrical_energy_j'],0)
        self.assertGreater(outgoing['wheel_input_energy_j'],0)

    def test_constant_spin_outward_extraction_and_wheel_work(self):
        r=np.linspace(50,3000,10001)
        m,w,v=200,.56,10
        p=radial_rotation_power(m,r,v,0,w,0)
        delta_k=.5*m*w*w*(r[-1]**2-r[0]**2)
        self.assertAlmostEqual(np.trapezoid(p['wheel_mechanical_w']/v,r)/(2*delta_k),1,places=10)
        self.assertAlmostEqual(np.trapezoid(p['radial_mechanical_w']/v,r)/(-delta_k),1,places=10)

    def test_torque_free_deployment_extracts_rotational_energy(self):
        r=np.linspace(50,3000,100001)
        m,I0,rd=200,1e7,10
        inertia=I0+m*r*r
        momentum=inertia[0]*.56
        w=momentum/inertia
        alpha=-2*m*r*rd*w/inertia
        p=radial_rotation_power(m,r,rd,0,w,alpha,I0)
        self.assertLess(np.max(np.abs(p['torque_n_m'])),1e-6)
        self.assertTrue(np.all(p['radial_mechanical_w']<0))
        delta_k=.5*inertia[-1]*w[-1]**2-.5*inertia[0]*w[0]**2
        work=np.trapezoid(p['radial_mechanical_w']/rd,r)
        self.assertAlmostEqual(work/delta_k,1,places=7)

    def test_rest_to_rest_travel_limits(self):
        for length, vmax, accel in [(1,10,1),(2950,10,1)]:
            total=travel_duration_s(length,vmax,accel)
            t=np.linspace(0,total,1001)
            x,v,a=travel_state(t,length,vmax,accel)
            self.assertAlmostEqual(x[0],0)
            self.assertAlmostEqual(x[-1],length)
            self.assertAlmostEqual(v[0],0)
            self.assertAlmostEqual(v[-1],0)
            self.assertLessEqual(max(v),vmax)
            self.assertLessEqual(max(abs(a)),accel)
            self.assertGreaterEqual(min(np.diff(x)),0)

    def test_work_energy_and_no_regeneration_credit(self):
        c=CycleInputs(50,3000,.56,100,100,10,10,1,.85,.8,60,60)
        result=ideal_cycle(c,6600,samples=16001)
        for s in result['segments']:
            self.assertTrue(np.all(s['electrical_w']>=0))
            self.assertLess(abs(s['work_energy_residual_j']),300)
            self.assertGreater(s['dumped_energy_j'],0)
        # Empty return has negative wheel work yet positive electrical demand.
        returning=result['segments'][1]
        self.assertLess(np.trapezoid(returning['wheel_mechanical_w'],returning['time_s']),0)
        self.assertGreater(returning['electrical_energy_j'],0)

    def test_slow_climbers_force_skipped_passes(self):
        c=CycleInputs(50,3000,.56,100,100,10,.5,1,.85,.8,60,60)
        result=ideal_cycle(c,6600)
        self.assertEqual(result['passes_skipped'],1)
        self.assertGreaterEqual(result['launch_interval_s'],result['minimum_cycle_s'])

    def test_sun_availability_has_no_night_energy(self):
        env=LunarEnvironment()
        self.assertEqual(minimum_solar_elevation_window(env,0)['available_fraction'],.5)
        self.assertAlmostEqual(minimum_solar_elevation_window(env,pi/18)['available_fraction'],4/9)
        with self.assertRaises(ValueError):
            minimum_solar_elevation_window(env,pi/2)
