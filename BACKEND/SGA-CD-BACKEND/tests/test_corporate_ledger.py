"""Dual authenticated identities, reviewed mapping and read-only ledger bridge."""
import os,uuid,unittest
from datetime import datetime,timezone,timedelta
from unittest.mock import patch
import httpx
import test_corporate_node as fixtures
from app.services import corporate_ledger as ledger
from app.models.corporate import CorporateLedgerBinding
from app.models.user import Usuario,RolesEnum
from fastapi import HTTPException
class CorporateLedgerTests(unittest.TestCase):
 setUpBase=fixtures.CorporateTests.setUp
 tearDown=fixtures.CorporateTests.tearDown
 login=fixtures.CorporateTests.login
 def setUp(self):
  self.setUpBase();self.provider=str(uuid.uuid4());self.tenant=str(uuid.uuid4());self.owner=self.db.get(Usuario,self.users['owner-admin_general']);self.operator=Usuario(inquilino_id=self.owner.inquilino_id,nombre_usuario='independent-reviewer',correo='reviewer@example.test',nombre_completo='Synthetic reviewer',rol=RolesEnum.admin_general,password_hash='test-no-login',activo=True);self.operator.roles=list(self.owner.roles);self.db.add(self.operator);self.db.commit();self.users['reviewer-admin_general']=self.operator.id
  self.review();self.login('owner-admin_general');self.client.cookies.set(ledger.COOKIE,'a'*32)
  self.env=patch.dict(os.environ,{'CORPORATE_LEDGER_ORIGIN':'http://127.0.0.1:19999'});self.env.start();self.addCleanup(self.env.stop)
 def review(self,**extra):
  args={'operator':self.operator,'owner_id':self.owner.id,'ledger_actor_id':'7','provider_id':self.provider,'tenant_id':self.tenant,'evidence_digest':'b'*64,'valid_until':datetime.now(timezone.utc)+timedelta(days=1),'apply':True};args.update(extra)
  return ledger.review_binding(self.db,**args)
 def query(self,**extra):return self.client.get('/api/v1/workspace/corporate/accounting/report',params={'report':'trial_balance','until':'2026-11-08',**extra})
 def transport(self,mode=None):
  def handle(request):
   self.assertEqual(request.method,'GET');self.assertEqual(request.headers.get('cookie'),ledger.COOKIE+'='+'a'*32);self.assertNotIn('authorization',request.headers)
   self.assertEqual(request.url.params['provider_id'],self.provider)
   if mode=='redirect':return httpx.Response(302,headers={'location':'https://unrelated.invalid'})
   if mode=='denied':return httpx.Response(403,json={'detail':'PRIVATE-UPSTREAM-DATA'})
   if request.url.path.endswith('identidad-contable/'):
    return httpx.Response(200,json={'company_id':self.tenant,'provider_id':self.provider,'actor_id':'8' if mode=='actor' else '7'})
   data={'tenant_id':self.tenant if mode!='company' else str(uuid.uuid4()),'cutoff_date':'2026-11-08','total_debit':'100.00','total_credit':'100.00','lines':[],'posted_only':True,'valuation':'base_currency'}
   if mode=='revoke':
    with self.factory() as db:
     row=db.get(CorporateLedgerBinding,1);row.revoked_at=datetime.now(timezone.utc);db.commit()
   if mode=='owner_role':
    with self.factory() as db:
     row=db.get(Usuario,self.owner.id);row.roles=[];row.rol=RolesEnum.alumno;db.commit()
   if mode=='float':data['total_debit']=100.0
   if mode=='oversize':return httpx.Response(200,content=b' '*(ledger.MAX_RESPONSE+1))
   return httpx.Response(200,json={'success':True,'data':data})
  return patch.object(ledger,'client',lambda:httpx.Client(transport=httpx.MockTransport(handle),follow_redirects=False))
 def test_verified_owner_report_and_private_headers(self):
  with self.transport():r=self.query()
  self.assertEqual(r.status_code,200,r.text);self.assertTrue(r.json()['read_only']);self.assertFalse(r.json()['ledger_written']);self.assertEqual(r.json()['data']['total_debit'],'100.00');self.assertIn('no-store',r.headers['cache-control'])
 def test_other_corporate_owner_cannot_use_binding(self):
  self.login('reviewer-admin_general')
  with patch.object(ledger,'client',side_effect=AssertionError('No upstream access')):self.assertEqual(self.query().status_code,403)
 def test_missing_erp_session_cannot_use_corporate_token_alone(self):
  self.client.cookies.clear();self.assertEqual(self.query().status_code,403)
 def test_client_cannot_override_tenant_provider_or_origin(self):
  for key in ['tenant_id','provider_id','url']:
   with patch.object(ledger,'client',side_effect=AssertionError('No upstream access')):self.assertEqual(self.query(**{key:'spoof'}).status_code,422)
 def test_reviewer_cannot_self_approve_or_overwrite_binding(self):
  with self.assertRaises(HTTPException):self.review(operator=self.owner)
  with self.assertRaises(HTTPException):self.review()
 def test_revoked_or_expired_binding_blocks_before_transport(self):
  row=self.db.get(CorporateLedgerBinding,1);row.revoked_at=datetime.now(timezone.utc);self.db.commit()
  with patch.object(ledger,'client',side_effect=AssertionError('No upstream access')):self.assertEqual(self.query().status_code,403)
  row.revoked_at=None;row.valid_until=datetime.now(timezone.utc)-timedelta(seconds=1);self.db.commit()
  with patch.object(ledger,'client',side_effect=AssertionError('No upstream access')):self.assertEqual(self.query().status_code,403)
 def test_changed_ledger_actor_and_foreign_report_rejected(self):
  for mode in ['actor','company']:
   with self.transport(mode):self.assertIn(self.query().status_code,[403,503])
 def test_redirect_not_followed_and_error_body_not_disclosed(self):
  for mode in ['redirect','denied']:
   with self.transport(mode):response=self.query()
   self.assertIn(response.status_code,[403,503]);self.assertNotIn('PRIVATE-UPSTREAM-DATA',response.text)
 def test_revocation_during_upstream_query_discards_result(self):
  with self.transport('revoke'):response=self.query()
  self.assertEqual(response.status_code,403);self.assertNotIn('total_debit',response.text)
 def test_owner_role_revoked_during_query_discards_result(self):
  with self.transport('owner_role'):response=self.query()
  self.assertEqual(response.status_code,403);self.assertNotIn('total_debit',response.text)
 def test_nonexact_money_and_oversize_response_fail_closed(self):
  for mode in ['float','oversize']:
   with self.transport(mode):self.assertEqual(self.query().status_code,503)
 def test_missing_binding_is_not_automatically_created(self):
  self.db.query(CorporateLedgerBinding).delete();self.db.commit()
  with patch.object(ledger,'client',side_effect=AssertionError('No upstream access')):self.assertEqual(self.query().status_code,503)
  self.assertIsNone(self.db.get(CorporateLedgerBinding,1))
 def test_inactive_independent_reviewer_blocks_reports(self):
  self.operator.activo=False;self.db.commit()
  with patch.object(ledger,'client',side_effect=AssertionError('No upstream access')):self.assertEqual(self.query().status_code,403)
 def test_dry_run_does_not_save_a_binding(self):
  self.db.delete(self.db.get(CorporateLedgerBinding,1));self.db.commit()
  row=self.review(apply=False);self.assertEqual(row.provider_id,self.provider)
  self.assertEqual(self.db.query(CorporateLedgerBinding).count(),0)
 def test_missing_binding_table_fails_closed(self):
  CorporateLedgerBinding.__table__.drop(self.engine)
  with patch.object(ledger,'client',side_effect=AssertionError('No upstream access')):response=self.query()
  self.assertEqual(response.status_code,503);self.assertNotIn('total_debit',response.text)
 def test_unsafe_origin_and_invalid_dates_rejected(self):
  for origin in ['http://example.org','http://user:secret@localhost','http://localhost/path','https://localhost:invalid']:
   with patch.dict(os.environ,{'CORPORATE_LEDGER_ORIGIN':origin}),self.transport():self.assertEqual(self.query().status_code,503)
  self.assertEqual(self.query(until='invalid').status_code,422)
if __name__=='__main__':unittest.main()
