"""Coalesced context preserves live identity/CSRF and propagates bounded backpressure."""
import os,unittest
from unittest.mock import patch
import httpx
from fastapi import HTTPException
import test_corporate_ledger_integration as integration
import test_corporate_ledger_financial_rehearsal as financial
import test_corporate_ledger_commercial_tax as tax
from app.services import corporate_ledger as ledger
class ThrottleChecks(unittest.TestCase):
 def test_retry_after_bounded_without_upstream_body_disclosure(self):
  for raw,expected in [('12','12'),('99999','3600'),('0','1'),('https://private.invalid','60'),('bad\r\nheader','60')]:
   with self.assertRaises(HTTPException) as raised:ledger.reject_upstream_throttle(httpx.Response(429,headers={'Retry-After':raw},json={'secret':'PRIVATE-UPSTREAM-BODY'}))
   self.assertEqual(raised.exception.status_code,429);self.assertEqual(raised.exception.headers['Retry-After'],expected);self.assertNotIn('PRIVATE',raised.exception.detail)
 def test_fetch_propagates_429_without_reading_or_retrying(self):
  calls=[]
  def handle(request):calls.append(request);return httpx.Response(429,headers={'Retry-After':'3'},json={'private':'not forwarded'})
  with httpx.Client(transport=httpx.MockTransport(handle)) as client:
   with self.assertRaises(HTTPException) as raised:ledger.fetch(client,'https://fixture.invalid/','a'*32,{})
  self.assertEqual(raised.exception.status_code,429);self.assertEqual(len(calls),1)
class CombinedContextTests(integration.DualLedgerIntegration):
 def setUp(self):
  self.mode=patch.dict(os.environ,{'CORPORATE_LEDGER_COMBINED_CONTEXT_ENABLED':'1'});self.mode.start();self.addCleanup(self.mode.stop);super().setUp()
 def test_combined_context_private_and_source_request_reduced(self):
  response=self.erp.get(ledger.BASE+'contexto-contable/',params={'provider_id':self.provider});self.assertEqual(response.status_code,200,response.text);body=self.unwrap(response.json());self.assertEqual(body['schema'],'sgacd-accounting-context-v1');self.assertTrue(body['authenticated']);self.assertEqual(len(body['csrf_token']),64);self.assertIn('no-store',response.headers['cache-control']);self.assertIn('Cookie',response.headers['vary'])
  paths=[];original=ledger.fetch
  def capture(client,url,*args,**kwargs):paths.append(url);return original(client,url,*args,**kwargs)
  with patch.object(ledger,'fetch',side_effect=capture):r=self.command('query',{'question':'liquidez','until':self.day})
  self.assertEqual(r.status_code,200,r.text);self.assertEqual(len(paths),1);self.assertTrue(paths[0].endswith('/contexto-contable/'))
 def test_combined_read_matches_legacy_and_reduces_roundtrips(self):
  params={'report':'trial_balance','until':self.day};url='/api/v1/workspace/corporate/accounting/report'
  with patch.dict(os.environ,{'CORPORATE_LEDGER_COMBINED_CONTEXT_ENABLED':'0'}):legacy=self.client.get(url,params=params)
  paths=[];original=ledger.fetch
  def capture(client,url,*args,**kwargs):paths.append(url);return original(client,url,*args,**kwargs)
  with patch.object(ledger,'fetch',side_effect=capture):combined=self.client.get(url,params=params)
  self.assertEqual(combined.status_code,200,combined.text);self.assertEqual(combined.json()['data'],legacy.json()['data']);self.assertEqual(len(paths),1);self.assertTrue(paths[0].endswith('/lectura-contable/'))
 def test_context_requires_web_session_and_unambiguous_company(self):
  r=self.erp.get(ledger.BASE+'contexto-contable/',params=[('provider_id',self.provider),('provider_id',self.provider)]);self.assertEqual(r.status_code,400)
  self.assertEqual(self.erp.get(ledger.BASE+'contexto-contable/',params={'provider_id':'00000000-0000-4000-8000-000000000000'}).status_code,403)
  session=self.unwrap(self.erp.get('/api/v1/erp-session/').json());self.erp.post('/api/v1/erp-session/logout/',headers={'X-CSRFToken':session['csrf_token']},json={});self.assertEqual(self.command('query',{'question':'liquidez','until':self.day}).status_code,403)
class CombinedFinancialTests(financial.CorporateFinancialRehearsalTests):
 def setUp(self):
  self.mode=patch.dict(os.environ,{'CORPORATE_LEDGER_COMBINED_CONTEXT_ENABLED':'1'});self.mode.start();self.addCleanup(self.mode.stop);super().setUp()
class CombinedTaxTests(tax.CorporateCommercialTaxChecks):
 def setUp(self):
  self.mode=patch.dict(os.environ,{'CORPORATE_LEDGER_COMBINED_CONTEXT_ENABLED':'1'});self.mode.start();self.addCleanup(self.mode.stop);super().setUp()
if __name__=='__main__':unittest.main()
