"""Actual scoped CRM cancellation adapter in both native systems; no external refunds."""
import runpy,unittest,importlib,os,uuid
from pathlib import Path
from unittest.mock import patch
fixture=runpy.run_path(str(Path(__file__).with_name('cancellation_timing_check.py')),run_name='crm_after_sales_fixture')
# Reuse this fixture's schema creator, avoiding a second bootstrap of content types.
from django.db import connection
from api.models import BusinessUserProfile
from apps.prestadores.mi_negocio.gestion_operativa.modulos_genericos.clientes.models import Cliente
for path in ('apps.prestadores.mi_negocio.gestion_comercial.pool08','apps.admin_plataforma.gestion_comercial.pool08'):
 crm_models=importlib.import_module(path+'.crm_models');identity_models=importlib.import_module(path+'.identity_models')
 with connection.schema_editor() as editor:
  for model in (Cliente,BusinessUserProfile,crm_models.CRMContact,crm_models.CRMEvent,identity_models.CommercialGrant,identity_models.CommercialConsent,identity_models.CommercialIdentityAlias,identity_models.CommercialPolicyEvent):
   if model._meta.db_table not in connection.introspection.table_names():editor.create_model(model)
from rest_framework.test import APIRequestFactory,force_authenticate
from django.utils import timezone
from apps.core_erp.accounting.models import JournalEntry
from apps.turismo.models import VerifiedCompanyLink

def cases(system,path):
 api=importlib.import_module(path+'.crm_api')
 class Checks(unittest.TestCase):
  def setUp(self):
   self.c=fixture['TimingAndRefundChecks']();self.c.setUp();self.base=self.c.base;self.user=self.base.user;self.provider=self.base.provider;env=patch.dict(os.environ,BACKEND_SERVICE=system);env.start();self.addCleanup(env.stop)
  def call(self,op,data,user=None):
   req=APIRequestFactory().post('/crm/?provider_id='+str(self.provider.pk),data,format='json');force_authenticate(req,user=user or self.user);return api.AfterSalesView.as_view()(req,operation=op)
  def test_publish_bind_case_replay_and_exceptions_from_own_crm(self):
   from datetime import timedelta
   type(self.c.booking).plain_objects.filter(pk=self.c.booking.pk).update(start_date=(timezone.now()+timedelta(days=30)));self.c.booking.refresh_from_db()
   config=self.c.config;r=self.call('review_policy',dict(request_id=str(uuid.uuid4()),policy_id=None,expected_revision=0,values=config,confirmed=True));self.assertEqual(r.status_code,200,r.data);review=r.data['result'];r=self.call('publish_policy',dict(review_id=review['review_id'],confirmed=True));self.assertEqual(r.status_code,200,r.data);p=r.data['result'];self.assertFalse(r.data['crm_customer_binding_inferred'])
   r=self.call('bind_policy',dict(reservation_id=str(self.c.booking.pk),policy_id=p['policy_id'],policy_revision=p['revision'],accepted_at=timezone.now().isoformat(),consent_kind='ACCEPTED_AMENDMENT',consent_digest='a'*64,confirmed=True));self.assertEqual(r.status_code,200,r.data)
   r=self.call('review_case',dict(reservation_id=str(self.c.booking.pk),request_id=str(uuid.uuid4()),requested_refund='100.00',reason_code='STANDARD_CANCELLATION',evidence_digest='b'*64,expected_revision=0,confirmed=True,cancellation_at=timezone.now().isoformat()));self.assertEqual(r.status_code,200,r.data);review=r.data['result'];self.assertEqual(review['preview']['calculation']['percentage'],'5.00');self.assertEqual(review['preview']['calculation']['refund_net'],'95.00')
   payload=dict(reservation_id=str(self.c.booking.pk),review_id=review['review_id'],confirmed=True);r=self.call('confirm_case',payload);self.assertEqual(r.status_code,200,r.data);self.assertFalse(r.data['result']['money_transferred']);self.assertTrue(self.call('confirm_case',payload).data['result']['replayed'])
  def test_existing_accepted_case_state_and_no_banking_success(self):
   self.c.saved_proposal();r=self.call('case_state',{'reservation_id':str(self.c.booking.pk)});self.assertEqual(r.status_code,200,r.data);self.assertFalse(r.data['result']['money_transferred']);self.assertIsNotNone(r.data['result']['registered'])
   review=self.call('review_refund',dict(reservation_id=str(self.c.booking.pk),request_id=str(uuid.uuid4()),original_payment_reference='SYNTHETIC-ONLY',evidence_digest='e'*64,confirmed=True));self.assertEqual(review.status_code,200,review.data);r=self.call('authorize_refund',dict(reservation_id=str(self.c.booking.pk),review_id=review.data['result']['review_id'],confirmed=True));self.assertEqual(r.status_code,200,r.data);self.assertFalse(r.data['result']['money_transferred'])
  def test_forged_actor_unknown_fields_and_other_company_rejected(self):
   self.assertEqual(self.call('case_state',{'reservation_id':str(self.c.booking.pk),'actor':'forged'}).status_code,422)
   from api.models import CustomUser
   stranger=CustomUser(username='after-sales-other-'+uuid.uuid4().hex,is_active=True,role='BUSINESS_OWNER');CustomUser.objects.bulk_create([stranger])
   self.assertEqual(self.call('case_state',{'reservation_id':str(self.c.booking.pk)},user=stranger).status_code,403)
   self.assertIn(self.call('case_state',{'reservation_id':str(uuid.uuid4())}).status_code,(409,404))
  def test_revoked_company_and_unsupported_action(self):
   self.assertEqual(self.call('anything',{}).status_code,422);VerifiedCompanyLink.objects.filter(provider=self.provider).update(revoked_at=timezone.now());self.assertEqual(self.call('sources',{'policy_after':None,'reservation_after':None}).status_code,403)
 Checks.__name__=system.replace('-','_')+'AfterSales';return Checks
ERP=cases('erp-tur','apps.prestadores.mi_negocio.gestion_comercial.pool08');Ana=cases('analematica','apps.admin_plataforma.gestion_comercial.pool08')
if __name__=='__main__':unittest.main()
