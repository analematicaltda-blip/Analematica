"""Real HTTP in own services/gateway: versioned artifacts, replay and isolation."""
import runpy,unittest,uuid,hashlib,io,copy
from pathlib import Path
from PIL import Image
f=runpy.run_path(str(Path(__file__).with_name('pool08_library_http_check.py')),run_name='adaptation_http_setup');base=f['Checks']
class Checks(unittest.TestCase):
 setUpClass=classmethod(base.setUpClass.__func__);tearDownClass=classmethod(base.tearDownClass.__func__);targets=base.targets;prefix=base.prefix;unwrap=base.unwrap;upload=base.upload
 def test_adapt_image_replay_source_and_foreign_access(self):
  for system,c,q,p in self.targets():
   with self.subTest(system=system):
    s='' if system=='sga-cd' else '/';ref=self.unwrap(self.upload(c,p,q,s))['item_id'];before=self.unwrap(c.get(p+'crm/library/'+ref+s,params=q));v=before['versions'][-1];raw=c.get(p+'crm/library/'+ref+'/versions/1/original'+s,params=q).content;catalog=self.unwrap(c.get(p+'crm/library'+s,params=q))['adaptation_profiles'];self.assertEqual(catalog['version'],'1.0');self.assertEqual(len(catalog['profiles']),6)
    command={'request_id':str(uuid.uuid4()),'operation':'adapt','item_id':ref,'expected_revision':1,'data':{'source_version':1,'source_sha256':v['delivery_sha256'],'profile':'image-vertical-v1','profile_version':'1.0','mode':'PAD','allow_upscale':False,'confirmed_crop':False,'audio':'NONE','subtitles':'BURNED_ONLY_NO_TEXT_TRACKS'}};url=p+'crm/library-commands'+s
    self.assertEqual(self.unwrap(c.post(url,params=q,json=command))['content_version'],2);self.assertTrue(self.unwrap(c.post(url,params=q,json=command))['replayed']);self.assertEqual(self.unwrap(c.get(p+'crm/library-receipts/'+command['request_id']+s,params=q))['content_version'],2)
    result=c.get(p+'crm/library/'+ref+'/versions/2/delivery'+s,params=q);self.assertEqual(result.status_code,200,result.text[:100]);self.assertEqual(Image.open(io.BytesIO(result.content)).size,(1080,1920));self.assertEqual(result.headers['cache-control'],'no-store');self.assertEqual(c.get(p+'crm/library/'+ref+'/versions/2/original'+s,params=q).content,raw);self.assertEqual(c.get(p+'media-library/'+ref+'/2'+s,headers={'Authorization':''}).status_code,404)
    credentials=(self.extra[system] if system in ('sga-cd','gateway') else self.servers[system])[1];self.assertIn(c.post(url,params=q,json=command,headers={'Authorization':'Bearer '+credentials['other_token']}).status_code,(403,404));self.assertIn(c.get(p+'crm/library/'+ref+'/versions/2/delivery'+s,params=q,headers={'Authorization':''}).status_code,(401,403))
    changed=copy.deepcopy(command);changed['data']['mode']='CROP';self.assertIn(c.post(url,params=q,json=changed).status_code,(409,422));self.assertEqual(len(self.unwrap(c.get(p+'crm/library/'+ref+s,params=q))['versions']),2)
if __name__=='__main__':raise SystemExit(not unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Checks)).wasSuccessful())
