"""Invoice-intent boundary: exact money, explicit tax and deterministic identity."""
import copy, importlib.util, unittest
from pathlib import Path
path=Path(__file__).resolve().parents[2]/'ANALEMATICA-BACKEND/core_erp/accounting/invoice_intent.py'
spec=importlib.util.spec_from_file_location('invoice_intent',path);engine=importlib.util.module_from_spec(spec);spec.loader.exec_module(engine)
class InvoiceIntentTests(unittest.TestCase):
    def setUp(self):
        self.company='00000000-0000-4000-8000-000000000001'
        self.value={'schema':engine.SCHEMA,'company_id':self.company,'source_type':'reservation','source_id':'00000000-0000-4000-8000-000000000002','revision':1,'state':'CONFIRMED','currency':'COP','items':[{'item_id':'00000000-0000-4000-8000-000000000003','net':'100.00','tax':'19.00','tax_category':'TAXABLE','policy_reference':'reviewed-policy:1'}]}
    def test_exact_totals_no_fiscal_or_ledger_claim(self):
        before=copy.deepcopy(self.value);r=engine.prepare_invoice_intent(self.value,self.company)
        self.assertEqual(r['payload']['totals']['gross'],'119.00');self.assertEqual(before,self.value)
        for key in ['fiscal_accepted','ledger_written','published','source_authority_verified','tax_policy_verified']:self.assertFalse(r[key])
    def test_same_revision_changed_payload_keeps_identity_changes_digest(self):
        a=engine.prepare_invoice_intent(self.value,self.company);self.value['items'][0]['net']='200.00';b=engine.prepare_invoice_intent(self.value,self.company)
        self.assertEqual(a['idempotency_key'],b['idempotency_key']);self.assertNotEqual(a['payload_digest'],b['payload_digest'])
    def test_new_revision_has_distinct_identity(self):
        a=engine.prepare_invoice_intent(self.value,self.company);self.value['revision']=2
        self.assertNotEqual(a['idempotency_key'],engine.prepare_invoice_intent(self.value,self.company)['idempotency_key'])
    def test_scope_states_and_revision(self):
        for key,value in [('company_id','00000000-0000-4000-8000-000000000009'),('state','DRAFT'),('revision',True),('revision',0),('source_type','unknown'),('currency','UNKNOWN')]:
            with self.subTest(key=key),self.assertRaises(ValueError):engine.prepare_invoice_intent({**self.value,key:value},self.company)
    def test_money_and_tax_rejections(self):
        for change in [{'net':1.0},{'net':'NaN'},{'net':'-1.00'},{'net':'0.001'},{'net':'0.00'},{'tax_category':'EXEMPT'},{'policy_reference':''},{'plaintext':'secret'}]:
            v=copy.deepcopy(self.value);v['items'][0].update(change)
            with self.subTest(change=change),self.assertRaises(ValueError):engine.prepare_invoice_intent(v,self.company)
    def test_items_bounded_and_unique(self):
        for items in [[],self.value['items']*2,self.value['items']*101]:
            with self.assertRaises(ValueError):engine.prepare_invoice_intent({**self.value,'items':items},self.company)
    def test_global_decimal_precision_cannot_round_invoice_totals(self):
        from decimal import localcontext, Inexact, Rounded
        with localcontext() as context:
            context.prec=2;context.traps[Inexact]=True;context.traps[Rounded]=True
            result=engine.prepare_invoice_intent(self.value,self.company)
        self.assertEqual(result['payload']['totals'],{'net':'100.00','tax':'19.00','gross':'119.00'})
    def test_maximum_components_keep_exact_minor_units(self):
        import uuid
        self.value['items']=[{**self.value['items'][0],'item_id':str(uuid.uuid4()),'net':'999999999999.99','tax':'0.01'} for _ in range(100)]
        result=engine.prepare_invoice_intent(self.value,self.company)
        self.assertEqual(result['payload']['totals']['gross'],'100000000000000.00')
        self.assertEqual(result['payload']['totals']['net'],'99999999999999.00')
    def test_component_order_does_not_change_digest(self):
        self.value['items'].append({**self.value['items'][0],'item_id':'00000000-0000-4000-8000-000000000004'})
        first=engine.prepare_invoice_intent(self.value,self.company);self.value['items'].reverse()
        second=engine.prepare_invoice_intent(self.value,self.company)
        self.assertEqual(first,second)
    def test_crm_and_explicit_exclusion(self):
        self.value.update(source_type='crm_opportunity',state='WON');self.value['items'][0].update(tax='0.00',tax_category='EXCLUDED')
        self.assertEqual(engine.prepare_invoice_intent(self.value,self.company)['payload']['totals']['gross'],'100.00')
if __name__=='__main__':unittest.main()
