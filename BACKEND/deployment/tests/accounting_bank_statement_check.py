"""Statement comparison against actual ledger, never a bank attestation or posting."""
import runpy,unittest,uuid
from pathlib import Path
fixture=runpy.run_path(str(Path(__file__).with_name('accounting_adapter_check.py')),run_name='bank_fixture')
from apps.core_erp.accounting.bank_statement import compare_statement,parse_statement
from apps.core_erp.accounting.exceptions import AccountingError
from apps.core_erp.accounting.ledger_engine import LedgerEngine
from apps.core_erp.accounting.models import JournalEntry
from apps.core_erp.outbox_models import OutboxEvent
from django.utils import timezone
from rest_framework.test import APIRequestFactory,force_authenticate
from apps.prestadores.mi_negocio.gestion_contable.contabilidad.views import PlanCuentaViewSet
class BankComparisonTests(unittest.TestCase):
 def setUp(self):
  self.case=fixture['AdapterTests']();self.case.setUp();self.case.configure_ratio(self.case.ratio_mapping());self.entry=self.case.post();self.day=timezone.localdate().isoformat()
  self.csv='transaction_id,date,direction,amount,currency\nprivate-reference-001,'+self.day+',IN,10.00,COP\n'
 def compare(self,**kwargs):return compare_statement(self.case.tenant.pk,**{'account_id':self.case.a.pk,'csv_text':self.csv,**kwargs})
 def test_unique_real_candidate_no_plaintext_reference_or_mutation(self):
  before=(JournalEntry.plain_objects.count(),OutboxEvent.objects.count());a=self.compare();b=self.compare()
  self.assertEqual(a,b);self.assertEqual(a['rows'][0]['status'],'UNIQUE_CANDIDATE');self.assertEqual(a['rows'][0]['candidates'][0]['journal_id'],str(self.entry.pk));self.assertNotIn('private-reference-001',str(a));self.assertEqual(before,(JournalEntry.plain_objects.count(),OutboxEvent.objects.count()));self.assertFalse(a['bank_verified']);self.assertFalse(a['ledger_written'])
 def test_unmatched_and_ambiguous_are_not_auto_confirmed(self):
  self.assertEqual(self.compare(csv_text=self.csv.replace('10.00','11.00'))['rows'][0]['status'],'UNMATCHED')
  self.case.post(idempotency_key='another-ten-units');r=self.compare();self.assertEqual(r['rows'][0]['status'],'AMBIGUOUS');self.assertFalse(r['reconciliation_confirmed'])
 def test_two_statement_rows_cannot_claim_one_line(self):
  r=self.compare(csv_text=self.csv+'another-private-reference,'+self.day+',IN,10.00,COP\n');self.assertEqual([row['status'] for row in r['rows']],['AMBIGUOUS_REUSED_LEDGER_LINE']*2)
 def test_duplicate_references_floats_currency_and_header_rejected(self):
  for text in [self.csv+self.csv.split('\n')[1]+'\n',self.csv.replace('10.00','NaN'),self.csv.replace('COP','USD'),self.csv.replace('10.00','10.001'),self.csv.replace('transaction_id,date','date,transaction_id')]:
   with self.assertRaises(AccountingError):self.compare(csv_text=text)
 def test_wrong_cash_role_and_foreign_account_rejected(self):
  for identifier in (self.case.b.pk,uuid.uuid4()):
   with self.assertRaises(AccountingError):self.compare(account_id=identifier)
 def test_reversed_receipt_is_not_a_valid_match(self):
  LedgerEngine.reverse_entry(self.entry.pk,'Synthetic bank receipt correction',tenant_id=self.case.tenant.pk,actor=self.case.user)
  self.assertEqual(self.compare()['rows'][0]['status'],'UNMATCHED')
 def test_real_scoped_api_and_private_response(self):
  request=APIRequestFactory().post('/fixture/?provider_id='+str(self.case.provider.pk),{'account_id':str(self.case.a.pk),'csv_text':self.csv},format='json');force_authenticate(request,user=self.case.user)
  result=PlanCuentaViewSet.as_view({'post':'bank_statement_comparison'})(request);self.assertEqual(result.status_code,200,result.data);self.assertIn('no-store',result['Cache-Control']);self.assertFalse(result.data['bank_connected'])
if __name__=='__main__':unittest.main()
