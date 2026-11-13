"""Real native ORM transactions and source revocation for public intake, both own systems."""
import runpy,unittest,importlib,re,html
from pathlib import Path
from unittest.mock import patch
f=runpy.run_path(str(Path(__file__).with_name('pool08_landings_native_check.py')),run_name='capture_native_setup')
from django.db import connection
from django.utils import timezone
from apps.turismo.models import VerifiedCompanyLink
for p in ('apps.prestadores.mi_negocio.gestion_comercial.pool08','apps.admin_plataforma.gestion_comercial.pool08'):
 models=importlib.import_module(p+'.capture_models')
 with connection.schema_editor() as editor:
  for m in (models.LandingCapture,models.CaptureEvent):
   if m._meta.db_table not in connection.introspection.table_names():editor.create_model(m)
def cases(system,path):
 m=importlib.import_module(path+'.capture_models');crm_m=importlib.import_module(path+'.crm_models');boundary=importlib.import_module(path+'.landing_capture_api');error=importlib.import_module(path+'.crm').CRMError
 class Checks(unittest.TestCase):
  def setUp(self):
   self.c=f['cases'](system,path)();self.c.setUp();self.addCleanup(self.c.doCleanups);self.b=self.c.body();self.b['data']['content']['capture']={'notice':'Aviso autorizado de prueba','privacy_url':'https://example.test/privacy','offer_ref':None}
   r=self.c.call(self.b);self.assertEqual(r.status_code,200,r.data);self.ref=r.data['landing_id']
   for op,rev in [('approve',1),('publish',2)]:
    b={**self.b,'request_id':__import__('uuid').uuid4().__str__(),'operation':op,'landing_id':self.ref,'expected_revision':rev,'data':{'confirmed':True}};self.assertEqual(self.c.call(b).status_code,200)
   self.handler=boundary.service(boundary.owner_crm(None,self.ref));self.browser='a'*32;page=self.handler.form(self.ref,self.browser,{},'/capture/','https://example.test/page');token=html.unescape(re.search('name="token" value="([^"]+)"',page).group(1));self.data={'token':token,'name':'Prospecto','email':'capture-'+__import__('uuid').uuid4().hex+'@example.test','phone':'','company_website':'','consent':'yes'}
  def submit(self):return self.handler.submit(self.ref,self.data,self.browser,'127.0.0.1')
  def test_audit_failure_rolls_back_contact_capture_and_consent(self):
   with patch.object(m.CaptureEvent.objects,'create',side_effect=RuntimeError('synthetic audit unavailable')):
    with self.assertRaises(RuntimeError):self.submit()
   self.assertEqual(m.LandingCapture.objects.filter(scope=str(self.c.c.base.tenant.pk)).count(),0);self.assertEqual(crm_m.CRMContact.objects.filter(scope=str(self.c.c.base.tenant.pk)).count(),0)
  def test_rate_limit_uses_committed_capture_rows(self):
   result=self.submit();row=m.LandingCapture.objects.get(pk=result['reference']);self.assertEqual(self.handler.store.recent(row.document['ip_digest'],'2000-01-01'),1)
   with patch.object(self.handler.store,'recent',return_value=10):
    page=self.handler.form(self.ref,self.browser,{},'/capture/','https://example.test/page');self.data['token']=html.unescape(re.search('name="token" value="([^"]+)"',page).group(1))
    with self.assertRaises(error) as caught:self.submit()
    self.assertEqual(caught.exception.status,429)
  def test_revoked_owner_cannot_receive_new_public_submission(self):
   VerifiedCompanyLink.objects.filter(pk=self.c.c.base.link.pk).update(revoked_at=timezone.now())
   with self.assertRaises(error) as caught:boundary.owner_crm(None,self.ref)
   self.assertEqual(caught.exception.status,403)
  def test_tampered_history_blocks_private_metrics(self):
   result=self.submit();m.CaptureEvent.objects.filter(item_id=result['reference']).update(document={'changed':True})
   with self.assertRaises(error):self.handler.metrics(self.ref)
  def test_anonymous_receipt_does_not_revoke_later_staff_authorization(self):
   from datetime import datetime,timezone,timedelta
   import uuid
   result=self.submit();record=self.handler.store.get(result['reference']);cid=record['contact_id']
   self.handler.crm.command({'request_id':str(uuid.uuid4()),'operation':'consent','contact_id':cid,'expected_revision':1,'data':{'channel':'EMAIL','purpose':'MARKETING','granted':True,'evidence_digest':'c'*64,'expires_at':(datetime.now(timezone.utc)+timedelta(days=30)).isoformat()}})
   self.handler.withdraw(self.ref,result['reference'],result['withdrawal_proof']);contact=self.handler.crm.get(cid);self.assertEqual(contact['status'],'PROSPECT');self.assertTrue(contact['consents']['EMAIL:MARKETING']['granted']);self.assertFalse(contact['consents']['EMAIL:SERVICE']['granted'])
  def test_expired_or_different_browser_proof_is_rejected(self):
   module=importlib.import_module(path+'.landing_capture')
   with self.assertRaises(error) as rejected:self.handler.submit(self.ref,self.data,'b'*32,'127.0.0.1')
   self.assertEqual(rejected.exception.status,403)
   import time
   with patch.object(module.time,'time',return_value=time.time()-1900):page=self.handler.form(self.ref,self.browser,{},'/capture/','https://example.test/page')
   self.data['token']=html.unescape(re.search('name="token" value="([^"]+)"',page).group(1))
   with self.assertRaises(error) as rejected:self.submit()
   self.assertEqual(rejected.exception.status,400)
  def test_withdrawal_replay_does_not_resurrect_contact(self):
   result=self.submit();self.handler.withdraw(self.ref,result['reference'],result['withdrawal_proof']);repeat=self.submit();self.assertTrue(repeat['withdrawn']);self.assertEqual(self.handler.metrics(self.ref)['observed']['created_prospects'],1)
 Checks.__name__=system.replace('-','')+'Capture';return Checks
ERP=cases('erp-tur','apps.prestadores.mi_negocio.gestion_comercial.pool08');Ana=cases('analematica','apps.admin_plataforma.gestion_comercial.pool08')
if __name__=='__main__':unittest.main()
