"""Confirmed partial batches -> complete period, with no new money or claims."""
import copy,runpy,unittest,uuid
from pathlib import Path
from unittest.mock import patch
f=runpy.run_path(str(Path(__file__).with_name('accounting_bank_grouped_check.py')),run_name='rollup_fixture')
from apps.core_erp.accounting import bank_period_rollup as engine,bank_grouped as grouped
from apps.core_erp.accounting.exceptions import AccountingError
from apps.core_erp.accounting.ledger_engine import LedgerEngine
from apps.core_erp.outbox_models import OutboxEvent
class RollupChecks(unittest.TestCase):
 def setUp(self):
  self.g=f['GroupedBankChecks']();self.g.setUp();self.c=self.g.case;self.ids=[]
  for name,amount in [('first','6.00'),('second','4.00')]:
   csv='transaction_id,date,direction,amount,currency\n'+name+','+self.g.base.bank.day+',IN,'+amount+',COP\n';r=self.g.review(csv_text=csv,groups=[{'group_id':str(uuid.uuid4()),'bank_rows':[1],'ledger_allocations':[{'ledger_line_id':self.g.line,'amount':amount}]}]);self.ids.append(self.g.confirm(r)['reconciliation_id'])
  self.period={'since':self.g.base.bank.day,'until':self.g.base.bank.day,'opening':'0.00','closing':'10.00','statement_complete':True,'evidence_digest':'f'*64};self.args={'actor':self.c.user,'account_id':str(self.c.a.pk),'reconciliation_ids':self.ids,'period':self.period,'expected_revision':0,'confirmed':True}
 def review(self,**kw):return engine.review(self.c.tenant.pk,**{**self.args,**kw})
 def confirm(self,r,**kw):return engine.confirm(self.c.tenant.pk,**{'actor':self.c.user,'review_id':r['review_id'],'confirmed':True,**kw})
 def state(self):return engine.state(self.c.tenant.pk,actor=self.c.user,account_id=str(self.c.a.pk),since=self.period['since'],until=self.period['until'])
 def release(self,index=0):
  p=OutboxEvent.objects.get(pk=self.ids[index]);return self.g.release({'reconciliation_id':str(p.pk)})
 def test_all_catalog_pages_use_stable_account_snapshot_and_reject_bad_cursors(self):
  for number in range(51):
   journal=self.post();line=f['engine'].LedgerEntry.plain_objects.get(journal_entry=journal,account=self.c.a)
   text='transaction_id,date,direction,amount,currency\npage-'+str(number)+','+self.period['since']+',IN,3.00,COP\n'
   reviewed=self.g.review(csv_text=text,groups=[{'group_id':str(uuid.uuid4()),'bank_rows':[1],'ledger_line_ids':[str(line.pk)]}]);self.g.confirm(reviewed)
  args={'actor':self.c.user,'account_id':str(self.c.a.pk)};first=engine.sources(self.c.tenant.pk,**args);self.assertEqual(first['total_count'],53);self.assertEqual(len(first['batches']),50);self.assertTrue(first['truncated'])
  cursor={'after_id':first['next_after'],'catalog_digest':first['catalog_digest']};second=engine.sources(self.c.tenant.pk,**args,**cursor);self.assertEqual(len(second['batches']),3);self.assertFalse(second['truncated']);self.assertIsNone(second['next_after']);self.assertEqual(engine.fingerprint(first['batches']+second['batches']),first['catalog_digest'])
  validate=runpy.run_path(str(Path(__file__).resolve().parents[2]/'SGA-CD-BACKEND/app/services/bank_rollup_contract.py'))['validate'];scope={'tenant_id':str(self.c.tenant.pk)};payload={'account_id':args['account_id'],**cursor};validate('bank_rollup_sources',second,payload,scope)
  response=self.c.call('bank_rollup_sources','post',payload);self.assertEqual(response.status_code,200,response.data);self.assertEqual(response.data,second)
  for bad in [{'after_id':first['next_after']},{'catalog_digest':first['catalog_digest']},{**cursor,'catalog_digest':'a'*64},{**cursor,'after_id':str(uuid.uuid4())},{**cursor,'after_id':first['batches'][0]['reconciliation_id']},{**cursor,'after_id':second['batches'][-1]['reconciliation_id']}]:
   with self.assertRaises(AccountingError):engine.sources(self.c.tenant.pk,**args,**bad)
  for bad in [{'total_count':2},{'catalog_digest':'x'},{'next_after':str(uuid.uuid4())},{'after_id':None},{'batches':list(reversed(second['batches']))}]:
   with self.assertRaises(ValueError):validate('bank_rollup_sources',{**second,**bad},payload,scope)
  self.release()
  with self.assertRaises(AccountingError):engine.sources(self.c.tenant.pk,**args,**cursor)
  self.assertEqual(engine.sources(self.c.tenant.pk,**args)['total_count'],52)
 def test_partial_batches_qualify_only_together_without_money_or_new_claims(self):
  counts=self.g.base.counts();claims=OutboxEvent.objects.filter(event_type=grouped.legacy.CLAIM).count();r=self.review();self.assertFalse(r['period_reconciled']);self.assertTrue(r['preview']['snapshot']['eligible']);a=self.confirm(r);self.assertTrue(a['period_reconciled']);self.assertEqual(a['batch_count'],2);self.assertEqual(a['bank_row_count'],2);self.assertEqual(a['ledger_line_count'],1);self.assertFalse(a['bank_verified']);self.assertFalse(a['ledger_written']);self.assertFalse(a['money_transferred']);self.assertEqual(counts,self.g.base.counts());self.assertEqual(claims,OutboxEvent.objects.filter(event_type=grouped.legacy.CLAIM).count());self.assertEqual(self.confirm(r)['confirmation_id'],a['confirmation_id']);self.assertTrue(self.confirm(r)['replayed'])
 def test_missing_batch_or_wrong_balances_does_not_qualify(self):
  for kw in [{'reconciliation_ids':self.ids[:1],'period':{**self.period,'closing':'6.00'}},{'period':{**self.period,'opening':'1.00','closing':'11.00'}},{'period':{**self.period,'closing':'11.00'}}]:
   with self.assertRaises(AccountingError):self.review(**kw)
 def test_duplicate_unknown_or_excess_batch_ids_rejected(self):
  for ids in [[],self.ids*2,[str(uuid.uuid4())],[str(uuid.uuid4()) for _ in range(21)]]:
   with self.assertRaises(AccountingError):self.review(reconciliation_ids=ids)
 def test_two_explicit_confirmations_and_revision_are_required(self):
  with self.assertRaises(AccountingError):self.review(confirmed=False)
  r=self.review()
  with self.assertRaises(AccountingError):self.confirm(r,confirmed=False)
  with self.assertRaises(AccountingError):self.review()
  newer=self.review(expected_revision=1)
  with self.assertRaises(AccountingError):self.confirm(r)
  self.assertTrue(self.confirm(newer)['period_reconciled'])
 def test_release_between_confirmations_blocks_rollup(self):
  r=self.review();self.release()
  with self.assertRaises(AccountingError):self.confirm(r)
  self.assertFalse(OutboxEvent.objects.filter(event_type=engine.APPLIED,payload__company_id=str(self.c.tenant.pk)).exists())
 def test_release_after_confirmation_invalidates_current_qualification(self):
  r=self.review();a=self.confirm(r);self.release();state=self.state();self.assertFalse(state['source_current']);self.assertFalse(state['applied']['period_reconciled']);self.assertTrue(state['applied']['requires_review']);self.assertEqual(state['applied']['confirmation_id'],a['confirmation_id']);self.assertFalse(state['confirmations_restored'])
 def post(self,opposite=False):
  return LedgerEngine.post_lines(tenant_id=self.c.tenant.pk,entry_date=self.g.base.bank.entry.date,description='Synthetic rollup omission',actor=self.c.user,idempotency_key=str(uuid.uuid4()),lines_data=[{'account':self.c.b if opposite else self.c.a,'debit':'3.00'},{'account':self.c.a if opposite else self.c.b,'credit':'3.00'}])
 def test_offsetting_omissions_cannot_hide_in_balanced_period(self):
  self.post();self.post(True)
  with self.assertRaises(AccountingError):self.review()
 def test_retroactive_posting_invalidates_confirmed_period(self):
  r=self.review();self.confirm(r);self.post();self.post(True);a=self.confirm(r);self.assertFalse(a['source_current']);self.assertFalse(a['period_reconciled'])
 def test_cash_reversal_invalidates_confirmed_period(self):
  r=self.review();self.confirm(r);LedgerEngine.reverse_entry(self.g.base.bank.entry.pk,tenant_id=self.c.tenant.pk,actor=self.c.user);self.assertFalse(self.state()['applied']['period_reconciled'])
 def test_missing_claim_fails_closed(self):
  r=self.review();self.confirm(r);OutboxEvent.objects.filter(event_type=grouped.legacy.CLAIM,payload__reconciliation_id=self.ids[0]).first().delete();s=self.state();self.assertFalse(s['applied']['period_reconciled'])
 def test_confirmation_failure_rolls_back_without_touching_prior_batches(self):
  r=self.review();create=OutboxEvent.objects.create
  def fail(**kw):
   if kw.get('event_type')==engine.APPLIED:raise RuntimeError('Synthetic rollup confirmation failure')
   return create(**kw)
  with patch.object(OutboxEvent.objects,'create',side_effect=fail):
   with self.assertRaises(RuntimeError):self.confirm(r)
  self.assertFalse(OutboxEvent.objects.filter(event_type=engine.APPLIED,payload__company_id=str(self.c.tenant.pk)).exists());self.assertEqual(len(engine.sources(self.c.tenant.pk,actor=self.c.user,account_id=str(self.c.a.pk))['batches']),2);self.assertTrue(self.confirm(r)['period_reconciled'])
 def test_catalog_and_recovery_do_not_restore_authorizations_or_plain_refs(self):
  rows=engine.sources(self.c.tenant.pk,actor=self.c.user,account_id=str(self.c.a.pk));self.assertTrue(rows['read_only']);self.assertEqual(len(rows['batches']),2);self.assertTrue(all(b['source_current'] for b in rows['batches']));self.assertFalse(rows['confirmations_restored']);r=self.review();s=self.state();self.assertEqual(s['review_id'],r['review_id']);self.assertTrue(s['source_current']);self.assertIsNone(s['applied']);self.assertFalse(s['confirmations_restored'])
 def test_empty_state_and_invalid_period_declaration(self):
  self.assertEqual(self.state()['revision'],0)
  for period in [{**self.period,'statement_complete':False},{**self.period,'opening':'-0.00'},{**self.period,'since':'1990-01-01'}]:
   with self.assertRaises(AccountingError):self.review(period=period)
 def test_owner_scoping_for_catalog_review_confirmation_and_recovery(self):
  r=self.review()
  requests=[('bank_rollup_sources',{'account_id':str(self.c.a.pk)}),('review_bank_rollup',{k:v for k,v in self.args.items() if k!='actor'}),('confirm_bank_rollup',{'review_id':r['review_id'],'confirmed':True}),('bank_rollup_state',{'account_id':str(self.c.a.pk),'since':self.period['since'],'until':self.period['until']})]
  for action,payload in requests:self.assertEqual(self.c.call(action,'post',payload,user=self.c.other).status_code,403)
 def test_foreign_or_unclassified_cash_account_cannot_adopt_batches(self):
  for account in [str(self.c.b.pk),str(uuid.uuid4())]:
   with self.assertRaises((AccountingError,ValueError)):self.review(account_id=account)
 def test_policy_change_invalidates_previously_confirmed_period(self):
  from apps.core_erp.accounting import ratios
  r=self.review();self.confirm(r);policy=ratios.latest(self.c.tenant.pk);ratios.configure(self.c.tenant.pk,actor=self.c.user,mapping=policy.mapping,evidence_digest='d'*64,expected_revision=1,confirmed=True);self.assertFalse(self.state()['applied']['period_reconciled'])
 def test_inflows_and_outflows_preserve_direction_not_just_net_balance(self):
  journal=self.post(True);line=f['engine'].LedgerEntry.plain_objects.get(journal_entry=journal,account=self.c.a)
  text='transaction_id,date,direction,amount,currency\nrollup-out,'+self.period['since']+',OUT,3.00,COP\n';review=self.g.review(csv_text=text,groups=[{'group_id':str(uuid.uuid4()),'bank_rows':[1],'ledger_allocations':[{'ledger_line_id':str(line.pk),'amount':'3.00'}]}]);identifier=self.g.confirm(review)['reconciliation_id'];r=self.review(reconciliation_ids=self.ids+[identifier],period={**self.period,'closing':'7.00'});a=self.confirm(r);self.assertTrue(a['period_reconciled']);assessment=r['preview']['snapshot']['assessment'];self.assertEqual(assessment['bank_in'],'10.00');self.assertEqual(assessment['bank_out'],'3.00')
 def test_opening_balance_comes_from_prior_verified_cash_not_zero_default(self):
  from datetime import timedelta
  LedgerEngine.post_lines(tenant_id=self.c.tenant.pk,entry_date=self.g.base.bank.entry.date-timedelta(days=1),description='Synthetic prior cash',actor=self.c.user,idempotency_key=str(uuid.uuid4()),lines_data=[{'account':self.c.a,'debit':'5.00'},{'account':self.c.b,'credit':'5.00'}])
  with self.assertRaises(AccountingError):self.review()
  r=self.review(period={**self.period,'opening':'5.00','closing':'15.00'});self.assertEqual(r['preview']['snapshot']['assessment']['ledger_opening'],'5.00');self.assertTrue(self.confirm(r)['period_reconciled'])
 def test_strict_erp_api_and_corporate_contract(self):
  payload={k:v for k,v in self.args.items() if k!='actor'};self.assertEqual(self.c.call('review_bank_rollup','post',{**payload,'tenant_id':str(uuid.uuid4())}).status_code,400);r=self.c.call('review_bank_rollup','post',payload);self.assertEqual(r.status_code,200,r.data);args={'review_id':r.data['review_id'],'confirmed':True};a=self.c.call('confirm_bank_rollup','post',args);self.assertEqual(a.status_code,200,a.data)
  validate=runpy.run_path(str(Path(__file__).resolve().parents[2]/'SGA-CD-BACKEND/app/services/bank_rollup_contract.py'))['validate'];scope={'tenant_id':str(self.c.tenant.pk)};validate('review_bank_rollup',r.data,payload,scope);validate('confirm_bank_rollup',a.data,args,scope)
  for change in [{'company_id':str(uuid.uuid4())},{'source_current':False},{'bank_verified':True},{'money_transferred':True}]:
   with self.assertRaises(ValueError):validate('confirm_bank_rollup',{**a.data,**change},args,scope)
  broken=copy.deepcopy(r.data);broken['preview']['snapshot']['allocations'][0]['allocated_amount']='9.00'
  with self.assertRaises(ValueError):validate('review_bank_rollup',broken,payload,scope)
if __name__=='__main__':unittest.main()
