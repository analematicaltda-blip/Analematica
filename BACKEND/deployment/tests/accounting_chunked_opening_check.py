"""Preserved source beyond100 accounts -> chunk proofs -> one atomic opening."""
import runpy,unittest,uuid,copy
from pathlib import Path
from unittest.mock import patch
from decimal import Decimal
f=runpy.run_path(str(Path(__file__).with_name('accounting_opening_check.py')),run_name='chunked_opening_fixture')
from apps.core_erp.accounting import chunked_opening as engine,opening_balances as old
from apps.core_erp.accounting.models import Account,JournalEntry,LedgerEntry,AccountingEventReceipt
from apps.core_erp.accounting.ledger_engine import LedgerEngine
from apps.core_erp.accounting.reports_engine import ReportsEngine
from apps.core_erp.accounting.exceptions import AccountingError
from apps.core_erp.outbox_models import OutboxEvent
class ChunkedOpeningChecks(unittest.TestCase):
 def setUp(self):
  self.b=f['OpeningTests']();self.b.setUp();self.company=self.b.company;self.actor=self.b.actor;accounts=[]
  for i in range(124):
   for kind,code in [('ASSET','150'),('EQUITY','350')]:accounts.append(Account(tenant=self.company,chart_of_accounts=self.b.case.chart,code=code+str(i).zfill(4),name='Synthetic opening '+kind+' '+str(i),type=kind,initial_balance=Decimal('1.00')))
  Account.plain_objects.bulk_create(accounts);self.page=engine.sources(self.company.pk,actor=self.actor);self.args={'actor':self.actor,'entry_date':self.b.case.day.isoformat(),'source_root_digest':self.page['source_root_digest'],'evidence_digest':'f'*64,'expected_revision':0,'confirmed':True}
 def review(self,**kw):return engine.review(self.company.pk,**{**self.args,**kw})
 def apply(self,r,**kw):return engine.apply(self.company.pk,actor=self.actor,review_id=r['review_id'],confirmed=kw.get('confirmed',True))
 def test_250_accounts_paged_without_mutation_or_truncating_source(self):
  rows=[];page=self.page
  while True:
   rows+=page['rows'];self.assertLessEqual(len(page['rows']),50);self.assertEqual(page['source_root_digest'],self.page['source_root_digest'])
   if not page['next_after']:break
   page=engine.sources(self.company.pk,actor=self.actor,after_id=page['next_after'])
  self.assertEqual(len(rows),250);self.assertEqual(len({r['account_id'] for r in rows}),250);self.assertEqual(self.page['total_debit'],'224.00');self.assertFalse(JournalEntry.plain_objects.filter(tenant=self.company).exists())
 def test_250_accounts_post_one_balanced_journal_and_unblock_actual_reports(self):
  before=list(Account.plain_objects.filter(tenant=self.company).order_by('pk').values_list('pk','initial_balance'));r=self.review();self.assertEqual(OutboxEvent.objects.filter(event_type=engine.CHUNK,aggregate_root=r['review_id']).count(),5);a=self.apply(r);self.assertEqual(a['account_count'],250);self.assertEqual(JournalEntry.plain_objects.filter(tenant=self.company).count(),1);self.assertEqual(LedgerEntry.plain_objects.filter(journal_entry_id=a['journal_id']).count(),250);report=ReportsEngine.get_trial_balance(self.company.pk,self.b.case.day);self.assertEqual(report['total_debit'],Decimal('224.00'));self.assertEqual(report['total_debit'],report['total_credit']);self.assertEqual(before,list(Account.plain_objects.filter(tenant=self.company).order_by('pk').values_list('pk','initial_balance')));self.assertTrue(old.inspect_opening(self.company.pk)['source_fields_preserved']);self.assertTrue(LedgerEngine.validate_ledger_integrity(self.company.pk)['is_valid'])
 def test_second_confirmation_and_current_review_required(self):
  with self.assertRaises(AccountingError):self.review(confirmed=False)
  r=self.review()
  with self.assertRaises(AccountingError):self.apply(r,confirmed=False)
  newer=self.review(expected_revision=1)
  with self.assertRaises(AccountingError):self.apply(r)
  self.apply(newer)
 def test_replay_and_state_do_not_duplicate_or_restore_authorization(self):
  r=self.review();a=self.apply(r);b=self.apply(r);self.assertEqual(a['journal_id'],b['journal_id']);self.assertTrue(b['replayed']);s=engine.state(self.company.pk,actor=self.actor);self.assertFalse(s['confirmations_restored']);self.assertEqual(s['applied']['journal_id'],a['journal_id'])
 def test_changed_source_and_unbalanced_reference_block_review_or_post(self):
  r=self.review();Account.plain_objects.filter(pk=self.b.equity.pk).update(initial_balance='99.00')
  with self.assertRaises(AccountingError):self.apply(r)
  page=engine.sources(self.company.pk,actor=self.actor)
  with self.assertRaises(AccountingError):self.review(expected_revision=1,source_root_digest=page['source_root_digest'])
 def test_missing_or_tampered_source_chunk_blocks_confirmation(self):
  r=self.review();OutboxEvent.objects.filter(event_type=engine.CHUNK,aggregate_root=r['review_id']).first().delete()
  with self.assertRaises(AccountingError):self.apply(r)
 def test_marker_failure_rolls_back_whole_journal_receipt_and_audit(self):
  r=self.review();create=OutboxEvent.objects.create
  def fail(**kw):
   if kw.get('event_type')==engine.APPLIED:raise RuntimeError('Synthetic opening proof failure')
   return create(**kw)
  with patch.object(OutboxEvent.objects,'create',side_effect=fail):
   with self.assertRaises(RuntimeError):self.apply(r)
  self.assertFalse(JournalEntry.plain_objects.filter(tenant=self.company).exists());self.assertFalse(AccountingEventReceipt.objects.filter(tenant=self.company).exists());self.apply(r)
 def test_review_chunk_failure_is_atomic(self):
  create=OutboxEvent.objects.create
  def fail(**kw):
   if kw.get('event_type')==engine.CHUNK and kw['payload']['index']==2:raise RuntimeError('Synthetic third chunk failure')
   return create(**kw)
  with patch.object(OutboxEvent.objects,'create',side_effect=fail):
   with self.assertRaises(RuntimeError):self.review()
  self.assertFalse(OutboxEvent.objects.filter(event_type=engine.REVIEW,payload__body__company_id=str(self.company.pk)).exists());self.assertFalse(OutboxEvent.objects.filter(event_type=engine.CHUNK,payload__company_id=str(self.company.pk)).exists());self.review()
 def test_251_accounts_fail_explicitly_without_partial_migration(self):
  Account.plain_objects.create(tenant=self.company,chart_of_accounts=self.b.case.chart,code='1509999',name='Synthetic over limit',type='ASSET',initial_balance='1.00')
  with self.assertRaises(AccountingError):engine.sources(self.company.pk,actor=self.actor)
  with self.assertRaises(AccountingError):self.review()
 def test_source_change_after_post_blocks_report_even_if_original_values_zeroed(self):
  self.apply(self.review());Account.plain_objects.filter(tenant=self.company).update(initial_balance='0.00')
  with self.assertRaises(AccountingError):ReportsEngine.get_trial_balance(self.company.pk,self.b.case.day)
 def test_contra_preserves_source_and_neutralizes_opening(self):
  a=self.apply(self.review());LedgerEngine.reverse_entry(a['journal_id'],tenant_id=self.company.pk,actor=self.actor);report=ReportsEngine.get_balance_sheet(self.company.pk,self.b.case.day);self.assertEqual(report['assets'],0);self.assertTrue(old.inspect_opening(self.company.pk)['reversed'])
 def test_reserved_namespace_cannot_bypass_opening_review(self):
  with self.assertRaises(AccountingError):LedgerEngine.post_lines(tenant_id=self.company.pk,entry_date=self.b.case.day,description='Synthetic opening bypass',actor=self.actor,idempotency_key=engine.PREFIX+str(uuid.uuid4()),lines_data=[{'account':self.b.case.asset,'debit':'1.00'},{'account':self.b.equity,'credit':'1.00'}])
 def test_original_opening_state_is_compatible_and_cannot_post_another_opening(self):
  s=old.opening_state(self.company.pk,actor=self.actor);self.assertEqual(s['opening_mode'],'CHUNKED_SOURCE');self.assertFalse(s['can_review_first_book']);r=self.review()
  with self.assertRaises(AccountingError):self.b.review()
  self.apply(r);s=old.opening_state(self.company.pk,actor=self.actor);self.assertEqual(s['applied']['journal_id'],engine.state(self.company.pk,actor=self.actor)['applied']['journal_id'])
 def test_account_code_change_after_review_blocks_posting(self):
  r=self.review();Account.plain_objects.filter(pk=self.b.case.asset.pk).update(code='1305999')
  with self.assertRaises(AccountingError):self.apply(r)
 def test_retired_account_preserves_posted_reference_and_replay(self):
  r=self.review();self.apply(r);Account.plain_objects.filter(pk=self.b.case.asset.pk).update(is_active=False,name='Retired renamed synthetic account');self.assertTrue(self.apply(r)['replayed']);self.assertEqual(ReportsEngine.get_trial_balance(self.company.pk,self.b.case.day)['total_debit'],Decimal('224.00'))
 def test_closed_period_rejects_single_atomic_opening(self):
  r=self.review();self.b.case.period.status='closed';self.b.case.period.save()
  with self.assertRaises(AccountingError):self.apply(r)
  self.assertFalse(JournalEntry.plain_objects.filter(tenant=self.company).exists())
 def test_real_scoped_api_and_corporate_manifest_contract(self):
  from rest_framework.test import APIRequestFactory,force_authenticate
  from apps.prestadores.mi_negocio.gestion_contable.contabilidad.views import PlanCuentaViewSet
  import sys
  sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'SGA-CD-BACKEND'))
  from app.services.chunked_opening_contract import validate
  def call(action,data,user=None):
   q=APIRequestFactory().post('/fixture/?provider_id='+str(self.b.case.case.provider.pk),data,format='json');force_authenticate(q,user=user or self.actor);return PlanCuentaViewSet.as_view({'post':action})(q)
  ctx={'tenant_id':str(self.company.pk),'ledger_actor_id':str(self.actor.pk)};page=call('opening_chunks_sources',{});self.assertEqual(page.status_code,200,page.data);validate('opening_chunks_sources',page.data,{},ctx);payload={k:v for k,v in self.args.items() if k!='actor'};self.assertEqual(call('review_opening_chunks',{**payload,'company_id':str(uuid.uuid4())}).status_code,400);r=call('review_opening_chunks',payload);self.assertEqual(r.status_code,200,r.data);validate('review_opening_chunks',r.data,payload,ctx);args={'review_id':r.data['review_id'],'confirmed':True};a=call('apply_opening_chunks',args);self.assertEqual(a.status_code,200,a.data);validate('apply_opening_chunks',a.data,args,ctx);state=call('opening_chunks_state',{});self.assertEqual(state.status_code,200,state.data);validate('opening_chunks_state',state.data,{},ctx)
  other=__import__('django.contrib.auth',fromlist=['get_user_model']).get_user_model().objects.exclude(pk=self.actor.pk).first()
  for action,data in [('opening_chunks_sources',{}),('review_opening_chunks',payload),('apply_opening_chunks',args),('opening_chunks_state',{})]:self.assertNotEqual(call(action,data,other).status_code,200)
  for change in [{'source_fields_preserved':False},{'source_independently_verified':True},{'money_transferred':True}]:
   with self.assertRaises(ValueError):validate('apply_opening_chunks',{**a.data,**change},args,ctx)
 def test_pending_original_review_is_superseded_without_rewriting_its_evidence(self):
  # A small first-book source may choose either workflow until chunk review exists.
  Account.plain_objects.filter(tenant=self.company,code__startswith='150').update(initial_balance='0.00');Account.plain_objects.filter(tenant=self.company,code__startswith='350').update(initial_balance='0.00');legacy=self.b.review();self.page=engine.sources(self.company.pk,actor=self.actor);r=self.review(source_root_digest=self.page['source_root_digest'])
  with self.assertRaises(AccountingError):self.b.apply(legacy)
  self.apply(r);self.assertTrue(OutboxEvent.objects.filter(pk=legacy['review_id']).exists())
 def test_orphan_chunks_cannot_be_adopted_or_reconstructed_as_new_review(self):
  r=self.review();OutboxEvent.objects.filter(pk=r['review_id']).delete()
  for call in [lambda:engine.sources(self.company.pk,actor=self.actor),lambda:engine.state(self.company.pk,actor=self.actor),lambda:self.review(),lambda:self.b.review()]:
   with self.assertRaises(AccountingError):call()
 def test_another_journal_cannot_borrow_a_valid_opening_origin(self):
  from types import SimpleNamespace
  self.apply(self.review())
  with self.assertRaises(AccountingError):engine.verify_posted_origin(self.company,SimpleNamespace(pk=uuid.uuid4(),financial_event_id=engine.PREFIX+str(uuid.uuid4())))
if __name__=='__main__':unittest.main()
