"""Multi-bank neutral import states; no authenticated provider or payment claims."""
import runpy,unittest
from pathlib import Path
fixture=runpy.run_path(str(Path(__file__).with_name('accounting_bank_statement_check.py')),run_name='acc015_fixture')
from apps.core_erp.accounting.bank_statement import parse_statement
from apps.core_erp.accounting import bank_reconciliation as bank,bank_groups
from apps.core_erp.accounting.exceptions import AccountingError
from apps.core_erp.accounting.models import JournalEntry
from apps.core_erp.outbox_models import OutboxEvent
class BankStateChecks(unittest.TestCase):
 def setUp(self):self.base=fixture['BankComparisonTests']();self.base.setUp();self.addCleanup(self.base.doCleanups)
 def csv(self,state='BOOKED',code='CO_BANK_A'):
  return 'transaction_id,date,direction,amount,currency,bank_id,status\nprivate-reference-001,'+self.base.day+',IN,10.00,COP,'+code+','+state+'\n'
 def test_booked_can_propose_candidate_without_bank_authentication(self):
  r=self.base.compare(csv_text=self.csv());self.assertEqual(r['rows'][0]['status'],'UNIQUE_CANDIDATE');self.assertEqual(r['rows'][0]['declared_bank_state'],'BOOKED');self.assertEqual(r['rows'][0]['bank_id'],'CO_BANK_A');self.assertFalse(r['bank_connected']);self.assertFalse(r['bank_verified']);self.assertFalse(r['money_transferred'])
 def test_pending_and_reversed_have_no_candidates_or_effect(self):
  before=(JournalEntry.plain_objects.count(),OutboxEvent.objects.count())
  for state in ['PENDING','REVERSED']:
   r=self.base.compare(csv_text=self.csv(state));row=r['rows'][0];self.assertEqual(row['status'],'EXTERNAL_'+state);self.assertEqual(row['candidates'],[]);self.assertEqual(r['summary']['EXTERNAL_'+state],1)
  self.assertEqual(before,(JournalEntry.plain_objects.count(),OutboxEvent.objects.count()))
 def test_manual_resolutions_cannot_bypass_external_state(self):
  for state in ['PENDING','REVERSED']:
   with self.assertRaisesRegex(AccountingError,'Pending or externally reversed'):
    bank.review_reconciliation(self.base.case.tenant.pk,actor=self.base.case.user,account_id=str(self.base.case.a.pk),csv_text=self.csv(state),evidence_digest='b'*64,expected_revision=0,confirmed=True,resolutions=[])
 def test_grouping_cannot_bypass_external_state(self):
  for state in ['PENDING','REVERSED']:
   with self.assertRaisesRegex(AccountingError,'Pending or externally reversed'):
    bank_groups.review_groups(self.base.case.tenant.pk,actor=self.base.case.user,account_id=str(self.base.case.a.pk),csv_text=self.csv(state),groups=[{'rows':[1],'ledger_line_ids':[]}],differences=[],evidence_digest='b'*64,confirmed=True)
 def test_cross_batch_grouping_cannot_bypass_external_state(self):
  from apps.core_erp.accounting import bank_grouped
  for state in ['PENDING','REVERSED']:
   with self.assertRaisesRegex(AccountingError,'Pending or externally reversed'):
    bank_grouped.review(self.base.case.tenant.pk,actor=self.base.case.user,account_id=str(self.base.case.a.pk),csv_text=self.csv(state),groups=[],evidence_digest='b'*64,expected_revision=0,confirmed=True)
 def test_booked_still_needs_confirmations(self):
  with self.assertRaises(AccountingError):bank.review_reconciliation(self.base.case.tenant.pk,actor=self.base.case.user,account_id=str(self.base.case.a.pk),csv_text=self.csv(),evidence_digest='b'*64,expected_revision=0,confirmed=False)
  r=bank.review_reconciliation(self.base.case.tenant.pk,actor=self.base.case.user,account_id=str(self.base.case.a.pk),csv_text=self.csv(),evidence_digest='b'*64,expected_revision=0,confirmed=True);self.assertFalse(r['ledger_written'])
 def test_bank_reference_namespace_separates_same_external_identifier(self):
  a=self.base.compare(csv_text=self.csv(code='CO_BANK_A'));b=self.base.compare(csv_text=self.csv(code='CO_BANK_B'));self.assertNotEqual(a['rows'][0]['transaction_ref_digest'],b['rows'][0]['transaction_ref_digest']);self.assertNotIn('private-reference-001',str(a))
 def test_mixed_banks_unknown_state_or_unsafe_code_rejected(self):
  for text in [self.csv()+self.csv(code='CO_BANK_B').split('\n')[1].replace('001','002')+'\n',self.csv('AUTHORIZED'),self.csv(code='https://untrusted.example')]:
   with self.assertRaises(AccountingError):parse_statement(text)
 def test_more_than_fifty_cash_accounts_are_retained_and_scoped(self):
  from apps.core_erp.accounting.models import Account
  case=self.base.case;rows=[Account.plain_objects.create(tenant=case.tenant,chart_of_accounts=case.chart,code='BANK'+str(i),name='Synthetic bank account '+str(i),type='ASSET') for i in range(120)]
  mapping=case.call('liquidity_classification').data['mapping'];mapping['cash_equivalents']=[str(row.pk) for row in rows]
  configured=case.configure_ratio(mapping,expected_revision=1);self.assertEqual(configured.status_code,201,configured.data)
  response=case.call('liquidity_classification');self.assertEqual(response.status_code,200);self.assertEqual(len(response.data['mapping']['cash_equivalents']),120)
  r=self.base.compare(account_id=str(rows[-1].pk),csv_text=self.csv());self.assertEqual(r['account_id'],str(rows[-1].pk));self.assertEqual(r['rows'][0]['status'],'UNMATCHED');self.assertEqual(case.call('liquidity_classification',user=case.other).status_code,403)
 def test_legacy_reference_and_shape_preserved(self):
  r=self.base.compare();self.assertNotIn('declared_bank_state',r['rows'][0]);self.assertEqual(r['rows'][0]['status'],'UNIQUE_CANDIDATE')
if __name__=='__main__':unittest.main(verbosity=2)
