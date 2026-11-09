"""Exact purchases/sales with tax/withholding and real canonical ledger writes."""
import copy,runpy,unittest,uuid
from pathlib import Path
from decimal import Decimal,localcontext
from datetime import timedelta
from unittest.mock import patch
from django.utils import timezone
fixture=runpy.run_path(str(Path(__file__).with_name('accounting_reservation_recognition_check.py')),run_name='commercial_tax_fixture')
from apps.core_erp.accounting import commercial_tax_posting as engine,tax_policies
from apps.core_erp.accounting.models import Account,JournalEntry,LedgerEntry,AccountingEventReceipt,FiscalPeriod
from apps.core_erp.accounting.exceptions import AccountingError
from apps.core_erp.accounting.integrity import fingerprint
from apps.core_erp.accounting.ledger_engine import LedgerEngine
from apps.core_erp.outbox_models import OutboxEvent
from apps.prestadores.mi_negocio.gestion_contable.contabilidad.views import PlanCuentaViewSet
from rest_framework.test import APIRequestFactory,force_authenticate
class CommercialTaxChecks(unittest.TestCase):
 def setUp(self):
  self.base=fixture['RecognitionTests']();self.base.setUp();self.company=self.base.case.tenant;self.actor=self.base.case.actor
  def account(code,kind):return Account.plain_objects.create(tenant=self.company,chart_of_accounts=self.base.chart,code=code,name='Synthetic '+kind,type=kind)
  self.expense=account('510001','EXPENSE');self.input_tax=account('135001','ASSET');self.payable=account('220001','LIABILITY');self.retention=account('236001','LIABILITY')
  self.policy={'code':'PURCHASE70','jurisdiction':'CO','currency':'COP','valid_from':self.base.day.replace(month=1,day=1).isoformat(),'valid_until':self.base.day.replace(month=12,day=31).isoformat(),'rounding':'PER_COMPONENT_HALF_UP','components':[{'code':'INPUT','kind':'INPUT_TAX','rate_bps':1900,'applies_to':['TAXABLE']},{'code':'RET','kind':'WITHHOLDING','rate_bps':250,'applies_to':['TAXABLE']}]}
  self.record_policy(self.policy)
  self.fact={'document_id':str(uuid.uuid4()),'document_digest':uuid.uuid4().hex*2,'counterparty_id':str(uuid.uuid4()),'direction':'PURCHASE','entry_date':self.base.day.isoformat(),'settlement_account_id':str(self.payable.pk),'items':[{'item_id':str(uuid.uuid4()),'net':'100.00','tax_category':'TAXABLE','policy_code':self.policy['code'],'policy_revision':1,'basis_account_id':str(self.expense.pk),'tax_accounts':{'INPUT':str(self.input_tax.pk),'RET':str(self.retention.pk)}}]}
 def record_policy(self,p):
  r=tax_policies.review_policy(self.company.pk,actor=self.actor,policy=p,evidence_digest='a'*64,expected_revision=0,confirmed=True);return tax_policies.record_policy(self.company.pk,actor=self.actor,review_id=r['review_id'],confirmed=True)
 def review(self,**extra):return engine.review_fact(self.company.pk,**{'actor':self.actor,'fact':self.fact,'evidence_digest':'b'*64,'expected_revision':0,'confirmed':True,**extra})
 def post(self,r,**extra):return engine.post_fact(self.company.pk,**{'actor':self.actor,'document_id':self.fact['document_id'],'review_id':r['review_id'],'confirmed':True,**extra})
 def call(self,action,payload):
  req=APIRequestFactory().post('/fixture/?provider_id='+str(self.base.case.provider.pk),payload,format='json');force_authenticate(req,user=self.actor);return PlanCuentaViewSet.as_view({'post':action})(req)
 def test_purchase_review_no_post_and_exact_component_totals(self):
  r=self.review();self.assertFalse(r['ledger_written']);self.assertEqual(r['preview']['totals'],{'net':'100.00','tax':'19.00','withholding':'2.50','gross':'119.00','settlement':'116.50'});self.assertFalse(JournalEntry.plain_objects.filter(tenant=self.company).exists())
 def test_purchase_posts_input_tax_withholding_and_payable_once(self):
  r=self.review();a=self.post(r);b=self.post(r);self.assertEqual(a['journal_id'],b['journal_id']);self.assertTrue(b['replayed'])
  lines=LedgerEntry.plain_objects.filter(journal_entry_id=a['journal_id']);self.assertEqual(lines.get(account=self.input_tax).debit_amount,Decimal('19'));self.assertEqual(lines.get(account=self.retention).credit_amount,Decimal('2.50'));self.assertEqual(lines.get(account=self.payable).credit_amount,Decimal('116.50'));self.assertTrue(LedgerEngine.validate_ledger_integrity(self.company.pk)['is_valid'])
 def test_sale_with_multiple_output_taxes_and_withheld_asset(self):
  p=copy.deepcopy(self.policy);p['code']='SALE70';p['components'][0]['kind']='OUTPUT_TAX';p['components'][0]['code']='OUTPUT';p['components'].append({'code':'ADDITIONAL','kind':'OUTPUT_TAX','rate_bps':100,'applies_to':['TAXABLE']});self.record_policy(p)
  self.fact.update(direction='SALE',settlement_account_id=str(self.base.asset.pk));self.fact['items'][0].update(policy_code=p['code'],basis_account_id=str(self.base.revenue.pk),tax_accounts={'OUTPUT':str(self.base.tax.pk),'ADDITIONAL':str(self.retention.pk),'RET':str(self.input_tax.pk)})
  r=self.post(self.review());lines=LedgerEntry.plain_objects.filter(journal_entry_id=r['journal_id']);self.assertEqual(lines.get(account=self.base.asset).debit_amount,Decimal('117.50'));self.assertEqual(lines.get(account=self.input_tax).debit_amount,Decimal('2.50'));self.assertEqual(lines.get(account=self.retention).credit_amount,Decimal('1'))
 def test_second_confirmation_and_same_actor_are_required(self):
  r=self.review()
  with self.assertRaises(AccountingError):self.post(r,confirmed=False)
  with self.assertRaises(AccountingError):self.post(r,actor=None)
 def test_account_inactivated_after_review_blocks_post(self):
  r=self.review();Account.plain_objects.filter(pk=self.input_tax.pk).update(is_active=False)
  with self.assertRaises(AccountingError):self.post(r)
  self.assertFalse(JournalEntry.plain_objects.filter(tenant=self.company).exists())
 def test_closed_period_blocks_post(self):
  r=self.review();FiscalPeriod.plain_objects.filter(pk=self.base.period.pk).update(status='closed')
  with self.assertRaises(AccountingError):self.post(r)
 def test_policy_tampering_blocks_post(self):
  r=self.review();row=tax_policies.versions(self.company.pk,self.policy['code']).first();payload=copy.deepcopy(row.payload);payload['policy']['terms']['components'][0]['rate_bps']=1800;OutboxEvent.objects.filter(pk=row.pk).update(payload=payload)
  with self.assertRaises(AccountingError):self.post(r)
 def test_review_tamper_and_stale_review_refused(self):
  r=self.review();next_review=self.review(expected_revision=1)
  with self.assertRaises(AccountingError):self.post(r)
  row=OutboxEvent.objects.get(pk=next_review['review_id']);p=copy.deepcopy(row.payload);p['body']['fact']['items'][0]['net']='900.00';OutboxEvent.objects.filter(pk=row.pk).update(payload=p)
  with self.assertRaises(AccountingError):self.post(next_review)
 def test_expired_review_is_not_an_authorization(self):
  r=self.review()
  with patch.object(engine.timezone,'now',return_value=timezone.now()+timedelta(minutes=16)):
   with self.assertRaises(AccountingError):self.post(r)
 def test_duplicate_document_digest_cannot_be_posted_under_another_id(self):
  r=self.review();self.post(r);self.fact['document_id']=str(uuid.uuid4())
  with self.assertRaises(AccountingError):self.review()
 def test_missing_origin_proof_never_reconstructed(self):
  r=self.review();self.post(r);OutboxEvent.objects.filter(event_type=engine.POSTED,payload__company_id=str(self.company.pk)).delete()
  with self.assertRaises(AccountingError):self.post(r)
  self.assertEqual(JournalEntry.plain_objects.filter(tenant=self.company).count(),1)
 def test_missing_document_claim_rejects_recovery(self):
  r=self.review();self.post(r);OutboxEvent.objects.filter(event_type=engine.DOCUMENT,payload__company_id=str(self.company.pk)).delete()
  with self.assertRaises(AccountingError):self.post(r)
 def test_proof_failure_rolls_back_journal_and_receipt(self):
  r=self.review();original=OutboxEvent.objects.create
  def create(**kw):
   if kw.get('event_type')==engine.DOCUMENT:raise RuntimeError('Synthetic storage failure')
   return original(**kw)
  with patch.object(OutboxEvent.objects,'create',side_effect=create):
   with self.assertRaises(RuntimeError):self.post(r)
  self.assertFalse(JournalEntry.plain_objects.filter(tenant=self.company).exists());self.assertFalse(AccountingEventReceipt.objects.filter(tenant=self.company).exists());self.assertTrue(self.post(r)['ledger_written'])
 def test_wrong_account_roles_missing_mapping_and_direction_are_refused(self):
  for field,value in [('settlement_account_id',str(self.base.asset.pk)),('direction','TRANSFER')]:
   f=copy.deepcopy(self.fact);f[field]=value
   with self.assertRaises(AccountingError):self.review(fact=f)
  f=copy.deepcopy(self.fact);f['items'][0]['tax_accounts'].pop('RET')
  with self.assertRaises(AccountingError):self.review(fact=f)
 def test_input_tax_cannot_be_reinterpreted_as_a_sale_quote(self):
  with self.assertRaises(AccountingError):tax_policies.quote_policy(self.company.pk,code=self.policy['code'],revision=1,economic_date=self.base.day.isoformat(),net='100.00',tax_category='TAXABLE',direction='SALE')
 def test_excluded_component_requires_no_positive_tax_accounts(self):
  self.fact['items'][0].update(tax_category='EXCLUDED',tax_accounts={});r=self.review();self.assertEqual(r['preview']['totals']['tax'],'0.00');self.assertEqual(r['preview']['totals']['withholding'],'0.00');self.assertTrue(self.post(r)['ledger_written'])
 def test_binary_float_and_future_date_are_refused(self):
  f=copy.deepcopy(self.fact);f['items'][0]['net']=100.0
  with self.assertRaises((AccountingError,TypeError,ValueError)):self.review(fact=f)
  f=copy.deepcopy(self.fact);f['entry_date']=(self.base.day+timedelta(days=1)).isoformat()
  with self.assertRaises(AccountingError):self.review(fact=f)
 def test_decimal_precision_does_not_change_integer_tax_calculation(self):
  self.fact['items'][0]['net']='999999999999.99'
  with localcontext() as ctx:
   ctx.prec=3;r=self.review()
  self.assertEqual(r['preview']['totals']['tax'],'190000000000.00')
 def test_api_two_confirmations_and_result_recovery(self):
  r=self.call('review_commercial_tax',{'fact':self.fact,'evidence_digest':'b'*64,'expected_revision':0,'confirmed':True});self.assertEqual(r.status_code,200,r.data)
  p=self.call('post_commercial_tax',{'document_id':self.fact['document_id'],'review_id':r.data['review_id'],'confirmed':True});self.assertEqual(p.status_code,200,p.data)
  state=self.call('commercial_tax_state',{'document_id':self.fact['document_id']});self.assertEqual(state.status_code,200,state.data);self.assertEqual(state.data['posted']['journal_id'],p.data['journal_id']);self.assertFalse(state.data['confirmations_restored'])
 def reversal_review(self):return engine.review_reversal(self.company.pk,actor=self.actor,document_id=self.fact['document_id'],reason_code='CORRECTION',evidence_digest='c'*64,confirmed=True)
 def reverse(self,r,**extra):return engine.reverse_fact(self.company.pk,**{'actor':self.actor,'document_id':self.fact['document_id'],'review_id':r['review_id'],'confirmed':True,**extra})
 def test_reversal_two_reviews_exact_contra_and_replay(self):
  initial=self.review();posted=self.post(initial);r=self.reversal_review();a=self.reverse(r);b=self.reverse(r);self.assertTrue(b['replayed']);self.assertEqual(a['journal_id'],b['journal_id']);self.assertNotEqual(a['journal_id'],posted['journal_id']);self.assertTrue(self.post(initial)['reversed']);self.assertEqual(JournalEntry.plain_objects.filter(tenant=self.company).count(),2);self.assertTrue(LedgerEngine.validate_ledger_integrity(self.company.pk)['is_valid'])
 def test_reversal_second_confirmation_and_expiry(self):
  self.post(self.review());r=self.reversal_review()
  with self.assertRaises(AccountingError):self.reverse(r,confirmed=False)
  with patch.object(engine.timezone,'now',return_value=timezone.now()+timedelta(minutes=16)):
   with self.assertRaises(AccountingError):self.reverse(r)
 def test_reversal_proof_failure_rolls_back_contra(self):
  self.post(self.review());r=self.reversal_review();original=OutboxEvent.objects.create
  def create(**kw):
   if kw.get('event_type')==engine.REVERSED:raise RuntimeError('Synthetic reverse storage failure')
   return original(**kw)
  with patch.object(OutboxEvent.objects,'create',side_effect=create):
   with self.assertRaises(RuntimeError):self.reverse(r)
  self.assertEqual(JournalEntry.plain_objects.filter(tenant=self.company).count(),1);self.assertTrue(self.reverse(r)['ledger_written'])
 def test_direct_unlinked_reversal_is_not_claimed_as_reviewed(self):
  posted=self.post(self.review());r=self.reversal_review();LedgerEngine.reverse_entry(posted['journal_id'],tenant_id=self.company.pk,actor=self.actor)
  with self.assertRaises(AccountingError):self.reverse(r)
 def test_revoked_company_identity_cannot_post_via_api(self):
  from apps.turismo.models import VerifiedCompanyLink
  r=self.review();VerifiedCompanyLink.objects.filter(provider=self.base.case.provider).update(revoked_at=timezone.now());response=self.call('post_commercial_tax',{'document_id':self.fact['document_id'],'review_id':r['review_id'],'confirmed':True});self.assertEqual(response.status_code,403)
 def test_different_active_actor_cannot_use_another_review(self):
  from django.contrib.auth import get_user_model
  other=get_user_model()(username='other-tax-reviewer-'+uuid.uuid4().hex,is_active=True);get_user_model().objects.bulk_create([other]);r=self.review()
  with self.assertRaises(AccountingError):self.post(r,actor=other)
 def test_foreign_company_account_is_not_an_admissible_role(self):
  other=fixture['RecognitionTests']();other.setUp();self.fact['settlement_account_id']=str(other.tax.pk)
  with self.assertRaises(AccountingError):self.review()
 def test_multiple_components_remain_separate_and_balance(self):
  second=copy.deepcopy(self.fact['items'][0]);second.update(item_id=str(uuid.uuid4()),net='0.03');second['tax_accounts'].pop('RET');self.fact['items'].append(second);r=self.review();self.assertEqual(r['preview']['totals']['net'],'100.03');self.assertEqual(r['preview']['totals']['tax'],'19.01');self.assertTrue(self.post(r)['ledger_written']);self.assertTrue(LedgerEngine.validate_ledger_integrity(self.company.pk)['is_valid'])
 def test_receipt_digest_tampering_blocks_recovery(self):
  r=self.review();self.post(r);AccountingEventReceipt.objects.filter(tenant=self.company,event_id=engine.event_key(self.company.pk,self.fact['document_id'])).update(payload_hash='0'*64)
  with self.assertRaises(AccountingError):self.post(r)
if __name__=='__main__':unittest.main()
