"""The full review cannot omit generation, command-staff or historical failures."""
import importlib.util,json,tempfile,unittest,sys
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[4]
def load(name,path):
 spec=importlib.util.spec_from_file_location(name,ROOT/path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
class AuditContracts(unittest.TestCase):
 def test_full_profile_contains_every_task_test_family_without_duplicate_ids(self):
  runner=load('audit_runner_test','BACKEND/INTEGRACIONES/operacion/verify_local.py');audit=load('audit_mapping_test','BACKEND/INTEGRACIONES/operacion/commercial_audit.py')
  with tempfile.TemporaryDirectory() as tmp:jobs=runner.suites(['commercial-audit'],sys.executable,Path(tmp),Path(tmp))
  names=[v[0] for v in jobs];self.assertEqual(len(names),len(set(names)))
  for prefixes in audit.PREFIXES:self.assertTrue(any(name.startswith(prefixes) for name in names),prefixes)
  for name in ['pool08_generation_native','pool08_generation_sga','pool08_generation_http','pool08_army_native','pool08_army_sga','commercial_staff_truth','commercial_audit_contract']:self.assertIn(name,names)
 def test_review_does_not_convert_present_sources_into_acceptance(self):
  audit=load('audit_evaluation_test','BACKEND/INTEGRACIONES/operacion/commercial_audit.py');r=audit.evaluate();self.assertEqual(len(r['tasks']),24);self.assertFalse(r['quality']['provided']);self.assertEqual(len(r['quality']['missing_mapped_tests']),24);self.assertFalse(r['production_enabled']);self.assertEqual(r['new_progress_credit'],0)
  for task in r['tasks']:
   self.assertFalse(task['source_presence_awards_credit']);self.assertFalse(task['mapped_test_scope_complete']);self.assertTrue(all(p['present'] for p in task['source_observations']),task['id'])
 def test_identity_maps_owned_access_module_and_tests(self):
  audit=load('audit_identity_mapping','BACKEND/INTEGRACIONES/operacion/commercial_audit.py')
  self.assertEqual(audit.MODULES[1],'access_admin');self.assertEqual(audit.PREFIXES[1],('pool08_access_',))
 def test_all_credited_milestones_have_distinct_ordinals_and_historical_review(self):
  audit=load('audit_credit_review','BACKEND/INTEGRACIONES/operacion/commercial_audit.py');result=audit.evaluate();credits=result['credited_milestones_review']
  self.assertEqual(len(credits),result['progress']['completed_milestones']);self.assertEqual([c['ordinal'] for c in credits],list(range(1,len(credits)+1)))
  self.assertEqual([c['milestone_id'] for c in credits],result['progress']['completed_milestone_ids']);self.assertFalse(result['quality']['current_regression_qualified']);self.assertEqual(len(result['remaining_plan_steps']),37)
  self.assertTrue(all(c['historical_artifacts_verified'] for c in credits));self.assertFalse(any(c['current_related_regression_passed'] for c in credits));self.assertTrue(all(not c['functional_scope_independently_reaccepted'] for c in credits))
 def test_current_hash_alone_cannot_qualify_failed_skipped_or_duplicate_suites(self):
  import copy
  audit=load('audit_qualification','BACKEND/INTEGRACIONES/operacion/commercial_audit.py');q={'local_checks_complete':True,'source_stable':True,'source_digest_before':'current','source_digest_after':'current','results':[{'id':'one','status':'PASSED','skipped':0}]}
  self.assertTrue(audit.qualify_report(q,'current'))
  variants=[{'local_checks_complete':False},{'source_stable':False},{'source_digest_before':'old'},{'results':[]},{'results':[{'id':'one','status':'FAILED'}]},{'results':[{'id':'one','status':'PASSED','skipped':1}]},{'results':[{'id':'one','status':'PASSED','log_truncated':True}]},{'results':q['results']*2}]
  for changes in variants:
   with self.subTest(changes=changes):self.assertFalse(audit.qualify_report({**copy.deepcopy(q),**changes},'current'))
 def test_historical_quality_changed_after_registry_anchor_is_rejected(self):
  audit=load('audit_historical_anchor','BACKEND/INTEGRACIONES/operacion/commercial_audit.py');runner=load('audit_anchor_runner','BACKEND/INTEGRACIONES/operacion/verify_local.py');plan=json.loads((ROOT/'ANALISIS/gestion-comercial/plan-pool08.json').read_text());ref=plan['tasks'][1]['milestones'][1]['evidence'][0];original=audit.safe_blob
  def changed(path):return b'{}' if str(path).endswith('/quality/report.json') else original(path)
  with patch.object(audit,'safe_blob',side_effect=changed):
   with self.assertRaisesRegex(ValueError,'HISTORICAL_QUALITY_HASH_MISMATCH'):audit.historical_quality(ref,runner)
 def test_embedded_contract_report_is_not_claimed_as_raw_logs(self):
  audit=load('audit_inline_history','BACKEND/INTEGRACIONES/operacion/commercial_audit.py');rows=audit.evaluate()['credited_milestones_review'][:3]
  self.assertTrue(all(c['historical_evidence'][0]['mode']=='HASHED_REGISTRY_EMBEDDED_REPORT_ONLY' for c in rows));self.assertTrue(all(not c['historical_evidence'][0]['raw_logs_verified'] for c in rows))
 def test_historical_quality_cannot_escape_repository(self):
  audit=load('audit_history_path','BACKEND/INTEGRACIONES/operacion/commercial_audit.py')
  for name in ('../outside','/etc/hosts'):
   with self.assertRaises(ValueError):audit.safe_blob(name)
 def test_missing_or_tampered_quality_cannot_be_used(self):
  audit=load('audit_tampering_test','BACKEND/INTEGRACIONES/operacion/commercial_audit.py')
  with tempfile.TemporaryDirectory() as tmp:
   with self.assertRaises((OSError,ValueError,KeyError)):audit.evaluate(Path(tmp))
if __name__=='__main__':unittest.main(verbosity=2)
