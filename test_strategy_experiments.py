import unittest
import numpy as np
from strategy_experiments import fan_weights,stress

class StrategyTests(unittest.TestCase):
    def setUp(self):self.prices=100*np.exp(np.cumsum(np.random.default_rng(3).normal(0,.01,(200,2)),axis=0))
    def test_causal(self):
        changed=self.prices.copy();changed[100:]*=2;np.testing.assert_array_equal(fan_weights(self.prices)[:102],fan_weights(changed)[:102])
    def test_scale_invariant(self):np.testing.assert_allclose(fan_weights(self.prices),fan_weights(self.prices*10))
    def test_no_leverage(self):self.assertTrue((fan_weights(self.prices).sum(axis=1)<=1).all())
    def test_no_change_revaluation(self):
        row=next(r for r in stress() if r['spot_change']==r['vol_change']==0);self.assertAlmostEqual(row['exact_pnl'],0);self.assertAlmostEqual(row['residual'],0)
    def test_volatility_monotonicity(self):
        rows=[r for r in stress() if r['spot_change']==0];self.assertEqual(sorted(r['exact_pnl'] for r in rows),[r['exact_pnl'] for r in rows])
    def test_invalid_slope(self):
        with self.assertRaises(ValueError):fan_weights(self.prices,slope=0)

if __name__=='__main__':unittest.main()
