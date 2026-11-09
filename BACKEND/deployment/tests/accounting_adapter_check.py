"""Verified provider/accounting adapter and real DRF catalog isolation contracts."""
import runpy,unittest,uuid
from pathlib import Path
from datetime import timedelta
from django.utils import timezone
fixture=runpy.run_path(str(Path(__file__).with_name('accounting_posting_check.py')),run_name='adapter_fixture')
from api.models import CustomUser
from apps.turismo.models import TourismProvider,BusinessProfile,VerifiedCompanyLink
from apps.turismo.services.company_identity import review_link
from apps.prestadores.mi_negocio.gestion_contable.contabilidad.services import ContabilidadService
from apps.prestadores.mi_negocio.gestion_contable.contabilidad.views import PlanCuentaViewSet
from apps.core_erp.accounting.models import Account,ChartOfAccounts,JournalEntry
from apps.core_erp.accounting.exceptions import AccountingError
from rest_framework.exceptions import APIException
from rest_framework.test import APIRequestFactory,force_authenticate
from apps.core_erp.accounting.ledger_engine import LedgerEngine
from apps.core_erp.accounting.delivery_models import AccountingDelivery,AccountingProjectionReceipt,AccountingDailyBalance
for model in (AccountingDelivery,AccountingProjectionReceipt,AccountingDailyBalance):fixture['fixture']['fixture']['fixture']['create'](model)

from apps.core_erp.accounting.ratio_models import AccountingRatioPolicy
fixture['fixture']['fixture']['fixture']['create'](AccountingRatioPolicy)

class AdapterTests(unittest.TestCase):
 def setUp(self):
  base=fixture['fixture']['AccountingFoundation'];base.setUp(self)
  self.user=fixture['fixture']['fixture']['F'].owner
  self.other=fixture['fixture']['fixture']['F'].other
  self.provider=TourismProvider.objects.create(owner=self.user,name='Adapter fixture',provider_type='GUIDE')
  BusinessProfile.objects.create(provider=self.provider,legal_name='Fixture',tax_id=self.tenant.tax_id,business_address='fixture',phone='fixture',email='fixture@example.test')
  reviewer=CustomUser(username=uuid.uuid4().hex,is_superuser=True,is_staff=True,is_active=True);CustomUser.objects.bulk_create([reviewer])
  self.link=review_link(operator=reviewer,provider_id=self.provider.pk,tenant_id=self.tenant.pk,evidence_digest='a'*64,valid_until=timezone.now()+timedelta(days=1),apply=True)
 def call(self,action,method='get',data=None,pk=None,user=None,query=None,**headers):
  path='/fixture/?provider_id='+str(query or self.provider.pk)
  request=getattr(APIRequestFactory(),method)(path,data or {},format='json',**headers)
  force_authenticate(request,user=user or self.user)
  return PlanCuentaViewSet.as_view({method:action})(request,**({'pk':pk} if pk else {}))
 def post(self,**extra):
  args=dict(provider=self.provider,date=timezone.localdate(),description='Verified manual fixture',periodo=self.period,creado_por=self.user,
            transacciones_data=[{'cuenta_id':self.a.pk,'debit':'10.00'},{'cuenta_id':self.b.pk,'credit':'10.00'}],idempotency_key='adapter-fixture')
  args.update(extra);return ContabilidadService.crear_asiento_completo(**args)
 def test_commercial_outbox_status_is_owner_scoped(self):
  from apps.core_erp.outbox_models import OutboxEvent
  OutboxEvent.objects.create(event_type='commercial.invoice.requested.v1',domain='commercial',aggregate_root=str(self.tenant.pk),payload={'company_id':str(self.tenant.pk),'amount':'DO-NOT-DISCLOSE'})
  response=self.call('commercial_outbox_status');self.assertEqual(response.status_code,200)
  self.assertEqual(response.data['transport_counts']['invoice_requests']['PENDING'],1)
  self.assertFalse(response.data['fiscal_consumer_available']);self.assertNotIn('DO-NOT-DISCLOSE',str(response.data))
  self.assertEqual(self.call('commercial_outbox_status',user=self.other).status_code,403)
 def test_commercial_outbox_status_rejects_revoked_identity(self):
  VerifiedCompanyLink.objects.filter(pk=self.link.pk).update(revoked_at=timezone.now())
  self.assertEqual(self.call('commercial_outbox_status').status_code,403)
 def test_accounting_query_is_owner_scoped_and_read_only(self):
  self.post();before=JournalEntry.plain_objects.count()
  response=self.call('accounting_query','post',{'question':'¿Cuál es la rentabilidad de mi empresa?','since':'2026-11-01','until':'2026-11-30'})
  self.assertEqual(response.status_code,200,response.data);self.assertTrue(response.data['read_only']);self.assertFalse(response.data['generated_sql'])
  self.assertEqual(response.data['company_id'],str(self.tenant.pk));self.assertEqual(JournalEntry.plain_objects.count(),before)
  self.assertEqual(self.call('accounting_query','post',{'question':'estado de la cola comercial'},user=self.other).status_code,403)
 def test_accounting_query_rejects_injection_unknown_tools_and_tenant_spoof(self):
  for body in [{'question':'DROP TABLE core_erp_journalentry'},{'question':'estado de la cola comercial','tenant_id':str(self.foreign.pk)},{'question':'transferir dinero'},{'question':'rentabilidad','since':'2026-12-01','until':'2026-01-01'}]:
   self.assertEqual(self.call('accounting_query','post',body).status_code,400)
  VerifiedCompanyLink.objects.filter(pk=self.link.pk).update(revoked_at=timezone.now())
  self.assertEqual(self.call('accounting_query','post',{'question':'estado de la cola comercial'}).status_code,403)
 def test_accounting_success_and_errors_are_not_cacheable(self):
  cases=[self.call('list'),self.call('commercial_outbox_status',user=self.other),self.call('accounting_query','post',{'question':'unsupported'})]
  self.assertEqual([r.status_code for r in cases],[200,403,400])
  for response in cases:
   self.assertIn('no-store',response['Cache-Control']);self.assertIn('private',response['Cache-Control'])
   self.assertEqual(response['Pragma'],'no-cache');self.assertEqual(response['Expires'],'0')
   vary={v.strip().lower() for v in response['Vary'].split(',')};self.assertTrue({'cookie','authorization'}<=vary)
 def test_unauthenticated_accounting_response_is_not_cacheable(self):
  request=APIRequestFactory().get('/fixture/?provider_id='+str(self.provider.pk))
  response=PlanCuentaViewSet.as_view({'get':'commercial_outbox_status'})(request)
  self.assertIn(response.status_code,[401,403]);self.assertIn('no-store',response['Cache-Control'])
 def test_accounting_query_uses_bounded_strict_parser(self):
  from unittest.mock import patch
  bodies=['{"question":"estado de la cola comercial","question":"rentabilidad"}','{"question":NaN}','['+'0,'*5000+'0]', '{"question":"'+'x'*9000+'"}']
  for body in bodies:
   request=APIRequestFactory().generic('POST','/fixture/?provider_id='+str(self.provider.pk),body,content_type='application/json')
   force_authenticate(request,user=self.user)
   with patch('apps.core_erp.accounting.query_assistant.answer_query',side_effect=AssertionError('Rejected body must not reach tool dispatch')):
    response=PlanCuentaViewSet.as_view({'post':'accounting_query'},parser_classes=PlanCuentaViewSet.accounting_query.kwargs['parser_classes'])(request)
   self.assertEqual(response.status_code,400);self.assertIn('no-store',response['Cache-Control'])
 def test_accounting_identity_returns_distinct_scoped_ids(self):
  response=self.call('accounting_identity');self.assertEqual(response.status_code,200)
  self.assertEqual(response.data['company_id'],str(self.tenant.pk));self.assertEqual(response.data['provider_id'],str(self.provider.pk));self.assertEqual(response.data['actor_id'],str(self.user.pk))
  self.assertNotEqual(response.data['company_id'],response.data['provider_id']);self.assertTrue(response.data['read_only'])
 def test_accounting_identity_denies_foreign_and_revoked_owner(self):
  self.assertEqual(self.call('accounting_identity',user=self.other).status_code,403)
  VerifiedCompanyLink.objects.filter(pk=self.link.pk).update(revoked_at=timezone.now())
  self.assertEqual(self.call('accounting_identity').status_code,403)
 def test_verified_ids_are_distinct_and_entry_replays_once(self):
  self.assertNotEqual(self.provider.pk,self.tenant.pk)
  entry=self.post();again=self.post();self.assertEqual(entry.pk,again.pk)
  self.assertEqual(entry.tenant_id,self.tenant.pk);self.assertEqual(entry.created_by_id,self.user.pk)
 def test_foreign_actor_account_and_period_rejected(self):
  with self.assertRaises(APIException):self.post(creado_por=self.other)
  with self.assertRaises(AccountingError):self.post(periodo=uuid.uuid4())
  chart=ChartOfAccounts.plain_objects.create(tenant=self.foreign,name='Foreign')
  foreign=Account.plain_objects.create(tenant=self.foreign,chart_of_accounts=chart,code='1105',name='Foreign',type='ASSET')
  with self.assertRaises(AccountingError):self.post(transacciones_data=[{'cuenta_id':foreign.pk,'debit':'10'},{'cuenta_id':self.b.pk,'credit':'10'}])
  self.assertFalse(JournalEntry.plain_objects.filter(tenant=self.tenant).exists())
 def test_revoked_link_blocks_posting_and_catalog(self):
  VerifiedCompanyLink.objects.filter(pk=self.link.pk).update(revoked_at=timezone.now())
  with self.assertRaises(APIException):self.post()
  self.assertEqual(self.call('list').status_code,403)
 def test_catalog_owner_scope_and_spoofed_tenant(self):
  response=self.call('list');self.assertEqual(response.status_code,200,response.data)
  self.assertEqual(self.call('list',user=self.other).status_code,403)
  self.assertIn(self.call('list',HTTP_X_TENANT_ID=str(self.foreign.pk)).status_code,[400,403])
 def test_create_partial_update_and_protected_fields(self):
  response=self.call('create','post',{'code':'1205','name':'Fixture account'})
  self.assertEqual(response.status_code,201,response.data)
  account=Account.plain_objects.get(pk=response.data['id']);self.assertEqual(account.tenant_id,self.tenant.pk)
  response=self.call('partial_update','patch',{'name':'Edited fixture'},pk=account.pk)
  self.assertEqual(response.status_code,200,response.data)
  self.assertEqual(self.call('partial_update','patch',{'initial_balance':'1000'},pk=account.pk).status_code,400)
  self.assertEqual(self.call('create','post',{'code':'1206','name':'No','tenant_id':str(self.foreign.pk)}).status_code,400)
 def test_parent_cycle_and_posted_reclassification_are_rejected(self):
  self.assertEqual(self.call('partial_update','patch',{'parent_account':str(self.a.pk)},pk=self.a.pk).status_code,400)
  self.post()
  self.assertEqual(self.call('partial_update','patch',{'code':'1205'},pk=self.a.pk).status_code,400)
  self.assertEqual(self.call('destroy','delete',pk=self.a.pk).status_code,400)
 def test_trial_balance_is_scoped_read_only_and_decimal_strings(self):
  self.post()
  response=self.call('trial_balance');self.assertEqual(response.status_code,200,response.data)
  self.assertEqual(response.data['total_debit'],'10.00');self.assertEqual(response.data['currency'],'COP')
  self.assertEqual(self.call('trial_balance',user=self.other).status_code,403)

 def test_projection_status_is_owner_scoped_and_hides_incomplete_amounts(self):
  self.post()
  response=self.call('projection_status');self.assertEqual(response.status_code,200,response.data)
  self.assertFalse(response.data['complete']);self.assertEqual(response.data['balances'],[])
  self.assertEqual(self.call('projection_status',user=self.other).status_code,403)

 def test_nonaccounting_owner_cannot_gain_access_by_superuser_role(self):
  self.other.is_superuser=True;self.other.is_staff=True;self.other.save()
  self.assertEqual(self.call('list',user=self.other).status_code,403)

 def test_profitability_scoped_exact_and_read_only(self):
  self.post();before=JournalEntry.plain_objects.count()
  response=self.call('profitability');self.assertEqual(response.status_code,200,response.data)
  self.assertEqual(response.data['net_profit'],'10.00')
  self.assertEqual(response.data['net_margin']['value'],'100.0000')
  self.assertEqual(response.data['scope'],'company')
  self.assertEqual(response.data['currency'],'COP')
  self.assertEqual(response.data['sources'][0]['account_id'],str(self.b.pk))
  self.assertEqual(JournalEntry.plain_objects.count(),before)
  self.assertEqual(self.call('profitability',user=self.other).status_code,403)
 def test_profitability_empty_and_invalid_dates(self):
  response=self.call('profitability');self.assertEqual(response.status_code,200)
  self.assertIsNone(response.data['net_margin']['value'])
  self.assertEqual(response.data['net_margin']['unavailable_reason'],'NON_POSITIVE_REVENUE')
  from apps.core_erp.accounting.reports_engine import ReportsEngine
  from datetime import date
  with self.assertRaises(AccountingError):ReportsEngine.get_profitability(self.tenant.pk,date(2026,12,1),date(2026,1,1))
  request=APIRequestFactory().get('/fixture/',{'provider_id':str(self.provider.pk),'desde':'invalid'})
  force_authenticate(request,user=self.user)
  self.assertEqual(PlanCuentaViewSet.as_view({'get':'profitability'})(request).status_code,400)
 def test_profitability_expenses_and_reversal(self):
  from apps.core_erp.accounting.reports_engine import ReportsEngine
  self.post()
  cost=Account.plain_objects.create(tenant=self.tenant,chart_of_accounts=self.chart,code='5105',name='Expense',type='EXPENSE')
  entry=LedgerEngine.post_lines(tenant_id=self.tenant.pk,entry_date=timezone.localdate(),description='Cost',
       lines_data=[{'account':cost,'debit':'4.00'},{'account':self.a,'credit':'4.00'}],
       actor=self.user,idempotency_key='profitability-cost')
  today=timezone.localdate()
  report=ReportsEngine.get_profitability(self.tenant.pk,today,today)
  self.assertEqual(report['net_margin']['value'],'60.0000')
  LedgerEngine.reverse_entry(entry.pk,'Correction',tenant_id=self.tenant.pk,actor=self.user)
  self.assertEqual(ReportsEngine.get_profitability(self.tenant.pk,today,today)['net_profit'],'10.00')

 def test_profitability_rejects_opening_and_currency_ambiguity(self):
  from apps.core_erp.accounting.reports_engine import ReportsEngine
  today=timezone.localdate()
  entry=self.post()
  JournalEntry.plain_objects.filter(pk=entry.pk).update(base_currency='USD')
  with self.assertRaises(AccountingError):ReportsEngine.get_profitability(self.tenant.pk,today,today)
  JournalEntry.plain_objects.filter(pk=entry.pk).update(base_currency='COP')
  Account.plain_objects.filter(pk=self.a.pk).update(initial_balance='1.00')
  with self.assertRaises(AccountingError):ReportsEngine.get_profitability(self.tenant.pk,today,today)
 def test_profitability_excludes_other_company_drafts_and_other_dates(self):
  from apps.core_erp.accounting.reports_engine import ReportsEngine
  today=timezone.localdate()
  self.post()
  foreign=ReportsEngine.get_profitability(self.foreign.pk,today,today)
  self.assertEqual(foreign['revenue'],'0.00');self.assertEqual(foreign['sources'],[])
  report=ReportsEngine.get_profitability(self.tenant.pk,today-timedelta(days=2),today-timedelta(days=1))
  self.assertEqual(report['revenue'],'0.00')
  from apps.core_erp.accounting.journal_service import JournalService
  JournalService.create_entry(str(self.tenant.pk),today,'Draft',[{'account':self.a,'debit':'10.00'},{'account':self.b,'credit':'10.00'}],created_by=self.user)
  self.assertEqual(ReportsEngine.get_profitability(self.tenant.pk,today,today)['revenue'],'10.00')

 def ratio_mapping(self):
  liability=Account.plain_objects.create(tenant=self.tenant,chart_of_accounts=self.chart,code='2105',name='Current liability',type='LIABILITY')
  return {'cash_equivalents':[str(self.a.pk)],'temporary_investments':[],
          'immediate_receivables':[],'current_liabilities':[str(liability.pk)]}
 def configure_ratio(self,mapping,**changes):
  data={'mapping':mapping,'evidence_digest':'b'*64,'expected_revision':0,'confirmed':True};data.update(changes)
  return self.call('liquidity_classification','post',data)
 def test_liquidity_explicit_review_calculation_and_no_payment(self):
  mapping=self.ratio_mapping();self.post()
  liability=Account.plain_objects.get(pk=mapping['current_liabilities'][0])
  LedgerEngine.post_lines(tenant_id=self.tenant.pk,entry_date=timezone.localdate(),description='Liability',
      lines_data=[{'account':self.a,'debit':'5.00'},{'account':liability,'credit':'5.00'}],
      actor=self.user,idempotency_key='liquidity-liability')
  self.assertEqual(self.configure_ratio(mapping).status_code,201)
  count=JournalEntry.plain_objects.count()
  response=self.call('liquidity_ratio');self.assertEqual(response.status_code,200,response.data)
  self.assertEqual(response.data['value'],'3.0000')
  self.assertEqual(response.data['totals']['cash_equivalents'],'15.00')
  self.assertEqual(response.data['policy']['revision'],1)
  self.assertEqual(JournalEntry.plain_objects.count(),count)
  self.assertEqual(self.call('liquidity_ratio',user=self.other).status_code,403)
  self.assertEqual(self.call('liquidity_classification',user=self.other).status_code,403)
 def test_liquidity_missing_classification_and_zero_denominator(self):
  self.assertEqual(self.call('liquidity_ratio').data['unavailable_reason'],'REVIEWED_CLASSIFICATION_REQUIRED')
  self.configure_ratio(self.ratio_mapping())
  response=self.call('liquidity_ratio');self.assertIsNone(response.data['value'])
  self.assertEqual(response.data['unavailable_reason'],'NON_POSITIVE_CURRENT_LIABILITIES')
 def test_liquidity_rejects_duplicate_foreign_and_wrong_type_accounts(self):
  mapping=self.ratio_mapping()
  mapping['temporary_investments']=[str(self.a.pk)]
  self.assertEqual(self.configure_ratio(mapping).status_code,400)
  mapping['temporary_investments']=[str(self.b.pk)]
  self.assertEqual(self.configure_ratio(mapping).status_code,400)
  mapping['temporary_investments']=[str(uuid.uuid4())]
  self.assertEqual(self.configure_ratio(mapping).status_code,400)
  self.assertFalse(AccountingRatioPolicy.objects.filter(tenant=self.tenant).exists())
 def test_liquidity_revision_conflict_and_immutable_review(self):
  mapping=self.ratio_mapping()
  self.assertEqual(self.configure_ratio(mapping,confirmed=False).status_code,400)
  self.assertEqual(self.configure_ratio(mapping,expected_revision=True).status_code,400)
  self.assertEqual(self.configure_ratio(mapping).status_code,201)
  self.assertEqual(self.configure_ratio(mapping).status_code,400)
  self.assertEqual(self.configure_ratio(mapping,expected_revision=1).status_code,201)
  self.assertEqual(AccountingRatioPolicy.objects.filter(tenant=self.tenant).count(),2)
  policy=AccountingRatioPolicy.objects.filter(tenant=self.tenant).first()
  with self.assertRaises(PermissionError):policy.save()
  with self.assertRaises(PermissionError):policy.delete()
 def test_liquidity_detects_policy_tamper_and_inactive_accounts(self):
  mapping=self.ratio_mapping();self.configure_ratio(mapping)
  Account.plain_objects.filter(pk=self.a.pk).update(is_active=False)
  self.assertEqual(self.call('liquidity_ratio').status_code,400)
  Account.plain_objects.filter(pk=self.a.pk).update(is_active=True)
  AccountingRatioPolicy.objects.filter(tenant=self.tenant).update(evidence_digest='c'*64)
  self.assertEqual(self.call('liquidity_ratio').status_code,400)
 def test_liquidity_negative_balance_requires_review(self):
  mapping=self.ratio_mapping();self.configure_ratio(mapping)
  liability=Account.plain_objects.get(pk=mapping['current_liabilities'][0])
  LedgerEngine.post_lines(tenant_id=self.tenant.pk,entry_date=timezone.localdate(),description='Review debit liability',
      lines_data=[{'account':liability,'debit':'5.00'},{'account':self.a,'credit':'5.00'}],
      actor=self.user,idempotency_key='liquidity-negative')
  result=self.call('liquidity_ratio').data
  self.assertIsNone(result['value']);self.assertEqual(result['unavailable_reason'],'NEGATIVE_ACCOUNT_BALANCE_REQUIRES_REVIEW')

 def test_liquidity_existing_uuid_cannot_overwrite_history(self):
  from django.db import IntegrityError,transaction
  self.configure_ratio(self.ratio_mapping())
  policy=AccountingRatioPolicy.objects.get(tenant=self.tenant)
  clone=AccountingRatioPolicy(id=policy.pk,tenant=self.tenant,revision=2,mapping=policy.mapping,
       reviewer=self.user,evidence_digest='c'*64,digest='c'*64)
  with self.assertRaises(IntegrityError),transaction.atomic():clone.save()
  policy.refresh_from_db();self.assertEqual(policy.revision,1);self.assertEqual(policy.evidence_digest,'b'*64)
 def test_liquidity_real_foreign_account_and_revoked_link(self):
  mapping=self.ratio_mapping()
  chart=ChartOfAccounts.plain_objects.create(tenant=self.foreign,name='Foreign ratio')
  foreign=Account.plain_objects.create(tenant=self.foreign,chart_of_accounts=chart,code='1105',name='Foreign',type='ASSET')
  mapping['cash_equivalents']=[str(foreign.pk)]
  self.assertEqual(self.configure_ratio(mapping).status_code,400)
  mapping['cash_equivalents']=[str(self.a.pk)]
  VerifiedCompanyLink.objects.filter(pk=self.link.pk).update(revoked_at=timezone.now())
  self.assertEqual(self.configure_ratio(mapping).status_code,403)
  self.assertFalse(AccountingRatioPolicy.objects.filter(tenant=self.tenant).exists())

 def test_liquidity_history_keyset_and_immutable_old_versions(self):
  from apps.core_erp.accounting import ratios
  mapping=self.ratio_mapping()
  for revision in range(3):self.assertEqual(self.configure_ratio(mapping,expected_revision=revision).status_code,201)
  first=ratios.history(self.tenant.pk,limit=2)
  self.assertEqual([r['revision'] for r in first['results']],[3,2]);self.assertEqual(first['next_before'],2)
  self.configure_ratio(mapping,expected_revision=3)
  second=ratios.history(self.tenant.pk,limit=2,before_revision=2)
  self.assertEqual([r['revision'] for r in second['results']],[1]);self.assertIsNone(second['next_before'])
  Account.plain_objects.filter(pk=self.a.pk).update(is_active=False)
  self.assertEqual(len(ratios.history(self.tenant.pk)['results']),4)
 def test_liquidity_history_owner_scope_and_invalid_cursors(self):
  from apps.core_erp.accounting import ratios
  self.configure_ratio(self.ratio_mapping())
  self.assertEqual(self.call('liquidity_history').status_code,200)
  self.assertEqual(self.call('liquidity_history',user=self.other).status_code,403)
  self.assertEqual(ratios.history(self.foreign.pk)['results'],[])
  for limit in [0,51,True,'2']:
   with self.assertRaises(AccountingError):ratios.history(self.tenant.pk,limit=limit)
  for query in [{'limite':'51'},{'antes_revision':'-1'},{'antes_revision':'x'}]:
   request=APIRequestFactory().get('/fixture/',{'provider_id':str(self.provider.pk),**query});force_authenticate(request,user=self.user)
   self.assertEqual(PlanCuentaViewSet.as_view({'get':'liquidity_history'})(request).status_code,400)
 def test_liquidity_history_detects_old_record_tamper(self):
  from apps.core_erp.accounting import ratios
  mapping=self.ratio_mapping();self.configure_ratio(mapping);self.configure_ratio(mapping,expected_revision=1)
  AccountingRatioPolicy.objects.filter(tenant=self.tenant,revision=1).update(evidence_digest='f'*64)
  with self.assertRaises(AccountingError):ratios.history(self.tenant.pk)
  self.assertEqual(self.call('liquidity_history').status_code,400)

 def test_explicit_liquidity_revision_reconstructs_without_overwriting(self):
  from apps.core_erp.accounting import ratios
  mapping=self.ratio_mapping();self.configure_ratio(mapping);self.post()
  liability=Account.plain_objects.get(pk=mapping['current_liabilities'][0])
  LedgerEngine.post_lines(tenant_id=self.tenant.pk,entry_date=timezone.localdate(),description='Revision funding',
   lines_data=[{'account':self.a,'debit':'5.00'},{'account':liability,'credit':'5.00'}],actor=self.user,idempotency_key='revision-funding')
  replacement=Account.plain_objects.create(tenant=self.tenant,chart_of_accounts=self.chart,code='1110',name='Other cash',type='ASSET')
  mapping['cash_equivalents']=[str(replacement.pk)];self.configure_ratio(mapping,expected_revision=1)
  today=timezone.localdate()
  self.assertEqual(ratios.quick_ratio(self.tenant.pk,today)['value'],'0.0000')
  prior=ratios.quick_ratio(self.tenant.pk,today,policy_revision=1)
  self.assertEqual(prior['value'],'3.0000');self.assertEqual(prior['policy']['revision'],1)
  self.assertEqual(prior['historical_policy'],'explicit_reviewed_revision_applied_to_cutoff')
  self.assertEqual(AccountingRatioPolicy.objects.filter(tenant=self.tenant).count(),2)
 def test_explicit_liquidity_revision_is_scoped_and_validated(self):
  from apps.core_erp.accounting import ratios
  self.configure_ratio(self.ratio_mapping());today=timezone.localdate()
  for value in [True,0,-1,'1',99]:
   with self.assertRaises(AccountingError):ratios.quick_ratio(self.tenant.pk,today,policy_revision=value)
  with self.assertRaises(AccountingError):ratios.quick_ratio(self.foreign.pk,today,policy_revision=1)
  request=APIRequestFactory().get('/fixture/',{'provider_id':str(self.provider.pk),'revision':'0'});force_authenticate(request,user=self.user)
  self.assertEqual(PlanCuentaViewSet.as_view({'get':'liquidity_ratio'})(request).status_code,400)

 def test_cash_simulation_owner_scope_and_no_accounting_writes(self):
  data={'opening_cash':'10.00','observations':[{'date':(timezone.localdate()-timedelta(days=6-i)).isoformat(),'net_cash_flow':'1.00'} for i in range(7)],'seed':7,'paths':100}
  before=JournalEntry.plain_objects.count()
  result=self.call('cash_simulation','post',data)
  self.assertEqual(result.status_code,200,result.data)
  self.assertEqual(result.data['results'][0]['ending_cash_p50'],'40.00')
  self.assertEqual(result.data['tenant_id'],str(self.tenant.pk));self.assertEqual(result.data['currency'],'COP')
  self.assertFalse(result.data['ledger_written']);self.assertEqual(JournalEntry.plain_objects.count(),before)
  self.assertEqual(self.call('cash_simulation','post',data,user=self.other).status_code,403)
  self.assertEqual(self.call('cash_simulation','post',{**data,'tenant_id':str(self.foreign.pk)}).status_code,400)

 def test_cash_backtest_is_owner_scoped_and_does_not_post(self):
  from datetime import date
  scenario={'opening_cash':'10.00','observations':[{'date':f'2026-01-{i:02}','net_cash_flow':'1.00'} for i in range(1,8)],'seed':1,'paths':100}
  data={'scenario':scenario,'actuals':[{'date':(date(2026,1,8)+timedelta(days=i)).isoformat(),'net_cash_flow':'1.00'} for i in range(365)]}
  before=JournalEntry.plain_objects.count();response=self.call('cash_backtest','post',data)
  self.assertEqual(response.status_code,200,response.data)
  self.assertEqual(response.data['mean_absolute_terminal_error_across_horizons'],'0.00')
  self.assertEqual(response.data['tenant_id'],str(self.tenant.pk))
  self.assertEqual(self.call('cash_backtest','post',data,user=self.other).status_code,403)
  self.assertEqual(JournalEntry.plain_objects.count(),before)

 def test_cash_sensitivity_owner_scope_and_unchanged_ledger(self):
  scenario={'opening_cash':'10.00','observations':[{'date':f'2026-01-{i:02}','net_cash_flow':'1.00'} for i in range(1,8)],'seed':1,'paths':100}
  data={'scenario':scenario,'shocks':[{'name':'Declared','opening_cash_delta':'5.00','daily_net_flow_delta':'0.00'}]}
  before=JournalEntry.plain_objects.count();result=self.call('cash_sensitivity','post',data)
  self.assertEqual(result.status_code,200,result.data)
  self.assertEqual(result.data['variants'][0]['changes_from_base'][0]['ending_cash_p50_delta'],'5.00')
  self.assertEqual(result.data['tenant_id'],str(self.tenant.pk))
  self.assertEqual(self.call('cash_sensitivity','post',data,user=self.other).status_code,403)
  self.assertEqual(JournalEntry.plain_objects.count(),before)

 def test_multi_window_backtest_owner_scope_and_no_posting(self):
  from datetime import date
  def window(offset):
   start=date(2026,1,1)+timedelta(days=offset)
   return {'scenario':{'opening_cash':'10.00','seed':1,'paths':100,'observations':[{'date':(start+timedelta(days=i)).isoformat(),'net_cash_flow':'1.00'} for i in range(7)]},
    'actuals':[{'date':(start+timedelta(days=7+i)).isoformat(),'net_cash_flow':'1.00'} for i in range(365)]}
  data={'windows':[window(0),window(7)]};before=JournalEntry.plain_objects.count()
  response=self.call('cash_backtest_windows','post',data)
  self.assertEqual(response.status_code,200,response.data);self.assertEqual(response.data['summary'][0]['mean_absolute_terminal_error'],'0.00')
  self.assertEqual(response.data['tenant_id'],str(self.tenant.pk))
  self.assertEqual(self.call('cash_backtest_windows','post',data,user=self.other).status_code,403)
  self.assertEqual(JournalEntry.plain_objects.count(),before)

 def test_reconciliation_clean_page_is_owner_scoped_and_read_only(self):
  self.post();before=list(JournalEntry.plain_objects.filter(tenant=self.tenant).values())
  result=self.call('reconciliation_diagnostic');self.assertEqual(result.status_code,200,result.data)
  self.assertEqual(result.data['entries'][0]['findings'],[]);self.assertFalse(result.data['full_ledger_certified'])
  self.assertEqual(self.call('reconciliation_diagnostic',user=self.other).status_code,403)
  self.assertEqual(before,list(JournalEntry.plain_objects.filter(tenant=self.tenant).values()))
 def test_reconciliation_flags_legacy_without_rehash_or_amount_disclosure(self):
  entry=self.post();JournalEntry.plain_objects.filter(pk=entry.pk).update(hash_version='legacy',posted_at=None)
  Account.plain_objects.filter(pk=self.a.pk).update(initial_balance='123.45')
  from apps.core_erp.accounting.reconciliation import inspect_company
  before=JournalEntry.plain_objects.get(pk=entry.pk).system_hash
  result=inspect_company(self.tenant.pk)
  self.assertEqual(result['initial_balance_account_count'],1)
  self.assertIn('LEGACY_HASH_REVIEW_REQUIRED',result['entries'][0]['findings'])
  self.assertIn('POSTED_TIMESTAMP_MISSING',result['entries'][0]['findings'])
  self.assertNotIn('123.45',str(result));self.assertEqual(JournalEntry.plain_objects.get(pk=entry.pk).system_hash,before)
 def test_reconciliation_pagination_and_validation(self):
  from apps.core_erp.accounting.reconciliation import inspect_company
  self.post(idempotency_key='diagnostic-1');self.post(idempotency_key='diagnostic-2')
  first=inspect_company(self.tenant.pk,limit=1);second=inspect_company(self.tenant.pk,limit=1,after_id=first['next_after'])
  self.assertNotEqual(first['entries'][0]['journal_id'],second['entries'][0]['journal_id']);self.assertIsNone(second['next_after'])
  self.assertEqual(inspect_company(self.foreign.pk)['entries'],[])
  for limit in [0,51,True]:
   with self.assertRaises(AccountingError):inspect_company(self.tenant.pk,limit=limit)
  with self.assertRaises(AccountingError):inspect_company(self.tenant.pk,after_id='invalid')
 def test_reconciliation_detects_hash_and_valuation_changes(self):
  from apps.core_erp.accounting.reconciliation import inspect_company
  entry=self.post()
  from apps.core_erp.accounting.models import LedgerEntry
  LedgerEntry.plain_objects.filter(journal_entry=entry).update(amount_base='0.00')
  findings=inspect_company(self.tenant.pk)['entries'][0]['findings']
  self.assertIn('HASH_MISMATCH',findings);self.assertIn('BASE_VALUATION_REVIEW_REQUIRED',findings)

 def test_fiscal_envelope_preview_is_owner_bound_and_not_persisted(self):
  import base64
  encode=lambda n:base64.urlsafe_b64encode(bytes(n)).rstrip(b'=').decode()
  data={'schema':'sgacd-fiscal-envelope-v1','algorithm':'AES-256-GCM+A256KW','context':{'company_id':str(self.tenant.pk),'document_id':str(uuid.uuid4())},'iv':encode(12),'wrapped_key':encode(40),'ciphertext':encode(17)}
  before=JournalEntry.plain_objects.count();result=self.call('validate_fiscal_envelope','post',data)
  self.assertEqual(result.status_code,200,result.data);self.assertFalse(result.data['stored'])
  self.assertFalse(result.data['authenticated_ciphertext_verified']);self.assertEqual(JournalEntry.plain_objects.count(),before)
  self.assertEqual(self.call('validate_fiscal_envelope','post',data,user=self.other).status_code,403)
  self.assertEqual(self.call('validate_fiscal_envelope','post',{**data,'plaintext':'forbidden'}).status_code,400)
  data['context']['company_id']=str(self.foreign.pk)
  self.assertEqual(self.call('validate_fiscal_envelope','post',data).status_code,400)

 def test_envelope_parser_bounds_read_and_accepts_small_json(self):
  from apps.core_erp.accounting.fiscal_envelope_parser import FiscalEnvelopeJSONParser
  from apps.core_erp.accounting.fiscal_envelope import MAX_WIRE_BYTES
  from rest_framework.exceptions import ParseError
  from io import BytesIO
  self.assertEqual(FiscalEnvelopeJSONParser().parse(BytesIO(b'{"schema":"test"}')),{'schema':'test'})
  stream=BytesIO(b' '* (MAX_WIRE_BYTES+100))
  with self.assertRaises(ParseError):FiscalEnvelopeJSONParser().parse(stream)
  self.assertEqual(stream.tell(),MAX_WIRE_BYTES+1)

if __name__=='__main__':unittest.main()
