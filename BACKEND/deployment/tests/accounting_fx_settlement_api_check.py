"""Scoped private API and corporate bridge contracts for recorded FX cash settlement."""
import runpy,unittest,uuid,sys,copy
from pathlib import Path
f=runpy.run_path(str(Path(__file__).with_name('accounting_fx_revaluation_api_check.py')),run_name='settlement_api_fixture')
from apps.core_erp.accounting.models import Account,LedgerEntry
from apps.core_erp.accounting.ledger_engine import LedgerEngine
from apps.core_erp.accounting import fx_revaluation
from apps.turismo.models import VerifiedCompanyLink
from django.utils import timezone
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'SGA-CD-BACKEND'))
from app.services.fx_settlement_contract import validate
class SettlementApiChecks(unittest.TestCase):
 def setUp(self):
  self.b=f['RevaluationApiChecks']();self.b.setUp();self.c=self.b.case;self.clearing=Account.plain_objects.create(tenant=self.c.tenant,chart_of_accounts=self.c.chart,code='240599',name='Synthetic pending receipt',type='LIABILITY');j=LedgerEngine.post_lines(tenant_id=self.c.tenant.pk,entry_date=self.b.base.entry.date,description='Synthetic API recorded cash',actor=self.c.user,idempotency_key=str(uuid.uuid4()),lines_data=[{'account':self.c.a,'debit':'17200.00'},{'account':self.clearing,'credit':'17200.00'}]);line=LedgerEntry.plain_objects.get(journal_entry=j,account=self.c.a)
  self.payload={**self.b.payload,'cash_line_id':str(line.pk),'clearing_account_id':str(self.clearing.pk),'quantity':'4.00','evidence_digest':'b'*64,'terms':{**self.b.payload['terms'],'rate':'4300.000000','source_version':'settlement'}};self.context=self.b.base.context
 def call(self,action,data,user=None):return self.b.call(action,data,user)
 def test_catalog_review_post_replay_and_read_only_recovery(self):
  catalog=self.call('fx_settlement_catalog',{});self.assertEqual(catalog.status_code,200,catalog.data);validate('fx_settlement_catalog',catalog.data,{},self.context);r=self.call('review_fx_settlement',self.payload);self.assertEqual(r.status_code,200,r.data);validate('review_fx_settlement',r.data,self.payload,self.context);args={'review_id':r.data['review_id'],'confirmed':True};a=self.call('post_fx_settlement',args);self.assertEqual(a.status_code,200,a.data);validate('post_fx_settlement',a.data,args,self.context);self.assertEqual(a.data['realized_difference_cop'],'1200.00');state=self.call('fx_settlement_state',{'review_id':r.data['review_id']});self.assertEqual(state.status_code,200,state.data);validate('fx_settlement_state',state.data,{'review_id':r.data['review_id']},self.context);self.assertFalse(state.data['confirmations_restored']);self.assertTrue(self.call('post_fx_settlement',args).data['replayed'])
 def test_request_lookup_recovers_initial_reply_without_recreating_review(self):
  q={'request_id':self.payload['request_id']};missing=self.call('fx_settlement_request_state',q);self.assertFalse(missing.data['found']);validate('fx_settlement_request_state',missing.data,q,self.context);r=self.call('review_fx_settlement',self.payload);found=self.call('fx_settlement_request_state',q);self.assertEqual(found.data['state']['review_id'],r.data['review_id']);validate('fx_settlement_request_state',found.data,q,self.context);self.assertFalse(found.data['confirmations_restored'])
 def test_second_confirmation_strict_fields_and_unauthorized_actor(self):
  self.assertEqual(self.call('review_fx_settlement',{**self.payload,'company_id':str(uuid.uuid4())}).status_code,400);r=self.call('review_fx_settlement',self.payload);self.assertEqual(self.call('post_fx_settlement',{'review_id':r.data['review_id'],'confirmed':False}).status_code,400)
  for action,payload in [('fx_settlement_catalog',{}),('review_fx_settlement',self.payload),('post_fx_settlement',{'review_id':r.data['review_id'],'confirmed':True}),('fx_settlement_state',{'review_id':r.data['review_id']}),('fx_settlement_request_state',{'request_id':self.payload['request_id']})]:self.assertEqual(self.call(action,payload,self.c.other).status_code,403)
 def test_revoked_identity_and_unknown_source_are_rejected(self):
  self.assertEqual(self.call('review_fx_settlement',{**self.payload,'cash_line_id':str(uuid.uuid4())}).status_code,400);VerifiedCompanyLink.objects.filter(provider=self.c.provider).update(revoked_at=timezone.now());self.assertNotEqual(self.call('review_fx_settlement',self.payload).status_code,200)
 def test_contract_rejects_tampered_source_quantity_and_fake_bank_authentication(self):
  r=self.call('review_fx_settlement',self.payload).data
  for mutate in [lambda x:x['preview']['source'].update(foreign_balance='20.00'),lambda x:x['preview']['calculation'].update(remaining_foreign='7.00'),lambda x:x['preview']['cash'].update(amount_cop='18000.00'),lambda x:x.update(bank_verified=True)]:
   broken=copy.deepcopy(r);mutate(broken)
   with self.assertRaises(ValueError):validate('review_fx_settlement',broken,self.payload,self.context)
if __name__=='__main__':unittest.main()
