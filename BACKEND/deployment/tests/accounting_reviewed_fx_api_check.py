"""Owner-scoped FX API and corporate response boundary using real disposable ORM."""
import copy,runpy,sys,unittest,uuid
from pathlib import Path
fixture=runpy.run_path(str(Path(__file__).with_name('accounting_bank_grouped_check.py')),run_name='fx_api_fixture')
from apps.core_erp.accounting import reviewed_fx as fx
from apps.core_erp.fx.models import Currency,FXRateTable
from apps.core_erp.accounting.journal_service import JournalService
from apps.core_erp.accounting.models import LedgerEntry
from apps.turismo.models import VerifiedCompanyLink
from django.utils import timezone
from rest_framework.test import APIRequestFactory,force_authenticate
from apps.prestadores.mi_negocio.gestion_contable.contabilidad.views import PlanCuentaViewSet
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'SGA-CD-BACKEND'))
from app.services.reviewed_fx_contract import validate
class FxApiChecks(unittest.TestCase):
 def setUp(self):
  self.base=fixture['GroupedBankChecks']();self.base.setUp();self.case=self.base.case
  for code in ['USD','EUR','COP']:Currency.objects.update_or_create(code=code,defaults={'name':'Synthetic '+code,'symbol':code,'is_active':True})
  self.entry=JournalService.create_entry(str(self.case.tenant.pk),timezone.localdate(),'Synthetic API FX',[{'account':self.case.a,'debit':'10.00'},{'account':self.case.b,'credit':'10.00'}],created_by=self.case.user,currency='USD');LedgerEntry.plain_objects.filter(journal_entry=self.entry).update(currency='USD')
  day=self.entry.date.isoformat();self.payload={'entry_id':str(self.entry.pk),'terms':{'base_currency':'USD','target_currency':'COP','rate':'4000.000000','source_reference':'synthetic:source','source_version':'v1','observed_at':timezone.now().isoformat(),'valid_from':day,'valid_until':day,'evidence_digest':'a'*64},'expected_revision':0,'confirmed':True}
  self.context={'tenant_id':str(self.case.tenant.pk),'ledger_actor_id':str(self.case.user.pk)}
 def call(self,action,payload,user=None):
  request=APIRequestFactory().post('/fixture/?provider_id='+str(self.case.provider.pk),payload,format='json');force_authenticate(request,user=user or self.case.user)
  return PlanCuentaViewSet.as_view({'post':action})(request)
 def test_real_api_review_post_recovery_and_strict_contract(self):
  state=self.call('foreign_journal_state',{'entry_id':str(self.entry.pk)});self.assertEqual(state.status_code,200,state.data);validate('foreign_journal_state',state.data,{'entry_id':str(self.entry.pk)},self.context)
  review=self.call('review_foreign_journal',self.payload);self.assertEqual(review.status_code,200,review.data);validate('review_foreign_journal',review.data,self.payload,self.context)
  payload={'entry_id':str(self.entry.pk),'review_id':review.data['review_id'],'confirmed':True};posted=self.call('post_foreign_journal',payload);self.assertEqual(posted.status_code,200,posted.data);validate('post_foreign_journal',posted.data,payload,self.context)
  state=self.call('foreign_journal_state',{'entry_id':str(self.entry.pk)});validate('foreign_journal_state',state.data,{'entry_id':str(self.entry.pk)},self.context);self.assertFalse(state.data['confirmations_restored'])
  self.assertTrue(self.call('post_foreign_journal',payload).data['replayed'])
 def test_spoofed_fields_foreign_actor_and_revocation_rejected(self):
  self.assertEqual(self.call('review_foreign_journal',{**self.payload,'company_id':str(uuid.uuid4())}).status_code,400)
  self.assertNotEqual(self.call('review_foreign_journal',self.payload,user=__import__('django.contrib.auth',fromlist=['get_user_model']).get_user_model().objects.exclude(pk=self.case.user.pk).first()).status_code,200)
  VerifiedCompanyLink.objects.filter(provider=self.case.provider).update(revoked_at=timezone.now());self.assertNotEqual(self.call('review_foreign_journal',self.payload).status_code,200)
 def test_contract_rejects_invented_conversion_or_claimed_external_verification(self):
  r=self.call('review_foreign_journal',self.payload).data
  for mutate in [lambda x:x['preview']['valuation'].update(total_debit_cop='40001.00'),lambda x:x['preview']['valuation']['lines'][0].update(base_amount='40001.00'),lambda x:x.update(rate_independently_verified=True),lambda x:x['preview']['quote'].update(source_version='wrong'),lambda x:x['preview']['source']['lines'].append(x['preview']['source']['lines'][0])]:
   bad=copy.deepcopy(r);mutate(bad)
   with self.assertRaises(ValueError):validate('review_foreign_journal',bad,self.payload,self.context)
 def test_catalog_excludes_other_actor_and_shows_pending_review(self):
  params={'after_id':None};r=self.call('foreign_journal_sources',params);self.assertEqual(r.status_code,200,r.data);validate('foreign_journal_sources',r.data,params,self.context);self.assertEqual([x['entry_id'] for x in r.data['sources']],[str(self.entry.pk)])
  self.call('review_foreign_journal',self.payload);self.assertTrue(self.call('foreign_journal_sources',params).data['sources'][0]['review_pending'])
  from django.contrib.auth import get_user_model
  other=get_user_model().objects.exclude(pk=self.case.user.pk).first()
  from apps.core_erp.accounting.models import JournalEntry
  JournalEntry.plain_objects.filter(pk=self.entry.pk).update(created_by=other)
  self.assertEqual(self.call('foreign_journal_sources',params).data['sources'],[])
 def test_catalog_cursor_is_bounded_without_duplicate_pages(self):
  for i in range(21):JournalService.create_entry(str(self.case.tenant.pk),self.entry.date,'Synthetic paged FX '+str(i),[{'account':self.case.a,'debit':'1.00'},{'account':self.case.b,'credit':'1.00'}],created_by=self.case.user,currency='USD')
  first=self.call('foreign_journal_sources',{'after_id':None}).data;self.assertEqual(len(first['sources']),20);validate('foreign_journal_sources',first,{'after_id':None},self.context)
  second=self.call('foreign_journal_sources',{'after_id':first['next_after']}).data;validate('foreign_journal_sources',second,{'after_id':first['next_after']},self.context);self.assertEqual(len(second['sources']),2);self.assertIsNone(second['next_after']);self.assertEqual(len({x['entry_id'] for x in first['sources']+second['sources']}),22)
 def test_api_rejects_unknown_source_and_missing_second_authorization(self):
  self.assertEqual(self.call('foreign_journal_state',{'entry_id':str(uuid.uuid4())}).status_code,400)
  r=self.call('review_foreign_journal',self.payload);payload={'entry_id':str(self.entry.pk),'review_id':r.data['review_id'],'confirmed':False};self.assertEqual(self.call('post_foreign_journal',payload).status_code,400)
if __name__=='__main__':unittest.main()
