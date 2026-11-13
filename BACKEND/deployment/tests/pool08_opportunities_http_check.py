"""Real loopback HTTP opportunity flows in SGA, ERP, Analematica and its gateway."""
import runpy,unittest,uuid
from pathlib import Path
fixture=runpy.run_path(str(Path(__file__).with_name('pool08_crm_http_check.py')),run_name='opportunity_http_fixture')
base=fixture['CRMHTTPChecks']
class OpportunityHTTP(unittest.TestCase):
 setUpClass=classmethod(base.setUpClass.__func__)
 tearDownClass=classmethod(base.tearDownClass.__func__)
 targets=base.targets
 prefix=base.prefix
 unwrap=base.unwrap
 def test_all_four_http_paths_complete_stages_without_financial_effect(self):
  for system,client,query,prefix in self.targets():
   suffix='' if system=='sga-cd' else '/'
   ctx=self.unwrap(client.get(prefix+'crm/context'+suffix,params=query))
   body=dict(request_id=str(uuid.uuid4()),operation='create',contact_id=None,expected_revision=0,data=dict(name='Contacto HTTP embudo',email=uuid.uuid4().hex+'@example.test',origin='HTTP_TEST',responsible_ref=ctx['actor_ref']))
   contact=self.unwrap(client.post(prefix+'crm/commands'+suffix,params=query,json=body))['contact_id']
   command=dict(request_id=str(uuid.uuid4()),operation='create',opportunity_id=None,expected_revision=0,data=dict(title='Oportunidad HTTP',contact_id=contact,value='1900000.25',currency='COP',responsible_ref=ctx['actor_ref']))
   url=prefix+'crm/opportunity-commands'+suffix
   first=self.unwrap(client.post(url,params=query,json=command));ref=first['opportunity_id'];self.assertTrue(self.unwrap(client.post(url,params=query,json=command))['replayed'])
   receipt=self.unwrap(client.get(prefix+'crm/opportunity-receipts/'+command['request_id']+suffix,params=query));self.assertEqual(receipt['opportunity_id'],ref)
   for revision,stage in enumerate(('CONTACTED','QUALIFIED','PROPOSAL','NEGOTIATION','WON'),1):
    data={'stage':stage,'reason':'Revisión documentada'}
    if stage=='WON':data.update(confirmation=True,evidence_digest='a'*64)
    body=dict(request_id=str(uuid.uuid4()),operation='transition',opportunity_id=ref,expected_revision=revision,data=data)
    result=self.unwrap(client.post(url,params=query,json=body));self.assertEqual(result['stage'],stage)
    for key in ('payment_verified','invoice_issued','ledger_written','revenue_recognized'):self.assertFalse(result[key])
   record=self.unwrap(client.get(prefix+'crm/opportunities/'+ref+suffix,params=query));self.assertEqual(record['stage'],'WON');self.assertEqual(record['score']['status'],'NOT_CALIBRATED');self.assertIsNone(record['score']['probability'])
   history=self.unwrap(client.get(prefix+'crm/opportunities/'+ref+'/history'+suffix,params=query));self.assertTrue(history['history_verified'])
 def test_errors_are_private_and_strict_on_all_backends(self):
  for system,client,query,prefix in self.targets():
   suffix='' if system=='sga-cd' else '/';url=prefix+'crm/opportunity-commands'+suffix
   for raw,status in [(' '*17000,413),('{"a":1,"a":2}',400)]:
    r=client.post(url,params=query,content=raw,headers={'content-type':'application/json'});self.assertEqual(r.status_code,status,r.text);self.assertEqual(r.headers['cache-control'],'no-store')
   self.assertEqual(client.get(prefix+'crm/opportunities'+suffix,params={**query,'tenant_ref':'forged'}).status_code,400)
   self.assertIn(client.get(prefix+'crm/opportunities'+suffix,params=query,headers={'Authorization':''}).status_code,(401,403))
 def test_tourism_has_no_enterprise_pipeline(self):
  client,cred=self.servers['turismo']
  for prefix in ('/api/v1/commercial-unified/','/api/v1/mi-negocio/comercial/unified/'):
   self.assertEqual(client.get(prefix+'crm/opportunities/',params={'provider_id':cred['provider_id']}).status_code,404)
if __name__=='__main__':raise SystemExit(not unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(OpportunityHTTP)).wasSuccessful())
