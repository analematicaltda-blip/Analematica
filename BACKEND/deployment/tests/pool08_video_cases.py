"""Actual FFmpeg composition and durable own-domain state; no synthetic AI claim."""
import importlib,json,hashlib,subprocess,tempfile,copy,uuid
from pathlib import Path
from unittest.mock import patch
PLAN={'format':'REEL','brand':'Marca sintética','scenes':[{'text':'Servicio de prueba, sin publicación','seconds':1},{'text':'Consulta condiciones','seconds':1}],'voice':None,'music':None}
class VideoCases:
 def prepare_video(self):
  self.video=importlib.import_module(self.module_path+'.video_composition');self.worker=importlib.import_module(self.module_path+'.generation_worker');config=copy.deepcopy(self.config);config[self.config_key]['video']={'adapter':'ffmpeg-composition','model':'ffmpeg-composition-v1','model_digest':self.video.fingerprint(),'rights_note':'Composición local; contenido sintético de pruebas','cost_units':100,'max_output_tokens':64};env=patch.dict('os.environ',{'COMMERCIAL_GENERATION_PROFILES':json.dumps(config)});env.start();self.addCleanup(env.stop)
 def create_video(self,plan=None):
  self.prepare_video();return self.gen.command(self.body(kind='VIDEO',profile_id='video',prompt=json.dumps(plan or PLAN)))['job_id']
 def test_actual_private_mp4_and_human_review(self):
  ref=self.create_video();self.worker.process(self.gen.crm,ref);item=self.gen.get(ref);self.assertEqual(item['status'],'SUCCEEDED',item.get('error_code'));raw,mime=self.gen.bytes(ref);artifact=Path('/tmp/gc014-rendered-artifacts');artifact.mkdir(exist_ok=True);(artifact/(self.module_path+'.mp4')).write_bytes(raw);self.assertEqual(mime,'video/mp4');self.assertTrue(item['trace']['composition']);self.assertFalse(item['trace']['generative_video']);self.assertFalse(item['trace']['voice_cloned']);self.assertEqual(len(item['trace']['subtitles']),2);self.assertFalse(item['published'])
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'test.mp4';p.write_bytes(raw);probe=json.loads(subprocess.run(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(p)],capture_output=True,check=True).stdout);v=next(s for s in probe['streams'] if s['codec_type']=='video');self.assertEqual((v['width'],v['height']),(360,640));self.assertEqual(v['codec_name'],'h264');self.assertAlmostEqual(float(probe['format']['duration']),2,delta=.15)
  self.gen.command(self.body('review',ref,3,confirmed_content=True,confirmed_rights=True,note='Revisión de laboratorio'));self.assertEqual(self.gen.get(ref)['status'],'REVIEWED')
  with self.assertRaises(self.error):self.worker.process(self.gen.crm,ref)
 def test_reject_invalid_scene_tool_url_and_audio_authorization(self):
  self.prepare_video()
  for edit in [dict(format='http://evil'),dict(scenes=[{'text':'x','seconds':True}]),dict(scenes=[{'text':'x','seconds':31}]),dict(voice={'url':'https://evil'}),dict(scenes=[{'text':'x','seconds':1,'shell':'touch x'}])]:
   with self.subTest(edit=edit):
    with self.assertRaises(self.error):self.gen.command(self.body(kind='VIDEO',profile_id='video',prompt=json.dumps({**PLAN,**edit})))
 def test_renderer_change_fails_without_fake_video(self):
  ref=self.create_video()
  with patch.object(self.video,'fingerprint',return_value='b'*64):self.worker.process(self.gen.crm,ref)
  self.assertEqual(self.gen.get(ref)['status'],'FAILED');self.assertEqual(self.gen.get(ref)['error_code'],'VIDEO_RENDERER_CHANGED')
  with self.assertRaises(self.error):self.gen.bytes(ref)
 def test_foreign_audio_cannot_be_read_or_processed(self):
  plan={**PLAN,'voice':{'item_id':str(uuid.uuid4()),'version':1,'sha256':'a'*64,'rights_confirmed':True}};ref=self.create_video(plan);self.worker.process(self.gen.crm,ref);self.assertEqual(self.gen.get(ref)['status'],'FAILED');self.assertIsNone(self.gen.get(ref)['result'])
 def test_render_deadline_error_is_explicit(self):
  self.prepare_video()
  with patch.object(self.video,'fingerprint',return_value='a'*64),patch.object(self.video.subprocess,'run',side_effect=subprocess.TimeoutExpired('ffmpeg',90)):
   with self.assertRaises(self.error) as exc:self.video.render(PLAN,'a'*64)
  self.assertEqual(str(exc.exception),'VIDEO_COMPOSITION_FAILED')
 def test_audio_bytes_require_matching_authorized_reference(self):
  self.prepare_video()
  with self.assertRaises(self.error):self.video.render(PLAN,self.video.fingerprint(),{'voice':b'not a file'})

 def test_reviewed_audio_sources_mix_and_revoked_source_is_rejected(self):
  self.prepare_video();lib=importlib.import_module(self.module_path+'.library_api').service(self.gen.crm)
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'tone.mp4';subprocess.run(['ffmpeg','-v','error','-nostdin','-f','lavfi','-i','color=c=blue:s=64x64:r=24:d=3','-f','lavfi','-i','sine=frequency=440:duration=3','-c:v','libx264','-pix_fmt','yuv420p','-c:a','aac','-threads','1','-shortest','-y',str(p)],capture_output=True,check=True,timeout=20);raw=p.read_bytes()
  meta={'title':'Audio de laboratorio, tono sintético','classification':'MARKETING','brand':{'name':'Prueba','tagline':'','template':'SQUARE'},'rights':{'holder':'Fixture','license':'OWNED','reference':'Tono sintético sin voz humana','valid_until':None,'public_web':True}}
  ref=lib.upload({'request_id':str(uuid.uuid4()),'item_id':None,'expected_revision':0,'metadata':meta},raw,'video/mp4')['item_id'];lib.command({'request_id':str(uuid.uuid4()),'operation':'approve','item_id':ref,'expected_revision':1,'data':{'rights_confirmed':True,'privacy_reviewed':True}})
  raw,mime=lib.bytes(ref,1);audio={'item_id':ref,'version':1,'sha256':hashlib.sha256(raw).hexdigest(),'rights_confirmed':True};plan={**PLAN,'voice':audio,'music':audio}
  job=self.gen.command(self.body(kind='VIDEO',profile_id='video',prompt=json.dumps(plan)))['job_id'];self.worker.process(self.gen.crm,job);item=self.gen.get(job);self.assertEqual(item['status'],'SUCCEEDED',item.get('error_code'));self.assertEqual(len(item['trace']['audio_source_hashes']),2);self.assertFalse(item['trace']['voice_cloned'])
  job=self.gen.command(self.body(kind='VIDEO',profile_id='video',prompt=json.dumps(plan)))['job_id'];meta['rights']['license']='UNCONFIRMED';lib.command({'request_id':str(uuid.uuid4()),'operation':'revise','item_id':ref,'expected_revision':2,'data':meta});self.worker.process(self.gen.crm,job);self.assertEqual(self.gen.get(job)['status'],'FAILED');self.assertIsNone(self.gen.get(job)['result'])
