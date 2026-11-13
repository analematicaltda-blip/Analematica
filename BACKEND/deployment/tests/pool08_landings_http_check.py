"""Actual own landing APIs and public HTML across three systems plus native gateway."""
import runpy,unittest,uuid,copy
from pathlib import Path
fixture=runpy.run_path(str(Path(__file__).with_name('pool08_crm_http_check.py')),run_name='landing_http_fixture')
base=fixture['CRMHTTPChecks']
def values(title='Servicios propios'):
 return {'brand':'Marca propia','title':title,'description':'Servicios culturales, deportivos y turísticos','template':'CULTURA','blocks':[{'kind':'HERO','heading':'Bienvenidos','body':'Experiencias locales','url':'','label':''}]}
class Checks(unittest.TestCase):
 setUpClass=classmethod(base.setUpClass.__func__);tearDownClass=classmethod(base.tearDownClass.__func__);targets=base.targets;prefix=base.prefix;unwrap=base.unwrap
 def body(self,op='create',ref=None,rev=0,**data):return dict(request_id=str(uuid.uuid4()),operation=op,landing_id=ref,expected_revision=rev,data=data)
 def command(self,c,p,q,body,suffix):return c.post(p+'crm/landing-commands'+suffix,params=q,json=body)
 def create(self,c,p,q,s):
  b=self.body(slug='pagina-'+uuid.uuid4().hex,content=values());return self.unwrap(self.command(c,p,q,b,s))['landing_id']
 def test_complete_publication_restore_and_withdrawal(self):
  for system,c,q,p in self.targets():
   s='' if system=='sga-cd' else '/';ref=self.create(c,p,q,s);public=p+'landing-pages/'+ref+s
   self.assertEqual(c.get(public,headers={'Authorization':''}).status_code,404)
   self.assertEqual(self.command(c,p,q,self.body('publish',ref,1,confirmed=True),s).status_code,409)
   self.unwrap(self.command(c,p,q,self.body('approve',ref,1,confirmed=True),s));self.unwrap(self.command(c,p,q,self.body('publish',ref,2,confirmed=True),s))
   r=c.get(public,headers={'Authorization':''});self.assertEqual(r.status_code,200,r.text);self.assertIn('Marca propia',r.text)
   self.assertIn("default-src 'none'",r.headers['content-security-policy']);self.assertEqual(r.headers['cache-control'],'no-store')
   self.unwrap(self.command(c,p,q,self.body('edit',ref,3,content=values('Borrador nuevo')),s));self.assertNotIn('Borrador nuevo',c.get(public).text)
   self.assertEqual(self.command(c,p,q,self.body('publish',ref,4,confirmed=True),s).status_code,409)
   self.unwrap(self.command(c,p,q,self.body('restore',ref,4,version=1),s));item=self.unwrap(c.get(p+'crm/landings/'+ref+s,params=q));self.assertEqual(item['versions'][-1]['restored_from'],1);self.assertEqual(item['versions'][-1]['content']['title'],'Servicios propios')
   self.unwrap(self.command(c,p,q,self.body('unpublish',ref,5,confirmed=True),s));self.assertEqual(c.get(public,headers={'Authorization':''}).status_code,404)
   hist=self.unwrap(c.get(p+'crm/landings/'+ref+'/history'+s,params=q));self.assertTrue(hist['history_verified']);self.assertEqual(len(hist['events']),6)
 def test_scoped_access_revoked_or_foreign_user_and_replay(self):
  for system,c,q,p in self.targets():
   s='' if system=='sga-cd' else '/';b=self.body(slug='reintento-'+uuid.uuid4().hex,content=values());r=self.unwrap(self.command(c,p,q,b,s));self.assertTrue(self.unwrap(self.command(c,p,q,b,s))['replayed']);ref=r['landing_id']
   receipt=self.unwrap(c.get(p+'crm/landing-receipts/'+b['request_id']+s,params=q));self.assertEqual(receipt['landing_id'],ref)
   summary=self.unwrap(c.get(p+'crm/landings'+s,params={**q,'limit':1,'offset':0}));self.assertLessEqual(len(summary['pages']),1);self.assertNotIn('versions',summary['pages'][0])
   bad=copy.deepcopy(b);bad['data']['content']['title']='Otro contenido';self.assertEqual(self.command(c,p,q,bad,s).status_code,409)
   self.assertIn(c.get(p+'crm/landings/'+ref+s,params=q,headers={'Authorization':''}).status_code,(401,403))
   badq={**q,'tenant_ref':'foreign'};self.assertEqual(c.get(p+'crm/landings/'+ref+s,params=badq).status_code,400)
   foreign=next(x[1] for x in self.targets() if x[0]==system);cred=(self.extra[system] if system in ('gateway','sga-cd') else self.servers[system])[1]
   self.assertIn(foreign.get(p+'crm/landings/'+ref+s,params=q,headers={'Authorization':'Bearer '+cred['other_token']}).status_code,(403,404))
   self.assertEqual(self.command(c,p,q,self.body('approve',ref,0,confirmed=True),s).status_code,409)
 def test_unsafe_content_unknown_fields_and_false_confirmations(self):
  for system,c,q,p in self.targets():
   s='' if system=='sga-cd' else '/'
   bad=values();bad['blocks'][0]={'kind':'CTA','heading':'Enlace','body':'','url':'javascript:alert(1)','label':'Abrir'}
   self.assertEqual(self.command(c,p,q,self.body(slug='unsafe-'+uuid.uuid4().hex,content=bad),s).status_code,422)
   bad=values();bad['html']='<script>alert(1)</script>';self.assertEqual(self.command(c,p,q,self.body(slug='unsafe-'+uuid.uuid4().hex,content=bad),s).status_code,422)
   ref=self.create(c,p,q,s);self.assertEqual(self.command(c,p,q,self.body('approve',ref,1,confirmed=1),s).status_code,422)
   r=c.get(p+'crm/landings/'+ref+'/preview'+s,params=q);self.assertEqual(r.status_code,200,r.text);self.assertIn('VISTA PREVIA',r.text);self.assertEqual(r.headers['x-robots-tag'],'noindex, nofollow')
 def test_render_escapes_html_and_public_has_no_private_audit_fields(self):
  for system,c,q,p in self.targets():
   s='' if system=='sga-cd' else '/';v=values('<script>alert(1)</script>');ref=self.unwrap(self.command(c,p,q,self.body(slug='escaped-'+uuid.uuid4().hex,content=v),s))['landing_id']
   self.unwrap(self.command(c,p,q,self.body('approve',ref,1,confirmed=True),s));self.unwrap(self.command(c,p,q,self.body('publish',ref,2,confirmed=True),s));r=c.get(p+'landing-pages/'+ref+s,headers={'Authorization':''});self.assertEqual(r.status_code,200);self.assertNotIn('<script>',r.text);self.assertIn('&lt;script&gt;',r.text)
   for forbidden in ['actor_ref','event_digest','scope','request_id']:self.assertNotIn(forbidden,r.text)
if __name__=='__main__':unittest.main()
