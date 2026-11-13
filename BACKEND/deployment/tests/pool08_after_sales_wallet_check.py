"""Own CRM wrappers preserve funded wallet/ledger atomicity; disposable funds only.
The financial-atomicity fixture explicitly disables hardware approvals; separate
negative checks enforce the device requirement. No physical/provider acceptance.
"""
import runpy,unittest,importlib,uuid,os
from pathlib import Path
from unittest.mock import patch
fixture=runpy.run_path(str(Path(__file__).with_name('accounting_wallet_refund_check.py')),run_name='crm_wallet_refund_fixture')
from django.db import connection
from django.test import override_settings
from api.models import BusinessUserProfile
from apps.prestadores.mi_negocio.gestion_operativa.modulos_genericos.clientes.models import Cliente
from rest_framework.test import APIRequestFactory,force_authenticate
from apps.core_erp.accounting.models import JournalEntry,LedgerEntry
from apps.wallet.services import access_policy
from decimal import Decimal
for path in ('apps.prestadores.mi_negocio.gestion_comercial.pool08','apps.admin_plataforma.gestion_comercial.pool08'):
 c=importlib.import_module(path+'.crm_models');i=importlib.import_module(path+'.identity_models')
 with connection.schema_editor() as editor:
  for m in (Cliente,BusinessUserProfile,c.CRMContact,c.CRMEvent,i.CommercialGrant,i.CommercialConsent,i.CommercialIdentityAlias,i.CommercialPolicyEvent):
   if m._meta.db_table not in connection.introspection.table_names():editor.create_model(m)
def cases(system,path):
 api=importlib.import_module(path+'.crm_api')
 class Checks(unittest.TestCase):
  def setUp(self):
   self.c=fixture['WalletRefundChecks']();self.c.setUp();self.addCleanup(self.c.doCleanups);env=patch.dict(os.environ,BACKEND_SERVICE=system);env.start();self.addCleanup(env.stop)
  def call(self,op,data):
   req=APIRequestFactory().post('/crm/?provider_id='+str(self.c.provider.pk),data,format='json');force_authenticate(req,user=self.c.actor);return api.AfterSalesView.as_view()(req,operation=op)
  def prepare(self):
   return self.call('prepare_wallet_refund',dict(reservation_id=self.c.rid,source_wallet_id=str(self.c.source.pk),destination_wallet_id=str(self.c.dest.pk),liability_line_id=str(self.c.line.pk),evidence_digest='e'*64,confirmed=True))
  def test_funded_refund_from_own_crm_is_atomic_and_idempotent(self):
   p=self.prepare();self.assertEqual(p.status_code,200,p.data);r=self.call('review_wallet_refund',dict(reservation_id=self.c.rid,device_proof=None,confirmed=True));self.assertEqual(r.status_code,200,r.data);data=dict(reservation_id=self.c.rid,confirmation=r.data['result']['confirmation'],device_proof=None,confirmed=True);a=self.call('execute_wallet_refund',data);self.assertEqual(a.status_code,200,a.data);self.assertEqual(self.c.balances(),(Decimal('10.00'),Decimal('90.00')));self.assertTrue(a.data['result']['ledger_written']);self.assertFalse(a.data['result']['bank_transfer_executed']);self.assertEqual(self.call('execute_wallet_refund',data).status_code,200);self.assertEqual(self.c.balances(),(Decimal('10.00'),Decimal('90.00')))
  def test_owner_cannot_skip_required_device_approval(self):
   self.assertEqual(self.prepare().status_code,200)
   with override_settings(WALLET_DEVICE_APPROVALS_REQUIRED=True):r=self.call('review_wallet_refund',dict(reservation_id=self.c.rid,device_proof=None,confirmed=True));self.assertIn(r.status_code,(400,403,409,503))
  def test_internal_followup_is_scoped_and_never_sends_marketing(self):
   req=APIRequestFactory().post('/crm/?provider_id='+str(self.c.provider.pk),dict(request_id=str(uuid.uuid4()),operation='create',contact_id=None,expected_revision=0,data=dict(name='Contacto de soporte',origin='AFTER_SALES',responsible_ref=str(self.c.actor.pk))),format='json');force_authenticate(req,user=self.c.actor);contact=api.CRMView.as_view()(req,section='commands').data['contact_id']
   from django.utils import timezone
   from datetime import timedelta
   payload=dict(request_id=str(uuid.uuid4()),contact_id=contact,expected_revision=1,reservation_id=self.c.rid,title='Revisar satisfacción del cliente',due_at=(timezone.now()+timedelta(days=1)).isoformat(),responsible_ref=str(self.c.actor.pk))
   r=self.call('followup',payload);self.assertEqual(r.status_code,200,r.data);self.assertFalse(r.data['outbound_message_sent']);self.assertFalse(r.data['customer_binding_verified'])
   repeated=self.call('followup',payload);self.assertEqual(repeated.status_code,200,repeated.data);self.assertTrue(repeated.data['result']['replayed'])
   duplicate=self.call('followup',{**payload,'request_id':str(uuid.uuid4()),'expected_revision':2});self.assertEqual(duplicate.status_code,409,duplicate.data);self.assertEqual(duplicate.data['code'],'FOLLOWUP_ALREADY_RECORDED')
 Checks.__name__=system.replace('-','_')+'AfterSalesWallet';return Checks
ERP=cases('erp-tur','apps.prestadores.mi_negocio.gestion_comercial.pool08');Ana=cases('analematica','apps.admin_plataforma.gestion_comercial.pool08')
if __name__=='__main__':unittest.main()
