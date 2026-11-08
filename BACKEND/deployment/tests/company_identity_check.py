"""Real ORM identity-link checks in an isolated schema; no external identity claims."""
import runpy,unittest,uuid
from pathlib import Path
from datetime import timedelta
from types import SimpleNamespace
from django.test import override_settings
fixture=runpy.run_path(str(Path(__file__).with_name('provider_security_check.py')),run_name='fixture_setup')
fixture['ProviderChecks'].setUpClass()
from django.utils import timezone
from rest_framework.exceptions import APIException
from apps.core_erp.tenancy.models import Tenant
from apps.turismo.models import VerifiedCompanyLink,BusinessProfile
from apps.turismo.services.company_identity import review_link,resolve_company
from apps.wallet.models import Wallet
from apps.wallet.services.company_administrator import TourismCompanyAdministrator
from apps.wallet.services.access_policy import accessible_wallets,require_wallet_access
from api.models import CustomUser
for model in (Tenant,VerifiedCompanyLink,Wallet):fixture['create'](model)
F=SimpleNamespace(**{name:getattr(fixture['ProviderChecks'],name) for name in ('owner','other','customer','p','q')})
class CompanyChecks(unittest.TestCase):
 def setUp(self):
  self.operator=CustomUser(username='identity-reviewer-'+uuid.uuid4().hex,is_superuser=True,is_staff=True,is_active=True);CustomUser.objects.bulk_create([self.operator])
  self.provider=type(F.p).objects.create(owner=F.owner,name='Synthetic company',provider_type='GUIDE')
  tax='fixture-'+uuid.uuid4().hex
  BusinessProfile.objects.create(provider=self.provider,legal_name='Synthetic company',tax_id=tax,business_address='test',phone='test',email='test@example.test')
  self.tenant=Tenant.objects.create(name='Synthetic accounting company',tax_id=tax,state='ACTIVE')
 def review(self,**extra):
  kwargs=dict(operator=self.operator,provider_id=self.provider.pk,tenant_id=self.tenant.pk,evidence_digest='a'*64,valid_until=timezone.now()+timedelta(days=1));kwargs.update(extra);return review_link(**kwargs)
 def test_dry_run_never_provisions_or_activates(self):
  self.review();self.assertFalse(VerifiedCompanyLink.objects.filter(provider=self.provider).exists());self.assertFalse(Wallet.objects.filter(owner_id=str(self.tenant.pk)).exists())
 def test_verified_mapping_returns_distinct_real_ids(self):
  link=self.review(apply=True);self.assertEqual(resolve_company(F.owner,self.provider.pk).tenant_id,self.tenant.pk);self.assertNotEqual(link.provider_id,link.tenant_id)
 def test_employee_other_owner_and_superuser_cannot_use_company_wallet(self):
  self.review(apply=True)
  for actor in (F.other,F.customer,self.operator):
   with self.assertRaises(APIException):resolve_company(actor,self.provider.pk)
 def test_self_review_and_unprivileged_review_rejected(self):
  for operator in (F.owner,F.customer):
   with self.assertRaises(APIException):self.review(operator=operator,apply=True)
  old=F.owner.is_superuser;F.owner.is_superuser=True
  try:
   with self.assertRaises(APIException):self.review(operator=F.owner,apply=True)
  finally:F.owner.is_superuser=old
 def test_legal_identity_mismatch_cannot_link(self):
  self.tenant.tax_id='different';self.tenant.save()
  with self.assertRaises(APIException):self.review(apply=True)
 def test_revocation_and_ownership_change_are_checked_live(self):
  link=self.review(apply=True);link.revoked_at=timezone.now();link.save()
  with self.assertRaises(APIException):resolve_company(F.owner,self.provider.pk)
  link.revoked_at=None;link.save();self.provider.owner=F.other;self.provider.save()
  with self.assertRaises(APIException):resolve_company(F.owner,self.provider.pk)
 def test_joint_legal_change_does_not_reuse_old_review(self):
  self.review(apply=True);self.tenant.tax_id='new-legal-id';self.tenant.save();BusinessProfile.objects.filter(provider=self.provider).update(tax_id='new-legal-id')
  with self.assertRaises(APIException):resolve_company(F.owner,self.provider.pk)
 def test_suspended_and_expired_companies_rejected(self):
  link=self.review(apply=True);self.tenant.state='SUSPENDED';self.tenant.save()
  with self.assertRaises(APIException):resolve_company(F.owner,self.provider.pk)
  self.tenant.state='ACTIVE';self.tenant.save();link.valid_until=timezone.now()-timedelta(seconds=1);link.save()
  with self.assertRaises(APIException):resolve_company(F.owner,self.provider.pk)
 def test_existing_mapping_cannot_be_silently_reassigned(self):
  self.review(apply=True)
  with self.assertRaises(APIException):self.review(apply=True)
 def test_opt_in_wallet_adapter_rechecks_each_access(self):
  self.review(apply=True);wallet=Wallet.objects.create(owner_type='CORPORATIVO',owner_id=str(self.tenant.pk),user_id=F.customer.pk)
  with override_settings(WALLET_COMPANY_ADMIN_VERIFIER=TourismCompanyAdministrator()):
   self.assertIn(wallet,list(accessible_wallets(F.owner)));self.assertNotIn(wallet,list(accessible_wallets(F.customer)))
   VerifiedCompanyLink.objects.filter(provider=self.provider).update(revoked_at=timezone.now())
   with self.assertRaises(APIException):require_wallet_access(F.owner,wallet)
 def test_identity_api_is_read_only_private_and_has_no_legal_documents(self):
  from apps.turismo.api.provider_views import TourismProviderViewSet
  from rest_framework.test import APIRequestFactory,force_authenticate
  self.review(apply=True)
  for user,expected in ((F.owner,200),(F.customer,404),(self.operator,403)):
   request=APIRequestFactory().get('/isolated/');force_authenticate(request,user=user)
   result=TourismProviderViewSet.as_view({'get':'company_identity'})(request,pk=self.provider.pk)
   self.assertEqual(result.status_code,expected)
   if expected==200:
    self.assertEqual(result['Cache-Control'],'no-store');self.assertFalse(result.data['financial_activation']);self.assertNotIn('evidence_digest',result.data);self.assertNotIn('verified_tax_id',result.data)
 def test_invalid_evidence_and_excessive_validity_rejected(self):
  for changes in ({'evidence_digest':'not-a-digest'},{'valid_until':timezone.now()-timedelta(seconds=1)},{'valid_until':timezone.now()+timedelta(days=31)}):
   with self.assertRaises(APIException):self.review(**changes)
 def test_management_command_defaults_to_no_write(self):
  from django.core.management import call_command
  from io import StringIO
  output=StringIO()
  call_command('review_company_link',operator=self.operator.pk,provider=str(self.provider.pk),tenant=str(self.tenant.pk),evidence_sha256='a'*64,days=1,stdout=output)
  self.assertIn('VALIDATED_ONLY_NO_WRITE',output.getvalue());self.assertFalse(VerifiedCompanyLink.objects.filter(provider=self.provider).exists())
 def quote_fixture(self):
  from apps.prestadores.mi_negocio.gestion_operativa.modulos_genericos.productos_servicios.models import Product
  from apps.prestadores.mi_negocio.gestion_operativa.modulos_genericos.clientes.models import Cliente
  for model in (Product,Cliente):fixture['create'](model)
  self.review(apply=True)
  customer=Cliente.objects.create(perfil_id=self.provider.pk,nombre='Synthetic buyer',email='buyer@example.test',id_publico=uuid.uuid4())
  product=Product.objects.create(provider_id=self.provider.pk,nombre='Synthetic service',base_price='12.50',base_price_currency='COP')
  return product,{'provider_id':str(self.provider.pk),'customer_id':customer.pk,'lines':[{'product_id':str(product.pk),'quantity':2}]}
 def test_quotation_preview_uses_server_prices_without_reserving_or_charging(self):
  from apps.prestadores.mi_negocio.gestion_comercial.quote_preview import preview
  product,data=self.quote_fixture();result=preview(F.owner,data)
  self.assertEqual(result['subtotal'],'25.00');self.assertIsNone(result['payable_total']);self.assertFalse(result['stock_reserved']);self.assertFalse(result['financial_transaction_created'])
  product.refresh_from_db();self.assertEqual(product.stock,0)
 def test_quotation_rejects_client_prices_other_company_and_invalid_quantities(self):
  from copy import deepcopy
  from apps.prestadores.mi_negocio.gestion_comercial.quote_preview import preview
  product,data=self.quote_fixture()
  bad=deepcopy(data);bad['lines'][0]['unit_price']='0.01'
  with self.assertRaises(APIException):preview(F.owner,bad)
  for qty in (True,0,-1,1.5,10001):
   bad=deepcopy(data);bad['lines'][0]['quantity']=qty
   with self.assertRaises(APIException):preview(F.owner,bad)
  with self.assertRaises(APIException):preview(F.other,data)
  product.provider_id=F.q.pk;product.save()
  with self.assertRaises(APIException):preview(F.owner,data)
 def test_quotation_rejects_currency_conversion_and_revocation(self):
  from apps.prestadores.mi_negocio.gestion_comercial.quote_preview import preview
  product,data=self.quote_fixture();self.tenant.currency='USD';self.tenant.save()
  with self.assertRaises(APIException):preview(F.owner,data)
  self.tenant.currency='COP';self.tenant.save();VerifiedCompanyLink.objects.filter(provider=self.provider).update(revoked_at=timezone.now())
  with self.assertRaises(APIException):preview(F.owner,data)
 def test_quotation_http_is_private_and_nonbinding(self):
  from apps.prestadores.mi_negocio.gestion_comercial.views import QuotationPreviewView
  from rest_framework.test import APIRequestFactory,force_authenticate
  product,data=self.quote_fixture();request=APIRequestFactory().post('/isolated/',data,format='json');force_authenticate(request,user=F.owner)
  response=QuotationPreviewView.as_view()(request);self.assertEqual(response.status_code,200,response.data);self.assertEqual(response['Cache-Control'],'no-store');self.assertEqual(response.data['status'],'NON_BINDING_PREVIEW')
 def draft_fixture(self):
  from apps.turismo.models import QuotationDraft
  product,data=self.quote_fixture();fixture['create'](QuotationDraft)
  data['idempotency_key']=str(uuid.uuid4())
  return product,data
 def test_draft_persists_and_retry_keeps_original_price(self):
  from apps.prestadores.mi_negocio.gestion_comercial.quote_drafts import create_draft
  product,data=self.draft_fixture();draft,created=create_draft(F.owner,data)
  self.assertTrue(created);product.base_price='99.00';product.save()
  retry,created=create_draft(F.owner,data)
  self.assertFalse(created);self.assertEqual(draft.pk,retry.pk);self.assertEqual(retry.snapshot['subtotal'],'25.00')
 def test_draft_idempotency_rejects_changed_content(self):
  from copy import deepcopy
  from apps.prestadores.mi_negocio.gestion_comercial.quote_drafts import create_draft,DraftConflict
  from apps.turismo.models import QuotationDraft
  product,data=self.draft_fixture();draft,_=create_draft(F.owner,data)
  bad=deepcopy(data);bad['lines'][0]['quantity']=3
  with self.assertRaises(DraftConflict):create_draft(F.owner,bad)
  self.assertEqual(QuotationDraft.objects.filter(provider=self.provider).count(),1)
 def test_draft_foreign_access_and_revocation_are_rejected(self):
  from django.http import Http404
  from apps.prestadores.mi_negocio.gestion_comercial.quote_drafts import create_draft,get_draft,withdraw
  product,data=self.draft_fixture();draft,_=create_draft(F.owner,data)
  with self.assertRaises(Http404):get_draft(F.other,draft.pk)
  VerifiedCompanyLink.objects.filter(provider=self.provider).update(revoked_at=timezone.now())
  for call in (lambda:get_draft(F.owner,draft.pk),lambda:create_draft(F.owner,data),lambda:withdraw(F.owner,draft.pk,draft.snapshot_digest)):
   with self.assertRaises(APIException):call()
 def test_draft_withdrawal_is_digest_bound_repeat_safe_and_preserves_snapshot(self):
  from apps.prestadores.mi_negocio.gestion_comercial.quote_drafts import create_draft,withdraw,present,DraftConflict
  product,data=self.draft_fixture();draft,_=create_draft(F.owner,data)
  with self.assertRaises(DraftConflict):withdraw(F.owner,draft.pk,'0'*64)
  withdrawn=withdraw(F.owner,draft.pk,draft.snapshot_digest);again=withdraw(F.owner,draft.pk,draft.snapshot_digest)
  self.assertEqual(withdrawn.withdrawn_at,again.withdrawn_at);self.assertEqual(present(again)['status'],'WITHDRAWN');self.assertEqual(again.snapshot,draft.snapshot)
  product.refresh_from_db();self.assertEqual(product.stock,0)
 def test_draft_expiry_cannot_be_reset_by_retry(self):
  from apps.prestadores.mi_negocio.gestion_comercial.quote_drafts import create_draft,present
  from apps.turismo.models import QuotationDraft
  product,data=self.draft_fixture();draft,_=create_draft(F.owner,data)
  QuotationDraft.objects.filter(pk=draft.pk).update(expires_at=timezone.now()-timedelta(seconds=1))
  retry,created=create_draft(F.owner,data);self.assertFalse(created);self.assertEqual(present(retry)['status'],'EXPIRED')
 def test_draft_snapshot_alteration_is_detected(self):
  from apps.prestadores.mi_negocio.gestion_comercial.quote_drafts import create_draft,get_draft,DraftConflict
  from apps.turismo.models import QuotationDraft
  product,data=self.draft_fixture();draft,_=create_draft(F.owner,data)
  QuotationDraft.objects.filter(pk=draft.pk).update(snapshot={'subtotal':'0'})
  with self.assertRaises(DraftConflict):get_draft(F.owner,draft.pk)
 def test_draft_http_create_list_read_and_withdraw(self):
  from apps.prestadores.mi_negocio.gestion_comercial.quote_views import QuotationDraftCollection,QuotationDraftDetail,QuotationDraftWithdraw
  from rest_framework.test import APIRequestFactory,force_authenticate
  product,data=self.draft_fixture()
  def call(view,method,user=F.owner,body=None,pk=None):
   path='/isolated/?provider_id='+str(self.provider.pk)
   request=getattr(APIRequestFactory(),method)(path,body or {},format='json')
   if user:force_authenticate(request,user=user)
   return view.as_view()(request,**({'pk':pk} if pk else {}))
  created=call(QuotationDraftCollection,'post',body=data);self.assertEqual(created.status_code,201,created.data)
  self.assertEqual(call(QuotationDraftCollection,'post',body=data).status_code,200)
  pk=created.data['id'];listed=call(QuotationDraftCollection,'get');self.assertEqual(listed.status_code,200);self.assertEqual(listed.data['count'],1)
  self.assertEqual(call(QuotationDraftDetail,'get',pk=pk)['Cache-Control'],'no-store')
  self.assertEqual(call(QuotationDraftDetail,'get',user=F.other,pk=pk).status_code,404)
  self.assertEqual(call(QuotationDraftDetail,'patch',body={'snapshot':{}},pk=pk).status_code,405)
  self.assertIn(call(QuotationDraftCollection,'post',user=None,body=data).status_code,(401,403))
  result=call(QuotationDraftWithdraw,'post',body={'digest':created.data['digest']},pk=pk);self.assertEqual(result.status_code,200);self.assertEqual(result.data['status'],'WITHDRAWN')
 def test_quotation_options_are_scoped_and_discover_real_customer_and_product(self):
  from apps.prestadores.mi_negocio.gestion_comercial.quote_views import QuotationOptions
  from rest_framework.test import APIRequestFactory,force_authenticate
  product,data=self.quote_fixture()
  def call(user,query=''):
   request=APIRequestFactory().get('/isolated/'+query);force_authenticate(request,user=user)
   return QuotationOptions.as_view()(request)
  discovered=call(F.owner);self.assertEqual(discovered.status_code,200);self.assertIn({'provider_id':str(self.provider.pk),'name':self.provider.name},discovered.data['companies'])
  self.assertEqual(call(F.customer).data['companies'],[])
  options=call(F.owner,'?provider_id='+str(self.provider.pk));self.assertEqual(options.data['products'][0]['id'],str(product.pk));self.assertEqual(options.data['customers'][0]['id'],data['customer_id']);self.assertNotIn('bank_account',options.data)
  self.assertEqual(call(F.customer,'?provider_id='+str(self.provider.pk)).status_code,403)
 def test_quotation_routes_are_mounted_in_actual_url_configuration(self):
  from django.urls import resolve
  from apps.prestadores.mi_negocio.gestion_comercial.quote_views import QuotationDraftCollection,QuotationDraftDetail,QuotationDraftWithdraw,QuotationOptions
  base='/api/v1/mi-negocio/comercial/'
  for path,view in [('quotation-options/',QuotationOptions),('quotation-drafts/',QuotationDraftCollection),('quotation-drafts/'+str(uuid.uuid4())+'/',QuotationDraftDetail),('quotation-drafts/'+str(uuid.uuid4())+'/withdraw/',QuotationDraftWithdraw)]:
   self.assertIs(resolve(base+path).func.view_class,view)
 def test_customer_with_quotation_history_cannot_be_deleted(self):
  from apps.prestadores.mi_negocio.gestion_comercial.quote_drafts import create_draft
  from apps.prestadores.mi_negocio.gestion_comercial.views import ClienteViewSet
  from apps.prestadores.mi_negocio.gestion_operativa.modulos_genericos.clientes.models import Cliente
  from rest_framework.test import APIRequestFactory,force_authenticate
  product,data=self.draft_fixture();create_draft(F.owner,data)
  request=APIRequestFactory().delete('/isolated/');force_authenticate(request,user=F.owner)
  from unittest.mock import patch
  with patch('apps.prestadores.mi_negocio.gestion_operativa.modulos_genericos.permissions.get_current_tenant',return_value=self.provider):
   result=ClienteViewSet.as_view({'delete':'destroy'})(request,pk=data['customer_id'])
  self.assertEqual(result.status_code,409);self.assertTrue(Cliente.objects.filter(pk=data['customer_id']).exists())
if __name__=='__main__':unittest.main()
