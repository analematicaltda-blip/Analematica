"""Authenticated tool queries with actual shared ledger and tamper rejection."""
import unittest,copy
from decimal import localcontext,Inexact,Rounded
import test_corporate_ledger_integration as base
from app.services.accounting_query_contract import validate
class QueryHTTP(unittest.TestCase):
 login=base.DualLedgerIntegration.login
 setUp=base.DualLedgerIntegration.setUp
 tearDown=base.DualLedgerIntegration.tearDown
 command=base.DualLedgerIntegration.command
 def test_liquidity_matches_shared_ledger_and_has_no_execution_authority(self):
  p={'question':'¿Cuál es mi liquidez ácida?','until':self.day};r=self.command('query',p);self.assertEqual(r.status_code,200,r.text);data=r.json()['data'];self.assertEqual(data['data']['value'],'3.0000');self.assertEqual(data['source'],'ratios.quick_ratio');self.assertFalse(data['external_model_used']);validate(data,p,{'tenant_id':data['company_id']})
  bad=copy.deepcopy(data);bad['data']['value']='9.0000'
  with self.assertRaises(ValueError):validate(bad,p,{'tenant_id':data['company_id']})
 def test_profitability_sources_and_requested_dates_reconciled(self):
  p={'question':'rentabilidad','since':self.since,'until':self.until};r=self.command('query',p);self.assertEqual(r.status_code,200,r.text);data=r.json()['data'];context={'tenant_id':data['company_id']}
  with localcontext() as ctx:
   ctx.prec=2;ctx.traps[Inexact]=True;ctx.traps[Rounded]=True;validate(data,p,context)
  for change in ['profit','source_amount','private','dates','tool']:
   bad=copy.deepcopy(data)
   if change=='profit':bad['data']['net_profit']='999.00'
   if change=='source_amount':bad['data']['sources'][0]['net_amount']='999.00'
   if change=='private':bad['data']['private_bank_password']='private'
   if change=='dates':bad['data']['start_date']='2000-01-01'
   if change=='tool':bad['intent']='commercial_queue'
   with self.assertRaises(ValueError):validate(bad,p,context)
 def test_queue_cannot_claim_fiscal_acceptance(self):
  p={'question':'estado de la cola comercial'};r=self.command('query',p);self.assertEqual(r.status_code,200,r.text);data=r.json()['data'];context={'tenant_id':data['company_id']};validate(data,p,context)
  for field,value in [('fiscal_acceptance','ACCEPTED'),('fiscal_receipt_verified',True),('published_by_this_call',True)]:
   bad=copy.deepcopy(data);bad['data'][field]=value
   with self.assertRaises(ValueError):validate(bad,p,context)
 def test_arbitrary_sql_tenant_override_and_session_revocation_denied(self):
  for p in [{'question':'liquidez; DROP TABLE users','until':self.day},{'question':'liquidez','until':self.day,'tenant_id':'foreign'}]:self.assertIn(self.command('query',p).status_code,[400,409,422])
  session=self.unwrap(self.erp.get('/api/v1/erp-session/').json());self.erp.post('/api/v1/erp-session/logout/',headers={'X-CSRFToken':session['csrf_token']},json={});self.assertEqual(self.command('query',{'question':'liquidez','until':self.day}).status_code,403)
if __name__=='__main__':unittest.main()
