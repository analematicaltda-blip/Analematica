"""Real owned library HTTP, private original preservation and reviewed derivative publication."""
import runpy,unittest,uuid,base64,json,io,hashlib,copy
from pathlib import Path
from PIL import Image,PngImagePlugin
f=runpy.run_path(str(Path(__file__).with_name('pool08_crm_http_check.py')),run_name='library_http_setup');base=f['CRMHTTPChecks']
def image():
 out=io.BytesIO();meta=PngImagePlugin.PngInfo();meta.add_text('private_test_marker','NEVER_PUBLIC_ORIGINAL_METADATA');Image.new('RGBA',(80,50),(10,45,80,180)).save(out,format='PNG',pnginfo=meta);return out.getvalue()+b'\nPRIVATE_APPENDIX_XML_SUPPORT'
def metadata():return {'title':'Pieza de marketing','classification':'MARKETING','brand':{'name':'Marca de la empresa','tagline':'Nuestra experiencia','template':'SQUARE'},'rights':{'holder':'Titular declarado','license':'OWNED','reference':'Autorización sintética','valid_until':None,'public_web':True}}
class Checks(unittest.TestCase):
 setUpClass=classmethod(base.setUpClass.__func__);tearDownClass=classmethod(base.tearDownClass.__func__);targets=base.targets;prefix=base.prefix;unwrap=base.unwrap
 def upload(self,c,p,q,s,body=None,raw=None,mime='image/png'):
  body=body or {'request_id':str(uuid.uuid4()),'item_id':None,'expected_revision':0,'metadata':metadata()};header=base64.b64encode(json.dumps(body,ensure_ascii=False).encode()).decode();return c.post(p+'crm/library-upload'+s,params=q,content=image() if raw is None else raw,headers={'Content-Type':mime,'X-Library-Metadata':header})
 def command(self,c,p,q,s,op,ref,rev,**data):return c.post(p+'crm/library-commands'+s,params=q,json=dict(request_id=str(uuid.uuid4()),operation=op,item_id=ref,expected_revision=rev,data=data))
 def create(self,c,p,q,s):return self.unwrap(self.upload(c,p,q,s))['item_id']
 def test_original_private_metadata_stripped_and_publication_withdrawal(self):
  for system,c,q,p in self.targets():
   s='' if system=='sga-cd' else '/';ref=self.create(c,p,q,s);item=self.unwrap(c.get(p+'crm/library/'+ref+s,params=q));v=item['versions'][0];self.assertEqual(v['original_sha256'],hashlib.sha256(image()).hexdigest());self.assertEqual(v['brand']['name'],'Marca de la empresa');self.assertEqual(item['system'],'analematica' if system=='gateway' else system)
   original=p+'crm/library/'+ref+'/versions/1/original'+s;r=c.get(original,params=q);self.assertEqual(r.status_code,200,r.text);self.assertEqual(r.content,image());self.assertIn('attachment',r.headers['content-disposition']);self.assertIn(c.get(original,params=q,headers={'Authorization':''}).status_code,(401,403))
   public=p+'media-library/'+ref+'/1'+s;self.assertEqual(c.get(public,headers={'Authorization':''}).status_code,404);self.assertEqual(self.command(c,p,q,s,'publish',ref,1,confirmed=True).status_code,409)
   self.unwrap(self.command(c,p,q,s,'approve',ref,1,rights_confirmed=True,privacy_reviewed=True));self.unwrap(self.command(c,p,q,s,'publish',ref,2,confirmed=True));r=c.get(public,headers={'Authorization':''});self.assertEqual(r.status_code,200,r.text);self.assertEqual(r.headers['content-type'].split(';')[0],'image/png');self.assertNotIn(b'NEVER_PUBLIC',r.content);self.assertNotIn(b'PRIVATE_APPENDIX',r.content);self.assertNotEqual(r.content,image());self.assertEqual(hashlib.sha256(r.content).hexdigest(),v['delivery_sha256']);self.assertEqual(r.headers['cache-control'],'no-store')
   self.assertEqual(c.get(public.rstrip('/')+'/original'+s,headers={'Authorization':''}).status_code,404)
   self.unwrap(self.command(c,p,q,s,'withdraw',ref,3,confirmed=True));self.assertEqual(c.get(public,headers={'Authorization':''}).status_code,404);self.assertEqual(c.get(original,params=q).content,image())
 def test_replay_new_version_preserves_first_original_and_own_brand(self):
  for system,c,q,p in self.targets():
   s='' if system=='sga-cd' else '/';body={'request_id':str(uuid.uuid4()),'item_id':None,'expected_revision':0,'metadata':metadata()};a=self.unwrap(self.upload(c,p,q,s,body));ref=a['item_id'];self.assertTrue(self.unwrap(self.upload(c,p,q,s,body))['replayed']);receipt=self.unwrap(c.get(p+'crm/library-receipts/'+body['request_id']+s,params=q));self.assertEqual(receipt['item_id'],ref)
   values=metadata();values['brand']['name']='Marca revisada';r=self.unwrap(self.command(c,p,q,s,'revise',ref,1,**values));self.assertEqual(r['content_version'],2);item=self.unwrap(c.get(p+'crm/library/'+ref+s,params=q));self.assertEqual(item['versions'][0]['brand']['name'],'Marca de la empresa');self.assertEqual(item['versions'][1]['brand']['name'],'Marca revisada');self.assertEqual(item['versions'][0]['blob_id'],item['versions'][1]['blob_id'])
   body['metadata']['title']='Otro';self.assertEqual(self.upload(c,p,q,s,body).status_code,409)
 def test_foreign_role_or_fiscal_content_cannot_be_used(self):
  for system,c,q,p in self.targets():
   s='' if system=='sga-cd' else '/';ref=self.create(c,p,q,s);cred=(self.extra[system] if system in ('sga-cd','gateway') else self.servers[system])[1]
   self.assertIn(c.get(p+'crm/library/'+ref+'/versions/1/original'+s,params=q,headers={'Authorization':'Bearer '+cred['other_token']}).status_code,(403,404))
   b={'request_id':str(uuid.uuid4()),'item_id':None,'expected_revision':0,'metadata':metadata()}
   for mime,data in [('application/pdf',b'%PDF-private'),('application/xml',b'<Invoice>private</Invoice>'),('image/svg+xml',b'<svg onload="alert(1)"/>')]:self.assertEqual(self.upload(c,p,q,s,b,raw=data,mime=mime).status_code,415)
   b['metadata']['classification']='FISCAL_SUPPORT';self.assertEqual(self.upload(c,p,q,s,b).status_code,422);self.assertEqual(self.command(c,p,q,s,'approve',ref,1,rights_confirmed=1,privacy_reviewed=True).status_code,422)
 def test_unconfirmed_or_expired_rights_remain_private(self):
  for system,c,q,p in self.targets():
   s='' if system=='sga-cd' else '/';b={'request_id':str(uuid.uuid4()),'item_id':None,'expected_revision':0,'metadata':metadata()};b['metadata']['rights']['license']='UNCONFIRMED';ref=self.unwrap(self.upload(c,p,q,s,b))['item_id'];self.assertEqual(self.command(c,p,q,s,'approve',ref,1,rights_confirmed=True,privacy_reviewed=True).status_code,409)
   b['request_id']=str(uuid.uuid4());b['metadata']['rights'].update(license='OWNED',valid_until='2000-01-01T00:00:00+00:00');ref=self.unwrap(self.upload(c,p,q,s,b))['item_id'];self.assertEqual(self.command(c,p,q,s,'approve',ref,1,rights_confirmed=True,privacy_reviewed=True).status_code,409)
if __name__=='__main__':unittest.main()
