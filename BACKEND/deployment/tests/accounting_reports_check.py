"""Profitability aggregate excludes balance-only groups after safety checks."""
import runpy,unittest,uuid
from pathlib import Path
from django.db import connection
from django.test.utils import CaptureQueriesContext
from django.utils import timezone
fixture=runpy.run_path(str(Path(__file__).with_name('accounting_posting_check.py')),run_name='report_fixture')
from apps.core_erp.accounting.models import Account,JournalEntry,LedgerEntry
from apps.core_erp.accounting.ledger_engine import LedgerEngine
from apps.core_erp.accounting.reports_engine import ReportsEngine
from apps.core_erp.accounting.journal_service import JournalService
from apps.core_erp.accounting.exceptions import AccountingError
class ReportTests(unittest.TestCase):
 def setUp(self):
  fixture['fixture']['AccountingFoundation'].setUp(self);self.actor=fixture['fixture']['fixture']['F'].owner;self.day=timezone.localdate()
 def asset(self,index):return Account.plain_objects.create(tenant=self.tenant,chart_of_accounts=self.chart,code='120'+str(index),name='Synthetic asset',type='ASSET')
 def post(self,left,right,amount='10.00'):
  return LedgerEngine.post_lines(tenant_id=self.tenant.pk,entry_date=self.day,description='Report fixture',lines_data=[{'account':left,'debit':amount},{'account':right,'credit':amount}],actor=self.actor,idempotency_key=uuid.uuid4().hex)
 def test_profitability_returns_same_revenue_without_balance_account_groups(self):
  self.post(self.a,self.b)
  for i in range(5):self.post(self.asset(i),self.a,'1.00')
  full=ReportsEngine._totals(self.tenant.pk,self.day,database='default');self.assertEqual(len(full),7)
  with CaptureQueriesContext(connection) as capture:report=ReportsEngine.get_profitability(self.tenant.pk,self.day,self.day)
  self.assertEqual(report['revenue'],'10.00');self.assertEqual(report['net_profit'],'10.00');self.assertEqual(len(report['sources']),1)
  aggregates=[q['sql'] for q in capture.captured_queries if 'SUM(' in q['sql'].upper() and 'GROUP BY' in q['sql'].upper()]
  self.assertEqual(len(aggregates),1);self.assertIn('"type" IN',aggregates[0]);self.assertIn('REVENUE',aggregates[0])
  filtered=ReportsEngine._totals(self.tenant.pk,self.day,database='default',account_types=('REVENUE',))
  self.assertEqual(len(filtered),1);self.assertEqual(filtered[0],next(row for row in full if row['account__type']=='REVENUE'))
 def test_invalid_foreign_asset_valuation_not_hidden_by_profitability_filter(self):
  other=self.asset(9)
  entry=JournalService.create_entry(str(self.tenant.pk),self.day,'Legacy fixture',[{'account':self.a,'debit':'10.00'},{'account':other,'credit':'10.00'}],created_by=self.actor,currency='USD',base_currency='COP')
  JournalEntry.plain_objects.filter(pk=entry.pk).update(is_posted=True)
  LedgerEntry.plain_objects.filter(journal_entry=entry).update(amount_base=0)
  with self.assertRaises(AccountingError):ReportsEngine.get_profitability(self.tenant.pk,self.day,self.day)
 def test_opening_balance_on_excluded_asset_still_blocks_report(self):
  Account.plain_objects.filter(pk=self.a.pk).update(initial_balance='1.00')
  with self.assertRaises(AccountingError):ReportsEngine.get_profitability(self.tenant.pk,self.day,self.day)
 def test_unsupported_projection_rejected(self):
  for types in ['REVENUE',[],('REVENUE; DROP TABLE users',),([1],),True]:
   with self.assertRaises(AccountingError):ReportsEngine._totals(self.tenant.pk,self.day,account_types=types)
if __name__=='__main__':unittest.main()
