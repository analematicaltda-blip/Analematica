"""Real ORM/DRF contracts for legacy report routes; no middleware tenant trust."""
import runpy,unittest,uuid
from pathlib import Path
from datetime import timedelta
from decimal import localcontext,Inexact,Rounded
fixture=runpy.run_path(str(Path(__file__).with_name('accounting_adapter_check.py')),run_name='presentation_fixture')
from rest_framework.test import APIRequestFactory,force_authenticate
from django.utils import timezone
from apps.core_erp.accounting.presentation.balances_views import AccountBalanceView
from apps.core_erp.accounting.presentation.reports_views import BalanceGeneralView,ProfitLossView
from apps.core_erp.accounting.presentation.finance_views import FinancialRatiosView,CashFlowView
from apps.turismo.models import VerifiedCompanyLink
from apps.core_erp.accounting.journal_service import JournalService
class PresentationChecks(unittest.TestCase):
 def setUp(self):
  self.base=fixture['AdapterTests']();self.base.setUp();self.addCleanup(self.base.doCleanups);self.day=timezone.localdate()
 def call(self,view,query='',*,user=None,company=None,context=None):
  req=APIRequestFactory().get('/fixture/'+query,HTTP_X_TENANT_ID=str(company or self.base.tenant.pk))
  if context is not None:req.tenant_id=context
  force_authenticate(req,user=user or self.base.user)
  return view.as_view()(req)
 def test_balance_dates_are_parsed_and_currency_comes_from_company(self):
  self.base.post();r=self.call(BalanceGeneralView,'?date='+self.day.isoformat())
  self.assertEqual(r.status_code,200);self.assertEqual(r.data['currency'],'COP');self.assertEqual(r.data['totals']['assets'],'10.00');self.assertEqual(r['Cache-Control'],'no-store')
 def test_default_cutoff_uses_local_date(self):
  r=self.call(BalanceGeneralView);self.assertEqual(r.status_code,200);self.assertEqual(r.data['date'],self.day.isoformat())
 def test_foreign_company_and_non_owner_rejected(self):
  for view in [AccountBalanceView,BalanceGeneralView,ProfitLossView,FinancialRatiosView,CashFlowView]:
   self.assertEqual(self.call(view,user=self.base.other).status_code,403)
   self.assertEqual(self.call(view,company=uuid.uuid4()).status_code,403)
 def test_revoked_link_rejected_on_every_report_route(self):
  VerifiedCompanyLink.objects.filter(pk=self.base.link.pk).update(revoked_at=timezone.now())
  for view in [AccountBalanceView,BalanceGeneralView,ProfitLossView,FinancialRatiosView,CashFlowView]:self.assertEqual(self.call(view).status_code,403)
 def test_mismatched_context_and_header_rejected(self):
  self.assertEqual(self.call(BalanceGeneralView,context=str(uuid.uuid4())).status_code,403)
 def test_bad_or_duplicate_dates_and_reversed_interval_rejected(self):
  for query in ['?date=bad','?date=2026-02-30','?date=20261111','?date=2026-01-01&date=2026-01-02','?tenant_id='+str(self.base.tenant.pk)]:
   self.assertEqual(self.call(BalanceGeneralView,query).status_code,400)
  self.assertEqual(self.call(ProfitLossView,'?start=2026-02-01&end=2026-01-01').status_code,400)
 def test_balances_use_uuid_posted_only_and_natural_revenue_sign(self):
  self.base.post()
  JournalService.create_entry(str(self.base.tenant.pk),self.day,'Unposted fixture',[{'account':self.base.a,'debit':'99.00'},{'account':self.base.b,'credit':'99.00'}],created_by=self.base.user)
  r=self.call(AccountBalanceView,'?date='+self.day.isoformat());self.assertEqual(r.status_code,200)
  rows={row['account_id']:row for row in r.data};self.assertEqual(rows[str(self.base.a.pk)]['debit'],'10.00');self.assertEqual(rows[str(self.base.b.pk)]['balance'],'10.00')
 def test_zero_denominators_are_unavailable_not_zero_ratios(self):
  r=self.call(FinancialRatiosView,'?date='+self.day.isoformat());self.assertEqual(r.status_code,200)
  for value in r.data['ratios'].values():self.assertIsNone(value['value']);self.assertEqual(value['status'],'NOT_CALCULABLE')
 def test_ratios_use_cutoff_month_and_independent_decimal_context(self):
  self.base.post();cutoff=self.day-timedelta(days=70)
  r=self.call(FinancialRatiosView,'?date='+cutoff.isoformat());self.assertEqual(r.status_code,200);self.assertEqual(r.data['summary']['net_income_month'],'0.00')
  expected=self.call(FinancialRatiosView,'?date='+self.day.isoformat()).data
  with localcontext() as ctx:
   ctx.prec=2;ctx.traps[Inexact]=True;ctx.traps[Rounded]=True
   self.assertEqual(self.call(FinancialRatiosView,'?date='+self.day.isoformat()).data,expected)
 def test_zero_accounts_remain_visible_without_per_account_aggregates(self):
  from apps.core_erp.accounting.models import Account
  from django.db import connection
  from django.test.utils import CaptureQueriesContext
  extras=[Account.plain_objects.create(tenant=self.base.tenant,chart_of_accounts=self.base.chart,
          code='AUDIT'+str(i),name='Unused synthetic account',type='ASSET') for i in range(12)]
  with CaptureQueriesContext(connection) as queries:r=self.call(AccountBalanceView)
  self.assertEqual(r.status_code,200)
  rows={row['account_id']:row for row in r.data}
  for account in extras:self.assertEqual(rows[str(account.pk)]['balance'],'0.00')
  aggregates=[q['sql'] for q in queries.captured_queries if 'SUM(' in q['sql'].upper()]
  self.assertEqual(len(aggregates),1)
 def test_inactive_current_user_cannot_reuse_authenticated_object(self):
  from django.contrib.auth import get_user_model
  get_user_model().objects.filter(pk=self.base.user.pk).update(is_active=False)
  self.addCleanup(lambda:get_user_model().objects.filter(pk=self.base.user.pk).update(is_active=True))
  self.assertEqual(self.call(BalanceGeneralView).status_code,403)

 def test_cashflow_returns_explicit_unavailable_not_server_error(self):
  r=self.call(CashFlowView);self.assertEqual(r.status_code,501);self.assertEqual(r.data['code'],'CASH_FLOW_NOT_CONFIGURED');self.assertEqual(r['Cache-Control'],'no-store')
 def test_legacy_source_errors_are_sanitized(self):
  from apps.core_erp.accounting.exceptions import AccountingError
  from unittest.mock import patch
  with patch('apps.core_erp.accounting.presentation.reports_views.ReportsEngine.get_balance_sheet',side_effect=AccountingError('private-source-detail')):
   r=self.call(BalanceGeneralView);self.assertEqual(r.status_code,400);self.assertNotIn('private-source-detail',str(r.data))
class LegacyViewSetChecks(unittest.TestCase):
 setUp=PresentationChecks.setUp
 def views(self):
  from apps.core_erp.accounting.presentation.views import AccountViewSet,JournalEntryViewSet
  return AccountViewSet,JournalEntryViewSet
 def invoke(self,view,action='list',method='get',*,user=None,pk=None,company=None,data=None):
  req=getattr(APIRequestFactory(),method)('/legacy/',data or {},format='json',HTTP_X_TENANT_ID=str(company or self.base.tenant.pk))
  force_authenticate(req,user=user or self.base.user)
  return view.as_view({method:action})(req,**({'pk':str(pk)} if pk else {}))
 def test_legacy_module_imports_and_uuid_serializers_are_read_only(self):
  accounts,journals=self.views()
  result=self.invoke(accounts);self.assertEqual(result.status_code,200)
  self.assertEqual(result['Cache-Control'],'no-store')
  self.assertTrue(all(str(uuid.UUID(row['id']))==row['id'] for row in (result.data['results'] if isinstance(result.data,dict) else result.data)))
  from apps.core_erp.accounting.presentation.serializers import AccountSerializer,JournalEntrySerializer
  for serializer in [AccountSerializer(),JournalEntrySerializer()]:self.assertTrue(all(f.read_only for f in serializer.fields.values()))
 def test_legacy_foreign_or_stale_authorization_cannot_read_catalog_or_journals(self):
  for view in self.views():
   self.assertEqual(self.invoke(view,user=self.base.other).status_code,403)
   self.assertEqual(self.invoke(view,company=uuid.uuid4()).status_code,403)
  VerifiedCompanyLink.objects.filter(pk=self.base.link.pk).update(revoked_at=timezone.now())
  for view in self.views():self.assertEqual(self.invoke(view).status_code,403)
 def test_legacy_retrieve_cannot_cross_company_even_with_known_uuid(self):
  accounts,_=self.views()
  from apps.core_erp.accounting.models import Account,ChartOfAccounts
  chart=ChartOfAccounts.plain_objects.create(tenant=self.base.foreign,name='Foreign synthetic chart')
  account=Account.plain_objects.create(tenant=self.base.foreign,chart_of_accounts=chart,code='FOREIGN',name='Foreign',type='ASSET')
  self.assertEqual(self.invoke(accounts,action='retrieve',pk=account.pk).status_code,404)
 def test_journal_compatibility_is_posted_only(self):
  _,journals=self.views();posted=self.base.post()
  draft=JournalService.create_entry(str(self.base.tenant.pk),self.day,'Unposted fixture',[{'account':self.base.a,'debit':'1.00'},{'account':self.base.b,'credit':'1.00'}],created_by=self.base.user)
  response=self.invoke(journals);self.assertEqual(response.status_code,200)
  rows=response.data['results'] if isinstance(response.data,dict) else response.data
  self.assertIn(str(posted.pk),[row['id'] for row in rows]);self.assertNotIn(str(draft.pk),[row['id'] for row in rows])
  self.assertEqual(self.invoke(journals,action='retrieve',pk=draft.pk).status_code,404)
 def test_legacy_reverse_does_not_bypass_reviewed_command_flow(self):
  from apps.core_erp.accounting.models import JournalEntry
  _,journals=self.views();posted=self.base.post();before=JournalEntry.plain_objects.count()
  response=self.invoke(journals,action='reverse',method='post',pk=posted.pk,data={'reason':'Unreviewed request'})
  self.assertEqual(response.status_code,409);self.assertEqual(response.data['code'],'USE_REVIEWED_REVERSAL_WORKFLOW')
  self.assertEqual(JournalEntry.plain_objects.count(),before)
  self.assertEqual(self.invoke(journals,action='reverse',method='post',pk=posted.pk,user=self.base.other).status_code,403)
 def test_generic_writes_are_not_exposed(self):
  from rest_framework.routers import SimpleRouter
  for index,view in enumerate(self.views()):
   router=SimpleRouter();router.register('readonly'+str(index),view,basename='readonly'+str(index))
   actions={a for route in router.get_routes(view) for a in router.get_method_map(view,route.mapping).values()}
   self.assertTrue({'create','update','partial_update','destroy'}.isdisjoint(actions))

if __name__=='__main__':unittest.main(verbosity=2)
