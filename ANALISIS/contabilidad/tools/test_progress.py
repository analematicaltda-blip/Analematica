"""Prevent silent denominator changes and unearned milestone credits."""
import copy,csv,json,unittest
from update_progress import calculate,HERE

class ProgressTests(unittest.TestCase):
    def setUp(self):
        self.registry=json.loads((HERE/'progress-registry.json').read_text())
        with (HERE/'matriz-pools.csv').open(newline='') as stream:self.rows=list(csv.DictReader(stream))
    def test_current_acceptance_does_not_claim_production(self):
        result=calculate(self.registry,self.rows)
        self.assertEqual(result['completed_milestones'],57)
        self.assertEqual(result['implementation_percent'],'79.17')
        self.assertEqual(result['fully_accepted_items'],9)
        self.assertFalse(result['production_ready'])
    def test_preserved_pre_acceptance_cut_is_48_of_72(self):
        previous=copy.deepcopy(self.registry)
        next(row for row in previous['items'] if row['id']=='ACC-010')['milestones']['full_acceptance']=[]
        for row in previous['items']:row['milestones']['full_acceptance']=[]
        result=calculate(previous,self.rows)
        self.assertEqual(result['completed_milestones'],48)
        self.assertEqual(result['implementation_percent'],'66.67')
        self.assertEqual(result['fully_accepted_items'],0)
    def test_first_acceptance_cut_remains_49_of_72(self):
        previous=copy.deepcopy(self.registry)
        next(row for row in previous['items'] if row['id']=='ACC-010')['milestones']['full_acceptance']=[]
        for row in previous['items']:
            if row['id'] in ['ACC-002','ACC-003','ACC-004','ACC-005','ACC-006','ACC-007','ACC-008']:row['milestones']['full_acceptance']=[]
        result=calculate(previous,self.rows)
        self.assertEqual(result['completed_milestones'],49)
        self.assertEqual(result['implementation_percent'],'68.06')
        self.assertEqual(result['fully_accepted_items'],1)
    def test_second_acceptance_cut_remains_50_of_72(self):
        previous=copy.deepcopy(self.registry)
        next(row for row in previous['items'] if row['id']=='ACC-010')['milestones']['full_acceptance']=[]
        for row in previous['items']:
            if row['id'] in ['ACC-003','ACC-004','ACC-005','ACC-006','ACC-007','ACC-008']:row['milestones']['full_acceptance']=[]
        result=calculate(previous,self.rows)
        self.assertEqual(result['completed_milestones'],50)
        self.assertEqual(result['implementation_percent'],'69.44')
        self.assertEqual(result['fully_accepted_items'],2)
    def test_third_acceptance_cut_remains_51_of_72(self):
        previous=copy.deepcopy(self.registry)
        next(row for row in previous['items'] if row['id']=='ACC-010')['milestones']['full_acceptance']=[]
        for row in previous['items']:
            if row['id'] in ['ACC-004','ACC-005','ACC-006','ACC-007','ACC-008']:row['milestones']['full_acceptance']=[]
        result=calculate(previous,self.rows)
        self.assertEqual(result['completed_milestones'],51)
        self.assertEqual(result['implementation_percent'],'70.83')
        self.assertEqual(result['fully_accepted_items'],3)
    def test_fourth_acceptance_cut_remains_52_of_72(self):
        previous=copy.deepcopy(self.registry)
        next(row for row in previous['items'] if row['id']=='ACC-010')['milestones']['full_acceptance']=[]
        for row in previous['items']:
            if row['id'] in ['ACC-005','ACC-006','ACC-007','ACC-008']:row['milestones']['full_acceptance']=[]
        result=calculate(previous,self.rows)
        self.assertEqual(result['completed_milestones'],52)
        self.assertEqual(result['implementation_percent'],'72.22')
        self.assertEqual(result['fully_accepted_items'],4)
    def test_fifth_acceptance_cut_remains_53_of_72(self):
        previous=copy.deepcopy(self.registry)
        next(row for row in previous['items'] if row['id']=='ACC-010')['milestones']['full_acceptance']=[]
        for row in previous['items']:
            if row['id'] in ['ACC-006','ACC-007','ACC-008']:row['milestones']['full_acceptance']=[]
        result=calculate(previous,self.rows)
        self.assertEqual(result['completed_milestones'],53)
        self.assertEqual(result['implementation_percent'],'73.61')
        self.assertEqual(result['fully_accepted_items'],5)
    def test_sixth_acceptance_cut_remains_54_of_72(self):
        previous=copy.deepcopy(self.registry)
        next(row for row in previous['items'] if row['id']=='ACC-010')['milestones']['full_acceptance']=[]
        for row in previous['items']:
            if row['id'] in ['ACC-007','ACC-008']:row['milestones']['full_acceptance']=[]
        result=calculate(previous,self.rows)
        self.assertEqual(result['completed_milestones'],54)
        self.assertEqual(result['implementation_percent'],'75.00')
        self.assertEqual(result['fully_accepted_items'],6)
    def test_seventh_acceptance_cut_remains_55_of_72(self):
        previous=copy.deepcopy(self.registry)
        next(row for row in previous['items'] if row['id']=='ACC-010')['milestones']['full_acceptance']=[]
        next(row for row in previous['items'] if row['id']=='ACC-008')['milestones']['full_acceptance']=[]
        result=calculate(previous,self.rows)
        self.assertEqual(result['completed_milestones'],55)
        self.assertEqual(result['implementation_percent'],'76.39')
        self.assertEqual(result['fully_accepted_items'],7)
    def test_eighth_acceptance_cut_remains_56_of_72_with_dian_open(self):
        previous=copy.deepcopy(self.registry)
        next(row for row in previous['items'] if row['id']=='ACC-010')['milestones']['full_acceptance']=[]
        result=calculate(previous,self.rows)
        self.assertEqual(result['completed_milestones'],56)
        self.assertEqual(result['implementation_percent'],'77.78')
        self.assertEqual(result['fully_accepted_items'],8)
        self.assertFalse(next(row for row in self.registry['items'] if row['id']=='ACC-009')['milestones']['full_acceptance'])
    def test_esg_increment_adds_only_two_credits_to_previous_cut(self):
        before=copy.deepcopy(self.registry)
        for row in before['items']:row['milestones']['full_acceptance']=[]
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

    def test_percentage_does_not_inherit_decimal_rounding_or_traps(self):
        from decimal import localcontext,Inexact,Rounded,ROUND_DOWN
        expected=calculate(self.registry,self.rows)
        with localcontext() as context:
            context.prec=2;context.rounding=ROUND_DOWN
            context.traps[Inexact]=True;context.traps[Rounded]=True
            self.assertEqual(calculate(self.registry,self.rows),expected)

    def test_all72_ids_are_stable_and_each_has_evidence_or_reason(self):
        result=calculate(self.registry,self.rows)
        milestones=result['milestones']
        self.assertEqual([m['number'] for m in milestones],list(range(1,73)))
        self.assertEqual([m['id'] for m in milestones],[f'H{i:03d}' for i in range(1,73)])
        self.assertEqual(sum(m['credited'] for m in milestones),57)
        for m in milestones:
            self.assertEqual(m['credited'],bool(m['evidence']))
            self.assertTrue(m['criterion'])
            if not m['credited']:self.assertTrue(m['remaining'])
        self.assertEqual([m['number'] for m in milestones if not m['credited']],[27,33,36,39,42,45,48,51,54,57,60,63,66,69,72])

    def test_registry_and_matrix_order_do_not_renumber_milestones(self):
        expected=calculate(self.registry,self.rows)
        self.registry['items'].reverse()
        self.assertEqual(calculate(self.registry,list(reversed(self.rows))),expected)

    def test_unknown_task_ids_rejected_before_group_indexing(self):
        self.registry['items'][0]['id']='ACC-999'
        self.rows[0]['id']='ACC-999'
        with self.assertRaises(ValueError):calculate(self.registry,self.rows)

if __name__=='__main__':unittest.main()
