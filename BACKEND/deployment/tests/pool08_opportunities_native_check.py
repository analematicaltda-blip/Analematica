"""Actual owned opportunity models/API, local authority and rollback boundaries."""
import runpy,unittest,importlib,os,uuid,copy
from pathlib import Path
from unittest.mock import patch
from datetime import timedelta
fixture=runpy.run_path(str(Path(__file__).with_name('pool08_crm_native_check.py')),run_name='opportunity_native_fixture')
from django.db import connection
from django.utils import timezone
from rest_framework.test import APIRequestFactory,force_authenticate
from apps.turismo.models import VerifiedCompanyLink
from apps.core_erp.accounting.models import JournalEntry
from apps.prestadores.mi_negocio.gestion_comercial.sales.models import Opportunity,StageHistory
for path in ('apps.prestadores.mi_negocio.gestion_comercial.pool08','apps.admin_plataforma.gestion_comercial.pool08'):
 models=importlib.import_module(path+'.opportunity_models')
 with connection.schema_editor() as editor:
  for model in (Opportunity,StageHistory,models.CommercialOpportunity,models.OpportunityEvent):
   if model._meta.db_table not in connection.introspection.table_names():editor.create_model(model)

def cases(system,path):
 api=importlib.import_module(path+'.crm_api');models=importlib.import_module(path+'.opportunity_models')
 class Checks(unittest.TestCase):
  def setUp(self):
   self.base=fixture['fixture']['AdapterTests']();self.base.setUp();env=patch.dict(os.environ,{'BACKEND_SERVICE':system});env.start();self.addCleanup(env.stop)
   request=APIRequestFactory().post('/crm/?provider_id='+str(self.base.provider.pk),dict(request_id=str(uuid.uuid4()),operation='create',contact_id=None,expected_revision=0,data={'name':'Contacto de oportunidad','email':uuid.uuid4().hex+'@example.test','origin':'MANUAL','responsible_ref':str(self.base.user.pk)}),format='json');force_authenticate(request,user=self.base.user)
   response=api.CRMView.as_view()(request,section='commands');self.assertEqual(response.status_code,200,response.data);self.contact=response.data['contact_id']
  def body(self,operation='create',ref=None,revision=0,**data):
   return dict(request_id=str(uuid.uuid4()),operation=operation,opportunity_id=ref,expected_revision=revision,data=data)
  def call(self,method='get',body=None,ref=None,section='list',user=None,**query):
   from urllib.parse import urlencode
   request=getattr(APIRequestFactory(),method)('/fixture/?'+urlencode({'provider_id':str(self.base.provider.pk),**query}),body,format='json');force_authenticate(request,user=user or self.base.user)
   return api.OpportunitiesView.as_view()(request,section='commands' if method=='post' else section,**({'opportunity_id':ref} if ref else {}))
  def create(self,**extra):
   data=dict(title='Plan turístico',contact_id=self.contact,value='1500000.00',currency='COP',responsible_ref=str(self.base.user.pk));data.update(extra)
   r=self.call('post',self.body(**data));self.assertEqual(r.status_code,200,r.data);return r.data['opportunity_id']
  def transition(self,ref,revision,stage,**extra):
   data=dict(stage=stage,reason='Revisión comercial documentada');data.update(extra)
   return self.call('post',self.body('transition',ref,revision,**data))
  def test_full_pipeline_never_posts_money(self):
   before=JournalEntry.plain_objects.count();ref=self.create()
   for revision,stage in enumerate(('CONTACTED','QUALIFIED','PROPOSAL','NEGOTIATION','WON'),start=1):
    extra={'confirmation':True,'evidence_digest':'a'*64} if stage=='WON' else {}
    r=self.transition(ref,revision,stage,**extra);self.assertEqual(r.status_code,200,r.data)
    for key in ('payment_verified','invoice_issued','ledger_written','revenue_recognized'):self.assertFalse(r.data[key])
   self.assertEqual(JournalEntry.plain_objects.count(),before)
   history=self.call(ref=ref,section='history');self.assertTrue(history.data['history_verified']);self.assertEqual(history.data['next_offset'],5)
   item=self.call(ref=ref).data;self.assertEqual(item['revision'],6);self.assertIsNone(item['score']['probability']);self.assertEqual(item['score']['status'],'NOT_CALIBRATED')
  def test_jump_win_confirmation_and_closure_guard(self):
   ref=self.create();self.assertEqual(self.transition(ref,1,'WON',confirmation=True,evidence_digest='a'*64).status_code,409)
   for rev,stage in enumerate(('CONTACTED','QUALIFIED','PROPOSAL','NEGOTIATION'),1):self.transition(ref,rev,stage)
   self.assertEqual(self.transition(ref,5,'WON').status_code,422)
   self.transition(ref,5,'WON',confirmation=True,evidence_digest='a'*64)
   self.assertEqual(self.call('post',self.body('update',ref,6,value='99.00')).status_code,409)
   r=self.call('post',self.body('reopen',ref,6,reason='Nueva revisión por el administrador'));self.assertEqual(r.status_code,200,r.data);self.assertEqual(r.data['stage'],'NEW')
  def test_loss_reason_required_and_history_retained_after_reopen(self):
   ref=self.create();self.assertEqual(self.transition(ref,1,'LOST').status_code,422)
   self.assertEqual(self.transition(ref,1,'LOST',loss_code='PRICE',loss_detail='Presupuesto insuficiente').status_code,200)
   self.assertEqual(self.call('post',self.body('reopen',ref,2,reason='Nueva solicitud del titular')).status_code,200)
   events=self.call(ref=ref,section='history').data['events'];self.assertEqual(events[1]['data']['loss_code'],'PRICE')
  def test_scoring_has_current_sources_and_no_claimed_calibration(self):
   ref=self.create(interest_evidence='b'*64,next_action={'description':'Revisar oferta','due_at':(timezone.now()+timedelta(days=1)).isoformat(),'responsible_ref':str(self.base.user.pk)})
   score=self.call(ref=ref).data['score'];self.assertEqual(score['value'],100);self.assertFalse(score['dataset_evaluated']);self.assertIsNone(score['accuracy']);self.assertTrue(all(c['source']['ref'] for c in score['criteria']))
  def test_stale_revision_and_request_replay(self):
   ref=self.create();body=self.body('update',ref,1,title='Oferta revisada');first=self.call('post',body)
   self.assertEqual(first.status_code,200);self.assertTrue(self.call('post',body).data['replayed'])
   changed=copy.deepcopy(body);changed['data']['title']='Distinta';self.assertEqual(self.call('post',changed).status_code,409)
   self.assertEqual(self.call('post',self.body('update',ref,1,title='Obsoleta')).status_code,409)
   self.assertEqual(self.call(ref=body['request_id'],section='receipt').data['opportunity_id'],ref)
  def test_foreign_company_revoked_identity_and_responsible(self):
   ref=self.create();self.assertEqual(self.call(ref=ref,user=self.base.other).status_code,403)
   self.assertEqual(self.call('post',self.body(contact_id=self.contact,title='Wrong',value='1.00',currency='COP',responsible_ref=str(self.base.other.pk))).status_code,403)
   VerifiedCompanyLink.objects.filter(pk=self.base.link.pk).update(revoked_at=timezone.now());self.assertEqual(self.call(ref=ref).status_code,403)
  def test_invalid_money_currency_and_payment_claims_rejected(self):
   for extra in ({'value':1.0},{'value':'1.001'},{'value':'1e2'},{'currency':'ANY'},{'payment_verified':True}):
    data=dict(title='Test',contact_id=self.contact,value='1.00',currency='COP',responsible_ref=str(self.base.user.pk));data.update(extra)
    self.assertEqual(self.call('post',self.body(**data)).status_code,422)
  def test_tasks_and_next_action_persist(self):
   ref=self.create();r=self.call('post',self.body('task',ref,1,title='Llamar al cliente',due_at=(timezone.now()+timedelta(days=1)).isoformat(),responsible_ref=str(self.base.user.pk)));self.assertEqual(r.status_code,200,r.data)
   task=self.call(ref=ref).data['tasks'][0];self.call('post',self.body('complete_task',ref,2,task_id=task['id']))
   self.assertTrue(self.call(ref=ref).data['tasks'][0]['completed'])
  def test_audit_failure_rolls_back_canonical_row_and_metadata(self):
   before=models.CommercialOpportunity.objects.count();legacy=Opportunity.objects.count()
   with patch.object(models.OpportunityEvent.objects,'create',side_effect=RuntimeError('audit unavailable')):
    with self.assertRaises(RuntimeError):self.create()
   self.assertEqual(models.CommercialOpportunity.objects.count(),before);self.assertEqual(Opportunity.objects.count(),legacy)
  def test_tampering_is_detected(self):
   ref=self.create();self.transition(ref,1,'CONTACTED');row=models.OpportunityEvent.objects.filter(opportunity=ref).order_by('sequence').first();doc=copy.deepcopy(row.document);doc['data']['title']='Alterado';models.OpportunityEvent.objects.filter(pk=row.pk).update(document=doc)
   self.assertEqual(self.call(ref=ref,section='history').status_code,503)
  def test_legacy_adoption_uses_explicit_company_contact_and_currency(self):
   if system!='erp-tur':return
   row=Opportunity.objects.create(provider_id=self.base.provider.pk,owner=self.base.user,name='Legado',stage='Proposal',value='125.50')
   StageHistory.objects.create(opportunity=row,from_stage='Contacted',to_stage='Proposal',user=self.base.user)
   ref=str(row.pk);item=self.call(ref=ref).data;self.assertTrue(item['requires_adoption']);self.assertIsNone(item['currency']);self.assertIsNone(item['score']['value'])
   self.assertEqual(self.call('post',self.body('update',ref,0,title='Bypass')).status_code,409)
   r=self.call('post',self.body('adopt',ref,0,contact_id=self.contact,currency='USD',responsible_ref=str(self.base.user.pk),review_reason='Origen revisado',evidence_digest='a'*64));self.assertEqual(r.status_code,200,r.data)
   self.assertEqual(r.data['opportunity_id'],ref);self.assertEqual(self.call(ref=ref).data['value'],'125.50')
   self.assertEqual(Opportunity.objects.filter(pk=row.pk).count(),1)
   history=self.call(ref=ref,section='history').data;self.assertTrue(history['legacy_events']);self.assertEqual(history['legacy_events'][0]['from_stage'],'Contacted')
  def test_legacy_history_tamper_and_unknown_stage_review(self):
   if system!='erp-tur':return
   row=Opportunity.objects.create(provider_id=self.base.provider.pk,owner=self.base.user,name='Etapa antigua',stage='old_custom_stage',value='10.00')
   ref=str(row.pk)
   data=dict(contact_id=self.contact,currency='COP',responsible_ref=str(self.base.user.pk),review_reason='Etapa antigua revisada',evidence_digest='a'*64)
   self.assertEqual(self.call('post',self.body('adopt',ref,0,**data)).status_code,409)
   self.assertEqual(self.call('post',self.body('adopt',ref,0,**data,review_stage='CONTACTED')).status_code,200)
   history=StageHistory.objects.filter(opportunity=row).first();StageHistory.objects.filter(pk=history.pk).update(to_stage='Alterado')
   self.assertEqual(self.call(ref=ref).status_code,409)
  def test_large_value_does_not_silently_round(self):
   if system!='erp-tur' or connection.vendor!='sqlite':return
   before=Opportunity.objects.count()
   data=dict(title='Precisión',contact_id=self.contact,value='9999999999999999.99',currency='COP',responsible_ref=str(self.base.user.pk))
   response=self.call('post',self.body(**data));self.assertEqual(response.status_code,422,response.data);self.assertEqual(Opportunity.objects.count(),before)
  def test_legacy_api_cannot_bypass_reviewed_transitions(self):
   if system!='erp-tur':return
   from apps.prestadores.mi_negocio.gestion_comercial.sales.views import OpportunityViewSet
   ref=self.create();request=APIRequestFactory().put('/legacy/?provider_id='+str(self.base.provider.pk),{'stage':'Won'},format='json');force_authenticate(request,user=self.base.user)
   response=OpportunityViewSet.as_view({'put':'move_opportunity'})(request,pk=ref);self.assertEqual(response.status_code,409)
   self.assertEqual(self.call(ref=ref).data['stage'],'NEW')
  def test_unscoped_legacy_not_inferred_and_tourism_closed(self):
   if system=='erp-tur':
    row=Opportunity.objects.create(owner=self.base.user,name='Sin empresa',value='1.00');self.assertEqual(self.call(ref=str(row.pk)).status_code,404)
   with patch.dict(os.environ,{'BACKEND_SERVICE':'turismo'}):self.assertEqual(self.call().status_code,404)
 return Checks
suite=unittest.TestSuite()
for system,path in [('erp-tur','apps.prestadores.mi_negocio.gestion_comercial.pool08'),('analematica','apps.admin_plataforma.gestion_comercial.pool08')]:suite.addTests(unittest.defaultTestLoader.loadTestsFromTestCase(cases(system,path)))
if __name__=='__main__':raise SystemExit(not unittest.TextTestRunner(verbosity=2).run(suite).wasSuccessful())
