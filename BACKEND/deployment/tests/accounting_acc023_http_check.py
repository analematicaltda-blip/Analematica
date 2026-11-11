"""Benchmark validates synthetic response authority before counting success."""
import sys,unittest,copy
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from benchmark_accounting_http import validate_reply,run
class HTTPBenchmarkChecks(unittest.TestCase):
 def test_bounds_reject_before_starting_fixture(self):
  for samples,clients in [(True,1),(4,1),(101,1),(5,True),(5,0),(5,9),(5,6)]:
   with self.assertRaises(ValueError):run(samples,clients)
 def test_scoped_trial_balance_must_match_expected_book(self):
  body={'company_id':'fixture','data':{'tenant_id':'fixture','currency':'COP','snapshot':{'database':'primary'},'total_debit':'15.00','total_credit':'15.00'}};validate_reply('trial_balance',body,'fixture','2026-11-11')
  for field,value in [('tenant_id','other'),('currency','USD'),('total_credit','99.00')]:
   bad=copy.deepcopy(body);bad['data'][field]=value
   with self.assertRaises(ValueError):validate_reply('trial_balance',bad,'fixture','2026-11-11')
 def test_queue_acceptance_or_financial_authority_cannot_count_as_success(self):
  data={'schema':'sgacd-accounting-query-v1','company_id':'fixture','read_only':True,'generated_sql':False,'external_model_used':False,'ledger_written':False,'financial_action_authorized':False,'intent':'commercial_queue','data':{'fiscal_acceptance':'NOT_VERIFIED','fiscal_receipt_verified':False}};body={'company_id':'fixture','data':data};validate_reply('commercial_queue',body,'fixture','2026-11-11')
  data['data']['fiscal_acceptance']='ACCEPTED'
  with self.assertRaises(ValueError):validate_reply('commercial_queue',body,'fixture','2026-11-11')
  data['data']['fiscal_acceptance']='NOT_VERIFIED';data['financial_action_authorized']=True
  with self.assertRaises(ValueError):validate_reply('commercial_queue',body,'fixture','2026-11-11')
 def test_malformed_body_never_counts_as_success(self):
  for body in [None,[],{}, {'company_id':'other','data':{}}]:
   with self.assertRaises(ValueError):validate_reply('trial_balance',body,'fixture','2026-11-11')
if __name__=='__main__':unittest.main(verbosity=2)
