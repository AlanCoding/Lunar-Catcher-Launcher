"""Checks independent of the event-search method; uses existing cached DEM."""
import json,unittest
import numpy as np
from scipy.integrate import solve_ivp
from . import calculate as c
from llo_catcher.analysis.terrain.terrain_band import TerrainBand

class EquatorialTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):c.initialize()

    def test_equatorial_slice_matches_original_dem_interpolator(self):
        lon=np.r_[0,360,45,90,np.linspace(.0001,359.9999,1001)]
        np.testing.assert_allclose(c.terrain(np.radians(lon)),TerrainBand().height_m(0,lon),atol=2e-6,rtol=0)

    def test_spherical_ground_has_no_impacts(self):
        saved=c._GROUND
        try:
            c._GROUND=np.full_like(saved,125.)
            for lon in [0,123,359]:
                row=c.classify((lon,10.,False))
                self.assertEqual(row['status'],'not_arrested')
                self.assertAlmostEqual(row['release_radius_m']-(c.RADIUS+125),10)
        finally:c._GROUND=saved

    def test_longitude_inversion_and_periapsis(self):
        o=c.orbit(48,2310.7)
        fs=np.linspace(0,3*np.pi,1001);r,t=c.motion(fs,o);x=fs-c.MOON_OMEGA*t
        rr,tt,ff,_=c.at_longitude(x,o)
        np.testing.assert_allclose(ff,fs,atol=1e-12,rtol=0)
        np.testing.assert_allclose(rr,r,atol=1e-7,rtol=0)
        self.assertGreaterEqual(float(r.min()),o['rp']-1e-8)
        self.assertAlmostEqual(float(t[-1]),1.5*o['T'],places=8)

    def test_interior_grazing_minimum_is_not_missed(self):
        # One synthetic straight terrain segment is tangent to radial height
        # at its midpoint, then lifted 1 micrometre. Both endpoints clear it.
        o=c.orbit(48,100.);lo=.45;hi=lo+c.STEP;mid=(lo+hi)/2
        rmid,_,_,slope=c.at_longitude(mid,o)
        endpoints=c.at_longitude(np.array([lo,hi]),o)[0]
        ground=rmid+slope*(np.array([lo,hi])-mid)+1e-6
        self.assertTrue(np.all(endpoints>ground))
        from scipy.optimize import brentq
        root=brentq(lambda x:float(c.at_longitude(x,o)[3])-float(slope),lo,hi,xtol=1e-14)
        self.assertAlmostEqual(root,mid,places=12)
        gap=float(c.at_longitude(root,o)[0]-(rmid+slope*(root-mid)+1e-6))
        self.assertLess(gap,0)

    def test_saved_contacts_with_independent_cartesian_propagation(self):
        result=json.loads((c.OUT/'results.json').read_text());tested=0
        for height in [10.,result['selected_height_for_at_least_50_percent_m']]:
            for status in ['outbound_collision','return_impact']:
                rows=[r for r in result['trajectories'] if r['release_height_m']==height and r['status']==status]
                for row in rows[:3]:
                    o=c.orbit(row['longitude_deg_east'],height);v=o['h']/o['rp'];t=row['impact_time_s']
                    def rhs(t,y):return np.r_[y[3:],-c.MU*y[:3]/np.linalg.norm(y[:3])**3]
                    sol=solve_ivp(rhs,(0,t),[o['rp'],0,0,0,v,0],method='DOP853',rtol=1e-12,atol=1e-8,max_step=20)
                    pos=sol.y[:3,-1];lon=o['lon']+np.arctan2(pos[1],pos[0])-c.MOON_OMEGA*t
                    gap=np.linalg.norm(pos)-c.RADIUS-float(c.terrain(lon))
                    self.assertTrue(sol.success);self.assertLess(abs(gap),1e-4)
                    self.assertLessEqual(t,1.5*o['T']);tested+=1
        self.assertEqual(tested,12)

if __name__=='__main__':unittest.main()
