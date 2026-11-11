"""Benchmark denominators, tails and failures cannot be presented as success."""
import sys,unittest
from decimal import localcontext,Inexact,Rounded,ROUND_DOWN
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from accounting_benchmark_metrics import summarize,classification_metrics,measure_attempt
class BenchmarkMetricChecks(unittest.TestCase):
 def test_nearest_rank_reports_tails_and_maximum(self):
  r=summarize([{'duration_ns':n*1000000,'ok':True} for n in range(1,101)])
  self.assertEqual((r['p50_ms'],r['p95_ms'],r['p99_ms'],r['maximum_ms']),('50.000','95.000','99.000','100.000'));self.assertTrue(r['local_target_met'])
 def test_one_slow_tail_is_not_hidden_by_average(self):
  r=summarize([{'duration_ns':1,'ok':True}]*99+[{'duration_ns':251000000,'ok':True}]);self.assertFalse(r['local_target_met']);self.assertEqual(r['maximum_ms'],'251.000')
 def test_failed_attempt_remains_in_latency_denominator(self):
  r=summarize([{'duration_ns':1000000,'ok':True},{'duration_ns':5000000,'ok':False}]);self.assertEqual(r['samples'],2);self.assertEqual(r['errors'],1);self.assertEqual(r['maximum_ms'],'5.000');self.assertFalse(r['local_target_met'])
 def test_empty_and_invalid_observations_are_rejected(self):
  for value in [[],[{'duration_ns':True,'ok':True}],[{'duration_ns':-1,'ok':True}],[{'duration_ns':1,'ok':1}]]:
   with self.assertRaises(ValueError):summarize(value)
 def test_threshold_uses_unrounded_measurement(self):
  r=summarize([{'duration_ns':250000001,'ok':True}]);self.assertEqual(r['maximum_ms'],'250.000');self.assertFalse(r['local_target_met'])
 def test_hostile_decimal_context_cannot_change_results(self):
  samples=[{'duration_ns':123456789,'ok':True},{'duration_ns':250000001,'ok':False}];rows=[{'sample_id':str(i),'expected_label':'A','predicted_label':'A' if i==0 else None,'abstained':i!=0} for i in range(3)];expected=(summarize(samples),classification_metrics(rows))
  with localcontext() as context:
   context.prec=2;context.rounding=ROUND_DOWN;context.traps[Inexact]=True;context.traps[Rounded]=True;self.assertEqual((summarize(samples),classification_metrics(rows)),expected);self.assertEqual(context.prec,2)
 def test_invalid_target_and_unbounded_duration_rejected(self):
  for target in [True,250,250.1,'NaN','Infinity','0','1e3','-1','1'*200]:
   with self.assertRaises(ValueError):summarize([{'duration_ns':1,'ok':True}],target_ms=target)
  with self.assertRaises(ValueError):summarize([{'duration_ns':2**65,'ok':True}])
 def test_failed_attempt_is_retained_without_exception_or_payload(self):
  rows={'post':[]};ticks=iter([100,500])
  def fail():raise RuntimeError('PRIVATE-DETAIL-DO-NOT-REPORT')
  self.assertEqual(measure_attempt(rows,'post',fail,clock=lambda:next(ticks)),(False,None));self.assertEqual(rows['post'],[{'duration_ns':400,'ok':False}])
 def test_coverage_separates_abstentions_and_all_abstain_is_not_perfect(self):
  r=classification_metrics([{'sample_id':'a','expected_label':'A','predicted_label':None,'abstained':True}]);self.assertEqual(r['coverage_percent'],'0.0000');self.assertIsNone(r['accepted_accuracy_percent']);self.assertEqual(r['accuracy_percent'],'0.0000');self.assertFalse(r['threshold_99_8_verified'])
 def test_missing_model_data_is_not_a_precision_claim(self):
  r=classification_metrics(None);self.assertIsNone(r['accuracy_percent']);self.assertFalse(r['threshold_99_8_verified']);self.assertEqual(r['status'],'NOT_EVALUATED')
 def test_abstention_is_not_removed_from_accuracy_denominator(self):
  r=classification_metrics([{'sample_id':'a','expected_label':'PUC1','predicted_label':'PUC1','abstained':False},{'sample_id':'b','expected_label':'PUC2','predicted_label':'PUC1','abstained':False},{'sample_id':'c','expected_label':'PUC3','predicted_label':None,'abstained':True}]);self.assertEqual((r['samples'],r['correct'],r['incorrect'],r['abstentions']),(3,1,1,1));self.assertEqual(r['accuracy_percent'],'33.3333');self.assertFalse(r['threshold_99_8_verified'])
 def test_duplicate_sample_labels_are_refused(self):
  row={'sample_id':'same','expected_label':'PUC1','predicted_label':'PUC1','abstained':False}
  with self.assertRaises(ValueError):classification_metrics([row,row])
 def test_supplied_perfect_labels_do_not_prove_model_precision(self):
  r=classification_metrics([{'sample_id':'a','expected_label':'PUC1','predicted_label':'PUC1','abstained':False}]);self.assertTrue(r['observed_accuracy_at_least_99_8']);self.assertFalse(r['model_executed']);self.assertFalse(r['threshold_99_8_verified'])
if __name__=='__main__':unittest.main()
