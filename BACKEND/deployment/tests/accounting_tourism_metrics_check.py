"""Room inventory observations and actual posted-ledger ratios, isolated synthetic data."""
import runpy,unittest,uuid,copy
from pathlib import Path
from datetime import timedelta
from unittest.mock import patch
fixture=runpy.run_path(str(Path(__file__).with_name('accounting_adapter_check.py')),run_name='tourism_metric_fixture')
from django.utils import timezone
from apps.prestadores.mi_negocio.gestion_contable.contabilidad import tourism_metrics as engine
from apps.prestadores.mi_negocio.gestion_operativa.modulos_especializados.hoteles.models import Room,RoomType
from apps.prestadores.mi_negocio.gestion_operativa.modulos_genericos.productos_servicios.models import Product,OperationalTag,PoliticaCancelacion
from apps.core.catalogs.models import Amenity
from apps.core_erp.accounting.models import Account,JournalEntry
from apps.core_erp.accounting.ledger_engine import LedgerEngine
from apps.core_erp.accounting.exceptions import AccountingError
from apps.core_erp.outbox_models import OutboxEvent
create=fixture['fixture']['fixture']['fixture']['fixture']['create']
for model in (PoliticaCancelacion,OperationalTag,Amenity,Product,RoomType,Room):create(model)
class TourismMetricsChecks(unittest.TestCase):
 def setUp(self):
  self.case=fixture['AdapterTests']();self.case.setUp();self.owner=self.case.user;self.company=self.case.tenant;self.provider=self.case.provider;self.day=timezone.localdate().isoformat()
  product=Product.objects.create(provider_id=self.provider.pk,nombre='Synthetic room product',tipo='SERVICIO',base_price='1.00')
  self.kind=RoomType.objects.create(provider_id=self.provider.pk,product=product,capacidad=2)
  self.rooms=[Room.objects.create(provider_id=self.provider.pk,room_type=self.kind,numero_habitacion=str(i+1)) for i in range(2)]
  self.expense=Account.plain_objects.create(tenant=self.company,chart_of_accounts=self.case.chart,code='HOTEL-COST',name='Synthetic operating expense',type='EXPENSE')
  self.case.post();self.expense_post()
  self.mapping={'room_revenue':[str(self.case.b.pk)],'other_operating_revenue':[],'operating_expenses':[str(self.expense.pk)],'excluded_nonoperating':[]}
  self.args={'actor':self.owner,'provider_id':self.provider.pk,'day':self.day,'room_ids':[str(r.pk) for r in self.rooms],'mapping':self.mapping,'evidence_digest':'a'*64,'expected_revision':0,'confirmed':True}
 def expense_post(self,amount='2.00',key=None):return LedgerEngine.post_lines(tenant_id=self.company.pk,entry_date=timezone.localdate(),description='Synthetic operating expense',lines_data=[{'account':self.expense,'debit':amount},{'account':self.case.a,'credit':amount}],actor=self.owner,idempotency_key=key or 'hotel-expense')
 def review(self,**extra):return engine.review_capacity(**{**self.args,**extra})
 def record(self,review,**extra):return engine.record_capacity(**{'actor':self.owner,'provider_id':self.provider.pk,'review_id':review['review_id'],'confirmed':True,**extra})
 def metrics(self,**extra):return engine.metrics(**{'actor':self.owner,'provider_id':self.provider.pk,'since':self.day,'until':self.day,**extra})
 def test_review_and_observation_need_separate_confirmations_without_ledger_write(self):
  count=JournalEntry.plain_objects.count()
  with self.assertRaises(AccountingError):self.review(confirmed=False)
  review=self.review()
  with self.assertRaises(AccountingError):self.record(review,confirmed=False)
  recorded=self.record(review);self.assertFalse(recorded['ledger_written']);self.assertTrue(self.record(review)['replayed']);self.assertEqual(JournalEntry.plain_objects.count(),count)
 def test_actual_revpar_goppar_reconcile_with_classified_ledger(self):
  self.record(self.review());result=self.metrics();self.assertEqual(result['room_revenue'],'10.00');self.assertEqual(result['operating_expenses'],'2.00');self.assertEqual(result['operating_profit'],'8.00');self.assertEqual(result['available_room_days'],2);self.assertEqual(result['revpar'],'5.0000');self.assertEqual(result['goppar'],'4.0000');self.assertIsNone(result['package_margin']);self.assertFalse(result['independently_verified'])
 def test_zero_capacity_is_unknown_ratio_not_zero_revenue(self):
  self.record(self.review(room_ids=[]));result=self.metrics();self.assertEqual(result['room_revenue'],'10.00');self.assertEqual(result['available_room_days'],0);self.assertIsNone(result['revpar']);self.assertIsNone(result['goppar']);self.assertEqual(result['unavailable_reason'],'ZERO_AVAILABLE_ROOM_DAYS')
 def test_current_inventory_never_fills_missing_historical_days(self):
  self.record(self.review());past=(timezone.localdate()-timedelta(days=1)).isoformat();r=self.metrics(since=past);self.assertEqual(r['missing_capacity_days'],[past]);self.assertIsNone(r['revpar']);self.assertEqual(r['unavailable_reason'],'MISSING_DAILY_CAPACITY')
 def test_capacity_cannot_be_backfilled_or_predated(self):
  for day in [(timezone.localdate()-timedelta(days=1)).isoformat(),(timezone.localdate()+timedelta(days=1)).isoformat()]:
   with self.assertRaises(AccountingError):self.review(day=day)
 def test_out_of_service_or_duplicate_room_is_rejected(self):
  Room.objects.filter(pk=self.rooms[0].pk).update(housekeeping_status='OUT_OF_ORDER')
  with self.assertRaises(AccountingError):self.review()
  with self.assertRaises(AccountingError):self.review(room_ids=[str(self.rooms[1].pk)]*2)
 def test_inventory_changed_after_review_requires_new_review(self):
  review=self.review();Room.objects.filter(pk=self.rooms[0].pk).update(housekeeping_status='DIRTY')
  with self.assertRaises(AccountingError):self.record(review)
 def test_stale_revision_cannot_overwrite_a_record(self):
  review=self.review();self.record(review)
  with self.assertRaises(AccountingError):self.review()
  different=self.review(room_ids=[str(self.rooms[0].pk)],expected_revision=1);self.record(different);self.assertEqual(self.metrics()['available_room_days'],1)
 def test_no_lookahead_from_later_capacity_amendment(self):
  self.record(self.review());cutoff=timezone.now().isoformat();self.record(self.review(room_ids=[str(self.rooms[0].pk)],expected_revision=1))
  self.assertEqual(self.metrics(as_of=cutoff)['available_room_days'],2);self.assertEqual(self.metrics()['available_room_days'],1)
 def test_no_lookahead_from_later_posted_revenue(self):
  self.record(self.review());cutoff=timezone.now().isoformat();self.case.post(idempotency_key='later-room-sale')
  self.assertEqual(self.metrics(as_of=cutoff)['room_revenue'],'10.00');self.assertEqual(self.metrics()['room_revenue'],'20.00')
 def test_pre_observation_cutoff_does_not_invent_capacity(self):
  cutoff=timezone.now().isoformat();self.record(self.review());r=self.metrics(as_of=cutoff);self.assertIsNone(r['revpar']);self.assertEqual(r['unavailable_reason'],'DAILY_CAPACITY_REQUIRED')
 def test_wrong_account_kind_and_duplicate_classification_fail(self):
  for mapping in [{'room_revenue':[str(self.case.a.pk)],'other_operating_revenue':[],'operating_expenses':[str(self.expense.pk)],'excluded_nonoperating':[]},{'room_revenue':[str(self.case.b.pk)],'other_operating_revenue':[str(self.case.b.pk)],'operating_expenses':[str(self.expense.pk)],'excluded_nonoperating':[]}]:
   with self.assertRaises(AccountingError):self.review(mapping=mapping)
 def test_unclassified_operating_amounts_remain_visible(self):
  other=Account.plain_objects.create(tenant=self.company,chart_of_accounts=self.case.chart,code='OTHER-COST',name='Unclassified expense',type='EXPENSE')
  LedgerEngine.post_lines(tenant_id=self.company.pk,entry_date=timezone.localdate(),description='Unclassified fixture',lines_data=[{'account':other,'debit':'1.00'},{'account':self.case.a,'credit':'1.00'}],actor=self.owner,idempotency_key='unclassified-hotel-cost')
  self.record(self.review());r=self.metrics();self.assertIn(str(other.pk),r['unmapped_account_ids']);self.assertIsNone(r['goppar']);self.assertEqual(r['unavailable_reason'],'UNCLASSIFIED_FINANCIAL_ACCOUNTS')
 def test_no_recorded_capacity_does_not_use_existing_room_count(self):
  r=self.metrics();self.assertEqual(r['unavailable_reason'],'DAILY_CAPACITY_REQUIRED');self.assertIsNone(r['available_room_days']);self.assertIsNone(r['room_revenue'])
 def test_naive_or_future_knowledge_cutoff_is_rejected(self):
  for cutoff in ['2026-01-01T00:00:00',(timezone.now()+timedelta(days=1)).isoformat()]:
   with self.assertRaises(AccountingError):self.metrics(as_of=cutoff)
 def test_other_actor_cannot_record_existing_capacity_review(self):
  from rest_framework.exceptions import APIException
  with self.assertRaises(APIException):engine.record_capacity(actor=self.case.other,provider_id=self.provider.pk,review_id=self.review()['review_id'],confirmed=True)
 def test_missing_review_origin_is_not_a_valid_capacity_source(self):
  review=self.review();self.record(review);OutboxEvent.objects.filter(pk=review['review_id']).delete()
  with self.assertRaises(AccountingError):self.metrics()
 def test_retired_room_does_not_rewrite_recorded_capacity(self):
  self.record(self.review());Room.objects.filter(pk=self.rooms[0].pk).update(is_active=False);self.assertEqual(self.metrics()['available_room_days'],2)
 def test_explicit_nonoperating_exclusion_is_traceable_not_omitted(self):
  other=Account.plain_objects.create(tenant=self.company,chart_of_accounts=self.case.chart,code='NONOP',name='Declared nonoperating expense',type='EXPENSE')
  LedgerEngine.post_lines(tenant_id=self.company.pk,entry_date=timezone.localdate(),description='Nonoperating fixture',lines_data=[{'account':other,'debit':'1.00'},{'account':self.case.a,'credit':'1.00'}],actor=self.owner,idempotency_key='nonoperating-hotel-cost')
  mapping=copy.deepcopy(self.mapping);mapping['excluded_nonoperating']=[str(other.pk)];self.record(self.review(mapping=mapping));r=self.metrics()
  self.assertEqual(r['goppar'],'4.0000');self.assertEqual(r['excluded_nonoperating'],'-1.00');self.assertFalse(r['unmapped_account_ids'])
 def test_room_type_cannot_reference_another_company(self):
  from apps.turismo.models import TourismProvider
  foreign=TourismProvider.objects.create(owner=self.case.other,name='Foreign hotel fixture',provider_type='GUIDE')
  RoomType.objects.filter(pk=self.kind.pk).update(provider_id=foreign.pk)
  with self.assertRaises(AccountingError):engine.sources(actor=self.owner,provider_id=self.provider.pk)
 def test_altering_capacity_knowledge_timestamp_requires_reconciliation(self):
  review=self.review();recorded=self.record(review);OutboxEvent.objects.filter(pk=recorded['observation_id']).update(created_at=timezone.now()-timedelta(hours=1))
  with self.assertRaises(AccountingError):self.metrics()
 def test_actual_scoped_api_and_private_response(self):
  from rest_framework.test import APIRequestFactory,force_authenticate
  from apps.prestadores.mi_negocio.gestion_contable.contabilidad.views import PlanCuentaViewSet
  def call(action,body,method='post'):
   if method=='get':body={'provider_id':str(self.provider.pk),**body}
   request=getattr(APIRequestFactory(),method)('/fixture/?provider_id='+str(self.provider.pk),body,format='json');force_authenticate(request,user=self.owner);return PlanCuentaViewSet.as_view({method:action})(request)
  payload={k:v for k,v in self.args.items() if k not in {'actor','provider_id'}}
  review=call('review_hotel_capacity',payload);self.assertEqual(review.status_code,200,review.data)
  recorded=call('record_hotel_capacity',{'review_id':review.data['review_id'],'confirmed':True});self.assertEqual(recorded.status_code,200,recorded.data)
  result=call('hotel_metrics',{'since':self.day,'until':self.day},'get');self.assertEqual(result.status_code,200,result.data);self.assertEqual(result.data['revpar'],'5.0000');self.assertIn('no-store',result['Cache-Control'])
 def test_superseded_versions_do_not_multiply_financial_query_count(self):
  from django.test.utils import CaptureQueriesContext
  from django.db import connection
  self.record(self.review())
  with CaptureQueriesContext(connection) as first:self.metrics()
  for revision in range(1,10):self.record(self.review(expected_revision=revision))
  with CaptureQueriesContext(connection) as later:result=self.metrics()
  self.assertEqual(result['capacity_sources'][0]['revision'],10);self.assertLessEqual(len(later),len(first)+1)
 def test_failure_to_seal_timestamp_rolls_back_observation(self):
  from django.db.models.query import QuerySet
  review=self.review();original=QuerySet.update
  def update(query,**kwargs):
   if query.model is OutboxEvent and 'known_at' in kwargs.get('payload',{}):raise RuntimeError('Seal failed')
   return original(query,**kwargs)
  with patch.object(QuerySet,'update',update):
   with self.assertRaises(RuntimeError):self.record(review)
  self.assertFalse(OutboxEvent.objects.filter(event_type=engine.RECORDED,payload__company_id=str(self.company.pk)).exists());self.assertTrue(OutboxEvent.objects.filter(pk=review['review_id']).exists());self.assertIsNone(self.metrics()['revpar'])
if __name__=='__main__':unittest.main()
