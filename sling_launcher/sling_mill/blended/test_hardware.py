import json, unittest
from pathlib import Path
from model import solve
from hardware import update
from optimize import evaluate
P=Path(__file__).parent
import sys
sys.path.insert(0,str(P))
class IronHardwareTests(unittest.TestCase):
    def test_continuous_frame_matches_rounded_audit(self):
        d=json.loads((P/'search_results/iron_hardware_audit.json').read_text());c=d['parameters']
        r,a,m=solve(c);r,a,m=update(c,r,a,m)
        self.assertLessEqual(m['frames'],d['masses']['frames']*(1+1e-10))
        self.assertGreater(m['frames'],d['masses']['frames']*.90)
        self.assertAlmostEqual(sum(m.values()),r['conditional_machine_mass_kg'])
        self.assertAlmostEqual(m['motors'],d['masses']['motors'],places=5)
    def test_iron_strength_and_front_pull(self):
        c=json.loads((P/'search_results/iron_hardware_audit.json').read_text())['parameters']
        c.update(front_pulling=True,hardware_audit_enabled=True,payload_working_allowable_Pa=70e6)
        r,a,m,q=evaluate(c)
        self.assertEqual(q['payload_buckling'],-1.)
        self.assertAlmostEqual(q['payload_end_load']+1,c['payload_density']*c['payload_length']*max(a['acceleration_m_s2'])/70e6)
        self.assertLess(q['payload_contact_pressure'],0.)
    def test_solar_budget_and_new_thickness_reference(self):
        d=json.loads((P/'search_results/iron_reference.json').read_text());c=d['parameters']
        r,a,m,q=evaluate(c)
        self.assertLessEqual(max(q.values()),1e-6)
        self.assertAlmostEqual(m['solar_array'],r['electrical_mean_W']*1.2/100.)
        self.assertAlmostEqual(sum(m.values()),r['conditional_machine_mass_kg'])
        self.assertGreater(c['payload_depth'],.0001*2)
        self.assertLess(c['payload_depth'],.005)
        self.assertEqual(c['maximum_occupancy'],1.)
        self.assertIsNone(c['maximum_feed_frequency_Hz'])
        self.assertEqual(q['feed_frequency'],-1.)
if __name__=='__main__':unittest.main()
