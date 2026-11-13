"""Real own-library adaptations: immutable originals, profiles, rollback and MP4 semantics."""
import importlib,io,json,hashlib,subprocess,tempfile,copy,uuid
from pathlib import Path
from unittest.mock import patch
from PIL import Image
class AdaptationCases:
 def library(self):return importlib.import_module(self.module_path+'.library_api').service(self.gen.crm)
 def upload_image(self):
  buf=io.BytesIO();im=Image.new('RGB',(120,80),'red');im.paste('blue',(40,0,80,80));im.save(buf,format='PNG');return self.upload_media(buf.getvalue(),'image/png')
 def upload_media(self,raw,mime):
  meta={'title':'Adaptación sintética','classification':'MARKETING','brand':{'name':'Empresa de prueba','tagline':'Sin publicación','template':'SQUARE'},'rights':{'holder':'Fixture','license':'OWNED','reference':'Material sintético','valid_until':None,'public_web':True}};lib=self.library();ref=lib.upload({'request_id':str(uuid.uuid4()),'item_id':None,'expected_revision':0,'metadata':meta},raw,mime)['item_id'];return lib,ref,raw
 def adaptation(self,lib,ref,**edits):
  item=lib.get(ref);v=item['versions'][-1];data={'source_version':v['number'],'source_sha256':v['delivery_sha256'],'profile':'image-square-v1','profile_version':'1.0','mode':'PAD','allow_upscale':False,'confirmed_crop':False,'audio':'NONE','subtitles':'BURNED_ONLY_NO_TEXT_TRACKS',**edits};return {'request_id':str(uuid.uuid4()),'operation':'adapt','item_id':ref,'expected_revision':item['revision'],'data':data}
 def test_image_profiles_real_dimensions_and_original_unchanged(self):
  for profile,size in [('image-vertical-v1',(1080,1920)),('image-square-v1',(1080,1080)),('image-landscape-v1',(1920,1080))]:
   with self.subTest(profile=profile):
    lib,ref,raw=self.upload_image();body=self.adaptation(lib,ref,profile=profile);receipt=lib.command(body);self.assertTrue(lib.command(body)['replayed']);self.assertEqual(receipt['content_version'],2);self.assertEqual(lib.bytes(ref,1,'original')[0],raw);self.assertEqual(lib.bytes(ref,2,'original')[0],raw);out,mime=lib.bytes(ref,2);self.assertEqual(mime,'image/png');im=Image.open(io.BytesIO(out));self.assertEqual(im.size,size);self.assertEqual(im.convert('RGB').getpixel((0,0)),(17,48,75));self.assertIsNone(lib.get(ref)['approved_digest']);self.assertIsNone(lib.get(ref)['published_version']);self.assertFalse(lib.get(ref)['versions'][-1]['media']['adaptation']['scaled_up']);self.assertFalse(lib.get(ref)['versions'][-1]['media']['adaptation']['quality_gain_claimed'])
 def test_crop_explicit_upscale_and_center_pixels(self):
  lib,ref,_=self.upload_image();body=self.adaptation(lib,ref,mode='CROP',confirmed_crop=True)
  with self.assertRaises(self.error):lib.command(body)
  body['data']['allow_upscale']=True;lib.command(body);raw,mime=lib.bytes(ref,2);im=Image.open(io.BytesIO(raw)).convert('RGB');self.assertEqual(im.size,(1080,1080));self.assertEqual(im.getpixel((540,540)),(0,0,255));self.assertTrue(lib.get(ref)['versions'][-1]['media']['adaptation']['scaled_up'])
 def test_invalid_contracts_stale_source_and_wrong_kind_never_append(self):
  lib,ref,_=self.upload_image()
  for edit in [dict(profile='video-square-v1',audio='KEEP'),dict(profile='4k'),dict(profile_version='2.0'),dict(mode='CROP'),dict(audio='KEEP'),dict(allow_upscale=1),dict(subtitles='INVENT_CAPTIONS'),dict(source_sha256='b'*64),dict(source_version=True),dict(url='https://example.test')]:
   with self.subTest(edit=edit):
    with self.assertRaises(self.error):lib.command(self.adaptation(lib,ref,**edit))
  self.assertEqual(len(lib.get(ref)['versions']),1)
 def test_same_request_cannot_change_profile_and_source_review_is_invalidated(self):
  lib,ref,_=self.upload_image();lib.command({'request_id':str(uuid.uuid4()),'operation':'approve','item_id':ref,'expected_revision':1,'data':{'rights_confirmed':True,'privacy_reviewed':True}});body=self.adaptation(lib,ref);lib.command(body);self.assertIsNone(lib.get(ref)['approved_digest']);body['data']['profile']='image-vertical-v1'
  with self.assertRaises(self.error):lib.command(body)
 def test_decoder_or_audit_failure_does_not_append(self):
  lib,ref,_=self.upload_image();module=importlib.import_module(self.module_path+'.media_adaptation')
  with patch.object(module,'adapt',side_effect=self.error('ADAPTATION_FAILED',503)):
   with self.assertRaises(self.error):lib.command(self.adaptation(lib,ref))
  with patch.object(lib.store,'append',side_effect=RuntimeError('Synthetic adaptation audit failure')):
   with self.assertRaises(RuntimeError):lib.command(self.adaptation(lib,ref))
  self.assertEqual(len(lib.get(ref)['versions']),1)
 def test_real_mp4_profiles_keep_mute_and_subtitle_policy(self):
  with tempfile.TemporaryDirectory() as d:
   file=Path(d)/'tone.mp4';subprocess.run(['ffmpeg','-v','error','-nostdin','-f','lavfi','-i','color=c=blue:s=160x90:r=24:d=1','-f','lavfi','-i','sine=frequency=330:duration=1','-c:v','libx264','-pix_fmt','yuv420p','-c:a','aac','-threads','1','-shortest','-y',str(file)],capture_output=True,check=True,timeout=20);raw=file.read_bytes()
  for profile,size,audio in [('video-vertical-v1',(720,1280),'KEEP'),('video-square-v1',(720,720),'MUTE'),('video-landscape-v1',(1280,720),'KEEP')]:
   with self.subTest(profile=profile):
    lib,ref,original=self.upload_media(raw,'video/mp4');lib.command(self.adaptation(lib,ref,profile=profile,audio=audio,allow_upscale=True));out,mime=lib.bytes(ref,2);self.assertEqual(mime,'video/mp4');self.assertEqual(lib.bytes(ref,1,'original')[0],original)
    with tempfile.TemporaryDirectory() as d:
     file=Path(d)/'adapted.mp4';file.write_bytes(out);meta=json.loads(subprocess.run(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(file)],capture_output=True,check=True).stdout);video=next(s for s in meta['streams'] if s['codec_type']=='video');self.assertEqual((video['width'],video['height']),size);self.assertEqual(video['codec_name'],'h264');self.assertEqual(any(s['codec_type']=='audio' for s in meta['streams']),audio=='KEEP');self.assertFalse(any(s['codec_type']=='subtitle' for s in meta['streams']));self.assertAlmostEqual(float(meta['format']['duration']),1,delta=.2)
    artifacts=Path('/tmp/gc015-adapted-artifacts');artifacts.mkdir(exist_ok=True);(artifacts/(self.module_path+'-'+profile+'.mp4')).write_bytes(out)

 def test_source_changed_during_processing_is_not_committed(self):
  lib,ref,_=self.upload_image();module=importlib.import_module(self.module_path+'.media_adaptation');original=module.adapt;body=self.adaptation(lib,ref)
  def changed(*args):
   result=original(*args);v=lib.get(ref)['versions'][-1];lib.command({'request_id':str(uuid.uuid4()),'operation':'revise','item_id':ref,'expected_revision':1,'data':{k:copy.deepcopy(v[k]) for k in ['title','classification','brand','rights']}});return result
  with patch.object(module,'adapt',side_effect=changed):
   with self.assertRaises(self.error):lib.command(body)
  self.assertEqual(len(lib.get(ref)['versions']),2);self.assertNotIn('adaptation',lib.get(ref)['versions'][-1]['media'])
 def test_existing_public_version_is_not_replaced_by_adaptation(self):
  lib,ref,_=self.upload_image();lib.command({'request_id':str(uuid.uuid4()),'operation':'approve','item_id':ref,'expected_revision':1,'data':{'rights_confirmed':True,'privacy_reviewed':True}});lib.command({'request_id':str(uuid.uuid4()),'operation':'publish','item_id':ref,'expected_revision':2,'data':{'confirmed':True}});old=lib.bytes(ref,1,'delivery',public=True)[0];lib.command(self.adaptation(lib,ref));self.assertEqual(lib.get(ref)['published_version'],1);self.assertEqual(lib.bytes(ref,1,'delivery',public=True)[0],old)
  with self.assertRaises(self.error):lib.bytes(ref,2,'delivery',public=True)
 def test_output_limit_and_quota_fail_without_new_version(self):
  lib,ref,_=self.upload_image();module=importlib.import_module(self.module_path+'.media_adaptation')
  with patch.object(module,'MAX_DELIVERY',1):
   with self.assertRaises(self.error):lib.command(self.adaptation(lib,ref))
  with patch.object(lib.store,'usage',return_value=(200,0)):
   with self.assertRaises(self.error):lib.command(self.adaptation(lib,ref))
  self.assertEqual(len(lib.get(ref)['versions']),1)
 def test_anamorphic_video_respects_display_aspect(self):
  with tempfile.TemporaryDirectory() as d:
   file=Path(d)/'anamorphic.mp4';subprocess.run(['ffmpeg','-v','error','-nostdin','-f','lavfi','-i','color=c=blue:s=160x90:r=24:d=1','-vf','setsar=2/1','-c:v','libx264','-pix_fmt','yuv420p','-threads','1','-y',str(file)],capture_output=True,check=True,timeout=20);raw=file.read_bytes()
  lib,ref,_=self.upload_media(raw,'video/mp4');lib.command(self.adaptation(lib,ref,profile='video-square-v1',audio='MUTE',allow_upscale=True));info=lib.get(ref)['versions'][-1]['media']['adaptation'];self.assertEqual(info['source_sample_aspect_ratio'],'2:1');self.assertEqual(info['content_width'],720);self.assertEqual(info['content_height'],202)
 def test_revoked_real_identity_cannot_adapt_or_read(self):
  lib,ref,_=self.upload_image();body=self.adaptation(lib,ref)
  if self.module_path.startswith('apps.'):
   from apps.turismo.models import VerifiedCompanyLink
   from django.utils import timezone
   VerifiedCompanyLink.objects.filter(provider_id=self.gen.store.provider).update(revoked_at=timezone.now())
  else:
   from app.models.user import Usuario
   user=self.gen.crm.store.db.get(Usuario,int(self.gen.crm.actor));user.activo=False;self.gen.crm.store.db.commit()
  with self.assertRaises(Exception):lib.command(body)
  with self.assertRaises(Exception):lib.bytes(ref,1)
  self.assertEqual(len(lib.store.get(ref)['versions']),1)

 def test_existing_revision_limit_cannot_be_bypassed_by_adaptation(self):
  lib,ref,_=self.upload_image()
  for revision in range(1,200):lib.command({'request_id':str(uuid.uuid4()),'operation':'approve','item_id':ref,'expected_revision':revision,'data':{'rights_confirmed':True,'privacy_reviewed':True}})
  self.assertEqual(lib.get(ref)['revision'],200)
  with self.assertRaises(self.error) as e:lib.command(self.adaptation(lib,ref))
  self.assertEqual(str(e.exception),'LIBRARY_REVISION_LIMIT');self.assertEqual(len(lib.get(ref)['versions']),1)
