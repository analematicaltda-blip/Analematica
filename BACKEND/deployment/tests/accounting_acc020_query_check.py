"""Reproducible bounded query evaluation and source contract regressions."""
import importlib.util,json,unittest,copy,sys
from pathlib import Path
from decimal import localcontext,Inexact,Rounded
root=Path(__file__).resolve().parents[3]
p=root/'BACKEND/ANALEMATICA-BACKEND/core_erp/accounting/query_assistant.py';s=importlib.util.spec_from_file_location('resolver',p);resolver=importlib.util.module_from_spec(s);s.loader.exec_module(resolver)
sys.path.insert(0,str(root/'BACKEND/SGA-CD-BACKEND'))
from app.services.accounting_query_contract import resolve,validate,QUESTIONS
class QueryEvaluation(unittest.TestCase):
 def test_both_resolvers_agree_with_versioned_synthetic_dataset(self):
  data=json.loads(Path(__file__).with_name('fixtures').joinpath('accounting_queries.json').read_text())
  self.assertEqual(data['version'],1);self.assertEqual(resolver.QUESTIONS,QUESTIONS);self.assertTrue(set(QUESTIONS)<=set(r['question'] for r in data['cases'] if isinstance(r['question'],str)))
  for row in data['cases']:
   for function in [resolve,resolver.resolve_question]:
    if row['intent'] is None:
     with self.assertRaises(ValueError):function(row['question'])
    else:self.assertEqual(function(row['question']),row['intent'])
 def test_liquidity_requires_only_explicit_cutoff_and_no_company_override(self):
  for p in [{'question':'liquidez'},{'question':'liquidez','until':'2026-01-01','tenant_id':'foreign'},{'question':'liquidez','since':'2026-01-01','until':'2026-01-02'},{'question':'liquidez','until':'20260101'}]:
   with self.assertRaises(ValueError):resolver.answer_query('unused',p)
 def test_sources_are_required_not_just_flags(self):
  data={'schema':'sgacd-accounting-query-v1','company_id':'company','read_only':True,'execution':'DETERMINISTIC_ALLOWLIST','intent':'profitability','source':'ReportsEngine.get_profitability','data':{},'generated_sql':False,'external_model_used':False,'ledger_written':False,'financial_action_authorized':False}
  with self.assertRaises(ValueError):validate(data,{'question':'rentabilidad','since':'2026-01-01','until':'2026-01-02'},{'tenant_id':'company'})
if __name__=='__main__':unittest.main(verbosity=2)
