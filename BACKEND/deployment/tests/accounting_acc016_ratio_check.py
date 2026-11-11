"""Exact ledger liquidity under hostile decimal contexts; no hotel/RAT changes."""
import runpy,unittest,uuid
from pathlib import Path
from decimal import localcontext,ROUND_DOWN,Inexact,Rounded
from datetime import timedelta
fixture=runpy.run_path(str(Path(__file__).with_name('accounting_adapter_check.py')),run_name='acc016_fixture')
from apps.core_erp.accounting import ratios
from apps.core_erp.accounting.models import JournalEntry,Account
from apps.core_erp.accounting.ledger_engine import LedgerEngine
from django.utils import timezone
class RatioChecks(unittest.TestCase):
 def setUp(self):
  self.base=fixture['AdapterTests']();self.base.setUp();self.addCleanup(self.base.doCleanups);self.mapping=self.base.ratio_mapping();self.base.configure_ratio(self.mapping);self.day=timezone.localdate()
 def seed(self):
  return LedgerEngine.post_lines(tenant_id=self.base.tenant.pk,entry_date=self.day,description='Synthetic liquidity',lines_data=[{'account':self.base.a,'debit':'123456.78'},{'account':Account.plain_objects.get(pk=self.mapping['current_liabilities'][0]),'credit':'98765.43'},{'account':self.base.b,'credit':'24691.35'}],actor=self.base.user,idempotency_key=uuid.uuid4().hex)
 def ratio(self,**extra):return ratios.quick_ratio(self.base.tenant.pk,self.day,**extra)
 def test_ratio_is_independent_of_precision_rounding_and_traps(self):
  self.seed();expected=self.ratio()
  with localcontext() as ctx:
   ctx.prec=2;ctx.rounding=ROUND_DOWN;ctx.traps[Inexact]=True;ctx.traps[Rounded]=True
   self.assertEqual(self.ratio(),expected)
  self.assertEqual(expected['totals']['cash_equivalents'],'123456.78');self.assertEqual(expected['value'],'1.2500')
 def test_currency_cutoff_unit_and_primary_snapshot_present(self):
  journal=self.seed();r=self.ratio();self.assertEqual(r['currency'],'COP');self.assertEqual(r['cutoff_date'],self.day.isoformat());self.assertEqual(r['unit'],'times');self.assertEqual(r['snapshot']['ledger_tail_id'],str(journal.pk));self.assertFalse(r['snapshot']['historical_publication_snapshot'])
 def test_zero_denominator_is_not_zero_ratio(self):
  r=self.ratio();self.assertIsNone(r['value']);self.assertEqual(r['unavailable_reason'],'NON_POSITIVE_CURRENT_LIABILITIES')
 def test_economic_cutoff_excludes_later_posting(self):
  self.seed();r=ratios.quick_ratio(self.base.tenant.pk,self.day-timedelta(days=1));self.assertIsNone(r['value']);self.assertEqual(r['totals']['cash_equivalents'],'0.00')
 def test_ratio_is_read_only_and_reconciles_sources(self):
  self.seed();before=JournalEntry.plain_objects.count();r=self.ratio();self.assertEqual(r['sources']['cash_equivalents'][0]['balance'],r['totals']['cash_equivalents']);self.assertEqual(JournalEntry.plain_objects.count(),before);self.assertTrue(r['read_only']);self.assertFalse(r['ledger_written']);self.assertFalse(r['money_transferred'])
if __name__=='__main__':unittest.main(verbosity=2)
