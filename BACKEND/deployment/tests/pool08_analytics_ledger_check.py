"""Analytics calculated from actual owned journals, not patched financial totals."""
import runpy,unittest,importlib
from pathlib import Path
from types import SimpleNamespace
from django.http import QueryDict
f=runpy.run_path(str(Path(__file__).with_name('pool08_sales_native_check.py')),run_name='analytics_ledger_setup')
suite=unittest.TestSuite()
for system,path in [('erp-tur','apps.prestadores.mi_negocio.gestion_comercial.pool08'),('analematica','apps.admin_plataforma.gestion_comercial.pool08')]:
 base=f['cases'](system,path)
 class Checks(base):
  module_path=path
  def context(self):
   api=importlib.import_module(self.module_path+'.crm_api');q=QueryDict('',mutable=True);q['provider_id']=str(self.base.provider.pk);return api.CRMView().service(SimpleNamespace(user=self.base.user,query_params=q,method='GET'))
  def source(self):return importlib.import_module(self.module_path+'.analytics_sources')
  def documents(self):return self.source().documents(importlib.import_module(self.module_path+'.sales_store').Store(self.context().store))
  def test_analytics_draft_contract_and_real_revenue(self):
   ref=self.create();self.assertEqual(self.source().income(self.context(),self.documents())['rows'],[]);self.confirm(ref,'UNCONDITIONAL_RECEIVABLE');self.assertEqual(self.source().income(self.context(),self.documents())['rows'],[])
  def test_analytics_actual_posting_reversal_and_hash_tamper(self):
   from decimal import Decimal
   from apps.core_erp.accounting.models import JournalEntry
   ref=self.create();result=self.confirm(ref);r=self.source().income(self.context(),self.documents());self.assertEqual(len(r['rows']),1);self.assertGreater(Decimal(r['rows'][0]['amount']),0);self.assertEqual(r['proof'][0]['hash'],result['journal']['hash'])
   self.assertEqual(self.call(self.body('review_reversal',ref,3,reason='Anulación revisada',support_digest='e'*64,confirmed=True)).status_code,200);self.assertEqual(self.call(self.body('reverse',ref,4,confirmed=True)).status_code,200);r=self.source().income(self.context(),self.documents());self.assertEqual(len(r['rows']),2);self.assertEqual(sum(Decimal(x['amount']) for x in r['rows']),0)
   JournalEntry.plain_objects.filter(pk=result['journal']['id']).update(system_hash='f'*64)
   with self.assertRaises(Exception):self.source().income(self.context(),self.documents())
 suite.addTests(Checks(n) for n in ('test_analytics_draft_contract_and_real_revenue','test_analytics_actual_posting_reversal_and_hash_tamper'))
if __name__=='__main__':raise SystemExit(not unittest.TextTestRunner(verbosity=2).run(suite).wasSuccessful())
