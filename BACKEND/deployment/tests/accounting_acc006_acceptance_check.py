"""ACC006: reviewed source, validity, direction and deterministic exact valuation."""
import copy,runpy,unittest,uuid
from pathlib import Path
from decimal import Decimal,localcontext,Inexact,ROUND_DOWN
from datetime import timedelta
f=runpy.run_path(str(Path(__file__).with_name('accounting_reviewed_fx_check.py')),run_name='acc006_fixture')
from django.utils import timezone
from apps.core_erp.accounting.exceptions import AccountingError
from apps.core_erp.accounting.models import JournalEntry,LedgerEntry,AccountingAuditLog
from apps.core_erp.accounting import reviewed_fx as engine
from apps.core_erp.fx.models import Currency,FXRateTable
from apps.core_erp.fx.fx_engine import FXEngine
class ACC006Acceptance(unittest.TestCase):
 def setUp(self):self.c=f['ReviewedFxTests']();self.c.setUp()
 def test_global_catalogue_cannot_authorize_unreviewed_post(self):
  usd=Currency.objects.get(code='USD');cop=Currency.objects.get(code='COP');FXRateTable.objects.create(base_currency=usd,target_currency=cop,rate='4000.000000',effective_from=timezone.now()-timedelta(days=1),version=uuid.uuid4().int%10000000)
  with self.assertRaises(AccountingError):self.c.case.post(self.c.entry)
  self.c.entry.refresh_from_db();self.assertFalse(self.c.entry.is_posted);self.assertFalse(AccountingAuditLog.plain_objects.filter(reference_entry=self.c.entry).exists())
 def test_missing_invalid_source_currency_validity_or_float_creates_no_review(self):
  changes=[{'source_reference':''},{'source_version':''},{'evidence_digest':'x'},{'base_currency':'EUR'},{'target_currency':'USD'},{'rate':4000.0},{'rate':'NaN'},{'rate':'0.000000'},{'rate':'4000.0000001'},{'valid_until':(self.c.entry.date-timedelta(days=1)).isoformat()},{'observed_at':(timezone.now()+timedelta(days=1)).isoformat()},{'observed_at':None},{'valid_from':True}]
  for change in changes:
   with self.subTest(change=change),self.assertRaises(AccountingError):self.c.review(terms={**self.c.terms,**change})
  self.assertIsNone(engine.latest(self.c.company,str(self.c.entry.pk)));self.c.entry.refresh_from_db();self.assertFalse(self.c.entry.is_posted)
 def test_valid_reviewed_post_ignores_hostile_decimal_context(self):
  with localcontext() as ctx:
   ctx.prec=3;ctx.rounding=ROUND_DOWN;ctx.traps[Inexact]=True
   review=self.c.review();posted=self.c.confirm(review)
  self.assertEqual(posted['total_debit_cop'],'40001.23');self.assertEqual(posted['total_credit_cop'],'40001.23');self.assertEqual(posted['source_reference'],self.c.terms['source_reference']);self.assertFalse(posted['rate_independently_verified'])
 def test_explicit_reviewed_unit_rate_is_not_an_implicit_fallback(self):
  reviewed=self.c.review(terms={**self.c.terms,'rate':'1.000000'});posted=self.c.confirm(reviewed);self.assertEqual(posted['total_debit_cop'],'10.00');self.assertEqual(posted['source_reference'],self.c.terms['source_reference'])
 def test_inactive_currency_blocks_confirmation_without_posting(self):
  review=self.c.review();Currency.objects.filter(code='USD').update(is_active=False)
  with self.assertRaises(AccountingError):self.c.confirm(review)
  self.c.entry.refresh_from_db();self.assertFalse(self.c.entry.is_posted)
 def test_quote_version_cannot_be_reused_for_a_different_rate(self):
  self.c.review()
  with self.assertRaises(AccountingError):self.c.review(expected_revision=1,terms={**self.c.terms,'rate':'4001.000000'})
 def test_reference_utility_never_returns_a_missing_pair_fallback(self):
  FXRateTable.objects.all().delete()
  with self.assertRaises(ValueError):FXEngine.get_rate('USD','COP')
  self.assertEqual(FXEngine.get_rate('COP','COP'),Decimal(1))
  for version in [0,True,-1,'1']:
   with self.assertRaises(ValueError):FXEngine.get_rate('COP','COP',version)
  with self.assertRaises(ValueError):FXEngine.get_rate('BAD','BAD')
 def test_conversion_and_catalogue_input_reject_float_nonfinite_and_rounding(self):
  for amount in [1.0,True,'NaN','Infinity','0.001']:
   with self.assertRaises(ValueError):FXEngine.convert(amount,'COP','COP')
  for rate in [1.0,True,'NaN','Infinity','-1','0.0000001']:
   with self.assertRaises(ValueError):FXEngine.update_rate('USD','COP',rate)
 def test_reference_conversion_is_exact_under_hostile_context(self):
  FXRateTable.objects.all().delete();FXEngine.update_rate('USD','COP','4000.123456')
  with localcontext() as ctx:
   ctx.prec=3;ctx.traps[Inexact]=True
   self.assertEqual(FXEngine.convert('10.00','USD','COP'),Decimal('40001.23'));self.assertEqual(FXEngine.convert('-10.00','USD','COP'),Decimal('-40001.23'))
if __name__=='__main__':unittest.main()
