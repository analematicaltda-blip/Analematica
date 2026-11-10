"""Actual many-to-many sources and shared bank/line reservations, no ledger writes."""
import runpy,unittest,uuid,copy,hashlib
from pathlib import Path
from unittest.mock import patch
fixture=runpy.run_path(str(Path(__file__).with_name('accounting_bank_reconciliation_check.py')),run_name='group_fixture')
from apps.core_erp.accounting import bank_grouped as engine
from apps.core_erp.accounting.exceptions import AccountingError
from apps.core_erp.accounting.ledger_engine import LedgerEngine
from apps.core_erp.outbox_models import OutboxEvent
from rest_framework.test import APIRequestFactory,force_authenticate
from apps.prestadores.mi_negocio.gestion_contable.contabilidad.views import PlanCuentaViewSet
class GroupedBankChecks(unittest.TestCase):
 def setUp(self):
  self.base=fixture['BankReconciliationTests']();self.base.setUp();self.case=self.base.case;self.csv='transaction_id,date,direction,amount,currency\npart-one,'+self.base.bank.day+',IN,6.00,COP\npart-two,'+self.base.bank.day+',IN,4.00,COP\n';self.args={'actor':self.case.user,'account_id':str(self.case.a.pk),'csv_text':self.csv};self.source=engine.sources(self.case.tenant.pk,**self.args);self.line=self.source['ledger_lines'][0]['ledger_line_id'];self.groups=[{'group_id':str(uuid.uuid4()),'bank_rows':[1,2],'ledger_line_ids':[self.line]}]
 def review(self,**kw):return engine.review(self.case.tenant.pk,**{**self.args,'groups':self.groups,'evidence_digest':'a'*64,'expected_revision':0,'confirmed':True,**kw})
 def confirm(self,r,**kw):return engine.confirm(self.case.tenant.pk,**{'actor':self.case.user,'statement_id':r['statement_id'],'review_id':r['review_id'],'confirmed':True,**kw})
 def release(self,a):
  r=engine.review_release(self.case.tenant.pk,actor=self.case.user,reconciliation_id=a['reconciliation_id'],reason_code='WRONG_MATCH',evidence_digest='b'*64,confirmed=True);return engine.confirm_release(self.case.tenant.pk,actor=self.case.user,review_id=r['review_id'],confirmed=True)
 def test_two_bank_installments_conserve_one_book_movement(self):
  before=self.base.counts();r=self.review();self.assertEqual(r['preview']['groups'][0]['amount'],'10.00');a=self.confirm(r);self.assertTrue(a['groups_confirmed']);self.assertEqual((a['bank_row_count'],a['ledger_line_count']),(2,1));self.assertEqual(self.base.counts(),before);self.assertFalse(a['money_transferred']);self.assertFalse(a['period_reconciled']);self.assertEqual(self.confirm(r)['reconciliation_id'],a['reconciliation_id'])
 def test_one_deposit_can_match_multiple_book_movements(self):
  LedgerEngine.post_lines(tenant_id=self.case.tenant.pk,entry_date=self.base.bank.entry.date,description='Synthetic second receipt',lines_data=[{'account':self.case.a,'debit':'5.00'},{'account':self.case.b,'credit':'5.00'}],actor=self.case.user,idempotency_key='grouped-five')
  text='transaction_id,date,direction,amount,currency\naggregate-one,'+self.base.bank.day+',IN,15.00,COP\n';source=engine.sources(self.case.tenant.pk,**{**self.args,'csv_text':text});r=self.review(csv_text=text,groups=[{'group_id':str(uuid.uuid4()),'bank_rows':[1],'ledger_line_ids':[l['ledger_line_id'] for l in source['ledger_lines']]}]);a=self.confirm(r);self.assertTrue(a['groups_confirmed']);self.assertEqual(a['ledger_line_count'],2)
 def test_unbalanced_or_uncovered_rows_are_rejected(self):
  for groups in [[{**self.groups[0],'bank_rows':[1]}],[{**self.groups[0],'ledger_line_ids':[]}],self.groups*2]:
   with self.assertRaises(AccountingError):self.review(groups=groups)
 def test_unknown_foreign_and_duplicate_ledger_lines_rejected(self):
  for ids in [[str(uuid.uuid4())],[self.line,self.line]]:
   with self.assertRaises(AccountingError):self.review(groups=[{**self.groups[0],'ledger_line_ids':ids}])
 def test_two_confirmations_required(self):
  with self.assertRaises(AccountingError):self.review(confirmed=False)
  with self.assertRaises(AccountingError):self.confirm(self.review(),confirmed=False)
 def test_source_reversal_blocks_confirmation_and_invalidates_replay(self):
  r=self.review();LedgerEngine.reverse_entry(self.base.bank.entry.pk,tenant_id=self.case.tenant.pk,actor=self.case.user)
  with self.assertRaises(AccountingError):self.confirm(r)
 def test_reversal_after_confirmation_is_not_qualified(self):
  r=self.review();self.confirm(r);LedgerEngine.reverse_entry(self.base.bank.entry.pk,tenant_id=self.case.tenant.pk,actor=self.case.user);a=self.confirm(r);self.assertFalse(a['groups_confirmed']);self.assertTrue(a['requires_review'])
 def test_legacy_active_match_blocks_grouped_match(self):
  self.base.confirm(self.base.review())
  with self.assertRaises(AccountingError):self.review()
 def test_grouped_active_match_blocks_legacy_match_and_release_reopens_it(self):
  a=self.confirm(self.review())
  with self.assertRaises(AccountingError):self.base.review()
  self.assertTrue(self.release(a)['released']);self.assertTrue(self.base.confirm(self.base.review())['reconciliation_confirmed'])
 def test_same_bank_reference_cannot_be_reused_with_another_group(self):
  self.confirm(self.review())
  with self.assertRaises(AccountingError):self.review(csv_text=self.csv.replace('part-one','another-id'))
 def test_two_pending_grouped_reviews_cannot_both_confirm(self):
  first=self.review();second=self.review(expected_revision=1)
  with self.assertRaises(AccountingError):self.confirm(first)
  self.assertTrue(self.confirm(second)['groups_confirmed'])
 def test_confirmation_failure_rolls_back_all_claims(self):
  r=self.review();original=OutboxEvent.objects.create
  def create(**kw):
   if kw.get('event_type')==engine.APPLIED:raise RuntimeError('Synthetic group proof failure')
   return original(**kw)
  with patch.object(OutboxEvent.objects,'create',side_effect=create):
   with self.assertRaises(RuntimeError):self.confirm(r)
  self.assertFalse(OutboxEvent.objects.filter(event_type=engine.legacy.CLAIM,payload__company_id=str(self.case.tenant.pk)).exists())
 def test_claim_tampering_blocks_recovery(self):
  r=self.review();a=self.confirm(r);OutboxEvent.objects.filter(event_type=engine.legacy.CLAIM,payload__reconciliation_id=a['reconciliation_id']).first().delete()
  with self.assertRaises(AccountingError):self.confirm(r)
 def test_state_is_private_and_never_restores_approvals_or_plain_refs(self):
  self.confirm(self.review());r=engine.state(self.case.tenant.pk,actor=self.case.user,account_id=str(self.case.a.pk),source_digest=hashlib.sha256(self.csv.encode()).hexdigest());self.assertFalse(r['confirmations_restored']);self.assertNotIn('part-one',str(r));self.assertTrue(r['applied']['groups_confirmed'])
 def test_cross_date_group_is_not_an_implicit_timing_adjustment(self):
  from datetime import timedelta
  yesterday=(self.base.bank.entry.date-timedelta(days=1)).isoformat();text=self.csv.replace('part-two,'+self.base.bank.day,'part-two,'+yesterday)
  with self.assertRaises(AccountingError):self.review(csv_text=text)
 def test_opposite_direction_cannot_be_netted_into_a_group(self):
  entry=LedgerEngine.post_lines(tenant_id=self.case.tenant.pk,entry_date=self.base.bank.entry.date,description='Synthetic outbound cash',lines_data=[{'account':self.case.b,'debit':'10.00'},{'account':self.case.a,'credit':'10.00'}],actor=self.case.user,idempotency_key='outbound-cash')
  source=engine.sources(self.case.tenant.pk,**self.args);line=next(r for r in source['ledger_lines'] if r['journal_id']==str(entry.pk))
  with self.assertRaises(AccountingError):self.review(groups=[{**self.groups[0],'ledger_line_ids':[line['ledger_line_id']]}])
 def test_actual_private_api_group_review(self):
  payload={k:v for k,v in {**self.args,'groups':self.groups,'evidence_digest':'a'*64,'expected_revision':0,'confirmed':True}.items() if k!='actor'};r=APIRequestFactory().post('/fixture/?provider_id='+str(self.case.provider.pk),payload,format='json');force_authenticate(r,user=self.case.user);response=PlanCuentaViewSet.as_view({'post':'review_bank_groups'})(r);self.assertEqual(response.status_code,200,response.data);self.assertIn('no-store',response['Cache-Control'])
if __name__=='__main__':unittest.main()
