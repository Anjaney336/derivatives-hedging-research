import unittest, math
from greek_audit import audit_rows,all_in,paired_ci
from gamma_hedge import simulate
from hedging import path

class GreekAuditTests(unittest.TestCase):
    def test_call_put_grid(self):
        rows=audit_rows()
        self.assertEqual(len(rows),360)
        for row in rows:
            with self.subTest(row=row):self.assertLess(row['scaled_error'],2e-4)
    def test_zero_entry_fee_matches_original(self):
        p=path(11)
        self.assertEqual(all_in(p,'delta',0)['pnl'],simulate(p,'delta')['terminal_pnl'])
    def test_entry_cost_financing_bridge(self):
        p=path(12);a=all_in(p,'delta_gamma');b=simulate(p,'delta_gamma')
        self.assertAlmostEqual(b['terminal_pnl']-a['pnl'],a['target_entry_fee']+a['target_fee_financing'])
        self.assertGreater(a['target_fee_financing'],0)
    def test_identical_policy_interval_zero(self):self.assertEqual(paired_ci([1,2,3],[1,2,3]),[0,0])
    def test_invalid_cost(self):
        for fee in [-1,float('nan')]:
            with self.assertRaises(ValueError):all_in(path(1),'delta',fee)
