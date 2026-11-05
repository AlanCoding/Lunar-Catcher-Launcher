import json
import unittest
import numpy as np
from .impact_demo import release_solution,first_impact,state,RADIUS
from .sweep_equator import possible_contact_intervals,first_impact_bounded,summarize,ROOT
from .test_impact_demo import Sphere
from .terrain_band import TerrainBand,CACHE


class SweepChecks(unittest.TestCase):
    def test_altitude_skips_are_clear(self):
        s=release_solution(Sphere(),0,1);ceiling=RADIUS+1000.
        intervals=possible_contact_intervals(s,ceiling)
        self.assertEqual(len(intervals),2)
        times=np.linspace(0,1.5*s['period_s'],10001)
        pos,_=state(s,times)
        within=np.zeros(len(times),dtype=bool)
        for lo,hi in intervals:within|=(times>=lo)&(times<=hi)
        self.assertTrue(np.all(np.linalg.norm(pos[~within],axis=1)>ceiling))
        self.assertFalse(possible_contact_intervals(s,RADIUS+1))

    def test_smooth_sphere_cutoff(self):
        for sign in [1,-1]:
            s=release_solution(Sphere(),0,sign)
            out=first_impact_bounded(s,Sphere())
            self.assertEqual(out['status'],'not_arrested')
            self.assertEqual(out['completed_orbits'],1.5)

    def test_conditional_denominators(self):
        statuses=[('outbound_collision','arrested_after_missed_capture'),('not_arrested','outbound_collision')]
        cases=[]
        for lon,pair in enumerate(statuses):
            arms=[dict(outcome=dict(status=s),outbound_clear=s!='outbound_collision',return_impact_given_outbound_clear=None if s=='outbound_collision' else s=='arrested_after_missed_capture') for s in pair]
            cases.append(dict(longitude_deg_east=lon,arms=arms,both_outbound_clear=False,both_arrested_after_missed_capture=False))
        out=summarize(cases)
        self.assertEqual(out['prograde']['outbound_clear_fraction'],.5)
        self.assertEqual(out['prograde']['conditional_return_impact_fraction'],0)
        self.assertEqual(out['retrograde']['conditional_return_impact_fraction'],1)
        self.assertEqual(out['paired']['both_outbound_clear'],0)

    def test_synthetic_return_obstruction(self):
        class ReturnRidge(Sphere):
            max_height_m=1000.
            def height_m(self,lat,lon):
                lon=np.asarray(lon)
                return 1000*np.maximum(0.,1-np.abs(lon-359)/.2)
        s=release_solution(ReturnRidge(),0,1)
        fast=first_impact_bounded(s,ReturnRidge(),10.)
        slow=first_impact(s,ReturnRidge(),10.)
        self.assertEqual(fast['status'],'arrested_after_missed_capture')
        self.assertAlmostEqual(fast['impact_time_s'],slow['impact_time_s'],places=5)

    @unittest.skipUnless((CACHE/'000.npy').exists(),'Downloaded corridor needed')
    def test_preserved_demo_matches(self):
        t=TerrainBand();data=json.loads((ROOT/'demo_results/results.json').read_text())
        for c in data['scenarios']:
            for s in c['arms']:
                out=first_impact_bounded(s,t,.25)
                self.assertEqual(out['status'],s['outcome']['status'])
                self.assertAlmostEqual(out['impact_time_s'],s['outcome']['impact_time_s'],places=6)


if __name__=='__main__':unittest.main()
