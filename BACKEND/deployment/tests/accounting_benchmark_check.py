"""Benchmark denominators, tails and failures cannot be presented as success."""
import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from accounting_benchmark_metrics import summarize,classification_metrics
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
