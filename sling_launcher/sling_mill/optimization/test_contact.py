import unittest,json,sys
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from contact import normal_force,indentation,compliance,screen
from registry import entries,BASE,CONTACT
from kinematics import evaluate
from structure import size

class ContactTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.c=json.loads((ROOT/'config_spaced.json').read_text());cls.a=CONTACT
        cls.k,cls.st=evaluate(cls.c)
        cls.b,extra,cls.mass=size(cls.c,cls.k,cls.st);cls.st.update(extra)
    def test_force_integral(self):
        C=compliance(self.a);delta=.0001;R=.1;W=.06;b=np.sqrt(2*R*delta)
        x=np.linspace(-b,b,10001)
        actual=W*np.trapezoid((delta-x*x/(2*R))/C,x)
        self.assertAlmostEqual(actual/normal_force(delta,R,W,C),1,places=7)
    def test_inverse(self):
        N=np.array([1,100,10000]);C=compliance(self.a)
        np.testing.assert_allclose(normal_force(indentation(N,.1,.06,C),.1,.06,C),N)
    def test_open_gap(self):
        self.assertEqual(normal_force(-1,.1,.06,compliance(self.a)),0)
    def test_width_scaling(self):
        C=compliance(self.a)
        self.assertAlmostEqual(indentation(2000,.1,.12,C),indentation(1000,.1,.06,C))
    def test_coating_mass_and_inertia(self):
        c=dict(self.c,coating_density=1400,coating_thickness=.0005)
        _,extra,mass=size(c,self.k,self.st)
        expected=2*len(self.st['position_m'])*2*np.pi*.1*.06*1400*.0005
        self.assertAlmostEqual(mass['contact_layers'],expected)
        self.assertTrue(np.all(extra['inertia_per_drum_kg_m2']>0))
    def test_peel_radius_scaling(self):
        _,one=screen(self.c,self.a,self.k,self.st)
        c=dict(self.c,radius=.2)
        _,two=screen(c,self.a,self.k,self.st)
        self.assertAlmostEqual(one['maximum_peel_Pa']/two['maximum_peel_Pa'],2)
    def test_wear_scales_with_coefficient(self):
        _,one=screen(self.c,self.a,self.k,self.st)
        _,two=screen(self.c,dict(self.a,wear_coefficient=self.a['wear_coefficient']*10),self.k,self.st)
        self.assertAlmostEqual(two['wear_mass_rate_kg_s']/one['wear_mass_rate_kg_s'],10)
        self.assertAlmostEqual(one['minimum_wear_life_hours']/two['minimum_wear_life_hours'],10)
    def test_registry_complete(self):
        rows=entries()
        self.assertEqual({r['name'] for r in rows if r['source']=='baseline'},set(BASE))
        self.assertEqual({r['name'] for r in rows if r['source']=='contact_assumptions'},set(CONTACT))
    def test_zero_layer_preserves_baseline(self):
        b,extra,mass=size(dict(self.c,coating_density=1400,coating_thickness=0),self.k,self.st)
        self.assertEqual(mass,self.mass)
        self.assertEqual(b['conditional_installed_mass_kg'],self.b['conditional_installed_mass_kg'])
if __name__=='__main__':unittest.main()
