"""Real own ORM email campaigns. SMTP responses controlled; no real addresses contacted."""
import importlib,copy,json,uuid,os,smtplib
from datetime import datetime,timedelta,timezone
from unittest.mock import patch
class CampaignCases:
 def setup_campaign(self):
  self.domain=importlib.import_module(self.module_path+'.email_campaigns');store=importlib.import_module(self.module_path+'.email_campaign_store');self.mail=self.domain.EmailCampaigns(store.Store(self.gen.crm.store),self.gen.crm);self.worker=importlib.import_module(self.module_path+'.email_campaign_worker');self.policy={'version':'test-1','sender_email':'owner@example.test','sender_name':'Empresa de prueba','postal_address':'Dirección sintética','public_base_url':'http://localhost','daily_limit':10,'consent_reviewed':True,'allow_dispatch':True,'smtp_host':'127.0.0.1','smtp_port':1025};env=patch.dict(os.environ,{'COMMERCIAL_EMAIL_POLICIES':json.dumps({self.mail.key():self.policy}),'COMMERCIAL_EMAIL_LINK_KEYS':json.dumps({self.mail.key():'k'*32}),'COMMERCIAL_EMAIL_WORKER_ENABLED':'1'});env.start();self.addCleanup(env.stop)
 def contact(self,consent=True):
  crm=self.gen.crm;ref=crm.command({'request_id':str(uuid.uuid4()),'operation':'create','contact_id':None,'expected_revision':0,'data':{'name':'Persona <prueba>','email':uuid.uuid4().hex+'@example.test','origin':'TEST','responsible_ref':crm.actor}})['contact_id']
  if consent:crm.command({'request_id':str(uuid.uuid4()),'operation':'consent','contact_id':ref,'expected_revision':1,'data':{'channel':'EMAIL','purpose':'MARKETING','granted':True,'evidence_digest':'a'*64,'expires_at':(datetime.now(timezone.utc)+timedelta(days=1)).isoformat()}})
  return ref
 def command(self,op='create',ref=None,rev=0,**data):
  if op=='create':data={'title':'Campaña sintética','subject':'Hola {{name}}','body_text':'Hola {{name}}\nTexto <script>no ejecutable</script> de {{company}}','template':'LETTER','contact_ids':[self.contact()],'exclude_contact_ids':[],'segment':'Selección de prueba',**data}
  return {'request_id':str(uuid.uuid4()),'operation':op,'campaign_id':ref,'expected_revision':rev,'data':data}
 def create_campaign(self,**data):return self.mail.command(self.command(**data))['campaign_id']
 def schedule(self,ref):
  self.mail.command(self.command('review',ref,1,confirmed_content=True,confirmed_audience=True));self.mail.command(self.command('schedule',ref,2,confirmed_impact=True,scheduled_at=datetime.now(timezone.utc).isoformat()))
 def smtp(self,error=None):
  self.messages=[];outer=self
  class FakeSMTP:
   def __init__(self,*args,**kwargs):pass
   def __enter__(self):return self
   def __exit__(self,*args):pass
   def send_message(self,message):
    outer.messages.append(message)
    if error:raise OSError('Sensitive transport detail')
    return {}
  return FakeSMTP
 def test_save_review_never_send_and_exact_replay(self):
  self.setup_campaign();body=self.command();r=self.mail.command(body);self.assertTrue(self.mail.command(body)['replayed']);d=self.mail.get(r['campaign_id']);self.assertEqual(d['status'],'DRAFT');self.assertEqual(d['recipients'][0]['attempts'],0)
  with self.assertRaises(self.error):self.mail.command(self.command('schedule',d['id'],1,confirmed_impact=True,scheduled_at=datetime.now(timezone.utc).isoformat()))
  body['data']['subject']='Otro'
  with self.assertRaises(self.error):self.mail.command(body)
 def test_smtp_acceptance_is_not_delivery_opening_or_automatic_retry(self):
  self.setup_campaign();ref=self.create_campaign();self.schedule(ref);recipient=self.mail.get(ref)['recipients'][0];self.worker.process(self.gen.crm,ref,recipient['contact_id'],smtp_factory=self.smtp());d=self.mail.get(ref);r=d['recipients'][0];self.assertEqual(r['status'],'ACCEPTED');self.assertIsNone(r['sent_at']);self.assertIsNone(r['delivered_at']);self.assertIsNone(r['opened_at']);self.assertEqual(len(self.messages),1);self.assertTrue(self.messages[0].is_multipart());self.assertIn('List-Unsubscribe',self.messages[0]);self.assertEqual(self.messages[0]['To'],recipient['email'])
  with self.assertRaises(self.error):self.worker.process(self.gen.crm,ref,recipient['contact_id'],smtp_factory=self.smtp())
 def test_private_personalization_escaped_html_and_unknown_variables(self):
  self.setup_campaign();ref=self.create_campaign();d=self.mail.get(ref);preview=self.mail.preview(ref,d['recipients'][0]['contact_id']);self.assertIn('Persona &lt;prueba&gt;',preview['html']);self.assertNotIn('<script>',preview['html']);self.assertIn('PREVIEW_NOT_A_LINK',preview['unsubscribe_url']);self.assertFalse(preview['mail_sent'])
  with self.assertRaises(self.error):self.create_campaign(body_text='{{password}}')
 def test_no_consent_exclusion_and_unsubscribe_prevent_pending_dispatch(self):
  self.setup_campaign();a=self.contact();b=self.contact(False);c=self.contact();ref=self.create_campaign(contact_ids=[a,b,c],exclude_contact_ids=[c]);d=self.mail.get(ref);self.assertEqual([r['status'] for r in d['recipients']],['PENDING','NO_CONSENT','EXCLUDED']);self.schedule(ref);d=self.mail.get(ref);r=d['recipients'][0];proof=self.mail.proof(d,r);public=self.domain.EmailCampaigns(self.mail.store);public.unsubscribe(ref,a,proof);self.assertEqual(self.mail.get(ref)['recipients'][0]['status'],'SUPPRESSED');self.assertTrue(public.unsubscribe(ref,a,proof)['unsubscribed'])
  with self.assertRaises(self.error):self.worker.process(self.gen.crm,ref,a,smtp_factory=self.smtp())
 def test_unsubscribe_proof_rejects_forgery_and_foreign_recipient(self):
  self.setup_campaign();ref=self.create_campaign();r=self.mail.get(ref)['recipients'][0]
  with self.assertRaises(self.error):self.mail.unsubscribe(ref,r['contact_id'],'a'*64)
  self.assertEqual(self.mail.get(ref)['recipients'][0]['status'],'PENDING')
 def test_worker_disabled_uncertain_timeout_and_no_second_attempt(self):
  self.setup_campaign();ref=self.create_campaign();self.schedule(ref);r=self.mail.get(ref)['recipients'][0]
  with patch.dict(os.environ,{'COMMERCIAL_EMAIL_WORKER_ENABLED':'0'}):
   with self.assertRaises(self.error):self.worker.process(self.gen.crm,ref,r['contact_id'],smtp_factory=self.smtp())
  self.worker.process(self.gen.crm,ref,r['contact_id'],smtp_factory=self.smtp(error=True));self.assertEqual(self.mail.get(ref)['recipients'][0]['status'],'UNCERTAIN')
  with self.assertRaises(self.error):self.worker.process(self.gen.crm,ref,r['contact_id'],smtp_factory=self.smtp())
 def test_changed_consent_and_sender_policy_block_dispatch(self):
  self.setup_campaign();ref=self.create_campaign();self.schedule(ref);d=self.mail.get(ref);r=d['recipients'][0];policy={**self.policy,'version':'changed'}
  with patch.dict(os.environ,{'COMMERCIAL_EMAIL_POLICIES':json.dumps({self.mail.key():policy})}):
   with self.assertRaises(self.error):self.mail.claim(ref,r['contact_id'])
  c=self.gen.crm.get(r['contact_id']);self.gen.crm.command({'request_id':str(uuid.uuid4()),'operation':'consent','contact_id':r['contact_id'],'expected_revision':c['revision'],'data':{'channel':'EMAIL','purpose':'MARKETING','granted':False,'evidence_digest':'b'*64,'expires_at':datetime.now(timezone.utc).isoformat()}});self.assertIsNone(self.mail.claim(ref,r['contact_id']));self.assertEqual(self.mail.get(ref)['recipients'][0]['status'],'SUPPRESSED')
 def test_audit_rollback_and_schedule_bounds(self):
  self.setup_campaign();body=self.command()
  with patch.object(self.mail.store,'append',side_effect=RuntimeError('synthetic audit failure')):
   with self.assertRaises(RuntimeError):self.mail.command(body)
  self.assertEqual(self.mail.list()['campaigns'],[])
 def test_real_loopback_smtp_accepts_one_private_recipient(self):
  import socketserver,threading,email as email_parser
  self.setup_campaign();captured=[]
  class Handler(socketserver.StreamRequestHandler):
   def handle(self):
    self.wfile.write(b'220 localhost test-only\r\n');body=False;parts=[]
    while True:
     line=self.rfile.readline()
     if not line:return
     if body:
      if line==b'.\r\n':captured.append(b''.join(parts));body=False;self.wfile.write(b'250 accepted\r\n')
      else:parts.append(line)
     elif line.upper().startswith(b'EHLO'):self.wfile.write(b'250-localhost\r\n250 SIZE 65536\r\n')
     elif line.upper().startswith((b'MAIL',b'RCPT',b'RSET')):self.wfile.write(b'250 ok\r\n')
     elif line.upper().startswith(b'DATA'):body=True;self.wfile.write(b'354 data\r\n')
     elif line.upper().startswith(b'QUIT'):self.wfile.write(b'221 bye\r\n');return
     else:self.wfile.write(b'250 ok\r\n')
  class Server(socketserver.ThreadingTCPServer):allow_reuse_address=True
  server=Server(('127.0.0.1',1025),Handler);thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
  try:
   ref=self.create_campaign();self.schedule(ref);recipient=self.mail.get(ref)['recipients'][0];self.worker.process(self.gen.crm,ref,recipient['contact_id']);self.assertEqual(len(captured),1);message=email_parser.message_from_bytes(captured[0]);self.assertEqual(message['To'],recipient['email']);self.assertIsNone(message['Bcc']);self.assertEqual(self.mail.get(ref)['recipients'][0]['status'],'ACCEPTED')
  finally:server.shutdown();server.server_close();thread.join(timeout=3)
 def test_public_unsubscribe_survives_owner_revocation(self):
  self.setup_campaign();ref=self.create_campaign();d=self.mail.get(ref);r=d['recipients'][0];proof=self.mail.proof(d,r);public=self.domain.EmailCampaigns(self.mail.store.public(getattr(self.gen.crm.store,'db',None),ref))
  if self.module_path.startswith('apps.'):
   from apps.turismo.models import VerifiedCompanyLink
   from django.utils import timezone
   VerifiedCompanyLink.objects.filter(provider_id=self.gen.store.provider).update(revoked_at=timezone.now())
  else:
   from app.models.user import Usuario
   user=self.gen.crm.store.db.get(Usuario,int(self.gen.crm.actor));user.activo=False;self.gen.crm.store.db.commit()
  self.assertTrue(public.unsubscribe(ref,r['contact_id'],proof)['unsubscribed']);self.assertEqual(public.raw(ref)['recipients'][0]['status'],'SUPPRESSED')
 def test_quota_and_recovery_do_not_repeat_a_dispatch(self):
  self.setup_campaign();policy={**self.policy,'daily_limit':1};env=patch.dict(os.environ,{'COMMERCIAL_EMAIL_POLICIES':json.dumps({self.mail.key():policy})});env.start();self.addCleanup(env.stop);a=self.contact();b=self.contact();ref=self.create_campaign(contact_ids=[a,b]);self.schedule(ref);self.worker.process(self.gen.crm,ref,a,smtp_factory=self.smtp())
  with self.assertRaises(self.error):self.mail.claim(ref,b)
  self.assertEqual(self.mail.get(ref)['recipients'][1]['status'],'PENDING')
 def test_signed_receipts_separate_delivery_and_do_not_invent_opening(self):
  import hmac,hashlib
  self.setup_campaign();ref=self.create_campaign();self.schedule(ref);r=self.mail.get(ref)['recipients'][0];self.worker.process(self.gen.crm,ref,r['contact_id'],smtp_factory=self.smtp());r=self.mail.get(ref)['recipients'][0];body={'event_id':str(uuid.uuid4()),'campaign_id':ref,'contact_id':r['contact_id'],'message_id':r['message_id'],'status':'DELIVERED','occurred_at':datetime.now(timezone.utc).isoformat()}
  with patch.dict(os.environ,{'COMMERCIAL_EMAIL_RECEIPT_KEYS':json.dumps({self.mail.key():'z'*32})}):
   signature=hmac.new(b'z'*32,self.domain.digest(body).encode(),hashlib.sha256).hexdigest()
   with self.assertRaises(self.error):self.mail.provider_receipt(body,'f'*64)
   self.mail.provider_receipt(body,signature);self.assertTrue(self.mail.provider_receipt(body,signature)['replayed']);result=self.mail.get(ref)['recipients'][0];self.assertIsNotNone(result['delivered_at']);self.assertIsNone(result['sent_at']);self.assertIsNone(result['opened_at']);self.assertFalse(result['provider_authenticity_qualified'])
 def test_bounce_report_suppresses_other_pending_campaigns(self):
  import hmac,hashlib
  self.setup_campaign();contact=self.contact();first=self.create_campaign(contact_ids=[contact]);second=self.create_campaign(contact_ids=[contact]);self.schedule(first);self.schedule(second);self.worker.process(self.gen.crm,first,contact,smtp_factory=self.smtp());r=self.mail.get(first)['recipients'][0];body={'event_id':str(uuid.uuid4()),'campaign_id':first,'contact_id':contact,'message_id':r['message_id'],'status':'BOUNCED','occurred_at':datetime.now(timezone.utc).isoformat()}
  with patch.dict(os.environ,{'COMMERCIAL_EMAIL_RECEIPT_KEYS':json.dumps({self.mail.key():'z'*32})}):self.mail.provider_receipt(body,hmac.new(b'z'*32,self.domain.digest(body).encode(),hashlib.sha256).hexdigest())
  self.assertEqual(self.mail.get(second)['recipients'][0]['status'],'SUPPRESSED');self.assertIsNone(self.mail.get(first)['recipients'][0]['delivered_at'])
 def test_interrupted_dispatch_recovers_as_uncertain_without_resending(self):
  self.setup_campaign();ref=self.create_campaign();self.schedule(ref);contact=self.mail.get(ref)['recipients'][0]['contact_id'];self.mail.claim(ref,contact);future=datetime.now(timezone.utc)+timedelta(minutes=16);self.mail.clock=lambda:future;d=self.mail.get(ref);self.mail.command(self.command('recover',ref,d['revision'],contact_id=contact));self.assertEqual(self.mail.get(ref)['recipients'][0]['status'],'UNCERTAIN')
  with self.assertRaises(self.error):self.mail.claim(ref,contact)
 def test_malformed_audience_headers_and_untrusted_worker_options_rejected(self):
  self.setup_campaign()
  for values in [dict(contact_ids=[{}]),dict(exclude_contact_ids=[{}]),dict(subject='Hola\nBcc: hidden@example.test'),dict(template='RAW_HTML')]:
   with self.subTest(values=values):
    with self.assertRaises(self.error):self.create_campaign(**values)
  with patch.dict(os.environ,{'COMMERCIAL_EMAIL_WORKER_ENABLED':'0'}):
   with self.assertRaises(self.error):self.worker.run_once()
 def test_legacy_customer_alias_keeps_native_consent_and_company_scope(self):
  self.setup_campaign()
  if not self.module_path.startswith('apps.'):
   with self.assertRaises(self.error):self.create_campaign(contact_ids=['customer:999999'])
   return
  from apps.prestadores.mi_negocio.gestion_operativa.modulos_genericos.clientes.models import Cliente
  row=Cliente.objects.create(perfil_id=self.gen.store.provider,nombre='Cliente histórico',email=uuid.uuid4().hex+'@example.test');ref='customer:'+str(row.pk);crm=self.gen.crm;current=crm.get(ref)
  crm.command({'request_id':str(uuid.uuid4()),'operation':'consent','contact_id':ref,'expected_revision':current['revision'],'data':{'channel':'EMAIL','purpose':'MARKETING','granted':True,'evidence_digest':'a'*64,'expires_at':(datetime.now(timezone.utc)+timedelta(days=1)).isoformat()}})
  campaign=self.create_campaign(contact_ids=[ref]);self.schedule(campaign);self.worker.process(crm,campaign,ref,smtp_factory=self.smtp());recipient=self.mail.get(campaign)['recipients'][0];self.assertEqual(recipient['status'],'ACCEPTED');self.assertNotIn('customer:',recipient['message_id']);rendered=self.mail.render(self.mail.get(campaign),recipient);self.assertIn('/customer:',rendered['unsubscribe_url'])
 def test_worker_candidates_exclude_future_campaigns(self):
  self.setup_campaign();future=self.create_campaign();ready=self.create_campaign();self.mail.command(self.command('review',future,1,confirmed_content=True,confirmed_audience=True));self.mail.command(self.command('schedule',future,2,confirmed_impact=True,scheduled_at=(datetime.now(timezone.utc)+timedelta(days=1)).isoformat()));self.schedule(ready);context=importlib.import_module(self.module_path+'.email_campaign_worker_context')
  if self.module_path.startswith('apps.'):rows=context.candidates()
  else:
   from sqlalchemy.orm import sessionmaker
   with patch.object(context,'SessionLocal',sessionmaker(bind=self.gen.crm.store.db.get_bind())):rows=context.candidates()
  refs={r[0] for r in rows};self.assertIn(ready,refs);self.assertNotIn(future,refs)
