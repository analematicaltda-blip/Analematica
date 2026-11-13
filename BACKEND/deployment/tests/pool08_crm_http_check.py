"""Real HTTP across all CRM backends and the native Analematica gateway."""
import runpy,unittest,uuid
from pathlib import Path
fixture=runpy.run_path(str(Path(__file__).with_name('pool08_native_http_check.py')),run_name='crm_http_setup')
base=fixture['NativeCommercialChecks']
class CRMHTTPChecks(unittest.TestCase):
 setUpClass=classmethod(base.setUpClass.__func__)
 tearDownClass=classmethod(base.tearDownClass.__func__)
 targets=base.targets
 prefix=base.prefix
 unwrap=base.unwrap
 def test_all_backends_and_gateway_complete_crm(self):
  for system,client,query,prefix in self.targets():
   suffix='' if system=='sga-cd' else '/'
   if system!='sga-cd':
    options=self.unwrap(client.get(prefix+'crm/companies/'));self.assertTrue(options['companies'])
   ctx=self.unwrap(client.get(prefix+'crm/context'+suffix,params=query))
   command=dict(request_id=str(uuid.uuid4()),operation='create',expected_revision=0,contact_id=None,data=dict(name='HTTP CRM',email=uuid.uuid4().hex+'@example.test',origin='HTTP_TEST',responsible_ref=ctx['actor_ref']))
   url=prefix+'crm/commands'+suffix
   result=self.unwrap(client.post(url,params=query,json=command));cid=result['contact_id']
   self.assertTrue(self.unwrap(client.post(url,params=query,json=command))['replayed'])
   receipt=self.unwrap(client.get(prefix+'crm/receipts/'+command['request_id']+suffix,params=query));self.assertEqual(receipt['contact_id'],cid)
   convert=dict(request_id=str(uuid.uuid4()),operation='convert',contact_id=cid,expected_revision=1,data={})
   result=self.unwrap(client.post(url,params=query,json=convert));self.assertEqual(result['status'],'CUSTOMER');self.assertTrue(result['customer_ref'])
   item=self.unwrap(client.get(prefix+'crm/contacts/'+cid+suffix,params=query));self.assertEqual(item['revision'],2)
   self.assertEqual(len(self.unwrap(client.get(prefix+'crm/contacts/'+cid+'/history'+suffix,params=query))['events']),2)
 def test_authentication_context_and_unsupported_methods(self):
  for system,client,query,prefix in self.targets():
   suffix='' if system=='sga-cd' else '/';url=prefix+'crm/contacts'+suffix
   self.assertIn(client.get(url,params=query,headers={'Authorization':''}).status_code,(401,403))
   self.assertEqual(client.get(url,params={**query,'tenant_ref':'foreign'}).status_code,400)
   response=client.get(prefix+'crm/commands'+suffix,params=query);self.assertEqual(response.status_code,405)
   self.assertEqual(response.headers['cache-control'],'no-store')
 def test_real_http_errors_and_body_limits(self):
  for system,client,query,prefix in self.targets():
   suffix='' if system=='sga-cd' else '/';url=prefix+'crm/commands'+suffix
   for raw,status in [('{"a":1,"a":2}',400),(' '*17000,413)]:
    response=client.post(url,params=query,content=raw,headers={'Content-Type':'application/json'});self.assertEqual(response.status_code,status,response.text)
 def test_national_tourism_does_not_acquire_crm_enterprise_routes(self):
  client,credentials=self.servers['turismo']
  for prefix in ['/api/v1/commercial-unified/','/api/v1/mi-negocio/comercial/unified/']:
   self.assertEqual(client.get(prefix+'crm/contacts/',params={'provider_id':credentials['provider_id']}).status_code,404)
if __name__=='__main__':raise SystemExit(not unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(CRMHTTPChecks)).wasSuccessful())
