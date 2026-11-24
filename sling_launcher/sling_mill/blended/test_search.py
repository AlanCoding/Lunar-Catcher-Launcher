import json,unittest
from pathlib import Path
import numpy as np
from optimize import evaluate
ROOT=Path(__file__).parent

class SearchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.d=json.loads((ROOT/'search_results/freehub_10gpa.json').read_text())
        cls.c=dict(cls.d['parameters'],velocity_grid_points=1281)
        cls.r,cls.a,cls.m,cls.q=evaluate(cls.c)
    def test_final_candidate_on_finer_grid(self):
        self.assertLessEqual(max(self.q.values()),1e-6)
        self.assertLess(abs(self.r['gross_operating_payback_hours']/self.d['summary']['gross_operating_payback_hours']-1),1e-4)
    def test_hub_bending_and_solid_capacity(self):
        self.assertLessEqual(float(self.a['hub_deflection_m'].max()),self.c['hub_deflection_limit_m']*(1+1e-8))
        self.assertLessEqual(float(self.a['hub_solid_capacity_utilization'].max()),1+1e-8)
        self.assertTrue(np.all(self.a['hub_wall_m']>0))
    def test_wider_hub_needs_more_support(self):
        r,a,m,q=evaluate(dict(self.c,payload_width=self.c['payload_width']*2))
        self.assertGreater(q['hub_solid_capacity'],0)
        self.assertGreater(q['hub_deflection'],0)
    def test_rounded_candidate(self):
        d=json.loads((ROOT/'search_results/rounded_reference.json').read_text())
        r,a,m,q=evaluate(d['parameters'])
        self.assertLessEqual(max(q.values()),1e-6)
        self.assertLess(r['maximum_belt_stress_Pa'],1e9)
    def test_lower_stress_has_small_mass_cost(self):
        high=json.loads((ROOT/'search_results/freehub_15gpa.json').read_text())
        fraction=self.r['conditional_machine_mass_kg']/high['summary']['conditional_machine_mass_kg']-1
        self.assertGreater(fraction,0)
        self.assertLess(fraction,.03)
if __name__=='__main__':unittest.main()
