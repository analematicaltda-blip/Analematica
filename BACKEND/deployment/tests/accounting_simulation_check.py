"""Exact-money bounded Monte Carlo contracts; no database or external services."""
import copy,importlib.util,random,unittest
from pathlib import Path
path=Path(__file__).resolve().parents[2]/'ANALEMATICA-BACKEND/core_erp/intelligence/cash_simulation.py'
spec=importlib.util.spec_from_file_location('cash_simulation_contract',path);engine=importlib.util.module_from_spec(spec);spec.loader.exec_module(engine)
class CashSimulationTests(unittest.TestCase):
 def setUp(self):self.data={'opening_cash':'10.00','observations':[{'date':f'2026-01-{i:02}','net_cash_flow':'1.00'} for i in range(1,8)],'seed':42,'paths':100}
 def test_constant_flow_exact_all_horizons(self):
  result=engine.simulate(self.data)
  self.assertEqual([r['ending_cash_p50'] for r in result['results']],['40.00','100.00','375.00'])
  self.assertTrue(all(r['ending_cash_p05']==r['ending_cash_p95'] for r in result['results']))
 def test_reproducible_seed_digest_and_global_rng_untouched(self):
  self.data['observations'][0]['net_cash_flow']='-2.00'
  state=random.getstate();a=engine.simulate(self.data);b=engine.simulate(self.data)
  self.assertEqual(a,b);self.assertEqual(random.getstate(),state)
  changed=engine.simulate({**self.data,'seed':43});self.assertNotEqual(a['input_digest'],changed['input_digest'])
 def test_deficit_risk_is_pathwise_and_explicit(self):
  self.data['opening_cash']='0.00'
  for row in self.data['observations']:row['net_cash_flow']='-1.00'
  result=engine.simulate(self.data)
  self.assertEqual(result['results'][0]['ending_cash_p50'],'-30.00')
  self.assertTrue(all(r['negative_cash_path_fraction']=='1.000000' for r in result['results']))
  self.assertFalse(result['financial_execution']);self.assertFalse(result['ledger_written'])
 def test_money_rejects_float_nonfinite_and_fractional_cents(self):
  for value in [1.0,True,'NaN','Infinity','0.001','1000000000000.00','1e999999999','0.'+'0'*80]:
   with self.subTest(value=value),self.assertRaises(ValueError):engine.simulate({**self.data,'opening_cash':value})
 def test_bounds_reject_unbounded_work_and_boolean_seed(self):
  for changes in [{'seed':True},{'seed':-1},{'paths':99},{'paths':2001},{'paths':100.0}]:
   with self.assertRaises(ValueError):engine.simulate({**self.data,**changes})
 def test_dates_must_be_unique_ordered_and_daily(self):
  for value in ['2026-01-01','2026-01-20','invalid']:
   data=copy.deepcopy(self.data);data['observations'][1]['date']=value
   with self.assertRaises(ValueError):engine.simulate(data)
 def test_explicit_inputs_and_minimum_history(self):
  with self.assertRaises(ValueError):engine.simulate({**self.data,'observations':[]})
  with self.assertRaises(ValueError):engine.simulate({**self.data,'imagined_income':'10'})
 def test_future_horizon_date_overflow_rejected(self):
  self.data['observations']=[{'date':f'9999-12-{i}','net_cash_flow':'0.00'} for i in range(25,32)]
  with self.assertRaises(ValueError):engine.simulate(self.data)
 def test_percentiles_ordered_and_zero_cash_not_fabricated_profit(self):
  self.data['observations'][0]['net_cash_flow']='-20.00'
  for row in engine.simulate(self.data)['results']:
   from decimal import Decimal
   self.assertLessEqual(Decimal(row['ending_cash_p05']),Decimal(row['ending_cash_p50']))
   self.assertLessEqual(Decimal(row['ending_cash_p50']),Decimal(row['ending_cash_p95']))
 def held_out(self,flow='1.00'):
  from datetime import date,timedelta
  return [{'date':(date(2026,1,8)+timedelta(days=i)).isoformat(),'net_cash_flow':flow} for i in range(365)]
 def test_backtest_constant_series_has_zero_error(self):
  result=engine.backtest({'scenario':self.data,'actuals':self.held_out()})
  self.assertEqual(result['mean_absolute_terminal_error_across_horizons'],'0.00')
  self.assertTrue(all(r['empirical_interval_contains_actual'] for r in result['evaluations']))
 def test_future_outcomes_never_change_training_forecast(self):
  first=engine.backtest({'scenario':self.data,'actuals':self.held_out('1.00')})
  changed=engine.backtest({'scenario':self.data,'actuals':self.held_out('-1.00')})
  self.assertEqual(first['forecast'],changed['forecast'])
  self.assertNotEqual(first['outcome_digest'],changed['outcome_digest'])
  self.assertEqual(changed['evaluations'][0]['actual_minus_predicted'],'-60.00')
  self.assertTrue(changed['evaluations'][0]['realized_path_ever_negative'])
  self.assertFalse(changed['evaluations'][0]['empirical_interval_contains_actual'])
 def test_backtest_overlap_gap_and_incomplete_holdout_rejected(self):
  for rows in [self.held_out()[:-1],self.held_out()[1:]+[self.held_out()[-1]]]:
   with self.assertRaises(ValueError):engine.backtest({'scenario':self.data,'actuals':rows})
  rows=self.held_out();rows[0]['date']='2026-01-07'
  with self.assertRaises(ValueError):engine.backtest({'scenario':self.data,'actuals':rows})
 def test_backtest_rejects_nonexact_outcomes_and_extra_fields(self):
  rows=self.held_out();rows[0]['net_cash_flow']=1.5
  with self.assertRaises(ValueError):engine.backtest({'scenario':self.data,'actuals':rows})
  with self.assertRaises(ValueError):engine.backtest({'scenario':self.data,'actuals':self.held_out(),'tenant':'spoof'})

 def shock(self,opening='5.00',daily='-2.00'):
  return {'name':'Declared stress','opening_cash_delta':opening,'daily_net_flow_delta':daily}
 def test_sensitivity_exact_paired_deltas(self):
  result=engine.sensitivity({'scenario':self.data,'shocks':[self.shock()]})
  self.assertEqual([r['ending_cash_p50_delta'] for r in result['variants'][0]['changes_from_base']],['-55.00','-175.00','-725.00'])
  self.assertEqual(result['variants'][0]['simulation']['results'][0]['ending_cash_p50'],'-15.00')
 def test_sensitivity_common_draws_and_no_mutation(self):
  self.data['observations'][0]['net_cash_flow']='-4.00';before=copy.deepcopy(self.data)
  args={'scenario':self.data,'shocks':[self.shock('0.00','1.00')]}
  a=engine.sensitivity(args);self.assertEqual(a,engine.sensitivity(args));self.assertEqual(before,self.data)
  self.assertEqual([r['ending_cash_p50_delta'] for r in a['variants'][0]['changes_from_base']],['30.00','90.00','365.00'])
 def test_sensitivity_zero_shock_reproduces_base(self):
  result=engine.sensitivity({'scenario':self.data,'shocks':[self.shock('0.00','0.00')]})
  self.assertEqual(result['base'],result['variants'][0]['simulation'])
 def test_sensitivity_bounds_duplicate_names_and_invalid_money(self):
  for shocks in [[],[self.shock()]*5,[self.shock(),self.shock()],[self.shock(-11,'0.00')],[self.shock('0.00',1.0)]]:
   with self.assertRaises(ValueError):engine.sensitivity({'scenario':self.data,'shocks':shocks})

 def window(self,offset=0,flow='1.00'):
  from datetime import date,timedelta
  start=date(2026,1,1)+timedelta(days=offset)
  scenario={**self.data,'observations':[{'date':(start+timedelta(days=i)).isoformat(),'net_cash_flow':'1.00'} for i in range(7)]}
  return {'scenario':scenario,'actuals':[{'date':(start+timedelta(days=7+i)).isoformat(),'net_cash_flow':flow} for i in range(365)]}
 def test_multiple_windows_exact_summary_and_overlap_disclosed(self):
  result=engine.backtest_windows({'windows':[self.window(),self.window(7,'-1.00')]})
  self.assertTrue(result['overlapping_holdouts'])
  self.assertEqual(result['summary'][0]['mean_absolute_terminal_error'],'30.00')
  self.assertEqual(result['summary'][0]['interval_contains_actual_fraction'],'0.500000')
 def test_disjoint_windows_and_reproducibility(self):
  data={'windows':[self.window(),self.window(400)]}
  result=engine.backtest_windows(data)
  self.assertFalse(result['overlapping_holdouts']);self.assertEqual(result,engine.backtest_windows(data))
  self.assertTrue(all(row['mean_absolute_terminal_error']=='0.00' for row in result['summary']))
 def test_windows_must_be_bounded_distinct_and_ordered(self):
  for windows in [[self.window()],[self.window()]*5,[self.window(),self.window()],[self.window(7),self.window()]]:
   with self.assertRaises(ValueError):engine.backtest_windows({'windows':windows})
 def test_changing_window_outcomes_does_not_change_any_forecast(self):
  baseline=engine.backtest_windows({'windows':[self.window(),self.window(7)]})
  altered=engine.backtest_windows({'windows':[self.window(),self.window(7,'-1.00')]})
  self.assertEqual([row['forecast'] for row in baseline['windows']],[row['forecast'] for row in altered['windows']])
  self.assertNotEqual(baseline['summary'],altered['summary'])

if __name__=='__main__':unittest.main()
