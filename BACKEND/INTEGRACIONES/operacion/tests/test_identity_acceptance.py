"""Acceptance cannot be manufactured by passing tests or editing JSON declarations."""
import importlib.util,json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[4]
spec=importlib.util.spec_from_file_location('identity_acceptance_test',ROOT/'BACKEND/INTEGRACIONES/operacion/commercial_identity_acceptance.py')
gate=importlib.util.module_from_spec(spec);spec.loader.exec_module(gate)
class AcceptanceChecks(unittest.TestCase):
 def entry(self):
  plan=json.loads((ROOT/'ANALISIS/gestion-comercial/plan-pool08.json').read_text());ref=plan['tasks'][1]['milestones'][1]['evidence'][0];entry=json.loads((ROOT/ref['artifact']).read_text())
  for key in ref['entry'].split('.'):entry=entry[key]
  return entry
 def test_current_real_repository_is_blocked_without_legitimate_acceptance(self):
  result=gate.evaluate();self.assertIn(result['gate'],('BLOCKED_LOCAL_EVIDENCE','BLOCKED_EXTERNAL_ACCEPTANCE'));self.assertFalse(result['acceptance_complete']);self.assertEqual(result['new_progress_credit'],0);self.assertFalse(result['permissions_changed']);self.assertEqual(result['gate']=='BLOCKED_EXTERNAL_ACCEPTANCE',result['local_evidence']['identity_sources_current']);self.assertEqual(len(result['external_review']),5)
 def test_rewritten_quality_cannot_pass_even_with_all_passed_claim(self):
  entry=self.entry();entry['quality']={**entry['quality'],'sha256':'0'*64}
  with self.assertRaisesRegex(ValueError,'QUALITY_HASH_MISMATCH'):gate.review_quality(ROOT,entry)
 def test_source_changed_after_verified_tests_is_reported(self):
  original=gate.blob
  def modified(root,path):
   raw=original(root,path)
   return raw+b'\n# changed\n' if str(path)=='BACKEND/SGA-CD-BACKEND/app/commercial/pool08/identity.py' else raw
  with patch.object(gate,'blob',side_effect=modified):
   result=gate.review_quality(ROOT,self.entry());self.assertFalse(result['identity_sources_current']);self.assertIn('BACKEND/SGA-CD-BACKEND/app/commercial/pool08/identity.py',result['changed_sources'])
 def test_altered_log_is_rejected(self):
  original=gate.blob
  def altered(root,path):
   return b'OK fabricated' if str(path).endswith('pool08_access_http.log') else original(root,path)
  with patch.object(gate,'blob',side_effect=altered):
   with self.assertRaisesRegex(ValueError,'QUALITY_ARTIFACT_ALTERED'):gate.review_quality(ROOT,self.entry())
 def test_missing_quality_stops_readiness(self):
  with patch.object(gate,'review_quality',side_effect=FileNotFoundError):
   result=gate.evaluate();self.assertEqual(result['gate'],'BLOCKED_LOCAL_EVIDENCE');self.assertFalse(result['acceptance_complete'])
 def test_external_declarations_do_not_auto_accept(self):
  result=gate.evaluate();self.assertTrue(all(row['state']=='NOT_INDEPENDENTLY_VERIFIED' for row in result['external_review']));self.assertFalse(result['production_enabled']);self.assertFalse(result['publication_performed'])
 def test_paths_and_symlinks_cannot_read_outside_root(self):
  with tempfile.TemporaryDirectory() as folder:
   root=Path(folder);(root/'escape').symlink_to('/etc/hosts')
   for name in ('../outside','/etc/hosts','escape'):
    with self.assertRaises(ValueError):gate.blob(root,name)
 def test_command_has_no_acceptance_override(self):
  import subprocess,sys
  response=subprocess.run([sys.executable,str(ROOT/'BACKEND/INTEGRACIONES/operacion/commercial_identity_acceptance.py'),'--accept'],capture_output=True,text=True)
  self.assertNotEqual(response.returncode,0)
 def test_crm_cannot_skip_identity_acceptance(self):
  with patch.object(gate,'review_quality',return_value={'identity_sources_current':True}):result=gate.evaluate(task_id='GC-003')
  self.assertEqual(result['gate'],'BLOCKED_DEPENDENCY_AND_EXTERNAL_ACCEPTANCE');self.assertEqual(result['dependencies_without_acceptance'],['GC-002']);self.assertEqual(result['milestone_id'],'GCH-009');self.assertFalse(result['acceptance_complete']);self.assertEqual(result['new_progress_credit'],0)
 def test_crm_uses_actual_crm_regression_not_just_identity_tests(self):
  result=gate.evaluate(task_id='GC-003');self.assertEqual(set(result['local_evidence']['suite_ids']),gate.CRM_JOBS);self.assertEqual(result['local_evidence']['artifact_integrity_verified'],True);self.assertEqual(result['local_evidence_origin_task'],'GC-002')
 def test_crm_checklist_contains_every_acceptance_journey(self):
  result=gate.evaluate(task_id='GC-003');self.assertEqual({r['id'] for r in result['external_review']},{'CRM_'+name for name in gate.CRM_CASES});self.assertTrue(all(r['state']=='NOT_INDEPENDENTLY_VERIFIED' for r in result['external_review']))
 def test_stale_sources_block_acceptance_even_when_tests_passed(self):
  for task in ('GC-002','GC-003'):
   with self.subTest(task=task),patch.object(gate,'review_quality',return_value={'identity_sources_current':False,'changed_sources':['changed.py']}):
    result=gate.evaluate(task_id=task);self.assertEqual(result['gate'],'BLOCKED_LOCAL_EVIDENCE');self.assertEqual(result['local_blocker'],'IDENTITY_SOURCES_CHANGED_AFTER_TESTS');self.assertFalse(result['acceptance_complete']);self.assertEqual(result['new_progress_credit'],0)
 def test_another_task_cannot_be_silently_evaluated_as_identity(self):
  with self.assertRaisesRegex(ValueError,'UNSUPPORTED_ACCEPTANCE_TASK'):gate.evaluate(task_id='GC-024')
if __name__=='__main__':unittest.main(verbosity=2)
