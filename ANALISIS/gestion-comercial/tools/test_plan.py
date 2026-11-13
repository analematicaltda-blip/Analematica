"""Prevent invented credit, denominator drift, and premature commercial closure."""
import copy
import importlib.util
import json
from pathlib import Path
from decimal import getcontext
import unittest
s=importlib.util.spec_from_file_location('commercial_plan',Path(__file__).with_name('update_plan.py'));tool=importlib.util.module_from_spec(s);s.loader.exec_module(tool)
class PlanChecks(unittest.TestCase):
 def setUp(self):
  self.plan=json.loads((tool.DIRECTORY/'plan-pool08.json').read_text())
  for task in self.plan['tasks']:
   task['state']='PENDIENTE_DE_NIVELACION'
   for row in task['milestones']:row.update(state='PENDIENTE_DE_ACREDITACION',evidence=[])
 def test_partial_increment_does_not_credit_any_milestone(self):
  self.plan['tasks'][0]['verified_increment']='Many passing partial tests'
  result=tool.measure(self.plan);self.assertEqual(result['completed_milestones'],0)
 def test_complete_declared_and_checked_task_has_three_credits(self):
  task=self.plan['tasks'][0];task['state']='COMPLETADA';seen=[]
  for row in task['milestones']:row.update(state='VERIFICADO',evidence=[{'fixture':'not a production proof'}])
  result=tool.measure(self.plan,checker=lambda reference,task,mid:seen.append((task,mid)))
  self.assertEqual(len(seen),3);self.assertEqual(result['fully_accepted_tasks'],1);self.assertEqual(result['credited_milestone_percent'],'4.17')
 def test_missing_or_duplicate_scope_is_rejected(self):
  self.plan['tasks'].pop()
  with self.assertRaises(ValueError):tool.measure(self.plan)
 def test_duplicate_milestone_is_rejected(self):
  self.plan['tasks'][1]['milestones'][0]['id']='GCH-001'
  with self.assertRaises(ValueError):tool.measure(self.plan)
 def test_unsubstantiated_credit_is_rejected(self):
  self.plan['tasks'][0]['milestones'][0]['state']='VERIFICADO'
  with self.assertRaises(ValueError):tool.measure(self.plan)
 def test_no_credit_for_tests_before_functionality(self):
  self.plan['tasks'][0]['milestones'][1].update(state='VERIFICADO',evidence=[{}])
  with self.assertRaises(ValueError):tool.measure(self.plan,checker=lambda *args:None)
 def test_closed_task_requires_all_stages(self):
  self.plan['tasks'][0]['state']='COMPLETADA'
  with self.assertRaises(ValueError):tool.measure(self.plan)
 def test_local_stages_do_not_require_false_external_acceptance(self):
  import tempfile,hashlib
  from unittest.mock import patch
  evidence={'systems':sorted(tool.SYSTEMS),'verified_task_ids':['GC-003'],'accepted_task_ids':[],
            'accepted_milestones':['GCH-007','GCH-008'],'functional_scope_complete':True,'tests_complete':True,'acceptance_complete':False}
  with tempfile.TemporaryDirectory() as directory:
   root=Path(directory);(root/'proof.json').write_text(json.dumps({'entry':evidence}))
   ref={'artifact':'proof.json','entry':'entry','entry_sha256':hashlib.sha256(tool.canonical(evidence)).hexdigest()}
   with patch.object(tool,'ROOT',root):
    tool.check_evidence(ref,'GC-003','GCH-007');tool.check_evidence(ref,'GC-003','GCH-008')
    with self.assertRaises(ValueError):tool.check_evidence(ref,'GC-003','GCH-009')
 def test_partial_functionality_cannot_credit_local_stage(self):
  import tempfile,hashlib
  from unittest.mock import patch
  evidence={'systems':sorted(tool.SYSTEMS),'verified_task_ids':['GC-003'],'accepted_task_ids':[],
            'accepted_milestones':['GCH-007'],'functional_scope_complete':False,'tests_complete':True,'acceptance_complete':False}
  with tempfile.TemporaryDirectory() as directory:
   root=Path(directory);(root/'proof.json').write_text(json.dumps({'entry':evidence}))
   ref={'artifact':'proof.json','entry':'entry','entry_sha256':hashlib.sha256(tool.canonical(evidence)).hexdigest()}
   with patch.object(tool,'ROOT',root):
    with self.assertRaises(ValueError):tool.check_evidence(ref,'GC-003','GCH-007')
 def test_decimal_global_precision_cannot_change_percentage(self):
  old=getcontext().prec
  try:
   getcontext().prec=2
   task=self.plan['tasks'][0];task['state']='COMPLETADA'
   for row in task['milestones']:row.update(state='VERIFICADO',evidence=[{}])
   self.assertEqual(tool.measure(self.plan,checker=lambda *args:None)['credited_milestone_percent'],'4.17')
  finally:getcontext().prec=old
if __name__=='__main__':unittest.main(verbosity=2)
