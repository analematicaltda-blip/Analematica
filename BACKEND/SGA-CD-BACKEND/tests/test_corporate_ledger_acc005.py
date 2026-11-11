"""ACC005 fresh bindings and actual HTTP result suppression after revocation."""
import unittest,uuid
from datetime import datetime,timezone
from contextlib import contextmanager
from unittest.mock import patch
from fastapi import HTTPException
import test_corporate_ledger as base
import test_corporate_ledger_native_purchase as native
import test_corporate_ledger_integration as integration
from app.models.user import Usuario,RolesEnum
from app.models.corporate import CorporateLedgerBinding
from app.services import corporate_ledger as ledger
class ACC005Freshness(base.CorporateLedgerTests):
 def test_cached_owner_active_flag_is_reloaded(self):
  with self.factory() as db:
   row=db.get(Usuario,self.owner.id);row.activo=False;db.commit()
  self.assertTrue(self.owner.activo)
  with self.assertRaises(HTTPException) as result:ledger.require_binding(self.db,self.owner)
  self.assertEqual(result.exception.status_code,403)
 def test_cached_reviewer_role_cannot_provision(self):
  with self.factory() as db:
   row=db.get(Usuario,self.operator.id);row.roles=[];row.rol=RolesEnum.alumno;db.commit()
  with self.assertRaises(HTTPException) as result:self.review(apply=False)
  self.assertEqual(result.exception.status_code,403)
 def test_changed_erp_actor_blocks_result(self):
  with self.transport('actor'):response=self.query()
  self.assertEqual(response.status_code,403);self.assertNotIn('total_debit',response.text)
class ACC005HTTP(unittest.TestCase):
 setUp=native.CorporateNativePurchaseChecks.setUp
 tearDown=native.CorporateNativePurchaseChecks.tearDown
 login=native.CorporateNativePurchaseChecks.login
 command=integration.DualLedgerIntegration.command
 prepare_recognition=integration.DualLedgerIntegration.prepare_recognition
 test_revocation_before_write_dispatch_does_not_post=integration.DualLedgerIntegration.test_revocation_before_write_dispatch_does_not_post
 test_revoked_erp_session_blocks_corporate_token=integration.DualLedgerIntegration.test_revoked_erp_session_blocks_corporate_token
 def revoking_client(self,path):
  original=ledger.client;factory=self.factory
  class RacingClient:
   def __enter__(self):self.client=original();self.client.__enter__();return self
   def __exit__(self,*args):return self.client.__exit__(*args)
   def __getattr__(self,name):return getattr(self.client,name)
   @contextmanager
   def stream(self,method,url,**kwargs):
    with self.client.stream(method,url,**kwargs) as response:yield response
    if method=='POST' and url.endswith(path):
     with factory() as db:
      row=db.get(CorporateLedgerBinding,1);row.revoked_at=datetime.now(timezone.utc);db.commit()
  return RacingClient
 def test_revocation_after_actual_post_retains_effect_but_suppresses_result(self):
  body={'request_id':str(uuid.uuid4()),'name':'ACC005 synthetic committed supplier','identification':'ACC005-SYNTHETIC','evidence_digest':'a'*64,'confirmed':True}
  with patch.object(ledger,'client',self.revoking_client('registrar-proveedor-nativo/')):response=self.command('record_native_supplier',body)
  self.assertEqual(response.status_code,403,response.text);self.assertIn('puede estar registrado',response.text);self.assertNotIn('supplier_id',response.text)
  session=self.unwrap(self.erp.get('/api/v1/erp-session/').json())
  direct=self.erp.post(ledger.BASE+'proveedores-compras-nativas/',params={'provider_id':self.provider},headers={'X-CSRFToken':session['csrf_token'],'Origin':self.origin,'Referer':self.origin+'/'},json={'after_id':None});self.assertEqual(direct.status_code,200,direct.text);rows=self.unwrap(direct.json())['suppliers'];self.assertEqual(sum(row['name']==body['name'] for row in rows),1)
 def test_recovery_response_also_rechecks_binding_after_dispatch(self):
  mapping={'framework':'GRI','version':'declared-v1','disclosure':'declared-emissions','boundary':'direct_combustion','applicability_reason':'Synthetic test scope','evidence_digest':'d'*64}
  with patch.object(ledger,'client',self.revoking_client('reporte-esg/')):response=self.command('esg_report',{'since':self.day,'until':self.day,'mappings':[mapping]})
  self.assertEqual(response.status_code,403,response.text);self.assertNotIn('disclosures',response.text);self.assertIn('puede estar registrado',response.text)
if __name__=='__main__':unittest.main()
