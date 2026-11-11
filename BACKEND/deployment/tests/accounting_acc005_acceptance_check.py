"""ACC005 authoritative identities, stale credentials and correct bridge lock order."""
import runpy,unittest,uuid
from pathlib import Path
from datetime import timedelta
f=runpy.run_path(str(Path(__file__).with_name('company_identity_check.py')),run_name='acc005_fixture')
from django.utils import timezone
from django.db import connection
from django.test.utils import CaptureQueriesContext
from rest_framework.exceptions import APIException
from apps.turismo.services.company_identity import resolve_company,review_link
from apps.turismo.models import VerifiedCompanyLink
from api.models import CustomUser
from apps.core_erp.accounting.models import ChartOfAccounts,Account,FiscalPeriod,JournalEntry,LedgerEntry,AccountingEventReceipt,AccountingAuditLog
from apps.core_erp.outbox_models import OutboxEvent
from apps.core_erp.fx.models import Currency,FXRateTable
from apps.prestadores.mi_negocio.gestion_contable.contabilidad.services import ContabilidadService
for model in [ChartOfAccounts,Account,FiscalPeriod,JournalEntry,LedgerEntry,AccountingEventReceipt,AccountingAuditLog,OutboxEvent,Currency,FXRateTable]:f['fixture']['create'](model)
class ACC005Acceptance(unittest.TestCase):
 def setUp(self):self.c=f['CompanyChecks']();self.c.setUp()
 def test_distinct_provider_and_tenant_are_resolved_from_review_not_uuid_equivalence(self):
  link=self.c.review(apply=True);self.assertNotEqual(link.provider_id,link.tenant_id);self.assertEqual(resolve_company(f['F'].owner,self.c.provider.pk).tenant_id,self.c.tenant.pk)
 def test_stale_active_actor_is_rechecked_against_database(self):
  self.c.review(apply=True);actor=CustomUser.objects.get(pk=f['F'].owner.pk);CustomUser.objects.filter(pk=actor.pk).update(is_active=False)
  try:
   with self.assertRaises(APIException):resolve_company(actor,self.c.provider.pk)
  finally:CustomUser.objects.filter(pk=actor.pk).update(is_active=True)
 def test_cached_superuser_privilege_does_not_authorize_review(self):
  CustomUser.objects.filter(pk=self.c.operator.pk).update(is_superuser=False)
  with self.assertRaises(APIException):self.c.review(apply=True)
  self.assertFalse(VerifiedCompanyLink.objects.filter(provider=self.c.provider).exists())
 def test_existing_link_rechecks_reviewer_privileges(self):
  self.c.review(apply=True);CustomUser.objects.filter(pk=self.c.operator.pk).update(is_superuser=False)
  with self.assertRaises(APIException):resolve_company(f['F'].owner,self.c.provider.pk)
 def test_self_reviewed_imported_link_is_not_accepted(self):
  link=self.c.review(apply=True);VerifiedCompanyLink.objects.filter(pk=link.pk).update(reviewed_by_id=link.administrator_id)
  with self.assertRaises(APIException):resolve_company(f['F'].owner,self.c.provider.pk)
 def test_future_revoked_and_expired_links_are_rejected(self):
  link=self.c.review(apply=True)
  for changes in [{'verified_at':timezone.now()+timedelta(days=1)},{'revoked_at':timezone.now()},{'valid_until':timezone.now()-timedelta(seconds=1)}]:
   old={key:getattr(link,key) for key in changes};VerifiedCompanyLink.objects.filter(pk=link.pk).update(**changes)
   with self.assertRaises(APIException):resolve_company(f['F'].owner,self.c.provider.pk)
   VerifiedCompanyLink.objects.filter(pk=link.pk).update(**old)
 def test_adapter_enforces_received_actor_and_period_from_verified_company(self):
  self.c.review(apply=True);tenant=self.c.tenant;chart=ChartOfAccounts.plain_objects.create(tenant=tenant,name='ACC005 scoped chart');a=Account.plain_objects.create(tenant=tenant,chart_of_accounts=chart,code='1105',name='Cash',type='ASSET');b=Account.plain_objects.create(tenant=tenant,chart_of_accounts=chart,code='4105',name='Income',type='REVENUE');day=timezone.localdate();period=FiscalPeriod.plain_objects.create(tenant=tenant,period_start=day,period_end=day,status='open')
  from apps.core_erp.tenancy.models import Tenant
  foreign=Tenant.objects.create(name='ACC005 foreign',tax_id=uuid.uuid4().hex,state='ACTIVE');wrong=FiscalPeriod.plain_objects.create(tenant=foreign,period_start=day,period_end=day,status='open');args={'provider':self.c.provider,'date':day,'description':'Verified adapter acceptance','periodo':period,'creado_por':f['F'].owner,'transacciones_data':[{'cuenta_id':a.pk,'debit':'10.00'},{'cuenta_id':b.pk,'credit':'10.00'}],'idempotency_key':'ACC005-adapter'}
  from apps.core_erp.accounting.exceptions import AccountingError
  with self.assertRaises(AccountingError):ContabilidadService.crear_asiento_completo(**{**args,'periodo':wrong})
  with self.assertRaises(APIException):ContabilidadService.crear_asiento_completo(**{**args,'creado_por':f['F'].other})
  self.assertFalse(JournalEntry.plain_objects.filter(tenant=tenant).exists());entry=ContabilidadService.crear_asiento_completo(**args);self.assertEqual(entry.tenant_id,tenant.pk);self.assertEqual(entry.period_id,period.pk);self.assertEqual(entry.created_by_id,f['F'].owner.pk)
 def test_review_locks_company_before_provider_and_validates_dates(self):
  with CaptureQueriesContext(connection) as queries:self.c.review()
  sql=[q['sql'].lower() for q in queries];self.assertLess(next(i for i,s in enumerate(sql) if 'from "core_erp_tenant"' in s),next(i for i,s in enumerate(sql) if 'from "turismo_tourismprovider"' in s))
  for until in [None,True,'2026-11-11',timezone.now()-timedelta(seconds=1),timezone.now()+timedelta(days=31)]:
   with self.assertRaises(APIException):self.c.review(valid_until=until)
if __name__=='__main__':unittest.main()
