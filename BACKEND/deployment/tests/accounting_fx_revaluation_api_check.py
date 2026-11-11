"""Owner API and corporate contract for ledger-backed monetary FX true-up."""
import copy,runpy,unittest,sys,uuid
from pathlib import Path
fixture=runpy.run_path(str(Path(__file__).with_name('accounting_reviewed_fx_api_check.py')),run_name='fx_revaluation_api_fixture')
from apps.core_erp.accounting.models import Account
from apps.core_erp.accounting.journal_service import JournalService
from apps.core_erp.accounting import reviewed_fx
from apps.turismo.models import VerifiedCompanyLink
from django.utils import timezone
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'SGA-CD-BACKEND'))
from app.services.fx_revaluation_contract import validate
class RevaluationApiChecks(unittest.TestCase):
 def setUp(self):
  self.base=fixture['FxApiChecks']();self.base.setUp();self.case=self.base.case
  self.monetary=Account.plain_objects.create(tenant=self.case.tenant,chart_of_accounts=self.case.chart,code='111099',name='Synthetic dedicated USD',type='ASSET')
  self.loss=Account.plain_objects.create(tenant=self.case.tenant,chart_of_accounts=self.case.chart,code='530599',name='Synthetic FX loss',type='EXPENSE')
  initial=JournalService.create_entry(str(self.case.tenant.pk),self.base.entry.date,'Synthetic USD monetary source',[{'account':self.monetary,'debit':'10.00'},{'account':self.case.b,'credit':'10.00'}],created_by=self.case.user,currency='USD')
  r=reviewed_fx.review(self.case.tenant.pk,actor=self.case.user,entry_id=str(initial.pk),terms=self.base.payload['terms'],expected_revision=0,confirmed=True);reviewed_fx.confirm(self.case.tenant.pk,actor=self.case.user,entry_id=str(initial.pk),review_id=r['review_id'],confirmed=True)
  self.payload={'request_id':str(uuid.uuid4()),'account_id':str(self.monetary.pk),'currency':'USD','as_of':self.base.entry.date.isoformat(),'terms':{**self.base.payload['terms'],'rate':'4200.000000','source_version':'2'},'gain_account_id':str(self.case.b.pk),'loss_account_id':str(self.loss.pk),'monetary_classification':'MONETARY_DECLARED','confirmed':True}
 def call(self,action,payload,user=None):return self.base.call(action,payload,user=user)
 def test_actual_api_catalog_review_post_and_recovery_contract(self):
  catalog=self.call('fx_revaluation_catalog',{});self.assertEqual(catalog.status_code,200,catalog.data);validate('fx_revaluation_catalog',catalog.data,{},self.base.context)
  r=self.call('review_fx_revaluation',self.payload);self.assertEqual(r.status_code,200,r.data);validate('review_fx_revaluation',r.data,self.payload,self.base.context)
  post={'review_id':r.data['review_id'],'confirmed':True};a=self.call('post_fx_revaluation',post);self.assertEqual(a.status_code,200,a.data);validate('post_fx_revaluation',a.data,post,self.base.context);self.assertEqual(a.data['difference_cop'],'2000.00')
  state=self.call('fx_revaluation_state',{'review_id':r.data['review_id']});self.assertEqual(state.status_code,200,state.data);validate('fx_revaluation_state',state.data,{'review_id':r.data['review_id']},self.base.context);self.assertFalse(state.data['confirmations_restored']);self.assertTrue(self.call('post_fx_revaluation',post).data['replayed'])
 def test_api_never_accepts_company_override_revoked_link_or_unknown_review(self):
  self.assertEqual(self.call('review_fx_revaluation',{**self.payload,'company_id':str(uuid.uuid4())}).status_code,400)
  self.assertEqual(self.call('fx_revaluation_state',{'review_id':str(uuid.uuid4())}).status_code,400)
  VerifiedCompanyLink.objects.filter(provider=self.case.provider).update(revoked_at=timezone.now());self.assertNotEqual(self.call('review_fx_revaluation',self.payload).status_code,200)
 def test_contract_rejects_false_balance_quote_adjustment_and_external_claims(self):
  r=self.call('review_fx_revaluation',self.payload).data
  for mutate in [lambda x:x['preview']['source'].update(foreign_balance='20.00'),lambda x:x['preview']['source']['records'][0].update(amount_base='50000.00'),lambda x:x['preview']['calculation'].update(difference_cop='3000.00'),lambda x:x.update(rate_independently_verified=True),lambda x:x['preview']['terms'].update(rate='4100.000000')]:
   bad=copy.deepcopy(r);mutate(bad)
   with self.assertRaises(ValueError):validate('review_fx_revaluation',bad,self.payload,self.base.context)
 def test_second_confirmation_and_mixed_cop_origin_rejected(self):
  r=self.call('review_fx_revaluation',self.payload);self.assertEqual(self.call('post_fx_revaluation',{'review_id':r.data['review_id'],'confirmed':False}).status_code,400)
  self.assertEqual(self.call('review_fx_revaluation',{**self.payload,'request_id':str(uuid.uuid4()),'account_id':str(self.case.a.pk)}).status_code,400)
if __name__=='__main__':unittest.main()
