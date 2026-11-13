"""Real HTTP native/gateway payment records, configured-off outbound Bold boundary."""
import runpy,unittest,uuid
from pathlib import Path
fixture=runpy.run_path(str(Path(__file__).with_name('pool08_sales_http_check.py')),run_name='payment_http_fixture');base=fixture['SalesHTTP']
class PaymentHTTP(unittest.TestCase):
 setUpClass=classmethod(base.setUpClass.__func__);tearDownClass=classmethod(base.tearDownClass.__func__)
 targets=base.targets;prefix=base.prefix;unwrap=base.unwrap;quote=base.quote;command=base.command
 def payment_body(self,operation='create',ref=None,revision=0,**data):return dict(request_id=str(uuid.uuid4()),operation=operation,payment_id=ref,expected_revision=revision,data=data)
 def test_native_gateway_intentions_and_disabled_provider_are_honest(self):
  for system,client,query,prefix in self.targets():
   if system=='sga-cd':continue
   cred=self.servers[system][1];qid=self.quote(system,client,query,prefix);url=prefix+'crm/sale-commands/';sale=self.unwrap(client.post(url,params=query,json=self.command(quotation_id=qid)))['sale_id'];terms=dict(economic_fact='SERVICE_DELIVERED',entry_date=cred['day'],accounts=cred['sale_accounts'],operation=dict(mode='NO_LABOR_REVIEWED',order_id=None,reason='Declarada sin personal',support_digest='b'*64),documents=[dict(kind='DELIVERY_SUPPORT',reference='HTTP-TEST',sha256='c'*64)],support_digest='d'*64,confirmed=True);self.unwrap(client.post(url,params=query,json=self.command('review',sale,1,**terms)));self.unwrap(client.post(url,params=query,json=self.command('confirm',sale,2,confirmed=True)))
   url=prefix+'crm/payment-commands/';create=self.payment_body(sale_id=sale,confirmed=True);r=self.unwrap(client.post(url,params=query,json=create));ref=r['payment_id'];self.assertTrue(self.unwrap(client.post(url,params=query,json=create))['replayed']);r=self.unwrap(client.post(url,params=query,json=self.payment_body('checkout',ref,1,confirmed=True)));self.assertEqual(r['status'],'BLOCKED');self.assertFalse(r['payment_verified']);self.assertIsNone(r['checkout_url']);self.assertEqual(r['error_code'],'BOLD_SCOPED_CONFIGURATION_REQUIRED');self.assertTrue(self.unwrap(client.get(prefix+'crm/payments/'+ref+'/history/',params=query))['history_verified'])
 def test_private_body_and_national_tourism_boundaries(self):
  for system,client,query,prefix in self.targets():
   suffix='' if system=='sga-cd' else '/';url=prefix+'crm/payment-commands'+suffix
   for raw,status in [(' '*17000,413),('{"x":1,"x":2}',400)]:self.assertEqual(client.post(url,params=query,content=raw,headers={'Content-Type':'application/json'}).status_code,status)
   self.assertIn(client.get(prefix+'crm/payments'+suffix,params=query,headers={'Authorization':''}).status_code,(401,403))
  client,cred=self.servers['turismo'];self.assertEqual(client.get('/api/v1/commercial-unified/crm/payments/').status_code,404)
if __name__=='__main__':unittest.main()
