import copy
import math
import unittest
from core import analyse, DEMO

class LoadFlowTests(unittest.TestCase):
    def test_no_load_is_flat(self):
        d=copy.deepcopy(DEMO);d['load_scale']=0
        r=analyse(d)['scenario']
        self.assertEqual(r['active_loss_pu'],0)
        self.assertTrue(all(b['voltage_pu']==1 for b in r['buses']))

    def test_two_bus_matches_analytic_high_voltage_root(self):
        # Real constant-power two-bus case: V² - V + R*P = 0.
        d={'buses':[{'id':'B','parent':'SOURCE','r':.1,'x':0,'p':.5,'q':0}]}
        r=analyse(d)['scenario'];expected=(1+math.sqrt(1-4*.1*.5))/2
        self.assertAlmostEqual(r['min_voltage_pu'],expected,places=6)

    def test_power_balance(self):
        r=analyse(DEMO)['scenario']
        self.assertAlmostEqual(r['source_p_pu'],sum(b['p'] for b in DEMO['buses'])+r['active_loss_pu'],places=7)
        self.assertAlmostEqual(r['source_q_pu'],sum(b['q'] for b in DEMO['buses'])+r['reactive_loss_pu'],places=7)

    def test_reactive_support_changes_result_and_balance(self):
        d=copy.deepcopy(DEMO);d['q_support']=.15
        r=analyse(d)
        self.assertGreater(r['scenario']['min_voltage_pu'],r['baseline']['min_voltage_pu'])
        s=r['scenario'];self.assertAlmostEqual(s['source_q_pu'],sum(b['q'] for b in d['buses'])-.15+s['reactive_loss_pu'],places=7)

    def test_unsorted_branches_work(self):
        d=copy.deepcopy(DEMO);d['buses'].reverse()
        self.assertEqual(analyse(d)['scenario'],analyse(DEMO)['scenario'])

    def test_cycle_rejected(self):
        d=copy.deepcopy(DEMO);d['buses'][0]['parent']='B4'
        with self.assertRaisesRegex(ValueError,'cycle'):analyse(d)

    def test_duplicate_rejected(self):
        d=copy.deepcopy(DEMO);d['buses'][1]['id']='B1'
        with self.assertRaises(ValueError):analyse(d)

    def test_nonfinite_rejected(self):
        d=copy.deepcopy(DEMO);d['load_scale']=float('nan')
        with self.assertRaises(ValueError):analyse(d)

    def test_high_load_no_false_convergence(self):
        d={'buses':[{'id':'B','parent':'SOURCE','r':1,'x':0,'p':1,'q':0}]}
        with self.assertRaises(ValueError):analyse(d)

if __name__=='__main__':unittest.main()
