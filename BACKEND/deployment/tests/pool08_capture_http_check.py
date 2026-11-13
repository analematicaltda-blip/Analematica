"""Public HTML posts create own canonical CRM contacts, with no real email or ad providers."""
import runpy,unittest,uuid,re,html
from pathlib import Path
f=runpy.run_path(str(Path(__file__).with_name('pool08_landings_http_check.py')),run_name='capture_http_setup');base=f['Checks']
def field(page,name):
 m=re.search(r'name="'+name+r'" value="([^"]*)"',page);return html.unescape(m.group(1)) if m else None
class Checks(unittest.TestCase):
 setUpClass=classmethod(base.setUpClass.__func__);tearDownClass=classmethod(base.tearDownClass.__func__);targets=base.targets;prefix=base.prefix;unwrap=base.unwrap;body=base.body;command=base.command
 def page(self,c,p,q,s,capture=True,offer=None):
  v=f['values']();v['capture']={'notice':'Aviso de tratamiento sintético para responder la solicitud.','privacy_url':'https://example.test/privacidad','offer_ref':offer} if capture else None
  ref=self.unwrap(self.command(c,p,q,self.body(slug='captacion-'+uuid.uuid4().hex,content=v),s))['landing_id'];self.unwrap(self.command(c,p,q,self.body('approve',ref,1,confirmed=True),s));self.unwrap(self.command(c,p,q,self.body('publish',ref,2,confirmed=True),s));return ref,p+'landing-pages/'+ref+s
 def form(self,c,url,**query):
  r=c.get(url,params=query,headers={'Authorization':''});self.assertEqual(r.status_code,200,r.text);token=field(r.text,'token');self.assertTrue(token);return {'token':token,'name':'Visitante público','email':uuid.uuid4().hex+'@example.test','phone':'','company_website':'','consent':'yes','marketing':'yes'}
 def send(self,c,url,s,data,origin='http://localhost'):
  return c.post(url.rstrip('/')+'/capture'+s,data=data,headers={'Authorization':'','Origin':origin})
 def test_capture_replay_attribution_private_crm_and_public_withdrawal(self):
  for system,c,q,p in self.targets():
   s='' if system=='sga-cd' else '/';ref,url=self.page(c,p,q,s);body=self.form(c,url,utm_source='campana-declarada',utm_campaign='cultura')
   r=self.send(c,url,s,body);self.assertEqual(r.status_code,200,r.text);rid=field(r.text,'reference');proof=field(r.text,'proof');self.assertTrue(rid);self.assertTrue(proof);self.assertNotIn(body['email'],r.text)
   repeat=self.send(c,url,s,body);self.assertEqual(repeat.status_code,200,repeat.text);self.assertEqual(field(repeat.text,'reference'),rid)
   stats=self.unwrap(c.get(p+'crm/landings/'+ref+'/captures'+s,params=q));self.assertEqual(stats['observed']['created_prospects'],1);self.assertEqual(stats['observed']['accepted_submissions'],1);cap=stats['captures'][0];self.assertEqual(cap['source']['utm']['utm_source'],'campana-declarada');self.assertFalse(cap['consent']['email_ownership_verified']);self.assertFalse(cap['consent']['delivery_authorized']);self.assertFalse(cap['source']['institutional_registration_created'])
   contact=self.unwrap(c.get(p+'crm/contacts/'+cap['contact_id']+s,params=q));self.assertEqual(contact['origin'],'LANDING_FORM');self.assertEqual(contact['landing_attribution']['page_id'],ref)
   self.unwrap(self.command(c,p,q,self.body('unpublish',ref,3,confirmed=True),s));self.assertEqual(c.get(url,headers={'Authorization':''}).status_code,404)
   recovered=self.send(c,url,s,body);self.assertEqual(recovered.status_code,200,recovered.text);self.assertEqual(field(recovered.text,'reference'),rid)
   wurl=url.rstrip('/')+'/withdraw'+s
   for _ in range(2):self.assertEqual(c.post(wurl,data={'reference':rid,'proof':proof},headers={'Authorization':'','Origin':'http://localhost'}).status_code,200)
   contact=self.unwrap(c.get(p+'crm/contacts/'+cap['contact_id']+s,params=q));self.assertEqual(contact['status'],'WITHDRAWN');self.assertFalse(contact['consents']['EMAIL:MARKETING']['granted']);self.assertFalse(contact['consents']['EMAIL:SERVICE']['granted'])
 def test_duplicate_email_never_overwrites_or_revives_contact(self):
  for system,c,q,p in self.targets():
   s='' if system=='sga-cd' else '/';ref,url=self.page(c,p,q,s);body=self.form(c,url);r=self.send(c,url,s,body);self.assertEqual(r.status_code,200,r.text);stats=self.unwrap(c.get(p+'crm/landings/'+ref+'/captures'+s,params=q));contact_id=stats['captures'][0]['contact_id'];before=self.unwrap(c.get(p+'crm/contacts/'+contact_id+s,params=q))
   r=c.post(url.rstrip('/')+'/withdraw'+s,data={'reference':field(r.text,'reference'),'proof':field(r.text,'proof')},headers={'Authorization':'','Origin':'http://localhost'});self.assertEqual(r.status_code,200,r.text)
   newer=self.form(c,url);newer.update(email=body['email'],name='No sobrescribir');r=self.send(c,url,s,newer);self.assertEqual(r.status_code,200,r.text);contact=self.unwrap(c.get(p+'crm/contacts/'+contact_id+s,params=q));self.assertEqual(contact['status'],'WITHDRAWN');self.assertEqual(contact['name'],before['name'])
   stats=self.unwrap(c.get(p+'crm/landings/'+ref+'/captures'+s,params=q));self.assertEqual(stats['observed']['created_prospects'],1);self.assertEqual(stats['observed']['review_required'],1)
 def test_spam_origin_tampering_and_foreign_context_rejected(self):
  for system,c,q,p in self.targets():
   s='' if system=='sga-cd' else '/';ref,url=self.page(c,p,q,s);body=self.form(c,url)
   self.assertEqual(c.get(url.rstrip('/')+'/capture'+s,headers={'Authorization':''}).status_code,405)
   self.assertEqual(c.post(url,data={},headers={'Authorization':''}).status_code,405)
   for patch,status in [({'company_website':'https://bot.test'},422),({'consent':''},422),({'provider_id':str(uuid.uuid4())},422),({'token':body['token']+'x'},400)]:
    bad={**body,**patch};r=self.send(c,url,s,bad);self.assertEqual(r.status_code,status,r.text)
   self.assertEqual(self.send(c,url,s,body,origin='https://evil.test').status_code,403)
   self.assertIn(c.get(p+'crm/landings/'+ref+'/captures'+s,params=q,headers={'Authorization':''}).status_code,(401,403))
   self.assertEqual(c.post(url.rstrip('/')+'/withdraw'+s,data={'reference':str(uuid.uuid4()),'proof':'a'*64},headers={'Authorization':'','Origin':'http://localhost'}).status_code,403)
 def test_owned_offer_is_attributed_and_unknown_offer_cannot_publish(self):
  from pool08_pricing_cases import PricingCases
  for system,c,q,p in self.targets():
   s='' if system=='sga-cd' else '/';price=self.unwrap(c.post(p+'crm/price-commands'+s,params=q,json=PricingCases.body(self,**PricingCases.values(self))))['item_id']
   ref,url=self.page(c,p,q,s,offer=price);body=self.form(c,url);r=self.send(c,url,s,body);self.assertEqual(r.status_code,200,r.text);stats=self.unwrap(c.get(p+'crm/landings/'+ref+'/captures'+s,params=q));self.assertEqual(stats['captures'][0]['source']['offer_ref'],price)
   v=f['values']();v['capture']={'notice':'Aviso de datos','privacy_url':'https://example.test/privacy','offer_ref':str(uuid.uuid4())};bad=self.unwrap(self.command(c,p,q,self.body(slug='foreign-'+uuid.uuid4().hex,content=v),s))['landing_id'];self.unwrap(self.command(c,p,q,self.body('approve',bad,1,confirmed=True),s));self.assertEqual(self.command(c,p,q,self.body('publish',bad,2,confirmed=True),s).status_code,409)
 def test_changed_public_version_rejects_old_form_and_seo_is_canonical(self):
  for system,c,q,p in self.targets():
   s='' if system=='sga-cd' else '/';ref,url=self.page(c,p,q,s);body=self.form(c,url,utm_source='declarado');r=c.get(url,params={'utm_source':'no-canonical'},headers={'Authorization':''});canonical=re.search(r'<link rel="canonical" href="([^"]+)"',r.text).group(1);self.assertNotIn('utm_',canonical);self.assertIn('og:title',r.text);self.assertIn("form-action 'self'",r.headers['content-security-policy'])
   self.unwrap(self.command(c,p,q,self.body('unpublish',ref,3,confirmed=True),s));self.assertEqual(self.send(c,url,s,body).status_code,409)
if __name__=='__main__':unittest.main()
