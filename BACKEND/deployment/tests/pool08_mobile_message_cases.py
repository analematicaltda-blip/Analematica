"""Own mobile messaging stores and strict provider request contracts. No real carrier calls."""
import importlib,json,os,uuid,io,hashlib,hmac,copy
from datetime import datetime,timedelta,timezone
from unittest.mock import patch
from urllib.parse import parse_qs
import httpx
from PIL import Image
class MobileCases:
 def setup_mobile(self):
  self.domain=importlib.import_module(self.module_path+'.mobile_messages');store=importlib.import_module(self.module_path+'.mobile_message_store');self.mobile=self.domain.MobileMessages(store.Store(self.gen.crm.store),self.gen.crm);self.worker=importlib.import_module(self.module_path+'.mobile_message_worker');self.adapter=importlib.import_module(self.module_path+'.mobile_message_adapters')
  p={'version':'fixture-1','adapter':'twilio-sms','from_id':'+15550000001','credential_env':'COMMERCIAL_MOBILE_SECRET_TWILIO_TEST','limit_daily':10,'max_segments':3,'estimate_minor':100,'currency':'COP','co_support_digest':'a'*64,'allow_dispatch':True,'media_max_bytes':1048576,'public_base_url':'https://media.example.test','wa_template_name':'','wa_language':'','wa_template_digest':'','allow_sms_link':False,'allowed_media_kinds':['IMAGE','VIDEO'],'wa_header_kind':'','media_max_seconds':60,'wa_template_body':''}
  self.policies={'SMS':p,'MMS':{**p,'adapter':'twilio-mms'},'WHATSAPP':{**p,'adapter':'meta-whatsapp','from_id':'12345678','credential_env':'COMMERCIAL_MOBILE_SECRET_META_TEST','wa_template_name':'approved_fixture','wa_language':'es_CO','wa_template_digest':'b'*64,'wa_header_kind':'IMAGE','wa_template_body':'Información autorizada: {{body}}'}}
  env=patch.dict(os.environ,{'COMMERCIAL_MOBILE_POLICIES':json.dumps({self.mobile.key():self.policies}),'COMMERCIAL_MOBILE_SECRET_TWILIO_TEST':json.dumps({'account_sid':'AC'+'a'*32,'auth_token':'t'*32}),'COMMERCIAL_MOBILE_SECRET_META_TEST':'test-token-not-a-real-account-00000000','COMMERCIAL_MOBILE_RECEIPT_KEYS':json.dumps({self.mobile.key():'r'*32}),'COMMERCIAL_MOBILE_WORKER_ENABLED':'1','COMMERCIAL_MOBILE_NETWORK_ENABLED':'1'});env.start();self.addCleanup(env.stop)
 def contact(self,channels=('SMS',)):
  crm=self.gen.crm;number='+573'+str(uuid.uuid4().int%1000000000).zfill(9);ref=crm.command({'request_id':str(uuid.uuid4()),'operation':'create','contact_id':None,'expected_revision':0,'data':{'name':'Contacto sintético','email':uuid.uuid4().hex+'@example.test','phone':number,'origin':'MOBILE_TEST','responsible_ref':crm.actor}})['contact_id']
  for channel in channels:
   c=crm.get(ref);crm.command({'request_id':str(uuid.uuid4()),'operation':'consent','contact_id':ref,'expected_revision':c['revision'],'data':{'channel':channel,'purpose':'MARKETING','granted':True,'evidence_digest':'a'*64,'expires_at':(datetime.now(timezone.utc)+timedelta(days=1)).isoformat()}})
  return ref
 def media(self,raw=None,mime='image/png'):
  lib=importlib.import_module(self.module_path+'.library_api').service(self.gen.crm);out=io.BytesIO();Image.new('RGB',(32,32),(17,48,75)).save(out,format='PNG');metadata={'title':'Marketing sintético','classification':'MARKETING','brand':{'name':'Empresa','tagline':'Prueba','template':'SQUARE'},'rights':{'holder':'Fixture','license':'OWNED','reference':'Imagen creada en laboratorio','valid_until':None,'public_web':True}};ref=lib.upload({'request_id':str(uuid.uuid4()),'item_id':None,'expected_revision':0,'metadata':metadata},raw if raw is not None else out.getvalue(),mime)['item_id']
  for op,rev,data in [('approve',1,{'rights_confirmed':True,'privacy_reviewed':True}),('publish',2,{'confirmed':True})]:lib.command({'request_id':str(uuid.uuid4()),'operation':op,'item_id':ref,'expected_revision':rev,'data':data})
  return {'item_id':ref,'version':1,'sha256':lib.get(ref)['versions'][0]['delivery_sha256']}
 def body(self,op='create',ref=None,rev=0,**data):
  if op=='create':data={'title':'Mensaje local','channel':'SMS','contact_id':self.contact(),'body':'Mensaje de prueba','mode':'TEXT','media_ref':None,'confirmed_link':False,**data}
  return {'request_id':str(uuid.uuid4()),'operation':op,'job_id':ref,'expected_revision':rev,'data':data}
 def create_mobile(self,**data):return self.mobile.command(self.body(**data))['job_id']
 def queue(self,ref):
  self.mobile.command(self.body('review',ref,1,confirmed_content=True,confirmed_recipient=True));self.mobile.command(self.body('queue',ref,2,confirmed_impact=True,max_estimated_minor=10000))
 def client(self,bad=None):
  self.requests=[]
  def send(request):
   self.requests.append(request)
   if bad=='timeout':raise httpx.ReadTimeout('PRIVATE_PROVIDER_ERROR',request=request)
   if bad=='redirect':return httpx.Response(302,headers={'Location':'https://untrusted.example.test'})
   if bad=='rejected':return httpx.Response(400,json={'error':'not accepted'})
   if request.url.host=='api.twilio.com':return httpx.Response(201,json={'sid':('invalid' if bad=='invalid' else 'SM'+'b'*32),'status':'queued'})
   if request.url.host=='graph.facebook.com':return httpx.Response(200,json={'messages':[{'id':'wamid.fixture_123'}]})
   raise AssertionError('Unapproved provider host')
  def factory(**kwargs):
   self.assertFalse(kwargs['follow_redirects']);self.assertFalse(kwargs['trust_env']);return httpx.Client(transport=httpx.MockTransport(send),**kwargs)
  return factory
 def test_draft_has_no_network_and_exact_idempotent_receipt(self):
  self.setup_mobile();body=self.body();r=self.mobile.command(body);self.assertTrue(self.mobile.command(body)['replayed']);self.assertEqual(self.mobile.receipt(body['request_id'])['job_id'],r['job_id']);self.assertEqual(self.mobile.get(r['job_id'])['attempts'],0)
  body['data']['body']='Otro mensaje'
  with self.assertRaises(self.error):self.mobile.command(body)
 def test_sms_encoding_length_and_cost_are_estimates(self):
  self.setup_mobile();self.assertEqual(self.domain.segments('a'*160)['segments'],1);self.assertEqual(self.domain.segments('a'*161)['segments'],2);self.assertEqual(self.domain.segments('^'*81)['segments'],2);self.assertEqual(self.domain.segments('😀'*36)['segments'],2)
  ref=self.create_mobile(body='😀'*36);prepared=self.mobile.get(ref)['prepared'];self.assertEqual(prepared['quote']['estimated_minor'],200);self.assertIsNone(prepared['quote']['actual_minor']);self.assertFalse(prepared['sms_contains_attachment'])
 def test_sms_request_contains_no_attachment_and_acceptance_is_not_delivery(self):
  self.setup_mobile();ref=self.create_mobile();self.queue(ref);self.worker.process(self.gen.crm,ref,client_factory=self.client());d=self.mobile.get(ref);self.assertEqual(d['status'],'ACCEPTED');self.assertIsNone(d['delivered_at']);self.assertIsNone(d['sent_at']);self.assertIsNone(d['read_at']);self.assertIsNone(d['actual_cost_minor']);fields=parse_qs(self.requests[0].content.decode());self.assertNotIn('MediaUrl',fields);self.assertEqual(fields['Body'],['Mensaje de prueba'])
  with self.assertRaises(self.error):self.worker.process(self.gen.crm,ref,client_factory=self.client())
 def test_separate_mms_and_whatsapp_contracts_use_reviewed_media(self):
  self.setup_mobile()
  for channel in ['MMS','WHATSAPP']:
   ref=self.create_mobile(channel=channel,contact_id=self.contact((channel,)),mode='MULTIMEDIA',media_ref=self.media());self.queue(ref);self.worker.process(self.gen.crm,ref,client_factory=self.client());self.assertEqual(self.mobile.get(ref)['status'],'ACCEPTED')
   if channel=='MMS':self.assertIn('MediaUrl',parse_qs(self.requests[0].content.decode()))
   else:
    data=json.loads(self.requests[0].content);self.assertEqual(data['type'],'template');self.assertEqual(data['template']['name'],'approved_fixture');self.assertEqual(data['template']['components'][0]['parameters'][0]['type'],'image')
 def test_consent_is_per_channel_and_no_implicit_fallback(self):
  self.setup_mobile();ref=self.create_mobile(channel='MMS',contact_id=self.contact(('SMS',)),mode='MULTIMEDIA',media_ref=self.media());self.mobile.command(self.body('review',ref,1,confirmed_content=True,confirmed_recipient=True))
  with self.assertRaises(self.error):self.mobile.command(self.body('queue',ref,2,confirmed_impact=True,max_estimated_minor=10000))
  with self.assertRaises(self.error):self.create_mobile(media_ref=self.media())
  with self.assertRaises(self.error):self.create_mobile(body='Consulta https://example.test')
 def test_sms_link_alternative_needs_policy_and_explicit_authorization(self):
  self.setup_mobile();asset=self.media()
  with self.assertRaises(self.error):self.create_mobile(mode='TEXT_WITH_LINK',media_ref=asset,confirmed_link=True)
  policies=copy.deepcopy(self.policies);policies['SMS']['allow_sms_link']=True
  with patch.dict(os.environ,{'COMMERCIAL_MOBILE_POLICIES':json.dumps({self.mobile.key():policies})}):
   with self.assertRaises(self.error):self.create_mobile(mode='TEXT_WITH_LINK',media_ref=asset,confirmed_link=False)
   ref=self.create_mobile(mode='TEXT_WITH_LINK',media_ref=asset,confirmed_link=True);self.queue(ref);self.worker.process(self.gen.crm,ref,client_factory=self.client());fields=parse_qs(self.requests[0].content.decode());self.assertNotIn('MediaUrl',fields);self.assertIn('https://media.example.test',fields['Body'][0])
 def test_withdrawn_media_or_consent_blocks_dispatch(self):
  self.setup_mobile();asset=self.media();ref=self.create_mobile(channel='MMS',contact_id=self.contact(('MMS',)),mode='MULTIMEDIA',media_ref=asset);self.queue(ref);lib=importlib.import_module(self.module_path+'.library_api').service(self.gen.crm);lib.command({'request_id':str(uuid.uuid4()),'operation':'withdraw','item_id':asset['item_id'],'expected_revision':3,'data':{'confirmed':True}})
  with self.assertRaises(self.error):self.worker.process(self.gen.crm,ref,client_factory=self.client())
  self.assertEqual(self.mobile.get(ref)['attempts'],0)
 def test_timeout_redirect_and_malformed_ack_never_infer_success(self):
  self.setup_mobile()
  for bad in ['timeout','redirect','invalid']:
   ref=self.create_mobile();self.queue(ref);self.worker.process(self.gen.crm,ref,client_factory=self.client(bad));self.assertEqual(self.mobile.get(ref)['status'],'UNCERTAIN')
   with self.assertRaises(self.error):self.mobile.claim(ref)
 def test_signed_receipt_and_opt_out_block_pending_jobs(self):
  self.setup_mobile();contact=self.contact();first=self.create_mobile(contact_id=contact);second=self.create_mobile(contact_id=contact);self.queue(first);self.queue(second);self.worker.process(self.gen.crm,first,client_factory=self.client());d=self.mobile.get(first);body={'event_id':str(uuid.uuid4()),'job_id':first,'provider_message_id':d['provider_message_id'],'status':'DELIVERED','occurred_at':datetime.now(timezone.utc).isoformat()};signature=hmac.new(b'r'*32,self.domain.digest(body).encode(),hashlib.sha256).hexdigest()
  with self.assertRaises(self.error):self.mobile.provider_receipt(body,'f'*64)
  self.mobile.provider_receipt(body,signature);self.assertTrue(self.mobile.provider_receipt(body,signature)['replayed']);self.assertIsNone(self.mobile.get(first)['sent_at']);self.assertIsNone(self.mobile.get(first)['read_at'])
  body={**body,'event_id':str(uuid.uuid4()),'status':'OPT_OUT'};self.mobile.provider_receipt(body,hmac.new(b'r'*32,self.domain.digest(body).encode(),hashlib.sha256).hexdigest());self.assertEqual(self.mobile.get(second)['status'],'SUPPRESSED')
 def test_network_and_worker_disabled_without_provider_calls(self):
  self.setup_mobile();ref=self.create_mobile();self.queue(ref)
  for key in ['COMMERCIAL_MOBILE_NETWORK_ENABLED','COMMERCIAL_MOBILE_WORKER_ENABLED']:
   with patch.dict(os.environ,{key:'0'}):
    with self.assertRaises(self.error):self.worker.process(self.gen.crm,ref,client_factory=self.client())
  self.assertEqual(self.mobile.get(ref)['attempts'],0)
 def test_audit_failure_rolls_back_draft(self):
  self.setup_mobile();body=self.body()
  with patch.object(self.mobile.store,'append',side_effect=RuntimeError('Synthetic audit error')):
   with self.assertRaises(RuntimeError):self.mobile.command(body)
  self.assertEqual(self.mobile.list()['jobs'],[])
 def test_limits_template_binding_and_malformed_text_rejected(self):
  self.setup_mobile()
  with self.assertRaises(self.error):self.create_mobile(body='😀'*200)
  with self.assertRaises(self.error):self.create_mobile(body='bad\ud800')
  policies=copy.deepcopy(self.policies);policies['WHATSAPP']['wa_header_kind']='VIDEO'
  with patch.dict(os.environ,{'COMMERCIAL_MOBILE_POLICIES':json.dumps({self.mobile.key():policies})}):
   with self.assertRaises(self.error):self.create_mobile(channel='WHATSAPP',contact_id=self.contact(('WHATSAPP',)),mode='MULTIMEDIA',media_ref=self.media())
 def test_daily_quota_lease_recovery_and_provider_rejection(self):
  self.setup_mobile();policies=copy.deepcopy(self.policies);policies['SMS']['limit_daily']=1
  with patch.dict(os.environ,{'COMMERCIAL_MOBILE_POLICIES':json.dumps({self.mobile.key():policies})}):
   first=self.create_mobile();second=self.create_mobile();self.queue(first);self.queue(second);self.worker.process(self.gen.crm,first,client_factory=self.client('rejected'));self.assertEqual(self.mobile.get(first)['status'],'REJECTED')
   with self.assertRaises(self.error):self.mobile.claim(second)
  ref=self.create_mobile();self.queue(ref);self.mobile.claim(ref);self.mobile.clock=lambda:datetime.now(timezone.utc)+timedelta(minutes=16);d=self.mobile.get(ref);self.mobile.command(self.body('recover',ref,d['revision']));self.assertEqual(self.mobile.get(ref)['status'],'UNCERTAIN')
  with self.assertRaises(self.error):self.mobile.claim(ref)
 def test_legacy_customer_alias_and_revoked_identity(self):
  self.setup_mobile()
  if self.module_path.startswith('apps.'):
   from apps.prestadores.mi_negocio.gestion_operativa.modulos_genericos.clientes.models import Cliente
   row=Cliente.objects.create(perfil_id=self.gen.store.provider,nombre='Cliente histórico',email=uuid.uuid4().hex+'@example.test',telefono='+573123456789');contact='customer:'+str(row.pk);c=self.gen.crm.get(contact);self.gen.crm.command({'request_id':str(uuid.uuid4()),'operation':'consent','contact_id':contact,'expected_revision':c['revision'],'data':{'channel':'SMS','purpose':'MARKETING','granted':True,'evidence_digest':'a'*64,'expires_at':(datetime.now(timezone.utc)+timedelta(days=1)).isoformat()}});ref=self.create_mobile(contact_id=contact);self.queue(ref)
   from apps.turismo.models import VerifiedCompanyLink
   from django.utils import timezone as tz
   VerifiedCompanyLink.objects.filter(provider_id=self.gen.store.provider).update(revoked_at=tz.now())
  else:
   ref=self.create_mobile();self.queue(ref)
   from app.models.user import Usuario
   u=self.gen.crm.store.db.get(Usuario,int(self.gen.crm.actor));u.activo=False;self.gen.crm.store.db.commit()
  with self.assertRaises(Exception):self.worker.process(self.gen.crm,ref,client_factory=self.client())
  self.assertEqual(self.mobile.raw(ref)['attempts'],0)
 def test_whatsapp_read_requires_signed_provider_report_sms_read_rejected(self):
  self.setup_mobile()
  for channel in ('SMS','WHATSAPP'):
   kw={} if channel=='SMS' else {'mode':'MULTIMEDIA','media_ref':self.media()};ref=self.create_mobile(channel=channel,contact_id=self.contact((channel,)),**kw);self.queue(ref);self.worker.process(self.gen.crm,ref,client_factory=self.client());d=self.mobile.get(ref);body={'event_id':str(uuid.uuid4()),'job_id':ref,'provider_message_id':d['provider_message_id'],'status':'READ','occurred_at':datetime.now(timezone.utc).isoformat()};signature=hmac.new(b'r'*32,self.domain.digest(body).encode(),hashlib.sha256).hexdigest()
   if channel=='SMS':
    with self.assertRaises(self.error):self.mobile.provider_receipt(body,signature)
    self.assertIsNone(self.mobile.get(ref)['read_at'])
   else:self.mobile.provider_receipt(body,signature);self.assertIsNotNone(self.mobile.get(ref)['read_at']);self.assertIsNone(self.mobile.get(ref)['delivered_at'])

 def test_video_media_uses_distinct_mms_and_whatsapp_video_payloads(self):
  import tempfile,subprocess
  from pathlib import Path
  self.setup_mobile()
  with tempfile.TemporaryDirectory() as directory:
   file=Path(directory)/'source.mp4';subprocess.run(['ffmpeg','-v','error','-nostdin','-f','lavfi','-i','color=c=blue:s=64x64:r=24:d=1','-c:v','libx264','-pix_fmt','yuv420p','-threads','1','-y',str(file)],capture_output=True,check=True,timeout=20);raw=file.read_bytes()
  policies=copy.deepcopy(self.policies);policies['WHATSAPP']['wa_header_kind']='VIDEO';policies['WHATSAPP']['wa_template_name']='approved_video_fixture';policies['WHATSAPP']['wa_template_digest']='c'*64
  with patch.dict(os.environ,{'COMMERCIAL_MOBILE_POLICIES':json.dumps({self.mobile.key():policies})}):
   for channel in ('MMS','WHATSAPP'):
    asset=self.media(raw,'video/mp4');ref=self.create_mobile(channel=channel,contact_id=self.contact((channel,)),mode='MULTIMEDIA',media_ref=asset);self.queue(ref);self.worker.process(self.gen.crm,ref,client_factory=self.client());self.assertEqual(self.mobile.get(ref)['prepared']['media']['kind'],'VIDEO');self.assertEqual(self.mobile.get(ref)['status'],'ACCEPTED')
    if channel=='MMS':self.assertIn('MediaUrl',parse_qs(self.requests[0].content.decode()))
    else:self.assertEqual(json.loads(self.requests[0].content)['template']['components'][0]['parameters'][0]['type'],'video')
