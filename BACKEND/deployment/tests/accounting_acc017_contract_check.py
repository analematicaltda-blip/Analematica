"""Untrusted analytical responses must reconcile with requested held-out data."""
import copy, importlib.util, runpy, unittest
from decimal import localcontext,Inexact,Rounded
from pathlib import Path
root=Path(__file__).resolve().parents[3]
f=runpy.run_path(str(Path(__file__).with_name('accounting_simulation_check.py')),run_name='scenario_fixture')
spec=importlib.util.spec_from_file_location('scenario_contract',root/'BACKEND/SGA-CD-BACKEND/app/services/cash_windows_contract.py');contract=importlib.util.module_from_spec(spec);spec.loader.exec_module(contract)
class ResponseChecks(unittest.TestCase):
 def setUp(self):
  cls=next(v for v in f.values() if isinstance(v,type) and issubclass(v,unittest.TestCase));base=cls();base.setUp()
  self.payload={'windows':[base.window(),base.window(7)]};self.data=f['engine'].backtest_windows(self.payload);self.data.update(tenant_id='test-company',currency='COP');self.context={'tenant_id':'test-company'}
 def test_valid_response(self):contract.validate(self.data,self.payload,self.context)
 def test_false_negative_cash_probability_rejected(self):
  data=copy.deepcopy(self.data);row=data['windows'][0]['forecast']['results'][0];row['negative_cash_path_fraction']='0.500000';data['windows'][0]['evaluations'][0]['scenario_negative_cash_fraction']='0.500000'
  with self.assertRaises(ValueError):contract.validate(data,self.payload,self.context)
 def test_altered_realized_path_rejected(self):
  data=copy.deepcopy(self.data);data['windows'][0]['evaluations'][0]['realized_path_ever_negative']=not data['windows'][0]['evaluations'][0]['realized_path_ever_negative']
  with self.assertRaises(ValueError):contract.validate(data,self.payload,self.context)
 def test_altered_original_outcome_rejected(self):
  payload=copy.deepcopy(self.payload);payload['windows'][0]['actuals'][0]['net_cash_flow']='999.00'
  with self.assertRaises(ValueError):contract.validate(self.data,payload,self.context)
 def test_altered_training_values_rejected(self):
  payload=copy.deepcopy(self.payload);payload['windows'][0]['scenario']['observations'][0]['net_cash_flow']='999.00'
  with self.assertRaises(ValueError):contract.validate(self.data,payload,self.context)
 def test_valid_integer_input_and_canonical_money_response(self):
  payload=copy.deepcopy(self.payload);payload['windows'][0]['scenario']['opening_cash']=10;payload['windows'][0]['actuals'][0]['net_cash_flow']=1
  data=f['engine'].backtest_windows(payload);data.update(tenant_id='test-company',currency='COP');contract.validate(data,payload,self.context)
 def test_validation_independent_of_callers_decimal_context(self):
  with localcontext() as ctx:
   ctx.prec=2;ctx.traps[Inexact]=True;ctx.traps[Rounded]=True
   contract.validate(self.data,self.payload,self.context);self.assertEqual(ctx.prec,2)
 def test_ever_negative_path_count_cannot_decrease_with_horizon(self):
  data=copy.deepcopy(self.data);data['windows'][0]['forecast']['results'][0].update(paths_with_negative_cash=1,negative_cash_path_fraction='0.010000');data['windows'][0]['evaluations'][0]['scenario_negative_cash_fraction']='0.010000'
  with self.assertRaises(ValueError):contract.validate(data,self.payload,self.context)
 def test_false_window_error_average_rejected(self):
  data=copy.deepcopy(self.data);data['windows'][0]['mean_absolute_terminal_error_across_horizons']='999.00'
  with self.assertRaises(ValueError):contract.validate(data,self.payload,self.context)
if __name__=='__main__':unittest.main(verbosity=2)
