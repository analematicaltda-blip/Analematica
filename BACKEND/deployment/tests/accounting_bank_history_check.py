"""Bounded keyset cash history, exact legacy digest and counterpart integrity."""
import copy,hashlib,runpy,unittest,uuid
from pathlib import Path
from datetime import timedelta
from decimal import Decimal
from unittest.mock import patch
fixture=runpy.run_path(str(Path(__file__).with_name('accounting_bank_period_check.py')),run_name='history_fixture')
from django.db import connection
from django.test.utils import CaptureQueriesContext
from apps.core_erp.accounting import bank_period as engine
from apps.core_erp.accounting.models import JournalEntry,LedgerEntry
from apps.core_erp.accounting.integrity import journal_hash,canonical
from apps.core_erp.accounting.exceptions import AccountingError
class HistoryChecks(unittest.TestCase):
 def setUp(self):
  self.base=fixture['BankPeriodChecks']();self.base.setUp();self.case=self.base.case;self.company=self.case.tenant;self.day=self.base.base.bank.entry.date;self.prior=self.day-timedelta(days=1);self.case.period.period_start=self.prior;self.case.period.save();self.rows=self.base.base.review()['preview']['rows']
 def seed(self,count,*,day=None,amount='1.00'):
  # Read-path fixture only: bulk-insert explicitly synthetic, balanced v2 history.
  # Does not credit the posting engine, migrations or proof/origin acceptance.
  template=self.base.base.bank.entry;journals=[];lines=[]
  for i in range(count):
   j=JournalEntry(id=uuid.uuid4(),tenant=self.company,period=self.case.period,date=day or self.prior,reference='SYNTHETIC-HISTORY',description='Synthetic history read fixture',currency='COP',base_currency='COP',exchange_rate=Decimal(1),is_posted=True,hash_version='v2',posted_at=template.posted_at,created_by=self.case.user,previous_hash=None)
   pair=[LedgerEntry(id=uuid.uuid4(),tenant=self.company,journal_entry=j,account=a,debit_amount=Decimal(amount) if debit else Decimal(0),credit_amount=Decimal(0) if debit else Decimal(amount),amount_transaction=Decimal(amount),amount_base=Decimal(amount),currency='COP') for a,debit in [(self.case.a,True),(self.case.b,False)]]
   j.system_hash=journal_hash(j,pair,None);journals.append(j);lines+=pair
  JournalEntry.plain_objects.bulk_create(journals,batch_size=100);LedgerEntry.plain_objects.bulk_create(lines,batch_size=100);return journals,lines
 def assess(self,opening='0.00'):
  return engine.assess(self.company,self.case.a.pk,{**self.base.period,'opening':opening,'closing':engine.fmt(engine.signed(opening)+1000)},self.rows,[])
 def test_over_two_thousand_historical_lines_no_longer_blocks_period(self):
  self.seed(2001);a=self.assess('2001.00');self.assertEqual(a['ledger_history_rows'],2002);self.assertEqual(a['ledger_period_rows'],1);self.assertTrue(a['eligible_for_period_reconciliation']);self.assertFalse(a['source_independently_verified'])
 def test_review_confirm_recover_with_large_history(self):
  self.seed(2001);terms={**self.base.period,'opening':'2001.00','closing':'2011.00'}
  r=self.base.base.review(period=terms,expected_revision=1);a=self.base.base.confirm(r);self.assertTrue(a['period_reconciled']);self.assertEqual(a['period_assessment']['ledger_history_rows'],2002);self.assertTrue(self.base.base.state()['applied']['period_reconciled'])
 def test_exact_twenty_thousand_line_boundary_and_next_line_rejection(self):
  import time,json
  self.seed(19999);started=time.perf_counter();a=self.assess('19999.00');elapsed=time.perf_counter()-started
  self.assertEqual(a['ledger_history_rows'],20000);self.assertTrue(a['eligible_for_period_reconciliation'])
  print(json.dumps({'measurement':'synthetic_sqlite_history','cash_lines':20000,'elapsed_seconds':round(elapsed,3),'production_latency_qualified':False}))
  self.seed(1)
  with self.assertRaises(AccountingError):self.assess('20000.00')
 def test_digest_exactly_matches_original_v1_order_and_arithmetic(self):
  self.seed(135);a=self.assess('135.00');digest=hashlib.sha256()
  for l in LedgerEntry.plain_objects.filter(tenant=self.company,account=self.case.a,journal_entry__is_posted=True).select_related('journal_entry').order_by('pk'):
   j=l.journal_entry;digest.update((canonical({'line_id':str(l.pk),'journal_id':str(j.pk),'journal_hash':j.system_hash,'date':j.date.isoformat(),'debit':engine._money(format(l.debit_amount,'.2f')),'credit':engine._money(format(l.credit_amount,'.2f'))})+'\n').encode())
  self.assertEqual(a['ledger_digest'],digest.hexdigest())
 def test_counterpart_tampering_outside_cash_is_rejected(self):
  js,ls=self.seed(130);LedgerEntry.plain_objects.filter(pk=ls[-1].pk).update(description='Tampered noncash side')
  with self.assertRaises(AccountingError):self.assess('130.00')
 def test_tampered_oldest_cash_page_is_rejected(self):
  self.seed(130);line=LedgerEntry.plain_objects.filter(tenant=self.company,account=self.case.a).order_by('pk').first();LedgerEntry.plain_objects.filter(pk=line.pk).update(amount_base='9.00')
  with self.assertRaises(AccountingError):self.assess('130.00')
 def test_page_size_does_not_change_digest_or_totals(self):
  self.seed(33);a=self.assess('33.00')
  with patch.object(engine,'HISTORY_BATCH',7):b=self.assess('33.00')
  self.assertEqual(a,b)
 def test_history_limit_is_fail_closed_not_silently_truncated(self):
  self.seed(9)
  with patch.object(engine,'HISTORY_LIMIT',5),self.assertRaises(AccountingError):self.assess('9.00')
 def test_period_movement_cap_still_applies(self):
  self.seed(200,day=self.day)
  with self.assertRaises(AccountingError):self.assess()
 def test_complete_journal_page_limit_is_fail_closed(self):
  self.seed(2)
  with patch.object(engine,'PAGE_JOURNAL_LINE_LIMIT',2),self.assertRaises(AccountingError):self.assess('2.00')
 def test_no_n_plus_one_journal_queries(self):
  self.seed(128)
  # Count the new stream alone, avoiding legacy candidate/review queries.
  from django.db import transaction
  with transaction.atomic(),CaptureQueriesContext(connection) as queries:
   rows=list(engine.verified_history(self.company,self.case.a,self.day))
  self.assertEqual(len(rows),129);self.assertLessEqual(len(queries),12)
 def test_source_account_metadata_change_is_rejected_before_history_read(self):
  self.seed(2);from apps.core_erp.accounting.models import Account
  original=Account.plain_objects.get(pk=self.case.b.pk).code
  with self.assertRaises(AccountingError):Account.plain_objects.filter(pk=self.case.b.pk).update(code='CHANGED-HISTORICAL-ACCOUNT')
  self.assertEqual(Account.plain_objects.get(pk=self.case.b.pk).code,original);self.assertTrue(self.assess('2.00')['eligible_for_period_reconciliation'])
 def test_foreign_chart_on_noncash_counterpart_is_rejected_even_with_valid_hash(self):
  from apps.core_erp.accounting.models import ChartOfAccounts,Account
  from apps.core_erp.tenancy.models import Tenant
  chart=ChartOfAccounts.plain_objects.create(tenant=self.company,name='Synthetic counterpart chart')
  other=Account.plain_objects.create(tenant=self.company,chart_of_accounts=chart,code='499999',name='Synthetic counterpart',type='REVENUE')
  self.case.b=other;self.seed(1);foreign=Tenant.objects.create(name='Synthetic foreign',tax_id='foreign-'+uuid.uuid4().hex,state='ACTIVE');ChartOfAccounts.plain_objects.filter(pk=chart.pk).update(tenant=foreign)
  with self.assertRaises(AccountingError):self.assess('1.00')
 def test_missing_noncash_counterpart_is_rejected(self):
  js,ls=self.seed(1);LedgerEntry.plain_objects.filter(pk=ls[-1].pk)._raw_delete('default')
  with self.assertRaises(AccountingError):self.assess('1.00')
if __name__=='__main__':unittest.main()
