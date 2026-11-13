"""Provider contracts with simulated HTTPS; real video conversion, no external sends."""
import base64
from email import policy
from email.parser import BytesParser
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import Mock,patch
import requests
from fastapi.testclient import TestClient
from BACKEND.infra.node6.engine import Config,Engine,WorkerError
from BACKEND.infra.node6.main import create_app
from BACKEND.infra.node6.social import Social,oauth1
from BACKEND.infra.node6.adaptation import adapt,PROFILES

class AdapterTests(unittest.TestCase):
 def setUp(self):
  switch=patch.dict(os.environ,{'NODE6_CAMPAIGNS_ENABLED':'1'});switch.start();self.addCleanup(switch.stop)
  self.temp=tempfile.TemporaryDirectory();self.engine=Engine(Config(token='internal-test-key',output=Path(self.temp.name)));self.engine.client=Mock();self.social=Social(self.engine)
  self.filename='a'*32+'.mp4';(self.engine.config.output/self.filename).write_bytes(b'\x00\x00\x00\x18ftypmp42test-video')
 def tearDown(self):self.temp.cleanup()
 def response(self,value=None,status=200,headers=None):return Mock(status_code=status,headers=headers or {},content=b'{}' if value is not None else b'',json=lambda:value)
 def test_preview_node_rejects_delivery_even_with_valid_operator_auth(self):
  client=TestClient(create_app(self.engine.config))
  body={'workspace':'tenant:1','job_id':'01234567-1234-4234-9234-012345678901','phase':0,'provider':'gmail','filename':self.filename,'credentials':{},'title':'Test'}
  with patch.dict(os.environ,{'NODE6_CAMPAIGNS_ENABLED':'0'}),patch('BACKEND.infra.node6.main.deliver_campaign') as send:
   self.assertEqual(client.post('/internal/campaigns/deliver',headers={'Authorization':'Bearer internal-test-key'},json=body).status_code,409);send.assert_not_called()
 def test_oauth1_matches_published_reference_vector(self):
  credentials={'consumer_key':'dpf43f3p2l4k3l03','consumer_secret':'kd94hf93k423kf44','access_token':'nnch734d00sl2jdk','access_secret':'pfkkdhi9sl3r4s00'}
  with patch('BACKEND.infra.node6.social.secrets.token_hex',return_value='kllo9940pd9333jh'),patch('BACKEND.infra.node6.social.time.time',return_value=1191242096):
   header=oauth1('GET','http://photos.example.net/photos?file=vacation.jpg&size=original',credentials)
  self.assertIn('tR3%2BTy81lMeYAr%2FFid0kMTYa%2FWM%3D',header)
 def test_instagram_create_poll_publish_uses_public_url_and_header_auth(self):
  self.engine.client.request.side_effect=[self.response({'id':'container'}),self.response({'status_code':'FINISHED'}),self.response({'id':'post'})]
  credentials={'account_id':'123','access_token':'test-secret'}
  first=self.social.deliver('instagram',self.filename,credentials,'Title','Caption',public_video_url='https://media.example.org/video')
  self.assertEqual(first['outcome'],'pending')
  result=self.social.deliver('instagram',self.filename,credentials,'Title','Caption',state=first['provider_state'],public_video_url='https://media.example.org/video')
  self.assertEqual(result['outcome'],'published')
  calls=self.engine.client.request.call_args_list;self.assertEqual(len(calls),3);self.assertTrue(calls[-1].args[1].endswith('/123/media_publish'));self.assertEqual(calls[0].kwargs['headers']['Authorization'],'Bearer test-secret');self.assertNotIn('test-secret',calls[0].args[1])
 def test_facebook_video_upload_and_processing_status(self):
  self.engine.client.request.side_effect=[self.response({'id':'video'}),self.response({'status':{'video_status':'ready'}})]
  first=self.social.deliver('facebook',self.filename,{'page_id':'123','access_token':'test'},'Title','Description');self.assertEqual(first['outcome'],'pending')
  final=self.social.deliver('facebook',self.filename,{'page_id':'123','access_token':'test'},'Title','Description',state=first['provider_state']);self.assertEqual(final['outcome'],'published')
 def test_whatsapp_uses_approved_video_template_and_single_recipient(self):
  self.engine.client.request.side_effect=[self.response({'id':'media'}),self.response({'messages':[{'id':'message'}]})]
  result=self.social.deliver('whatsapp',self.filename,{'phone_number_id':'123','access_token':'test'},'Title','Description','+573001234567',options={'template_name':'approved_video','template_language':'es','template_variables':['One']})
  self.assertEqual(result['outcome'],'accepted');body=self.engine.client.request.call_args.kwargs['json'];self.assertEqual(body['to'],'573001234567');self.assertEqual(body['type'],'template');self.assertEqual(body['template']['components'][0]['parameters'][0]['video']['id'],'media')
 def test_gmail_has_individual_to_and_video_mime_attachment(self):
  self.engine.client.request.side_effect=[self.response({'access_token':'temporary-access'}),self.response({'id':'gmail-id'})]
  result=self.social.deliver('gmail',self.filename,{'client_id':'test','client_secret':'test','refresh_token':'test','sender_email':'sender@example.org'},'Title','Description','one@example.org',unsubscribe_url='https://example.org/unsubscribe?token=test')
  self.assertEqual(result['outcome'],'accepted');raw=self.engine.client.request.call_args.kwargs['json']['raw'];message=BytesParser(policy=policy.default).parsebytes(base64.urlsafe_b64decode(raw))
  self.assertEqual(message['To'],'one@example.org');self.assertIsNone(message['Bcc']);self.assertEqual(len(list(message.iter_attachments())),1);self.assertIn('One-Click',message['List-Unsubscribe-Post']);self.assertEqual(list(message.iter_attachments())[0].get_content_type(),'video/mp4')
 def test_x_chunked_upload_is_finalized_before_tweet(self):
  self.engine.client.request.side_effect=[self.response({'media_id_string':'123'}),self.response(status=204),self.response({'processing_info':{'state':'pending'}}),self.response({'processing_info':{'state':'succeeded'}}),self.response({'data':{'id':'tweet'}})]
  credentials={'consumer_key':'test','consumer_secret':'test','access_token':'test','access_secret':'test'}
  first=self.social.deliver('x',self.filename,credentials,'Title','Description');self.assertEqual(first['outcome'],'pending')
  result=self.social.deliver('x',self.filename,credentials,'Title','Description',state=first['provider_state']);self.assertEqual(result['outcome'],'published');self.assertEqual(self.engine.client.request.call_args.kwargs['json']['media']['media_ids'],['123']);self.assertTrue(self.engine.client.request.call_args.kwargs['headers']['Authorization'].startswith('OAuth '))
 def test_tiktok_queries_creator_privacy_then_uploads_and_polls(self):
  self.engine.client.request.side_effect=[self.response({'data':{'privacy_level_options':['SELF_ONLY']}}),self.response({'data':{'publish_id':'pub','upload_url':'https://open-upload.tiktokapis.com/upload/test'}}),self.response(status=204),self.response({'data':{'status':'PUBLISH_COMPLETE'}})]
  first=self.social.deliver('tiktok',self.filename,{'access_token':'test'},'Title','Description',options={'privacy':'SELF_ONLY'});self.assertEqual(first['outcome'],'pending')
  result=self.social.deliver('tiktok',self.filename,{'access_token':'test'},'Title','Description',state=first['provider_state']);self.assertEqual(result['outcome'],'published')
  self.assertTrue(self.engine.client.request.call_args_list[0].args[1].endswith('/creator_info/query/'));self.assertEqual(self.engine.client.request.call_args_list[1].kwargs['json']['post_info']['privacy_level'],'SELF_ONLY')
 def test_tiktok_refuses_unapproved_privacy_and_foreign_upload_host(self):
  self.engine.client.request.return_value=self.response({'data':{'privacy_level_options':['SELF_ONLY']}})
  with self.assertRaises(WorkerError):self.social.deliver('tiktok',self.filename,{'access_token':'test'},'Title','Description',options={'privacy':'PUBLIC_TO_EVERYONE'})
  self.engine.client.request.side_effect=[self.response({'data':{'privacy_level_options':['SELF_ONLY']}}),self.response({'data':{'publish_id':'pub','upload_url':'https://evil.example/upload'}})]
  result=self.social.deliver('tiktok',self.filename,{'access_token':'test'},'Title','Description');self.assertEqual(result['outcome'],'unknown');self.assertNotEqual(self.engine.client.request.call_args.args[0],'PUT')
 def test_rate_limits_wait_but_uncertain_network_failures_do_not_auto_resend(self):
  self.engine.client.request.return_value=self.response({'error':'quota'},429,{'Retry-After':'120'})
  result=self.social.deliver('gmail',self.filename,{'client_id':'test','client_secret':'test','refresh_token':'test','sender_email':'sender@example.org'},'Title','Description','one@example.org');self.assertEqual(result['retry_after'],120)
  self.engine.client.request.side_effect=requests.Timeout('NEVER-EXPOSE-THIS-CREDENTIAL')
  result=self.social.deliver('gmail',self.filename,{'client_id':'test','client_secret':'test','refresh_token':'test','sender_email':'sender@example.org'},'Title','Description','one@example.org');self.assertEqual(result['outcome'],'unknown');self.assertNotIn('NEVER-EXPOSE',str(result))
 def test_node_journal_prevents_duplicate_phase_and_never_saves_credentials(self):
  app=create_app(self.engine.config);client=TestClient(app);headers={'Authorization':'Bearer internal-test-key'}
  body={'workspace':'tenant:1','job_id':'01234567-1234-4234-9234-012345678901','phase':0,'provider':'gmail','filename':self.filename,'credentials':{'client_secret':'not-real-secret'},'title':'Title','recipient':'one@example.org'}
  with patch('BACKEND.infra.node6.campaign_dispatch.Social.deliver',autospec=True,return_value={'outcome':'accepted','remote_id':'once','provider_state':{}}) as deliver:
   for _ in range(2):self.assertEqual(client.post('/internal/campaigns/deliver',headers=headers,json=body).json()['remote_id'],'once')
   self.assertEqual(deliver.call_count,1);self.assertIsNot(deliver.call_args.args[0].engine.client,app.state.engine.client)
  cached=client.get('/internal/campaigns/result/tenant:1/'+body['job_id']+'/0',headers=headers);self.assertTrue(cached.json()['found']);self.assertNotIn('not-real-secret',cached.text)
  self.assertEqual(client.post('/internal/campaigns/deliver',headers=headers,json={**body,'title':'changed'}).status_code,409)
  self.assertEqual(client.post('/internal/campaigns/deliver',json=body).status_code,401)
 def test_real_adaptations_preserve_original_and_match_each_frame(self):
  generated=self.engine.reel('Adaptation test','Keep original',1);source=self.engine.artifact(generated['filename']);digest=hashlib.sha256(source.read_bytes()).digest()
  for profile,spec in PROFILES.items():
   result=adapt(self.engine,generated['filename'],profile);file=self.engine.artifact(result['filename']);metadata=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-of','json',str(file)]));video=next(stream for stream in metadata['streams'] if stream['codec_type']=='video');self.assertEqual((video['width'],video['height']),(spec['width'],spec['height']));self.assertEqual(video['codec_name'],'h264');self.assertEqual(video['pix_fmt'],'yuv420p');self.assertEqual(hashlib.sha256(source.read_bytes()).digest(),digest)

if __name__=='__main__':unittest.main()
