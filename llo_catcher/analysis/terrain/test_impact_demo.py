import unittest
import numpy as np
from scipy.integrate import solve_ivp
from .impact_demo import Inputs,release_solution,state,ground_coordinates,clearance,first_impact,MU,MOON_OMEGA,RADIUS
from .terrain_band import TerrainBand,CACHE


class Sphere:
    max_height_m=0.
    def height_m(self,lat,lon):
        return np.zeros(np.broadcast_arrays(lat,lon)[0].shape)


class ImpactChecks(unittest.TestCase):
    def test_release_and_node_constraints_both_directions(self):
        for sign in [1,-1]:
            s=release_solution(Sphere(),123,sign)
            p,v=state(s,0.)
            self.assertAlmostEqual(np.linalg.norm(p)-RADIUS,3.,places=6)
            self.assertAlmostEqual(np.dot(p,v),0.,places=4)
            self.assertAlmostEqual(np.linalg.norm(np.cross(p,v))**2/MU,s['catcher_radius_m'],places=6)
            pc,vc=state(s,s['ideal_catch_time_s'])
            self.assertAlmostEqual(pc[2],0.,places=6)
            self.assertAlmostEqual(np.linalg.norm(pc),s['catcher_radius_m'],places=6)
            self.assertAlmostEqual(np.linalg.norm(vc-[-np.sqrt(MU/s['catcher_radius_m']),0,0]),s['catch_relative_speed_m_s'],places=7)

    def test_kepler_against_independent_cartesian_integrator(self):
        s=release_solution(Sphere(),0,1);p,v=state(s,0.)
        duration=1.5*s['period_s']
        def rhs(t,y):return np.r_[y[3:],-MU*y[:3]/np.linalg.norm(y[:3])**3]
        result=solve_ivp(rhs,(0,duration),np.r_[p,v],method='DOP853',rtol=1e-12,atol=1e-8,max_step=30)
        self.assertTrue(result.success)
        expected=np.r_[*state(s,duration)]
        self.assertLess(np.linalg.norm(result.y[:3,-1]-expected[:3]),.001)
        self.assertLess(np.linalg.norm(result.y[3:,-1]-expected[3:]),1e-6)

    def test_rotation_and_scope_cutoff(self):
        for sign in [1,-1]:
            s=release_solution(Sphere(),20,sign)
            lat,lon,r=ground_coordinates(s,s['period_s'])
            self.assertAlmostEqual(float(lon),(20-np.degrees(MOON_OMEGA*s['period_s']))%360,places=8)
            self.assertAlmostEqual(float(lat),s['release_latitude_deg'],places=8)
            out=first_impact(s,Sphere(),spatial_step_m=1000.)
            self.assertEqual(out['status'],'not_arrested')
            self.assertEqual(out['horizon_s'],1.5*s['period_s'])

    def test_early_terrain_contact_classification(self):
        class Wall(Sphere):
            max_height_m=100.
            def height_m(self,lat,lon):
                return np.clip(np.asarray(lon)*1000,0,100)
        s=release_solution(Wall(),0,1)
        out=first_impact(s,Wall(),10.)
        self.assertEqual(out['status'],'outbound_collision')
        self.assertLess(out['impact_time_s'],1.)
        self.assertLess(abs(float(clearance(s,out['impact_time_s'],Wall()))),1e-5)

    @unittest.skipUnless((CACHE/'000.npy').exists(),'Downloaded corridor needed')
    def test_terrain_longitude_wrap_and_probe_agreement(self):
        t=TerrainBand()
        self.assertAlmostEqual(float(t.height_m(.1,0)),float(t.height_m(.1,360)),places=10)
        probe=np.load(CACHE.parent/'equator_000_045.npz')
        idx=np.arange(0,len(probe['height_m']),300)
        np.testing.assert_allclose(t.height_m(0,probe['longitude_deg_east'][idx]),probe['height_m'][idx],atol=1e-8)


if __name__=='__main__':unittest.main()
