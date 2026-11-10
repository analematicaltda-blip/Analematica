"""Prevent silent denominator changes and unearned milestone credits."""
import copy,csv,json,unittest
from update_progress import calculate,HERE

class ProgressTests(unittest.TestCase):
    def setUp(self):
        self.registry=json.loads((HERE/'progress-registry.json').read_text())
        with (HERE/'matriz-pools.csv').open(newline='') as stream:self.rows=list(csv.DictReader(stream))
    def test_baseline_has_no_full_acceptance_or_production_claim(self):
        result=calculate(self.registry,self.rows)
        self.assertEqual(result['completed_milestones'],48)
        self.assertEqual(result['implementation_percent'],'66.67')
        self.assertEqual(result['fully_accepted_items'],0)
        self.assertFalse(result['production_ready'])
    def test_esg_increment_adds_only_two_credits_to_previous_cut(self):
        before=copy.deepcopy(self.registry)
        task=next(row for row in before['items'] if row['id']=='ACC-019')
        self.assertFalse(task['milestones']['full_acceptance'])
        task['milestones']['functional_increment']=[]
        task['milestones']['automated_verification']=[]
        result=calculate(before,self.rows)
        self.assertEqual(result['completed_milestones'],46)
        self.assertEqual(result['implementation_percent'],'63.89')
        self.assertEqual(result['fully_accepted_items'],0)
    def test_fronts_partition_existing_milestones_without_double_count(self):
        result=calculate(self.registry,self.rows)
        self.assertEqual(sum(r['completed_milestones'] for r in result['fronts']),result['completed_milestones'])
        self.assertEqual(sum(r['total_milestones'] for r in result['fronts']),72)
        self.assertEqual(len([i for r in result['fronts'] for i in r['items']]),24)
    def test_missing_task_cannot_inflate_denominator(self):
        with self.assertRaises(ValueError):calculate(self.registry,self.rows[:-1])
    def test_duplicate_or_missing_task_rejected(self):
        self.registry['items'][1]=copy.deepcopy(self.registry['items'][0])
        with self.assertRaises(ValueError):calculate(self.registry,self.rows)
    def test_tests_without_implementation_rejected(self):
        self.registry['items'][0]['milestones']['functional_increment']=[]
        with self.assertRaises(ValueError):calculate(self.registry,self.rows)
    def test_nonexistent_or_external_evidence_rejected(self):
        for ref in ['no-such-accounting-evidence','../../etc/passwd']:
            with self.subTest(ref=ref):
                data=copy.deepcopy(self.registry);data['items'][0]['milestones']['functional_increment']=[ref]
                with self.assertRaises(ValueError):calculate(data,self.rows)
    def test_evidence_duplicates_do_not_increase_score(self):
        before=calculate(self.registry,self.rows)['completed_milestones']
        self.registry['items'][0]['milestones']['functional_increment']*=3
        self.assertEqual(calculate(self.registry,self.rows)['completed_milestones'],before)

if __name__=='__main__':unittest.main()
