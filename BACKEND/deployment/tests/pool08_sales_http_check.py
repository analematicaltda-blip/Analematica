"""Real loopback native HTTP and Analemática gateway; synthetic disposable records."""
import runpy,unittest,uuid,os
from pathlib import Path
from unittest.mock import patch
from pool08_pricing_cases import PricingCases
from pool08_quotation_cases import QuotationCases
fixture=runpy.run_path(str(Path(__file__).with_name('pool08_crm_http_check.py')),run_name='sales_http_fixture');base=fixture['CRMHTTPChecks']
class SalesHTTP(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  env=patch.dict(os.environ,{'COMMERCIAL_QUOTE_LINK_KEY':'synthetic-sales-http-link-key-at-least-32'});env.start();cls.addClassCleanup(env.stop);base.setUpClass.__func__(cls)
 tearDownClass=classmethod(base.tearDownClass.__func__)
 targets=base.targets;prefix=base.prefix;unwrap=base.unwrap
 def command(self,op='create',ref=None,rev=0,**data):return dict(request_id=str(uuid.uuid4()),operation=op,sale_id=ref,expected_revision=rev,data=data)
 def quote(self,system,client,query,prefix):
  suffix='' if system=='sga-cd' else '/';price=self.unwrap(client.post(prefix+'crm/price-commands'+suffix,params=query,json=PricingCases.body(self,**PricingCases.values(self))))['item_id'];ctx=self.unwrap(client.get(prefix+'crm/context'+suffix,params=query));self.contact=self.unwrap(client.post(prefix+'crm/commands'+suffix,params=query,json=dict(request_id=str(uuid.uuid4()),operation='create',contact_id=None,expected_revision=0,data=dict(name='Venta HTTP',origin='TEST',responsible_ref=ctx['actor_ref']))))['contact_id'];url=prefix+'crm/quotation-commands'+suffix
  self.unwrap(client.post(url,params=query,json=QuotationCases.body(self,'review_capacity',item_id=price,price_revision=1,mode='NOT_APPLICABLE',resource_ref=None,reason='Revisada',support_digest='a'*64)));ref=self.unwrap(client.post(url,params=query,json=QuotationCases.body(self,**QuotationCases.values(self,price))))['quotation_id'];self.unwrap(client.post(url,params=query,json=QuotationCases.body(self,'issue',ref,1)));link=self.unwrap(client.post(url,params=query,json=QuotationCases.body(self,'link',ref,2,confirm_share=True)));view=self.unwrap(client.get(prefix+'crm/quotations/'+ref+suffix,params=query));self.unwrap(client.post(prefix+'quote-links/'+ref+'/'+link['link_id']+suffix,headers={'Authorization':'','X-Quote-Token':link['link_token']},json=dict(request_id=str(uuid.uuid4()),version=view['version'],content_digest=view['content_digest'],confirmed=True)));return ref
 def test_native_and_gateway_post_replay_and_reversal(self):
  for system,client,query,prefix in self.targets():
   if system=='sga-cd':continue
   cred=self.servers[system][1];qid=self.quote(system,client,query,prefix);url=prefix+'crm/sale-commands/';ref=self.unwrap(client.post(url,params=query,json=self.command(quotation_id=qid)))['sale_id']
   terms=dict(economic_fact='SERVICE_DELIVERED',entry_date=cred['day'],accounts=cred['sale_accounts'],operation=dict(mode='NO_LABOR_REVIEWED',order_id=None,reason='Actividad sin personal declarada',support_digest='b'*64),documents=[dict(kind='DELIVERY_SUPPORT',reference='SYNTHETIC-HTTP',sha256='c'*64)],support_digest='d'*64,confirmed=True)
   self.unwrap(client.post(url,params=query,json=self.command('review',ref,1,**terms)));body=self.command('confirm',ref,2,confirmed=True);r=self.unwrap(client.post(url,params=query,json=body));self.assertEqual(r['status'],'CONFIRMED');self.assertTrue(r['journal']['posted']);self.assertFalse(r['money_transferred']);replay=self.unwrap(client.post(url,params=query,json=body));self.assertTrue(replay['replayed']);self.assertEqual(r['journal'],replay['journal']);self.assertTrue(self.unwrap(client.get(prefix+'crm/sales/'+ref+'/history/',params=query))['history_verified'])
   self.unwrap(client.post(url,params=query,json=self.command('review_reversal',ref,3,reason='Revisión HTTP',support_digest='e'*64,confirmed=True)));r=self.unwrap(client.post(url,params=query,json=self.command('reverse',ref,4,confirmed=True)));self.assertEqual(r['status'],'REVERSED');self.assertTrue(r['reversal']['posted'])
 def test_all_private_boundaries_and_strict_bodies(self):
  for system,client,query,prefix in self.targets():
   suffix='' if system=='sga-cd' else '/';url=prefix+'crm/sale-commands'+suffix
   for raw,status in [(' '*17000,413),('{"x":1,"x":2}',400)]:
    r=client.post(url,params=query,content=raw,headers={'Content-Type':'application/json'});self.assertEqual(r.status_code,status,r.text)
   self.assertIn(client.get(prefix+'crm/sales'+suffix,params=query,headers={'Authorization':''}).status_code,(401,403))
 def test_national_tourism_has_no_sale_api(self):
  client,cred=self.servers['turismo']
  for prefix in ('/api/v1/commercial-unified/','/api/v1/mi-negocio/comercial/unified/'):
   self.assertEqual(client.get(prefix+'crm/sales/',params={'provider_id':cred['provider_id']}).status_code,404)
if __name__=='__main__':unittest.main()
