import unittest,json
from pathlib import Path
import numpy as np
from geometry import geometry
from kinematics import evaluate
from structure import cable_mass

class PhysicsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.c=json.loads(Path(__file__).with_name('config.json').read_text())
        cls.k,cls.st=evaluate(cls.c)
    def test_hub_tangency(self):
        for ratio in [.1,.25,.8]:
            O,P,Q,H=geometry(2,2*ratio)
            self.assertAlmostEqual(np.dot(H,P-H),0,places=13)
            self.assertAlmostEqual(np.linalg.norm(H),2*ratio)
            self.assertAlmostEqual(np.linalg.norm(P-H),np.sqrt(4-(2*ratio)**2))
    def test_torque_and_components(self):
        O,P,Q,H=geometry(.1,.025)
        direction=(H-P)/np.linalg.norm(H-P)
        self.assertAlmostEqual(direction[1],.25)
        self.assertLess(direction[0],0)
        self.assertAlmostEqual(P[0]*direction[1],.025)
    def test_kinetic_energy(self):
        self.assertLess(abs(self.k['energy_error_fraction']),1e-10)
    def test_baseline(self):
        self.assertAlmostEqual(self.k['mass_flow_kg_s'],317.0979198,places=6)
        self.assertAlmostEqual(self.k['payload_mass_kg'],7.2)
        self.assertAlmostEqual(self.k['ideal_power_W']/1e6,404.2998478,places=5)
        self.assertTrue(3.7e6<self.k['slip_heat_W']<4.4e6)
        self.assertAlmostEqual(self.k['contact_peak_force_pair_N'],14121.576,places=5)
    def test_forward_slip_and_recharge(self):
        self.assertGreaterEqual(self.k['minimum_slip_m_s'],0)
        self.assertTrue(np.all(self.st['recharge_interval_s']>0))
    def test_independent_pitch_keeps_flow_and_energy(self):
        c=self.c.copy();c['pitch']=.30
        k,_=evaluate(c)
        self.assertAlmostEqual(k['mass_flow_kg_s'],self.k['mass_flow_kg_s'])
        self.assertAlmostEqual(k['ideal_power_W'],self.k['ideal_power_W'])
        self.assertLess(k['installed_pairs'],self.k['installed_pairs'])
        self.assertGreater(k['contact_peak_force_pair_N'],self.k['contact_peak_force_pair_N'])
        self.assertLess(abs(k['energy_error_fraction']),1e-10)
    def test_wide_pitch_rejects_uncovered_intervals(self):
        c=self.c.copy();c['pitch']=1.10
        with self.assertRaisesRegex(ValueError,'Unsupported rod'):
            evaluate(c)
    def test_constant_force_slip_identity(self):
        F,a,vi,vf=1000,100,20,40
        v=np.linspace(vi,vf,10001)
        integrated=np.trapezoid(F*(vf-v),v/a)
        self.assertAlmostEqual(integrated,F/(2*a)*(vf-vi)**2)
    def test_force_work_with_partial_contacts(self):
        c=self.c.copy();c.update(payload_length=.93,contact_patch=.031)
        k,st=evaluate(c)
        self.assertLess(abs(k['energy_error_fraction']),1e-10)
    def test_taper_self_load(self):
        m,ar,at=cable_mass(np.array([1000.]),np.array([1.,0]),np.array([.25,0]),np.array([100.]),1500,1e9)
        self.assertGreater(ar[0],at[0]);self.assertGreater(m[0],1500*.75*at[0])
    def test_spatial_convergence(self):
        c=self.c.copy();c['integration_steps_per_pitch']=60
        k,_=evaluate(c)
        self.assertLess(abs(k['slip_heat_W']/self.k['slip_heat_W']-1),.001)
    def test_occupancy_changes_with_payload_section(self):
        c=self.c.copy();c['payload_depth']/=4
        k,_=evaluate(c)
        self.assertGreater(k['entry_occupancy'],1)
if __name__=='__main__':unittest.main()
