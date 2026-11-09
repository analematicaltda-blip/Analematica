"""Explicit partial/ambiguous statement decisions, append-only claims and release."""
import runpy,unittest,uuid,copy,hashlib
from pathlib import Path
from unittest.mock import patch
fixture=runpy.run_path(str(Path(__file__).with_name('accounting_bank_reconciliation_check.py')),run_name='bank_resolution_fixture')
from apps.core_erp.accounting import bank_reconciliation as engine
from apps.core_erp.accounting.bank_statement import compare_statement
from apps.core_erp.accounting.exceptions import AccountingError
from apps.core_erp.accounting.ledger_engine import LedgerEngine
from apps.core_erp.outbox_models import OutboxEvent
from rest_framework.test import APIRequestFactory,force_authenticate
from apps.prestadores.mi_negocio.gestion_contable.contabilidad.views import PlanCuentaViewSet
class BankResolutionChecks(unittest.TestCase):
 def setUp(self):
  self.base=fixture['BankReconciliationTests']();self.base.setUp();self.case=self.base.case;self.csv=self.base.bank.csv+'private-fee-002,'+self.base.bank.day+',OUT,2.00,COP\n'
  c=compare_statement(self.case.tenant.pk,account_id=str(self.case.a.pk),csv_text=self.csv);self.line=c['rows'][0]['candidates'][0]['ledger_line_id'];self.resolutions=[{'row':1,'ledger_line_id':self.line,'reason_code':None},{'row':2,'ledger_line_id':None,'reason_code':'BANK_FEE_UNPOSTED'}]
 def review(self,**kw):return self.base.review(**{'csv_text':self.csv,'resolutions':self.resolutions,**kw})
 def test_partial_result_is_not_full_reconciliation_and_ledger_unchanged(self):
  before=self.base.counts();r=self.review();p=r['preview'];self.assertEqual(p['coverage'],{'total_rows':2,'matched_rows':1,'unresolved_rows':1,'matched_in':'10.00','matched_out':'0.00','unresolved_in':'0.00','unresolved_out':'2.00'});a=self.base.confirm(r);self.assertTrue(a['associations_confirmed']);self.assertFalse(a['fully_reconciled']);self.assertFalse(a['reconciliation_confirmed']);self.assertFalse(a['money_transferred']);self.assertEqual(self.base.counts(),before)
 def test_replay_and_recovery_preserve_differences_without_approval(self):
  r=self.review();a=self.base.confirm(r);b=self.base.confirm(r);self.assertEqual(a['reconciliation_id'],b['reconciliation_id']);self.assertTrue(b['replayed']);state=engine.reconciliation_state(self.case.tenant.pk,actor=self.case.user,account_id=self.case.a.pk,source_digest=hashlib.sha256(self.csv.encode()).hexdigest());self.assertFalse(state['confirmations_restored']);self.assertEqual(state['preview']['differences'][0]['reason_code'],'BANK_FEE_UNPOSTED');self.assertNotIn('private-fee-002',str(state))
 def test_ambiguous_row_requires_explicit_actual_candidate(self):
  self.case.post(idempotency_key='ambiguous-reviewed-bank');c=compare_statement(self.case.tenant.pk,account_id=self.case.a.pk,csv_text=self.csv);self.assertEqual(c['rows'][0]['status'],'AMBIGUOUS');self.resolutions[0]['ledger_line_id']=c['rows'][0]['candidates'][1]['ledger_line_id'];a=self.base.confirm(self.review());self.assertTrue(a['associations_confirmed']);self.assertEqual(a['coverage']['unresolved_rows'],1)
 def test_resolution_must_cover_every_row_once(self):
  for rows in [self.resolutions[:1],self.resolutions*2,[{**self.resolutions[0],'row':True},self.resolutions[1]],[{**self.resolutions[0],'row':3},self.resolutions[1]]]:
   with self.assertRaises(AccountingError):self.review(resolutions=rows)
 def test_foreign_or_wrong_amount_candidate_and_unknown_reason_rejected(self):
  for change in [{'ledger_line_id':str(uuid.uuid4())},{'reason_code':'IGNORE_AND_PAY'}]:
   rows=copy.deepcopy(self.resolutions);rows[0].update(change)
   with self.assertRaises(AccountingError):self.review(resolutions=rows)
 def test_unmatched_row_cannot_be_assigned_a_different_amount(self):
  rows=copy.deepcopy(self.resolutions);rows[1].update(ledger_line_id=self.line,reason_code=None)
  with self.assertRaises(AccountingError):self.review(resolutions=rows)
 def test_all_differences_are_not_confirmable_matches(self):
  rows=[{'row':r['row'],'ledger_line_id':None,'reason_code':'UNIDENTIFIED'} for r in self.resolutions]
  with self.assertRaises(AccountingError):self.review(resolutions=rows)
 def test_same_ledger_line_cannot_be_selected_twice(self):
  text=self.base.bank.csv+'another-reference,'+self.base.bank.day+',IN,10.00,COP\n';rows=[{'row':i,'ledger_line_id':self.line,'reason_code':None} for i in (1,2)]
  with self.assertRaises(AccountingError):self.review(csv_text=text,resolutions=rows)
 def test_difference_reference_is_reserved_until_explicit_release(self):
  a=self.base.confirm(self.review());LedgerEngine.post_lines(tenant_id=self.case.tenant.pk,entry_date=self.base.bank.entry.date,description='Synthetic fee already posted separately',lines_data=[{'account':self.case.b,'debit':'2.00'},{'account':self.case.a,'credit':'2.00'}],actor=self.case.user,idempotency_key='synthetic-fee')
  text='transaction_id,date,direction,amount,currency\nprivate-fee-002,'+self.base.bank.day+',OUT,2.00,COP\n'
  with self.assertRaises(AccountingError):self.base.review(csv_text=text)
  self.base.release(self.base.release_review(a));self.assertTrue(self.base.confirm(self.base.review(csv_text=text))['fully_reconciled'])
 def test_competing_drafts_cannot_claim_same_difference(self):
  one=self.review();other=self.review(expected_revision=1);self.base.confirm(other)
  with self.assertRaises(AccountingError):self.base.confirm(one)
 def test_missing_difference_claim_invalidates_recovery(self):
  r=self.review();self.base.confirm(r);OutboxEvent.objects.filter(event_type=engine.CLAIM,payload__company_id=str(self.case.tenant.pk),payload__ledger_line_id=None).delete()
  with self.assertRaises(AccountingError):self.base.confirm(r)
 def test_partial_proof_failure_rolls_back_every_claim(self):
  r=self.review();original=OutboxEvent.objects.create
  def create(**kw):
   if kw.get('event_type') in (engine.APPLIED,engine.APPLIED_V2):raise RuntimeError('Synthetic proof failure')
   return original(**kw)
  with patch.object(OutboxEvent.objects,'create',side_effect=create):
   with self.assertRaises(RuntimeError):self.base.confirm(r)
  self.assertFalse(OutboxEvent.objects.filter(event_type=engine.CLAIM,payload__company_id=str(self.case.tenant.pk)).exists())
 def test_complete_explicit_selection_is_reported_complete(self):
  r=self.base.review(resolutions=[self.resolutions[0]]);a=self.base.confirm(r);self.assertTrue(a['fully_reconciled']);self.assertTrue(a['reconciliation_confirmed']);self.assertEqual(a['coverage']['unresolved_rows'],0)
 def test_reversal_does_not_leave_partial_associations_qualified(self):
  r=self.review();self.base.confirm(r);LedgerEngine.reverse_entry(self.base.bank.entry.pk,tenant_id=self.case.tenant.pk,actor=self.case.user);a=self.base.confirm(r);self.assertFalse(a['associations_confirmed']);self.assertTrue(a['requires_review']);self.assertFalse(a['fully_reconciled'])
 def test_partial_flow_still_requires_two_confirmations(self):
  with self.assertRaises(AccountingError):self.review(confirmed=False)
  with self.assertRaises(AccountingError):self.base.confirm(self.review(),confirmed=False)
 def test_explicit_partial_events_require_v2_reader_with_legacy_claim_guards(self):
  r=self.review();a=self.base.confirm(r);proof=OutboxEvent.objects.get(pk=a['reconciliation_id']);review=OutboxEvent.objects.get(pk=r['review_id']);self.assertEqual((proof.event_type,proof.version),(engine.APPLIED_V2,2));self.assertEqual((review.event_type,review.version),(engine.REVIEW_V2,2));self.assertFalse(OutboxEvent.objects.filter(pk=proof.pk,event_type=engine.APPLIED).exists());self.assertEqual(OutboxEvent.objects.filter(event_type=engine.CLAIM,payload__reconciliation_id=str(proof.pk)).count(),2)
 def test_current_private_http_boundary_accepts_explicit_resolutions(self):
  body={**self.base.args,'csv_text':self.csv,'resolutions':self.resolutions};body.pop('actor');r=APIRequestFactory().post('/fixture/?provider_id='+str(self.case.provider.pk),body,format='json');force_authenticate(r,user=self.case.user);response=PlanCuentaViewSet.as_view({'post':'review_bank_reconciliation'})(r);self.assertEqual(response.status_code,200,response.data);self.assertIn('no-store',response['Cache-Control']);self.assertEqual(response.data['preview']['coverage']['unresolved_rows'],1)
if __name__=='__main__':unittest.main()
