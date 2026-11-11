"""Chronological scenarios through both backends; no real-bank qualification."""
import unittest,copy
from datetime import date,timedelta
import test_corporate_ledger_integration as base
from app.services.cash_windows_contract import validate
class WindowsHTTP(unittest.TestCase):
 login=base.DualLedgerIntegration.login
 setUp=base.DualLedgerIntegration.setUp
 tearDown=base.DualLedgerIntegration.tearDown
 command=base.DualLedgerIntegration.command
 def payload(self):
  windows=[]
  for offset in [0,7]:
   start=date(2024,1,1)+timedelta(days=offset);rows=lambda begin,n:[{'date':(begin+timedelta(days=i)).isoformat(),'net_cash_flow':'1.00'} for i in range(n)]
   windows.append({'scenario':{'opening_cash':'10.00','observations':rows(start,7),'seed':42,'paths':100},'actuals':rows(start+timedelta(days=7),365)})
  return {'windows':windows}
 def test_scoped_windows_zero_error_and_no_financial_authority(self):
  p=self.payload();r=self.command('backtest_cash_windows',p);self.assertEqual(r.status_code,200,r.text);data=r.json()['data'];self.assertTrue(data['overlapping_holdouts']);self.assertTrue(all(row['mean_absolute_terminal_error']=='0.00' for row in data['summary']));self.assertFalse(data['financial_execution']);self.assertFalse(data['production_qualified']);validate(data,p,{'tenant_id':data['tenant_id']})
  for change in ['summary','private','execution','median','probability','realized_path','window_average','outcome_digest','input_digest']:
   bad=copy.deepcopy(data)
   if change=='summary':bad['summary'][0]['mean_absolute_terminal_error']='1.00'
   if change=='private':bad['windows'][0]['forecast']['private_bank_password']='secret'
   if change=='execution':bad['financial_execution']=True
   if change=='median':bad['windows'][0]['evaluations'][0]['predicted_ending_cash_p50']='999.00'
   if change=='probability':bad['windows'][0]['forecast']['results'][0]['negative_cash_path_fraction']='0.500000'
   if change=='realized_path':bad['windows'][0]['evaluations'][0]['realized_path_ever_negative']=True
   if change=='window_average':bad['windows'][0]['mean_absolute_terminal_error_across_horizons']='999.00'
   if change=='outcome_digest':bad['windows'][0]['outcome_digest']='0'*64
   if change=='input_digest':bad['windows'][0]['forecast']['input_digest']='0'*64
   with self.assertRaises(ValueError):validate(bad,p,{'tenant_id':data['tenant_id']})
 def test_outcomes_do_not_leak_into_training_forecast(self):
  p=self.payload();first=self.command('backtest_cash_windows',p);self.assertEqual(first.status_code,200,first.text);p['windows'][1]['actuals'][0]['net_cash_flow']='-50.00';second=self.command('backtest_cash_windows',p);self.assertEqual(second.status_code,200,second.text);self.assertEqual([w['forecast'] for w in first.json()['data']['windows']],[w['forecast'] for w in second.json()['data']['windows']])
 def test_analytical_limit_does_not_relax_financial_routes(self):
  url='/api/v1/workspace/corporate/accounting/commands/'
  self.assertEqual(self.client.post(url+'apply_opening',content=b' '*8193,headers={'Content-Type':'application/json'}).status_code,413)
  self.assertEqual(self.client.post(url+'backtest_cash_windows',content=b' '*262145,headers={'Content-Type':'application/json'}).status_code,413)
  self.assertEqual(self.client.post(url+'backtest_cash_windows',content=b'{"windows":[],"windows":[]}',headers={'Content-Type':'application/json'}).status_code,422)
if __name__=='__main__':unittest.main()
