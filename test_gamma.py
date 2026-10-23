import unittest
from pricing import greeks
from gamma_hedge import positions,simulate
from hedging import path
class GammaTests(unittest.TestCase):
 def test_neutrality(self):
  g=greeks(100,100,.25,.02,.25);h=greeks(100,100,.4,.02,.25);s,q=positions(g,h,'delta_gamma');self.assertAlmostEqual(g['delta']+s+q*h['delta'],0);self.assertAlmostEqual(g['gamma']+q*h['gamma'],0)
 def test_self_financing(self):
  for x in simulate(path(8))['ledger']:self.assertAlmostEqual(x['pre_wealth']-x['fee'],x['post_wealth'],places=9)
 def test_cost_direction(self):self.assertLess(simulate(path(9))['terminal_pnl'],simulate(path(9),stock_bps=0,option_bps=0)['terminal_pnl'])
 def test_liquidation(self):
  r=simulate(path(11))['ledger'][-1];self.assertEqual(r['stock'],0);self.assertEqual(r['hedge_options'],0)
 def test_gamma_cap(self):
  s,q=positions({'delta':1,'gamma':100},{'delta':.1,'gamma':.01},'delta_gamma');self.assertEqual(q,-5)
 def test_invalid(self):
  with self.assertRaises(ValueError):simulate([100,-1,102])
if __name__=='__main__':unittest.main()
