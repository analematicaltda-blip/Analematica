"""Reproducible scenario arithmetic and backtesting, not real-bank calibration."""
import runpy,unittest,copy
from pathlib import Path
from decimal import localcontext,ROUND_DOWN,Inexact,Rounded
f=runpy.run_path(str(Path(__file__).with_name('accounting_simulation_check.py')),run_name='acc017_fixture');engine=f['engine']
class ExactScenarioChecks(unittest.TestCase):
 def setUp(self):
  cls=next(value for value in f.values() if isinstance(value,type) and issubclass(value,unittest.TestCase));self.base=cls();self.base.setUp()
 def test_simulation_independent_of_decimal_precision_and_traps(self):
  data=copy.deepcopy(self.base.data);data['opening_cash']='123456789.12';data['observations'][0]['net_cash_flow']='-12345.67';expected=engine.simulate(data)
  with localcontext() as ctx:
   ctx.prec=2;ctx.rounding=ROUND_DOWN;ctx.traps[Inexact]=True;ctx.traps[Rounded]=True;actual=engine.simulate(data);self.assertEqual(ctx.prec,2)
  self.assertEqual(actual,expected)
 def test_backtest_windows_independent_of_decimal_context(self):
  p={'windows':[self.base.window(),self.base.window(7,'-1.00')]};expected=engine.backtest_windows(p)
  with localcontext() as ctx:
   ctx.prec=2;ctx.traps[Inexact]=True;ctx.traps[Rounded]=True;self.assertEqual(engine.backtest_windows(p),expected)
 def test_sensitivity_independent_of_decimal_context(self):
  p={'scenario':copy.deepcopy(self.base.data),'shocks':[{'name':'declared','opening_cash_delta':'12345.67','daily_net_flow_delta':'-0.37'}]};expected=engine.sensitivity(p)
  with localcontext() as ctx:
   ctx.prec=2;ctx.traps[Inexact]=True;ctx.traps[Rounded]=True;self.assertEqual(engine.sensitivity(p),expected)
 def test_four_windows_return_three_descriptive_horizons(self):
  result=engine.backtest_windows({'windows':[self.base.window(i*7) for i in range(4)]});self.assertEqual(len(result['windows']),4);self.assertEqual([r['days'] for r in result['summary']],[30,90,365]);self.assertTrue(all(r['windows']==4 for r in result['summary']))
if __name__=='__main__':unittest.main(verbosity=2)
