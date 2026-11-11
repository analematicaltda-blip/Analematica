"""Actual ledger partial settlement, realized difference and remaining revaluation."""
import runpy,unittest,uuid,copy
from pathlib import Path
from unittest.mock import patch
from decimal import Decimal
f=runpy.run_path(str(Path(__file__).with_name('accounting_fx_revaluation_check.py')),run_name='settlement_fixture')
from apps.core_erp.accounting import fx_settlement as engine,fx_revaluation,ratios
from apps.core_erp.accounting.models import Account,JournalEntry,LedgerEntry
from apps.core_erp.accounting.ledger_engine import LedgerEngine
from apps.core_erp.accounting.exceptions import AccountingError
from apps.core_erp.outbox_models import OutboxEvent
from apps.core_erp.accounting.ratio_models import AccountingRatioPolicy
node=f
while 'create' not in node:node=node['fixture']
node['create'](AccountingRatioPolicy)
class SettlementChecks(unittest.TestCase):
 def setUp(self):
  self.b=f['RevaluationChecks']();self.b.setUp();self.company=self.b.company;self.actor=self.b.actor;self.case=self.b.case
  self.cash=Account.plain_objects.create(tenant=self.company,chart_of_accounts=self.case.chart,code='111006',name='Synthetic recorded COP cash',type='ASSET');self.clearing=Account.plain_objects.create(tenant=self.company,chart_of_accounts=self.case.chart,code='240599',name='Synthetic pending receipt',type='LIABILITY');ratios.configure(self.company.pk,actor=self.actor,mapping={'cash_equivalents':[str(self.cash.pk)],'temporary_investments':[],'immediate_receivables':[],'current_liabilities':[str(self.clearing.pk)]},evidence_digest='f'*64,expected_revision=0,confirmed=True)
  self.line=self.receipt('17200.00');self.args={'actor':self.actor,'request_id':str(uuid.uuid4()),'account_id':str(self.case.a.pk),'currency':'USD','as_of':self.b.base.day,'cash_line_id':str(self.line.pk),'clearing_account_id':str(self.clearing.pk),'quantity':'4.00','terms':{**self.b.args['terms'],'rate':'4300.000000','source_version':'settlement-1'},'gain_account_id':str(self.case.b.pk),'loss_account_id':str(self.b.loss.pk),'evidence_digest':'c'*64,'monetary_classification':'MONETARY_DECLARED','confirmed':True}
 def receipt(self,amount):
  journal=LedgerEngine.post_lines(tenant_id=self.company.pk,entry_date=self.b.base.entry.date,description='Synthetic recorded receipt',actor=self.actor,idempotency_key=str(uuid.uuid4()),lines_data=[{'account':self.cash,'debit':amount},{'account':self.clearing,'credit':amount}]);return LedgerEntry.plain_objects.get(journal_entry=journal,account=self.cash)
 def review(self,**kw):return engine.review(self.company.pk,**{**self.args,**kw})
 def confirm(self,r,**kw):return engine.confirm(self.company.pk,actor=self.actor,review_id=r['review_id'],confirmed=kw.get('confirmed',True))
 def balance(self):return fx_revaluation.source(self.company,str(self.case.a.pk),'USD',self.b.base.day,allow_zero=True)
 def test_partial_receipt_reclassifies_clearing_preserves_cash_and_foreign_original(self):
  oldhash=JournalEntry.plain_objects.get(pk=self.b.base.entry.pk).system_hash;cashhash=self.line.journal_entry.system_hash;r=self.review();self.assertEqual(r['preview']['calculation']['carrying_released_cop'],'16000.00');a=self.confirm(r);self.assertEqual(a['realized_difference_cop'],'1200.00');self.assertEqual((a['remaining_foreign'],a['remaining_cop']),('6.00','24000.00'));self.assertFalse(a['money_transferred']);self.assertEqual(JournalEntry.plain_objects.get(pk=self.b.base.entry.pk).system_hash,oldhash);self.assertEqual(JournalEntry.plain_objects.get(pk=self.line.journal_entry_id).system_hash,cashhash);self.assertFalse(LedgerEntry.plain_objects.filter(journal_entry_id=a['journal_id'],account=self.cash).exists());self.assertEqual(self.balance()['foreign_balance'],'6.00');self.assertTrue(LedgerEngine.validate_ledger_integrity(self.company.pk)['is_valid'])
 def test_after_revaluation_only_difference_from_current_carrying_is_realized(self):
  self.b.confirm(self.b.review());a=self.confirm(self.review());self.assertEqual(a['carrying_released_cop'],'16800.00');self.assertEqual(a['realized_difference_cop'],'400.00');self.assertEqual(self.balance()['carrying_cop'],'25200.00');r=self.b.review(request_id=str(uuid.uuid4()),terms={**self.b.args['terms'],'source_version':'after-settlement','rate':'4250.000000'});self.assertEqual(r['preview']['calculation']['difference_cop'],'300.00');self.b.confirm(r)
 def test_full_settlement_clears_last_cent_and_leaves_no_foreign_or_cop_residual(self):
  self.confirm(self.review());cash=self.receipt('26400.00');r=self.review(request_id=str(uuid.uuid4()),cash_line_id=str(cash.pk),quantity='6.00',terms={**self.args['terms'],'rate':'4400.000000','source_version':'settlement-2'});a=self.confirm(r);self.assertEqual(a['remaining_foreign'],'0.00');self.assertEqual(a['remaining_cop'],'0.00');self.assertEqual(self.balance()['foreign_balance'],'0.00');self.assertEqual(self.balance()['carrying_cop'],'0.00')
 def test_replay_and_state_never_duplicate_or_restore_approval(self):
  r=self.review();a=self.confirm(r);b=self.confirm(r);self.assertTrue(b['replayed']);self.assertEqual(a['journal_id'],b['journal_id']);s=engine.state(self.company.pk,actor=self.actor,review_id=r['review_id']);self.assertFalse(s['confirmations_restored']);self.assertTrue(s['source_current']);self.assertEqual(self.review()['review_id'],r['review_id'])
 def test_same_cash_source_cannot_be_used_twice(self):
  self.confirm(self.review())
  with self.assertRaises(AccountingError):self.review(request_id=str(uuid.uuid4()))
 def test_competing_reviews_cannot_double_consume_foreign_balance_or_cash(self):
  a=self.review();b=self.review(request_id=str(uuid.uuid4()));self.confirm(a)
  with self.assertRaises(AccountingError):self.confirm(b)
 def test_missing_cash_invalid_rate_quantity_or_confirmation_rejected(self):
  for kw in [{'cash_line_id':str(uuid.uuid4())},{'quantity':'11.00'},{'quantity':'4.001'},{'quantity':'0.00'},{'quantity':4.0},{'confirmed':False},{'terms':{**self.args['terms'],'rate':'4200.000000'}},{'monetary_classification':'AUTO'}]:
   with self.assertRaises((AccountingError,ValueError)):self.review(**kw)
  with self.assertRaises(AccountingError):self.confirm(self.review(),confirmed=False)
 def test_proof_failure_rolls_back_journal_receipt_and_claim(self):
  r=self.review();before=JournalEntry.plain_objects.filter(tenant=self.company).count();create=OutboxEvent.objects.create
  def fail(**kw):
   if kw.get('event_type')==engine.CLAIM:raise RuntimeError('Synthetic claim failure')
   return create(**kw)
  with patch.object(OutboxEvent.objects,'create',side_effect=fail):
   with self.assertRaises(RuntimeError):self.confirm(r)
  self.assertEqual(JournalEntry.plain_objects.filter(tenant=self.company).count(),before);self.assertEqual(self.balance()['foreign_balance'],'10.00');self.confirm(r)
 def test_missing_proof_blocks_replay_generic_posting_reversal_and_cash_reuse(self):
  r=self.review();a=self.confirm(r);OutboxEvent.objects.filter(event_type=engine.POSTED,payload__journal_id=a['journal_id'])._raw_delete('default')
  for call in [lambda:self.confirm(r),lambda:LedgerEngine.post_entry(a['journal_id'],tenant_id=self.company.pk,actor=self.actor),lambda:LedgerEngine.reverse_entry(a['journal_id'],tenant_id=self.company.pk,actor=self.actor),lambda:self.review(request_id=str(uuid.uuid4()))]:
   with self.assertRaises(AccountingError):call()
 def test_reserved_prefix_cannot_bypass_review_using_generic_journal(self):
  with self.assertRaises(AccountingError):LedgerEngine.post_lines(tenant_id=self.company.pk,entry_date=self.b.base.entry.date,description='Synthetic bypass',actor=self.actor,idempotency_key=engine.PREFIX+str(uuid.uuid4()),lines_data=[{'account':self.cash,'debit':'1.00'},{'account':self.case.b,'credit':'1.00'}])
 def test_reversal_preserves_original_and_restores_quantity_and_carrying(self):
  a=self.confirm(self.review());reverse=LedgerEngine.reverse_entry(a['journal_id'],tenant_id=self.company.pk,actor=self.actor);self.assertTrue(reverse.is_reversal);self.assertEqual(self.balance()['foreign_balance'],'10.00');self.assertEqual(self.balance()['carrying_cop'],'40000.00');s=engine.state(self.company.pk,actor=self.actor,review_id=a['review_id']);self.assertTrue(s['applied']['original_reversed']);self.confirm(self.review(request_id=str(uuid.uuid4())))
 def test_asset_loss_uses_expense_and_zero_difference_needs_no_fake_gain_line(self):
  cash=self.receipt('15200.00');a=self.confirm(self.review(cash_line_id=str(cash.pk),terms={**self.args['terms'],'rate':'3800.000000','source_version':'loss'}));self.assertEqual(a['realized_difference_cop'],'-800.00')
 def test_zero_difference_posts_only_monetary_and_clearing_lines(self):
  cash=self.receipt('16000.00');r=self.review(cash_line_id=str(cash.pk),terms={**self.args['terms'],'rate':'4000.000000','source_version':'zero-difference'});a=self.confirm(r);self.assertEqual(a['realized_difference_cop'],'0.00');self.assertEqual(LedgerEntry.plain_objects.filter(journal_entry_id=a['journal_id']).count(),2)
 def test_active_settlement_blocks_reversal_of_its_recorded_cash_source(self):
  r=self.review();a=self.confirm(r)
  with self.assertRaises(AccountingError):LedgerEngine.reverse_entry(self.line.journal_entry_id,tenant_id=self.company.pk,actor=self.actor)
  LedgerEngine.reverse_entry(a['journal_id'],tenant_id=self.company.pk,actor=self.actor);LedgerEngine.reverse_entry(self.line.journal_entry_id,tenant_id=self.company.pk,actor=self.actor)
 def test_liability_payment_posts_loss_and_reduces_signed_payable(self):
  from apps.core_erp.accounting import reviewed_fx
  from apps.core_erp.accounting.journal_service import JournalService
  payable=Account.plain_objects.create(tenant=self.company,chart_of_accounts=self.case.chart,code='220599',name='Synthetic USD payable',type='LIABILITY');clearing=Account.plain_objects.create(tenant=self.company,chart_of_accounts=self.case.chart,code='138099',name='Synthetic paid clearing',type='ASSET')
  journal=JournalService.create_entry(str(self.company.pk),self.b.base.entry.date,'Synthetic foreign payable',[{'account':self.b.loss,'debit':'10.00'},{'account':payable,'credit':'10.00'}],created_by=self.actor,currency='USD');r=reviewed_fx.review(self.company.pk,actor=self.actor,entry_id=str(journal.pk),terms={**self.b.base.terms,'rate':'4000.000000'},expected_revision=0,confirmed=True);reviewed_fx.confirm(self.company.pk,actor=self.actor,entry_id=str(journal.pk),review_id=r['review_id'],confirmed=True)
  payment=LedgerEngine.post_lines(tenant_id=self.company.pk,entry_date=self.b.base.entry.date,description='Synthetic recorded payment',actor=self.actor,idempotency_key=str(uuid.uuid4()),lines_data=[{'account':clearing,'debit':'17200.00'},{'account':self.cash,'credit':'17200.00'}]);cash_line=LedgerEntry.plain_objects.get(journal_entry=payment,account=self.cash);r=self.review(account_id=str(payable.pk),cash_line_id=str(cash_line.pk),clearing_account_id=str(clearing.pk));a=self.confirm(r);self.assertEqual(a['realized_difference_cop'],'-1200.00');self.assertEqual(a['remaining_foreign'],'-6.00');self.assertEqual(a['remaining_cop'],'-24000.00')
  payment2=LedgerEngine.post_lines(tenant_id=self.company.pk,entry_date=self.b.base.entry.date,description='Synthetic second recorded payment',actor=self.actor,idempotency_key=str(uuid.uuid4()),lines_data=[{'account':clearing,'debit':'16000.00'},{'account':self.cash,'credit':'16000.00'}]);cash2=LedgerEntry.plain_objects.get(journal_entry=payment2,account=self.cash);r=self.review(request_id=str(uuid.uuid4()),account_id=str(payable.pk),cash_line_id=str(cash2.pk),clearing_account_id=str(clearing.pk),terms={**self.args['terms'],'rate':'4000.000000','source_version':'liability-zero'});zero=self.confirm(r);self.assertEqual(zero['realized_difference_cop'],'0.00');self.assertEqual(zero['remaining_foreign'],'-2.00');self.assertEqual(LedgerEntry.plain_objects.filter(journal_entry_id=zero['journal_id']).count(),2)
 def test_request_recovery_is_read_only_and_cannot_restore_confirmations(self):
  missing=engine.request_state(self.company.pk,actor=self.actor,request_id=self.args['request_id']);self.assertFalse(missing['found']);r=self.review();found=engine.request_state(self.company.pk,actor=self.actor,request_id=self.args['request_id']);self.assertTrue(found['found']);self.assertEqual(found['state']['review_id'],r['review_id']);self.assertFalse(found['state']['confirmations_restored'])
 def test_recorded_cash_catalog_never_claims_external_authentication(self):
  c=engine.catalog(self.company.pk,actor=self.actor);self.assertIn(str(self.line.pk),[r['cash_line_id'] for r in c['recorded_cash']]);self.assertFalse(c['bank_verified']);self.assertFalse(c['ledger_written'])
 def test_corporate_contract_checks_exact_proposal_and_posted_state(self):
  import sys
  sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'SGA-CD-BACKEND'))
  from app.services.fx_settlement_contract import validate
  r=self.review();payload={k:v for k,v in self.args.items() if k!='actor'};context={'tenant_id':str(self.company.pk),'ledger_actor_id':str(self.actor.pk)};validate('review_fx_settlement',r,payload,context);a=self.confirm(r);validate('post_fx_settlement',a,{'review_id':r['review_id']},context);state=engine.state(self.company.pk,actor=self.actor,review_id=r['review_id']);validate('fx_settlement_state',state,{'review_id':r['review_id']},context)
  broken=copy.deepcopy(r);broken['preview']['calculation']['remaining_cop']='24001.00'
  with self.assertRaises(ValueError):validate('review_fx_settlement',broken,payload,context)
  for change in [{'bank_verified':True},{'money_transferred':True},{'company_id':str(uuid.uuid4())}]:
   with self.assertRaises(ValueError):validate('post_fx_settlement',{**a,**change},{'review_id':r['review_id']},context)
 def test_existing_revaluation_contract_accepts_explicit_settlement_quantity_provenance(self):
  import sys
  sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'SGA-CD-BACKEND'))
  from app.services.fx_revaluation_contract import validate
  self.confirm(self.review());r=self.b.review(request_id=str(uuid.uuid4()));payload={k:v for k,v in self.b.args.items() if k!='actor'};payload['request_id']=r['preview']['request_id'];validate('review_fx_revaluation',r,payload,{'tenant_id':str(self.company.pk),'ledger_actor_id':str(self.actor.pk)})
 def test_cash_already_bound_to_advance_recognition_cannot_fund_settlement(self):
  OutboxEvent.objects.create(event_type='accounting.reservation.advance-applied.v1',domain='accounting',aggregate_root=str(uuid.uuid4()),payload={'company_id':str(self.company.pk),'allocation':{'journal_id':str(self.line.journal_entry_id)}})
  with self.assertRaises(AccountingError):self.review()
 def test_settled_cash_cannot_be_reused_as_advance_despite_pooled_clearing_balance(self):
  from types import SimpleNamespace
  from apps.domain_business.comercial.services.reservation_recognition import validated_advance
  from rest_framework.exceptions import ValidationError
  self.confirm(self.review());self.receipt('17200.00');source=SimpleNamespace(deposit_paid=Decimal('17200.00'),total_price=Decimal('17200.00'),pk=uuid.uuid4(),customer_id=uuid.uuid4())
  with self.assertRaises(ValidationError):validated_advance(self.company,source,{'journal_id':str(self.line.journal_entry_id),'liability_account_id':str(self.clearing.pk),'evidence_digest':'e'*64},self.b.base.entry.date)
 def test_later_contra_does_not_release_cash_capacity_for_an_earlier_cutoff(self):
  from datetime import timedelta
  a=self.confirm(self.review());LedgerEngine.reverse_entry(a['journal_id'],tenant_id=self.company.pk,actor=self.actor)
  with self.assertRaises(AccountingError):engine.available_cash(self.company,str(self.line.pk),(self.b.base.entry.date-timedelta(days=1)).isoformat())
  engine.available_cash(self.company,str(self.line.pk),self.b.base.day)
 def test_trial_balance_reports_remaining_cop_and_unchanged_recorded_cash(self):
  from apps.core_erp.accounting.reports_engine import ReportsEngine
  self.confirm(self.review());r=ReportsEngine.get_trial_balance(self.company.pk,self.b.base.entry.date);lines={row['account_code']:row for row in r['lines']};self.assertEqual(lines[self.case.a.code]['balance'],Decimal('24000.00'));self.assertEqual(lines[self.cash.code]['balance'],Decimal('17200.00'));self.assertEqual(lines[self.clearing.code]['balance'],Decimal('0.00'));self.assertEqual(r['total_debit'],r['total_credit'])
 def test_closed_period_rejects_settlement_without_partial_effect(self):
  r=self.review();before=JournalEntry.plain_objects.filter(tenant=self.company).count();self.case.period.status='closed';self.case.period.save()
  with self.assertRaises(AccountingError):self.confirm(r)
  self.assertEqual(JournalEntry.plain_objects.filter(tenant=self.company).count(),before)
 def test_three_partial_quantities_release_fractional_carrying_exactly_on_last_post(self):
  self.b.confirm(self.b.review(terms={**self.b.args['terms'],'rate':'4000.123456','source_version':'fractional-revaluation'}));released=[]
  for quantity,cash_amount in [('3.33','14319.00'),('3.33','14319.00'),('3.34','14362.00')]:
   line=self.receipt(cash_amount);r=self.review(request_id=str(uuid.uuid4()),cash_line_id=str(line.pk),quantity=quantity);a=self.confirm(r);released.append(Decimal(a['carrying_released_cop']))
  self.assertEqual(sum(released),Decimal('40001.23'));self.assertEqual(released[-1],Decimal('13360.41'));self.assertEqual(self.balance()['foreign_balance'],'0.00');self.assertEqual(self.balance()['carrying_cop'],'0.00')
if __name__=='__main__':unittest.main()
