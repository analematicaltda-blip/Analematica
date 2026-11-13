"""Revalidate SGA financial evidence through actual JWT/HMAC native HTTP."""
import runpy,unittest
from pathlib import Path
f=runpy.run_path(str(Path(__file__).with_name('pool08_sales_saga_http_check.py')),run_name='analytics_saga_http_setup')
class Checks(f['HTTPChecks']):
 def test_analytics_native_http_revalidates_hash_instead_of_cached_ack(self):
  from app.commercial.pool08.analytics_api import service
  from apps.core_erp.accounting.models import JournalEntry
  ref=self.reviewed();r=self.sales.command(self.body('confirm',ref,2,confirmed=True));analytics=service(self.crm,self.sales.bridge.request);report=analytics.collect(self.n.terms()['entry_date'],self.n.terms()['entry_date']);self.assertEqual(report['sources']['ledger']['state'],'AVAILABLE');self.assertEqual(report['period_economics']['net_revenue_cop'],'0.00');self.assertEqual(report['period_economics']['recognized_sales'],0)
  JournalEntry.plain_objects.filter(pk=r['journal']['id']).update(system_hash='f'*64);report=analytics.collect(self.n.terms()['entry_date'],self.n.terms()['entry_date']);self.assertEqual(report['sources']['ledger']['state'],'UNAVAILABLE');self.assertIsNone(report['period_economics'])
if __name__=='__main__':raise SystemExit(not unittest.TextTestRunner(verbosity=2).run(unittest.TestSuite([Checks('test_analytics_native_http_revalidates_hash_instead_of_cached_ack')])).wasSuccessful())
