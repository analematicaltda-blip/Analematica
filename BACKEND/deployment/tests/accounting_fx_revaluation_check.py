"""Ledger-backed monetary true-up and contra; synthetic reviewed FX only."""
import copy,runpy,unittest,uuid
from pathlib import Path
from unittest.mock import patch
from decimal import Decimal
fixture=runpy.run_path(str(Path(__file__).with_name('accounting_reviewed_fx_check.py')),run_name='revaluation_fixture')
from apps.core_erp.accounting import fx_revaluation as engine,reviewed_fx
from apps.core_erp.accounting.models import Account,JournalEntry,LedgerEntry,AccountingAuditLog
from apps.core_erp.accounting.ledger_engine import LedgerEngine
from apps.core_erp.accounting.journal_service import JournalService
from apps.core_erp.accounting.exceptions import AccountingError
from apps.core_erp.outbox_models import OutboxEvent
class RevaluationChecks(unittest.TestCase):
 def setUp(self):
  self.base=fixture['ReviewedFxTests']();self.base.setUp();self.case=self.base.case;self.company=self.base.company;self.actor=self.base.actor
  terms={**self.base.terms,'rate':'4000.000000'};r=self.base.review(terms=terms);self.base.confirm(r)
  self.loss=Account.plain_objects.create(tenant=self.company,chart_of_accounts=self.case.chart,code='5305',name='Synthetic declared FX loss',type='EXPENSE')
  self.args={'actor':self.actor,'request_id':str(uuid.uuid4()),'account_id':str(self.case.a.pk),'currency':'USD','as_of':self.base.day,'terms':{**terms,'rate':'4200.000000','source_version':'2'},'gain_account_id':str(self.case.b.pk),'loss_account_id':str(self.loss.pk),'monetary_classification':'MONETARY_DECLARED','confirmed':True}
 def review(self,**kw):return engine.review(self.company.pk,**{**self.args,**kw})
 def confirm(self,r,**kw):return engine.confirm(self.company.pk,actor=self.actor,review_id=r['review_id'],confirmed=kw.get('confirmed',True))
 def test_gain_revalues_real_balance_and_preserves_original(self):
  original=JournalEntry.plain_objects.get(pk=self.base.entry.pk);oldhash=original.system_hash;r=self.review();p=r['preview'];self.assertEqual(p['source']['foreign_balance'],'10.00');self.assertEqual(p['source']['carrying_cop'],'40000.00');self.assertEqual(p['calculation']['difference_cop'],'2000.00');a=self.confirm(r)
  self.assertTrue(a['source_current']);self.assertEqual(a['desired_cop'],'42000.00');self.assertFalse(a['money_transferred']);self.assertEqual(JournalEntry.plain_objects.get(pk=original.pk).system_hash,oldhash)
  self.assertTrue(LedgerEngine.validate_ledger_integrity(self.company.pk)['is_valid'])
 def test_decreasing_rate_uses_expense_not_income(self):
  r=self.review(terms={**self.args['terms'],'rate':'3800.000000'});lines=r['preview']['calculation']['lines'];self.assertEqual(lines[0]['credit'],'2000.00');self.assertEqual(lines[1]['account_id'],str(self.loss.pk));self.assertEqual(lines[1]['debit'],'2000.00');self.confirm(r)
 def test_replay_is_single_post_and_state_restores_no_approval(self):
  r=self.review();a=self.confirm(r);b=self.confirm(r);self.assertEqual(a['journal_id'],b['journal_id']);self.assertTrue(b['replayed']);self.assertEqual(AccountingAuditLog.plain_objects.filter(reference_entry_id=a['journal_id'],action='POST').count(),1);s=engine.state(self.company.pk,actor=self.actor,review_id=r['review_id']);self.assertFalse(s['confirmations_restored']);self.assertTrue(s['source_current'])
 def test_second_revaluation_posts_only_increment_from_previous_carrying_value(self):
  first=self.review();self.confirm(first);second=self.review(request_id=str(uuid.uuid4()),terms={**self.args['terms'],'source_version':'3','rate':'4300.000000'});self.assertEqual(second['preview']['source']['carrying_cop'],'42000.00');self.assertEqual(second['preview']['calculation']['difference_cop'],'1000.00');self.confirm(second);self.assertFalse(engine.state(self.company.pk,actor=self.actor,review_id=first['review_id'])['source_current'])
 def test_competing_reviews_cannot_both_post_same_difference(self):
  a=self.review();b=self.review(request_id=str(uuid.uuid4()));self.confirm(a)
  with self.assertRaises(AccountingError):self.confirm(b)
 def test_unknown_cop_movement_or_legacy_balance_blocks_guessing(self):
  self.case.a.initial_balance=Decimal('1');self.case.a.save()
  with self.assertRaises(AccountingError):self.review()
  self.case.a.initial_balance=Decimal('0');self.case.a.save();LedgerEngine.post_lines(tenant_id=self.company.pk,entry_date=self.base.entry.date,description='Synthetic unexplained COP source',lines_data=[{'account':self.case.a,'debit':'1.00'},{'account':self.case.b,'credit':'1.00'}],actor=self.actor,idempotency_key='cop-source')
  with self.assertRaises(AccountingError):self.review()
 def test_changed_ledger_after_review_blocks_posting(self):
  r=self.review();entry=JournalService.create_entry(str(self.company.pk),self.base.entry.date,'Synthetic extra foreign line',self.case.lines(),created_by=self.actor,currency='USD');new=reviewed_fx.review(self.company.pk,actor=self.actor,entry_id=str(entry.pk),terms={**self.base.terms,'rate':'4000.000000'},expected_revision=0,confirmed=True);reviewed_fx.confirm(self.company.pk,actor=self.actor,entry_id=str(entry.pk),review_id=new['review_id'],confirmed=True)
  with self.assertRaises(AccountingError):self.confirm(r)
 def test_first_and_second_authorizations_required(self):
  with self.assertRaises(AccountingError):self.review(confirmed=False)
  r=self.review()
  with self.assertRaises(AccountingError):self.confirm(r,confirmed=False)
 def test_reused_request_id_cannot_change_source_or_terms(self):
  first=self.review();again=self.review();self.assertEqual(first['review_id'],again['review_id'])
  with self.assertRaises(AccountingError):self.review(terms={**self.args['terms'],'source_version':'3','rate':'4300.000000'})
 def test_proof_write_failure_rolls_back_ledger_receipt_and_audit(self):
  r=self.review();before=JournalEntry.plain_objects.filter(tenant=self.company).count();original=OutboxEvent.objects.create
  def create(**kw):
   if kw.get('event_type')==engine.POSTED:raise RuntimeError('Synthetic FX proof failure')
   return original(**kw)
  with patch.object(OutboxEvent.objects,'create',side_effect=create):
   with self.assertRaises(RuntimeError):self.confirm(r)
  self.assertEqual(JournalEntry.plain_objects.filter(tenant=self.company).count(),before);self.assertTrue(self.confirm(r)['ledger_written'])
 def test_missing_proof_blocks_recovery_generic_replay_and_contra(self):
  r=self.review();a=self.confirm(r);OutboxEvent.objects.filter(event_type=engine.POSTED,payload__journal_id=a['journal_id'])._raw_delete('default')
  for call in [lambda:self.confirm(r),lambda:LedgerEngine.post_entry(a['journal_id'],tenant_id=self.company.pk,actor=self.actor),lambda:LedgerEngine.reverse_entry(a['journal_id'],tenant_id=self.company.pk,actor=self.actor)]:
   with self.assertRaises(AccountingError):call()
 def test_reversal_is_preserved_and_next_valuation_uses_effective_carrying_value(self):
  r=self.review();a=self.confirm(r);reverse=LedgerEngine.reverse_entry(a['journal_id'],tenant_id=self.company.pk,actor=self.actor);s=engine.state(self.company.pk,actor=self.actor,review_id=r['review_id']);self.assertTrue(s['applied']['original_reversed']);self.assertEqual(reverse.currency,'COP');next=self.review(request_id=str(uuid.uuid4()));self.assertEqual(next['preview']['source']['carrying_cop'],'40000.00');self.assertEqual(next['preview']['calculation']['difference_cop'],'2000.00')
 def test_backdated_revaluation_is_blocked_after_later_adjustment(self):
  from datetime import timedelta
  previous=self.base.entry.date-timedelta(days=1);entry=JournalService.create_entry(str(self.company.pk),previous,'Synthetic earlier FX source',self.case.lines(),created_by=self.actor,currency='USD')
  terms={**self.base.terms,'rate':'4000.000000','source_version':'earlier-source','valid_from':previous.isoformat(),'valid_until':previous.isoformat()}
  r=reviewed_fx.review(self.company.pk,actor=self.actor,entry_id=str(entry.pk),terms=terms,expected_revision=0,confirmed=True);reviewed_fx.confirm(self.company.pk,actor=self.actor,entry_id=str(entry.pk),review_id=r['review_id'],confirmed=True)
  self.confirm(self.review())
  with self.assertRaisesRegex(AccountingError,'later FX revaluation'):
   self.review(request_id=str(uuid.uuid4()),as_of=previous.isoformat(),terms={**self.args['terms'],'source_version':'earlier-revaluation','valid_from':previous.isoformat(),'valid_until':previous.isoformat()})
 def test_zero_delta_does_not_create_zero_post(self):
  with self.assertRaises(AccountingError):self.review(terms={**self.args['terms'],'rate':'4000.000000'})
 def test_liability_rate_increase_posts_loss_with_negative_signed_balance(self):
  liability=Account.plain_objects.create(tenant=self.company,chart_of_accounts=self.case.chart,code='2205',name='Synthetic foreign payable',type='LIABILITY')
  entry=JournalService.create_entry(str(self.company.pk),self.base.entry.date,'Synthetic foreign liability',[{'account':self.loss,'debit':'10.00'},{'account':liability,'credit':'10.00'}],created_by=self.actor,currency='USD')
  r=reviewed_fx.review(self.company.pk,actor=self.actor,entry_id=str(entry.pk),terms={**self.base.terms,'rate':'4000.000000'},expected_revision=0,confirmed=True);reviewed_fx.confirm(self.company.pk,actor=self.actor,entry_id=str(entry.pk),review_id=r['review_id'],confirmed=True)
  proposal=self.review(account_id=str(liability.pk));self.assertEqual(proposal['preview']['source']['foreign_balance'],'-10.00');self.assertEqual(proposal['preview']['calculation']['difference_cop'],'-2000.00');self.assertEqual(proposal['preview']['calculation']['lines'][1]['account_id'],str(self.loss.pk));self.confirm(proposal)
 def test_partial_consumption_is_not_mislabelled_unrealized_revaluation(self):
  entry=JournalService.create_entry(str(self.company.pk),self.base.entry.date,'Synthetic foreign consumption',[{'account':self.loss,'debit':'1.00'},{'account':self.case.a,'credit':'1.00'}],created_by=self.actor,currency='USD')
  r=reviewed_fx.review(self.company.pk,actor=self.actor,entry_id=str(entry.pk),terms={**self.base.terms,'rate':'4000.000000'},expected_revision=0,confirmed=True);reviewed_fx.confirm(self.company.pk,actor=self.actor,entry_id=str(entry.pk),review_id=r['review_id'],confirmed=True)
  with self.assertRaisesRegex(AccountingError,'settlement/consumption'):self.review()
 def test_deleted_initial_fx_provenance_blocks_revaluation(self):
  OutboxEvent.objects.filter(event_type=reviewed_fx.POSTED,payload__entry_id=str(self.base.entry.pk))._raw_delete('default')
  with self.assertRaises(AccountingError):self.review()
 def test_wrong_mapping_classification_foreign_account_and_closed_period_rejected(self):
  for change in [{'loss_account_id':str(self.case.b.pk)},{'monetary_classification':'AUTO'},{'account_id':str(uuid.uuid4())}]:
   with self.assertRaises(AccountingError):self.review(**change)
  r=self.review();self.case.period.status='closed';self.case.period.save()
  with self.assertRaises(AccountingError):self.confirm(r)
if __name__=='__main__':unittest.main()
