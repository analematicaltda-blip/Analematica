"""Four actual HTTP targets, public link possession and bounded native proxy media."""
import runpy,unittest,uuid,os,io
from pathlib import Path
from unittest.mock import patch
from PIL import Image
from pool08_pricing_cases import PricingCases
from pool08_quotation_cases import QuotationCases
fixture=runpy.run_path(str(Path(__file__).with_name('pool08_crm_http_check.py')),run_name='quote_http_fixture');base=fixture['CRMHTTPChecks']
class QuotationHTTP(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  env=patch.dict(os.environ,{'COMMERCIAL_QUOTE_LINK_KEY':'synthetic-quotation-test-key-32-chars-only'});env.start();cls.addClassCleanup(env.stop);base.setUpClass.__func__(cls)
 tearDownClass=classmethod(base.tearDownClass.__func__)
 targets=base.targets
 prefix=base.prefix
 unwrap=base.unwrap
 def test_full_flow_media_public_accept_and_replay_all_paths(self):
  for system,client,query,prefix in self.targets():
   suffix='' if system=='sga-cd' else '/';url=prefix+'crm/quotation-commands'+suffix
   price=self.unwrap(client.post(prefix+'crm/price-commands'+suffix,params=query,json=PricingCases.body(self,**PricingCases.values(self))))['item_id'];ctx=self.unwrap(client.get(prefix+'crm/context'+suffix,params=query));contact=self.unwrap(client.post(prefix+'crm/commands'+suffix,params=query,json=dict(request_id=str(uuid.uuid4()),operation='create',contact_id=None,expected_revision=0,data=dict(name='Contacto HTTP cotización',origin='HTTP',responsible_ref=ctx['actor_ref']))))['contact_id'];self.contact=contact
   policy=QuotationCases.body(self,'review_capacity',item_id=price,price_revision=1,mode='NOT_APPLICABLE',resource_ref=None,reason='Revisión declarada',support_digest='a'*64);self.unwrap(client.post(url,params=query,json=policy))
   asset=str(uuid.uuid4());image=io.BytesIO();Image.new('RGB',(12,12),(20,40,80)).save(image,format='PNG');self.unwrap(client.post(prefix+'crm/quotation-media/'+asset+suffix,params=query,content=image.getvalue(),headers={'Content-Type':'image/png'}))
   body=QuotationCases.body(self,**QuotationCases.values(self,price,media_ids=[asset]));created=self.unwrap(client.post(url,params=query,json=body));ref=created['quotation_id'];self.assertTrue(self.unwrap(client.post(url,params=query,json=body))['replayed'])
   for operation,revision,data in [('issue',1,{}),('link',2,{'confirm_share':True})]:result=self.unwrap(client.post(url,params=query,json=QuotationCases.body(self,operation,ref,revision,**data)))
   link=result;public=prefix+'quote-links/'+ref+'/'+link['link_id']+suffix;headers={'Authorization':'','X-Quote-Token':link['link_token']};view=self.unwrap(client.get(public,headers=headers));self.assertNotIn('contact_id',view['content']);media=client.get(prefix+'quote-links/'+ref+'/'+link['link_id']+'/media/'+asset+suffix,headers=headers);self.assertEqual(media.status_code,200);self.assertEqual(media.headers['Content-Type'].split(';')[0],'image/png');self.assertEqual(media.headers['Cache-Control'],'no-store')
   for raw,status,ctype in [(' '*17000,413,'application/json'),('{"x":1,"x":2}',400,'application/json'),('{}',415,'text/plain')]:
    response=client.post(public,content=raw,headers={**headers,'Content-Type':ctype});self.assertEqual(response.status_code,status);self.assertEqual(response.headers['Cache-Control'],'no-store')
   command=dict(request_id=str(uuid.uuid4()),version=view['version'],content_digest=view['content_digest'],confirmed=True);accepted=self.unwrap(client.post(public,json=command,headers=headers));self.assertEqual(accepted['status'],'ACCEPTED');self.assertFalse(accepted['reservation_created']);self.assertTrue(self.unwrap(client.post(public,json=command,headers=headers))['replayed']);self.assertFalse(self.unwrap(client.get(public,headers=headers))['acceptance']['customer_identity_verified'])
   self.assertEqual(client.get(public,headers={'Authorization':'','X-Quote-Token':'0'*64}).status_code,403)
 def test_strict_requests_private_errors_and_media_limits(self):
  for system,client,query,prefix in self.targets():
   suffix='' if system=='sga-cd' else '/';url=prefix+'crm/quotation-commands'+suffix
   for raw,status in [(' '*17000,413),('{"x":1,"x":2}',400)]:
    r=client.post(url,params=query,content=raw,headers={'Content-Type':'application/json'});self.assertEqual(r.status_code,status);self.assertEqual(r.headers['Cache-Control'],'no-store')
   r=client.post(prefix+'crm/quotation-media/'+str(uuid.uuid4())+suffix,params=query,content=b'x'*262145,headers={'Content-Type':'video/mp4'});self.assertEqual(r.status_code,413)
 def test_tourism_has_no_company_quote_or_link_api(self):
  client,cred=self.servers['turismo']
  for prefix in ('/api/v1/commercial-unified/','/api/v1/mi-negocio/comercial/unified/'):
   self.assertEqual(client.get(prefix+'crm/quotations/',params={'provider_id':cred['provider_id']}).status_code,404);self.assertEqual(client.get(prefix+'quote-links/'+str(uuid.uuid4())+'/'+str(uuid.uuid4())+'/').status_code,404)
QuotationHTTP.body=PricingCases.body
if __name__=='__main__':raise SystemExit(not unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(QuotationHTTP)).wasSuccessful())
