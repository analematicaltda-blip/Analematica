"""Paged real catalogs/source history and coherent primary report contracts."""
import runpy,unittest,uuid
from pathlib import Path
from unittest.mock import patch
from datetime import date
fixture=runpy.run_path(str(Path(__file__).with_name('accounting_reservation_recognition_check.py')),run_name='catalog_fixture')
from apps.core_erp.accounting.catalog import recognition_catalog
from apps.core_erp.accounting.models import Account
from apps.core_erp.accounting.reports_engine import ReportsEngine
from apps.core_erp.accounting.exceptions import AccountingError
from apps.core_erp.tenancy.models import Tenant
from apps.domain_business.operativa.models import Reservation
from apps.domain_business.comercial.services.reservation_fiscal import list_reservation_sources
class RemediationCatalogTests(unittest.TestCase):
 def setUp(self):
  self.case=fixture['RecognitionTests']();self.case.setUp();self.company=self.case.case.tenant
 def test_page_over_500_accounts_no_duplicate_or_foreign_rows(self):
  Account.plain_objects.bulk_create([Account(tenant=self.company,chart_of_accounts=self.case.chart,code='qa-'+str(i),name='Paged account',type='ASSET') for i in range(530)])
  seen=[];after=None
  while True:
   data=recognition_catalog(self.company,paged='1',after=after);self.assertLessEqual(len(data['accounts']),100);seen.extend(str(r['id']) for r in data['accounts']);after=data['next_after']
   if after is None:break
  expected={str(pk) for pk in Account.plain_objects.filter(tenant=self.company).values_list('pk',flat=True)}
  self.assertEqual(set(seen),expected);self.assertEqual(len(seen),len(expected))
  with self.assertRaises(AccountingError):recognition_catalog(self.company)
 def test_search_cursor_and_company_scope(self):
  data=recognition_catalog(self.company,paged='1',search='130505');self.assertEqual([r['id'] for r in data['accounts']],[self.case.asset.pk])
  other=Tenant.objects.create(name='Other catalog',tax_id=uuid.uuid4().hex,state='ACTIVE')
  self.assertEqual(recognition_catalog(other,paged='1')['accounts'],[])
  with self.assertRaises((ValueError,AccountingError)):recognition_catalog(self.company,paged='1',after='invalid')
 def test_over_20_sources_page_without_duplicate(self):
  original=Reservation.plain_objects.get(pk=self.case.case.reservation.pk)
  Reservation.plain_objects.bulk_create([Reservation(tenant=self.company,customer_id=uuid.uuid4(),content_type_id=original.content_type_id,object_id=uuid.uuid4(),start_date=original.start_date,end_date=original.end_date,status='CONFIRMED',total_price='1.00') for _ in range(45)])
  seen=[];after=None
  while True:
   data=list_reservation_sources(actor=self.case.case.actor,provider_id=self.case.case.provider.pk,after=after);seen.extend(r['reservation_id'] for r in data['sources']);after=data['next_after']
   if after is None:break
  self.assertEqual(len(seen),46);self.assertEqual(len(set(seen)),46)
 def test_primary_snapshot_ignores_replica_selection_and_has_stable_watermark(self):
  self.case.post(self.case.review())
  with patch.object(ReportsEngine,'get_read_db',side_effect=AssertionError('Replica not allowed for authoritative report')):
   report=ReportsEngine.get_trial_balance(self.company.pk,self.case.day)
  self.assertEqual(report['snapshot']['database'],'primary');self.assertTrue(report['snapshot']['ledger_tail_hash']);self.assertFalse(report['snapshot']['historical_publication_snapshot'])
  self.assertEqual(report['snapshot'],ReportsEngine.get_trial_balance(self.company.pk,self.case.day)['snapshot'])
 def test_inactive_company_and_bad_dates_cannot_report(self):
  with self.assertRaises(AccountingError):ReportsEngine.get_trial_balance(self.company.pk,'2026-11-08')
  Tenant.objects.filter(pk=self.company.pk).update(is_active=False)
  for report in (ReportsEngine.get_trial_balance,ReportsEngine.get_balance_sheet):
   with self.assertRaises(AccountingError):report(self.company.pk,self.case.day)
if __name__=='__main__':unittest.main()
