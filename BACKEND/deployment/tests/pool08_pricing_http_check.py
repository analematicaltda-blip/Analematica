"""Actual HTTP catalog, server offer math and strict boundaries on all owned routes."""
import runpy,unittest,uuid
from pathlib import Path
from pool08_pricing_cases import PricingCases
fixture=runpy.run_path(str(Path(__file__).with_name('pool08_crm_http_check.py')),run_name='pricing_http_fixture');base=fixture['CRMHTTPChecks']
class PricingHTTP(unittest.TestCase):
 setUpClass=classmethod(base.setUpClass.__func__)
 tearDownClass=classmethod(base.tearDownClass.__func__)
 targets=base.targets
 prefix=base.prefix
 unwrap=base.unwrap
 def test_server_totals_replay_updates_and_history_all_paths(self):
  for system,client,query,prefix in self.targets():
   suffix='' if system=='sga-cd' else '/';url=prefix+'crm/price-commands'+suffix
   body=PricingCases.body(self,**PricingCases.values(self));first=self.unwrap(client.post(url,params=query,json=body));ref=first['item_id'];self.assertTrue(self.unwrap(client.post(url,params=query,json=body))['replayed'])
   body=PricingCases.offer(self,ref);result=self.unwrap(client.post(url,params=query,json=body));self.assertEqual(result['estimate']['total'],'26444.43');self.assertFalse(result['estimate']['payment_verified']);self.assertEqual(result['estimate']['price_source'],'OWNED_SERVER_CATALOG')
   receipt=self.unwrap(client.get(prefix+'crm/price-receipts/'+body['request_id']+suffix,params=query));self.assertEqual(result['estimate'],receipt['estimate'])
   change=PricingCases.body(self,'update',ref,1,unit_price='2.00');self.assertEqual(client.post(url,params=query,json=change).status_code,200)
   body=PricingCases.offer(self,ref);self.assertEqual(client.post(url,params=query,json=body).status_code,409)
   history=self.unwrap(client.get(prefix+'crm/prices/'+ref+'/history'+suffix,params=query));self.assertTrue(history['history_verified']);self.assertEqual(len(history['events']),2)
   self.assertEqual(self.unwrap(client.get(prefix+'crm/prices/'+ref+suffix,params=query))['unit_price'],'2.00')
 def test_private_strict_json_no_scope_forgery(self):
  for system,client,query,prefix in self.targets():
   suffix='' if system=='sga-cd' else '/';url=prefix+'crm/price-commands'+suffix
   for raw,status in [(' '*17000,413),('{"a":1,"a":2}',400)]:
    r=client.post(url,params=query,content=raw,headers={'content-type':'application/json'});self.assertEqual(r.status_code,status);self.assertEqual(r.headers['cache-control'],'no-store')
   self.assertEqual(client.get(prefix+'crm/prices'+suffix,params={**query,'tenant_ref':'forged'}).status_code,400);self.assertIn(client.get(prefix+'crm/prices'+suffix,params=query,headers={'Authorization':''}).status_code,(401,403))
 def test_tourism_has_no_company_price_catalog(self):
  client,cred=self.servers['turismo']
  for prefix in ('/api/v1/commercial-unified/','/api/v1/mi-negocio/comercial/unified/'):self.assertEqual(client.get(prefix+'crm/prices/',params={'provider_id':cred['provider_id']}).status_code,404)
PricingHTTP.body=PricingCases.body
if __name__=='__main__':raise SystemExit(not unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(PricingHTTP)).wasSuccessful())
