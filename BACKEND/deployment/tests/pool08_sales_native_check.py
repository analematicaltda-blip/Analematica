"""Actual native journal, owned quota and reversal transaction contracts."""
import runpy,importlib,unittest,os,uuid,copy
from pathlib import Path
from datetime import datetime,timezone,timedelta
from unittest.mock import patch
from django.test import override_settings
from django.db import connection
fixture=runpy.run_path(str(Path(__file__).with_name('pool08_quotations_native_check.py')),run_name='sales_native_fixture')
from rest_framework.test import APIRequestFactory,force_authenticate
from apps.core_erp.accounting.models import Account,JournalEntry,LedgerEntry
from apps.core_erp.outbox_models import OutboxEvent
from apps.core_erp.accounting.ledger_engine import LedgerEngine
from apps.core_erp.accounting.exceptions import AccountingError
from apps.turismo.models import AvailabilityHold,TourismService
for path in ('apps.prestadores.mi_negocio.gestion_comercial.pool08','apps.admin_plataforma.gestion_comercial.pool08'):
 models=importlib.import_module(path+'.sales_models')
 with connection.schema_editor() as editor:
  for model in (models.CommercialSale,models.SaleEvent,models.SaleSourceBinding):
   if model._meta.db_table not in connection.introspection.table_names():editor.create_model(model)
def cases(system,path):
 api=importlib.import_module(path+'.crm_api');models=importlib.import_module(path+'.sales_models');quote_case=fixture['ERP'] if system=='erp-tur' else fixture['Ana']
 class Checks(unittest.TestCase):
  def setUp(self):
   self.q=quote_case();self.q.setUp();self.addCleanup(self.q.doCleanups);self.base=self.q.base
   self.ar=Account.plain_objects.create(tenant=self.base.tenant,chart_of_accounts=self.base.chart,code='1305-'+uuid.uuid4().hex[:4],name='Cartera revisada',type='ASSET');self.liability=Account.plain_objects.create(tenant=self.base.tenant,chart_of_accounts=self.base.chart,code='2805-'+uuid.uuid4().hex[:4],name='Pasivo de contrato',type='LIABILITY');self.tax=Account.plain_objects.create(tenant=self.base.tenant,chart_of_accounts=self.base.chart,code='2408-'+uuid.uuid4().hex[:4],name='Impuesto declarado revisado',type='LIABILITY')
   now=datetime.now(timezone.utc);self.policy={'version':'synthetic-reviewed-roles','valid_from':(now-timedelta(days=1)).isoformat(),'valid_until':(now+timedelta(days=1)).isoformat(),'reviewer_ref':str(self.base.link.reviewed_by_id),'support_digest':'a'*64,'roles':{'receivable':[str(self.ar.pk)],'revenue':[str(self.base.b.pk)],'contract_liability':[str(self.liability.pk)],'tax_liability':[str(self.tax.pk)]}};self.settings=override_settings(COMMERCIAL_SALE_ACCOUNT_POLICIES={str(self.base.tenant.pk):self.policy});self.settings.enable();self.addCleanup(self.settings.disable)
  def tearDown(self):self.q.tearDown()
  def body(self,op='create',ref=None,rev=0,**data):return dict(request_id=str(uuid.uuid4()),operation=op,sale_id=ref,expected_revision=rev,data=data)
  def call(self,body=None,ref=None,section='list',user=None):
   request=(APIRequestFactory().post('/fixture/?provider_id='+str(self.base.provider.pk),body,format='json') if body else APIRequestFactory().get('/fixture/?provider_id='+str(self.base.provider.pk)));force_authenticate(request,user=user or self.base.user);return api.SalesView.as_view()(request,section='commands' if body else section,**({'sale_id':ref} if ref else {}))
  def create(self,quote=None):
   quote=quote or self.q.create();self.q.issue(quote);link=self.q.link(quote);self.assertEqual(self.q.public(quote,link,self.q.acceptance(quote)).status_code,200);r=self.call(self.body(quotation_id=quote));self.assertEqual(r.status_code,200,r.data);return r.data['sale_id']
  def terms(self,fact='SERVICE_DELIVERED'):
   return dict(economic_fact=fact,entry_date=__import__('django.utils.timezone',fromlist=['localdate']).localdate().isoformat(),accounts={'receivable':str(self.ar.pk),'contra':str(self.base.b.pk if fact=='SERVICE_DELIVERED' else self.liability.pk),'tax_liability':str(self.tax.pk) if fact=='SERVICE_DELIVERED' else None},operation={'mode':'NO_LABOR_REVIEWED','order_id':None,'reason':'Revisión declarada de actividad sin personal operativo','support_digest':'b'*64},documents=[{'kind':'CONTRACT','reference':'BYOS-SYNTHETIC','sha256':'c'*64}],support_digest='d'*64,confirmed=True)
  def confirm(self,ref,fact='SERVICE_DELIVERED'):
   r=self.call(self.body('review',ref,1,**self.terms(fact)));self.assertEqual(r.status_code,200,r.data);r=self.call(self.body('confirm',ref,2,confirmed=True));self.assertEqual(r.status_code,200,r.data);return r.data
  def test_quote_alone_and_review_do_not_post(self):
   ref=self.create();self.assertEqual(JournalEntry.plain_objects.filter(tenant=self.base.tenant).count(),0);self.assertEqual(self.call(self.body('review',ref,1,**self.terms())).status_code,200);self.assertEqual(JournalEntry.plain_objects.filter(tenant=self.base.tenant).count(),0)
  def test_confirm_balances_canonical_ledger_and_outbox(self):
   ref=self.create();r=self.confirm(ref);row=JournalEntry.plain_objects.get(pk=r['journal']['id']);self.assertTrue(row.is_posted);self.assertEqual(row.system_hash,row.compute_hash());lines=LedgerEntry.plain_objects.filter(journal_entry=row);self.assertEqual(sum(x.debit_amount for x in lines),sum(x.credit_amount for x in lines));self.assertTrue(r['ledger_written']);self.assertFalse(r['money_transferred']);self.assertFalse(r['fiscal_document_issued']);self.assertEqual(OutboxEvent.objects.filter(event_type='commercial.sale.confirmed.v1',aggregate_root=ref).count(),1)
  def test_reversal_two_steps_exact_opposite(self):
   ref=self.create();r=self.confirm(ref);self.assertEqual(self.call(self.body('review_reversal',ref,3,reason='Anulación revisada',support_digest='e'*64,confirmed=True)).status_code,200);r=self.call(self.body('reverse',ref,4,confirmed=True));self.assertEqual(r.status_code,200,r.data);self.assertEqual(r.data['status'],'REVERSED');self.assertTrue(JournalEntry.plain_objects.get(pk=r.data['reversal']['id']).is_reversal)
  def test_duplicate_quote_commands_and_account_bypass_blocked(self):
   ref=self.create();record=self.call(ref=ref).data;self.assertEqual(self.call(self.body(quotation_id=record['quotation_id'])).status_code,409);terms=self.terms();terms['accounts']['receivable']=str(self.base.a.pk);self.assertEqual(self.call(self.body('review',ref,1,**terms)).status_code,422);self.assertEqual(self.call(self.body('confirm',ref,1,confirmed=True)).status_code,409)
  def test_post_replay_same_journal_and_no_second_entry(self):
   ref=self.create();self.call(self.body('review',ref,1,**self.terms()));body=self.body('confirm',ref,2,confirmed=True);a=self.call(body);b=self.call(body);self.assertEqual(a.data['journal'],b.data['journal']);self.assertTrue(b.data['replayed']);self.assertEqual(JournalEntry.plain_objects.filter(tenant=self.base.tenant).count(),1)
  def test_generic_ledger_cannot_reverse_sale(self):
   ref=self.create();r=self.confirm(ref)
   with self.assertRaises(AccountingError):LedgerEngine.reverse_entry(r['journal']['id'],tenant_id=self.base.tenant.pk,actor=self.base.user)
  def test_audit_failure_rolls_back_ledger_and_sale(self):
   ref=self.create();self.call(self.body('review',ref,1,**self.terms()))
   with patch.object(models.SaleEvent.objects,'create',side_effect=RuntimeError('audit unavailable')):
    with self.assertRaises(RuntimeError):self.call(self.body('confirm',ref,2,confirmed=True))
   self.assertEqual(JournalEntry.plain_objects.filter(tenant=self.base.tenant).count(),0);self.assertEqual(self.call(ref=ref).data['status'],'REVIEWED')
  def test_real_capacity_hold_and_generic_release_guard(self):
   service=TourismService.objects.create(provider=self.base.provider,name='Cupo de venta',description='test',service_type='EXPERIENCE',price='10.00',capacity=1)
   price=self.q.price();self.q.policy(price,'REQUIRED',str(service.pk));start=datetime.now(timezone.utc)+timedelta(days=2);end=start+timedelta(hours=1)
   quote=self.q.create(price,policy=False,service_windows=[dict(item_id=price,start_at=start.isoformat(),end_at=end.isoformat())]);ref=self.create(quote);r=self.confirm(ref,'UNCONDITIONAL_RECEIVABLE');hold=AvailabilityHold.objects.get(pk=self.call(ref=ref).data['operation_refs'][0]['hold_id']);self.assertIsNone(hold.released_at)
   from apps.prestadores.mi_negocio.gestion_comercial.availability import release_hold
   with self.assertRaises(AccountingError):release_hold(self.base.user,hold.pk)
   self.assertEqual(self.call(self.body('review_reversal',ref,3,reason='Revisión y liberación',support_digest='e'*64,confirmed=True)).status_code,200);r=self.call(self.body('reverse',ref,4,confirmed=True));self.assertEqual(r.status_code,200,r.data);hold.refresh_from_db();self.assertIsNotNone(hold.released_at)
  def test_capacity_taken_after_review_rolls_back_without_journal(self):
   service=TourismService.objects.create(provider=self.base.provider,name='Cupo con carrera',description='test',service_type='EXPERIENCE',price='10.00',capacity=1);price=self.q.price();self.q.policy(price,'REQUIRED',str(service.pk));start=datetime.now(timezone.utc)+timedelta(days=2);end=start+timedelta(hours=1);quote=self.q.create(price,policy=False,service_windows=[dict(item_id=price,start_at=start.isoformat(),end_at=end.isoformat())]);ref=self.create(quote);r=self.call(self.body('review',ref,1,**self.terms('UNCONDITIONAL_RECEIVABLE')));self.assertEqual(r.status_code,200,r.data)
   AvailabilityHold.objects.create(provider=self.base.provider,service=service,requested_by=self.base.user,idempotency_key=uuid.uuid4(),request_digest='a'*64,start_at=start,end_at=end,quantity=1,expires_at=end)
   self.assertEqual(self.call(self.body('confirm',ref,2,confirmed=True)).status_code,409);self.assertEqual(JournalEntry.plain_objects.filter(tenant=self.base.tenant).count(),0)
  def test_account_deactivation_after_review_prevents_posting(self):
   ref=self.create();self.call(self.body('review',ref,1,**self.terms()));Account.plain_objects.filter(pk=self.ar.pk).update(is_active=False);self.assertEqual(self.call(self.body('confirm',ref,2,confirmed=True)).status_code,422);self.assertEqual(JournalEntry.plain_objects.filter(tenant=self.base.tenant).count(),0)
  def test_labor_order_requires_recorded_dispatch(self):
   ref=self.create();terms=self.terms();terms['operation'].update(mode='EXISTING_LABOR_ORDER',order_id=str(uuid.uuid4()),cost_since=terms['entry_date'],cost_until=terms['entry_date']);r=self.call(self.body('review',ref,1,**terms));self.assertIn(r.status_code,(403,404,409));self.assertEqual(JournalEntry.plain_objects.filter(tenant=self.base.tenant).count(),0)
  def test_cancelled_unposted_sale_can_be_reviewed_again_without_duplicate(self):
   ref=self.create();r=self.call(self.body('cancel',ref,1,reason='Intento anterior no ejecutado'));self.assertEqual(r.status_code,200,r.data);r=self.call(self.body('review',ref,2,**self.terms()));self.assertEqual(r.status_code,200,r.data);r=self.call(self.body('confirm',ref,3,confirmed=True));self.assertEqual(r.status_code,200,r.data);self.assertEqual(r.data['sale_id'],ref);self.assertEqual(JournalEntry.plain_objects.filter(tenant=self.base.tenant).count(),1)
  def test_other_company_and_revoked_qualification(self):
   ref=self.create();self.assertEqual(self.call(ref=ref,user=self.base.other).status_code,403)
   with override_settings(COMMERCIAL_SALE_ACCOUNT_POLICIES={}):self.assertEqual(self.call(self.body('review',ref,1,**self.terms())).status_code,503)
 Checks.__name__=system.replace('-','_')+'Sales';return Checks
ERP=cases('erp-tur','apps.prestadores.mi_negocio.gestion_comercial.pool08');Ana=cases('analematica','apps.admin_plataforma.gestion_comercial.pool08')
if __name__=='__main__':unittest.main()
