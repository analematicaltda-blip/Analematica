"""Both authenticated backends: ledger liquidity with scoped read-only sources."""
import unittest,copy
import test_corporate_ledger_integration as integration
from app.services.quick_ratio_contract import validate
class RatioHTTP(unittest.TestCase):
 login=integration.DualLedgerIntegration.login
 setUp=integration.DualLedgerIntegration.setUp
 tearDown=integration.DualLedgerIntegration.tearDown
 command=integration.DualLedgerIntegration.command
 def direct(self):return self.unwrap(self.erp.get(integration.bridge.BASE+'liquidez-acida/',params={'provider_id':self.provider,'fecha_corte':self.day}).json())
 def request(self):return self.client.get('/api/v1/workspace/corporate/accounting/report',params={'report':'quick_ratio','until':self.day})
 def test_corporate_ratio_matches_primary_erp(self):
  direct=self.direct();r=self.request();self.assertEqual(r.status_code,200,r.text);self.assertEqual(r.json()['data'],direct);self.assertEqual(direct['unit'],'times');self.assertEqual(direct['value'],'3.0000');self.assertFalse(r.json()['ledger_written'])
 def test_contract_rejects_arithmetic_and_private_fields(self):
  direct=self.direct();args={'company_id':direct['tenant_id'],'cutoff':self.day};validate(direct,**args)
  for path in ['value','total','private','snapshot','source']:
   data=copy.deepcopy(direct)
   if path=='value':data['value']='999.0000'
   if path=='total':data['totals']['cash_equivalents']='999.00'
   if path=='private':data['private_bank_password']='private'
   if path=='snapshot':data['snapshot']['historical_publication_snapshot']=True
   if path=='source':data['sources']['cash_equivalents'][0]['balance']='99.00'
   with self.assertRaises(ValueError):validate(data,**args)
 def test_zero_denominator_is_unavailable_in_corporate_report(self):
  from datetime import date,timedelta
  prior=(date.fromisoformat(self.day)-timedelta(days=1)).isoformat();r=self.client.get('/api/v1/workspace/corporate/accounting/report',params={'report':'quick_ratio','until':prior});self.assertEqual(r.status_code,200,r.text);data=r.json()['data'];self.assertIsNone(data['value']);self.assertEqual(data['unavailable_reason'],'NON_POSITIVE_CURRENT_LIABILITIES');self.assertEqual(data['cutoff_date'],prior)
 def test_erp_session_revocation_rejects_ratio(self):
  session=self.unwrap(self.erp.get('/api/v1/erp-session/').json());self.erp.post('/api/v1/erp-session/logout/',headers={'X-CSRFToken':session['csrf_token']},json={});self.assertEqual(self.request().status_code,403)
if __name__=='__main__':unittest.main()
