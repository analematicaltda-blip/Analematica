import base64
import io
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import Mock,patch
from fastapi.testclient import TestClient
from PIL import Image
from BACKEND.infra.node6.engine import Config
from BACKEND.infra.node6.main import create_app

class NodeTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.config=Config(token='test-node-token',api_key='test-provider-key-not-real',youtube_id='test-client',youtube_secret='test-secret',youtube_refresh='test-refresh',output=Path(self.temp.name))
        self.app=create_app(self.config);self.client=TestClient(self.app);self.headers={'Authorization':'Bearer test-node-token'}
    def tearDown(self):self.temp.cleanup()
    def test_provider_secret_is_persisted_privately_and_not_reflected(self):
        body={'api_key':'test-replacement-key','text_model':'gemini-2.5-flash','image_model':'gemini-2.5-flash-image'}
        result=self.client.put('/internal/providers/gemini',headers=self.headers,json=body)
        self.assertEqual(result.status_code,200)
        self.assertNotIn(body['api_key'],result.text)
        state=self.config.output/'.provider-settings.json'
        self.assertEqual(state.stat().st_mode & 0o777,0o600)
        restarted=create_app(self.config)
        self.assertEqual(restarted.state.engine.config.api_key,body['api_key'])
        invalid=self.client.put('/internal/providers/gemini',headers=self.headers,json={**body,'text_model':'bad/model'})
        self.assertEqual(invalid.status_code,422);self.assertNotIn(body['api_key'],invalid.text)
    def test_company_upload_uses_company_credentials_and_private_only(self):
        body={'filename':'a'*32+'.mp4','title':'test','description':'','made_for_kids':False,'confirm_private':True,'workspace':'tenant:123','youtube_client_id':'company-client','youtube_client_secret':'company-secret','youtube_refresh_token':'company-refresh'}
        with patch('BACKEND.infra.node6.main.YouTube') as youtube:
            youtube.return_value.upload.return_value={'privacy':'private','video_id':'test-only'}
            result=self.client.post('/internal/youtube/upload-private',headers=self.headers,json=body)
            self.assertEqual(result.status_code,200,result.text)
            self.assertEqual(youtube.call_args.kwargs['scope'],'tenant:123')
            self.assertEqual(youtube.call_args.args[0].config.youtube_refresh,'company-refresh')
            self.assertEqual(self.config.youtube_refresh,'test-refresh')
        result=self.client.post('/internal/youtube/upload-private',headers=self.headers,json={**body,'confirm_private':False})
        self.assertEqual(result.status_code,422);self.assertNotIn('company-secret',result.text)
    def test_auth_health_and_secret_redaction(self):
        self.assertEqual(self.client.get('/health').status_code,200)
        self.assertEqual(self.client.get('/status').status_code,401)
        response=self.client.get('/status',headers=self.headers)
        self.assertEqual(response.status_code,200)
        self.assertNotIn(self.config.api_key,response.text)
        self.assertFalse(response.json()['remote_inference_verified'])
    def test_gemini_text_image_and_errors(self):
        transport=Mock();self.app.state.engine.client=transport
        transport.request.return_value=Mock(status_code=200,content=b'{}',json=lambda:{'candidates':[{'content':{'parts':[{'text':'Guion para prueba'}]}}]})
        response=self.client.post('/studio/script',headers=self.headers,json={'prompt':'Prueba deportiva'})
        self.assertEqual(response.json()['text'],'Guion para prueba')
        args=transport.request.call_args
        self.assertEqual(args.kwargs['headers']['x-goog-api-key'],self.config.api_key)
        self.assertNotIn(self.config.api_key,args.args[1])
        picture=io.BytesIO();Image.new('RGB',(100,100),'#38BDF8').save(picture,format='PNG')
        transport.request.return_value=Mock(status_code=200,content=b'{}',json=lambda:{'candidates':[{'content':{'parts':[{'inlineData':{'mimeType':'image/png','data':base64.b64encode(picture.getvalue()).decode()}}]}}]})
        response=self.client.post('/studio/image',headers=self.headers,json={'prompt':'Imagen azul'})
        self.assertEqual(response.status_code,200)
        self.assertTrue((self.config.output/response.json()['filename']).exists())
        transport.request.return_value=Mock(status_code=403,content=self.config.api_key.encode())
        response=self.client.post('/studio/script',headers=self.headers,json={'prompt':'Prueba'})
        self.assertEqual(response.status_code,503);self.assertNotIn(self.config.api_key,response.text)
    def test_mcp_and_disabled_colibri(self):
        result=self.client.post('/mcp',headers=self.headers,json={'jsonrpc':'2.0','id':1,'method':'initialize','params':{'protocolVersion':'2025-03-26'}})
        self.assertEqual(result.json()['result']['serverInfo']['name'],'sgacd-node6')
        result=self.client.post('/mcp',headers=self.headers,json={'jsonrpc':'2.0','id':2,'method':'tools/list'})
        self.assertEqual(len(result.json()['result']['tools']),5)
        result=self.client.post('/mcp',headers=self.headers,json={'jsonrpc':'2.0','id':3,'method':'tools/call','params':{'name':'generate_script','arguments':{'prompt':'test','provider':'colibri'}}})
        self.assertTrue(result.json()['result']['isError'])
    def test_colibri_uses_the_advertised_model(self):
        self.config.colibri_url='http://colibri:8000/v1'
        transport=Mock();self.app.state.engine.client=transport
        transport.get.return_value=Mock(json=lambda:{'data':[{'id':'configured-model'}]})
        transport.post.return_value=Mock(json=lambda:{'choices':[{'message':{'content':'Local test response'}}]})
        response=self.client.post('/studio/script',headers=self.headers,json={'prompt':'Test','provider':'colibri'})
        self.assertEqual(response.status_code,200)
        self.assertEqual(transport.post.call_args.kwargs['json']['model'],'configured-model')
        self.assertEqual(transport.get.call_args.args[0],'http://colibri:8000/v1/models')
        self.assertEqual(self.client.post('/studio/image',headers=self.headers,json={'prompt':'Test','provider':'colibri'}).status_code,422)
    def test_real_reel_and_draft(self):
        result=self.client.post('/studio/reel',headers=self.headers,json={'title':"Prueba: 'segura' $(sin ejecutar)",'caption':'Deporte y cultura','duration':1})
        self.assertEqual(result.status_code,200,result.text)
        body=result.json();self.assertFalse(body['ai_video'])
        file=self.config.output/body['filename']
        metadata=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(file)]))
        self.assertEqual((metadata['streams'][0]['width'],metadata['streams'][0]['height']),(1080,1920))
        self.assertGreater(float(metadata['format']['duration']),.9)
        self.assertEqual(self.client.get('/artifacts/'+body['filename'],headers=self.headers).status_code,200)
        draft=self.client.post('/social/draft',headers=self.headers,json={'filename':body['filename'],'title':'Prueba','description':'Contenido de prueba','platforms':['youtube']}).json()
        self.assertFalse(draft['published'])
        self.assertEqual(draft['status'],'draft')
        self.assertEqual(self.client.get('/artifacts/..%2Fsecret.env',headers=self.headers).status_code,404)
        self.assertEqual(self.client.post('/studio/reel',headers=self.headers,json={'title':'test','duration':9999}).status_code,422)
    def test_youtube_is_private_and_duplicate_prevented(self):
        name='a'*32+'.mp4';(self.config.output/name).write_bytes(b'fake-media-unit-test')
        transport=Mock();self.app.state.engine.client=transport
        transport.post.side_effect=[Mock(status_code=200,json=lambda:{'access_token':'test-google-token'}),Mock(status_code=200,headers={'Location':'https://www.googleapis.com/upload/youtube/v3/videos?upload_id=test'})]
        transport.put.return_value=Mock(status_code=200,json=lambda:{'id':'private123','status':{'privacyStatus':'private'}})
        payload={'filename':name,'title':'Prueba privada','description':'Prueba','made_for_kids':False,'confirm_private':True}
        response=self.client.post('/youtube/upload-private',headers=self.headers,json=payload)
        self.assertEqual(response.status_code,200,response.text)
        self.assertEqual(transport.post.call_args_list[1].kwargs['json']['status']['privacyStatus'],'private')
        response=self.client.post('/youtube/upload-private',headers=self.headers,json=payload)
        self.assertTrue(response.json()['duplicate_prevented']);self.assertEqual(transport.put.call_count,1)
        payload['privacyStatus']='public'
        self.assertEqual(self.client.post('/youtube/upload-private',headers=self.headers,json=payload).status_code,422)
        self.assertEqual(transport.put.call_count,1)
    def test_youtube_rejects_foreign_upload_location(self):
        name='b'*32+'.mp4';(self.config.output/name).write_bytes(b'fake-media-unit-test')
        transport=Mock();self.app.state.engine.client=transport
        transport.post.side_effect=[Mock(json=lambda:{'access_token':'test-token'}),Mock(headers={'Location':'https://attacker.example/upload'})]
        response=self.client.post('/youtube/upload-private',headers=self.headers,json={'filename':name,'title':'Prueba','made_for_kids':False,'confirm_private':True})
        self.assertEqual(response.status_code,502);transport.put.assert_not_called()

if __name__=='__main__':unittest.main()
