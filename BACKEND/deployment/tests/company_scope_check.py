"""Positive and negative company selection contracts on isolated domain tables."""
import runpy,unittest,uuid
from pathlib import Path
from unittest.mock import patch
fixture=runpy.run_path(str(Path(__file__).with_name('erp_customer_check.py')),run_name='scope_fixture')
from api.models import CustomUser
from apps.turismo.models import TourismProvider
from apps.prestadores.mi_negocio.gestion_operativa.modulos_genericos.productos_servicios.models import Product
from apps.prestadores.mi_negocio.gestion_operativa.modulos_genericos.productos_servicios.views import ProductViewSet
from apps.prestadores.mi_negocio.gestion_operativa.modulos_genericos.reservas.models import PoliticaCancelacion
from apps.prestadores.mi_negocio.gestion_operativa.modulos_genericos.clientes.views import ClienteViewSet
from rest_framework.test import APIRequestFactory,force_authenticate
for model in (Product,PoliticaCancelacion):fixture['fixture']['create'](model)

class ScopeChecks(unittest.TestCase):
 def setUp(self):
  self.owner=CustomUser(username='scope-'+uuid.uuid4().hex,role='BUSINESS_OWNER');self.other=CustomUser(username='other-'+uuid.uuid4().hex,role='BUSINESS_OWNER');CustomUser.objects.bulk_create([self.owner,self.other])
  self.a=TourismProvider.objects.create(owner=self.owner,name='A',provider_type='GUIDE');self.b=TourismProvider.objects.create(owner=self.owner,name='B',provider_type='GUIDE');self.foreign=TourismProvider.objects.create(owner=self.other,name='Foreign',provider_type='GUIDE')
 def call(self,view,action,user=None,method='get',data=None,pk=None,query='',headers=None):
  request=getattr(APIRequestFactory(),method)('/isolated/'+query,data or {},format='json',**(headers or {}))
  if user:force_authenticate(request,user=user)
  return view.as_view({method:action})(request,**({'pk':pk} if pk else {}))
 def create(self,selected=None,**extra):
  return self.call(ProductViewSet,'create',self.owner,'post',{'nombre':'Synthetic product','base_price':'10.00',**extra},query='?provider_id='+str((selected or self.a).pk))
 def test_multiple_companies_require_selection_for_products_and_crm(self):
  for view in (ProductViewSet,ClienteViewSet):self.assertEqual(self.call(view,'list',self.owner).status_code,403)
 def test_explicit_owned_company_creates_and_filters_product(self):
  response=self.create();self.assertEqual(response.status_code,201,response.data);pk=response.data['id']
  product=Product.objects.get(pk=pk);self.assertEqual(product.provider_id,self.a.pk);self.assertIsNotNone(product.id_publico)
  self.assertEqual(self.call(ProductViewSet,'retrieve',self.owner,pk=pk,query='?provider_id='+str(self.b.pk)).status_code,404)
  self.assertEqual(self.call(ProductViewSet,'retrieve',self.other,pk=pk,query='?provider_id='+str(self.foreign.pk)).status_code,404)
 def test_owner_cannot_move_product_even_between_own_companies(self):
  response=self.create();pk=response.data['id']
  result=self.call(ProductViewSet,'partial_update',self.owner,'patch',{'provider':str(self.b.pk)},pk,query='?provider_id='+str(self.a.pk));self.assertEqual(result.status_code,400)
  self.assertEqual(Product.objects.get(pk=pk).provider_id,self.a.pk)
 def test_create_cannot_inject_foreign_provider(self):
  response=self.create(selected=self.a,provider=str(self.foreign.pk))
  self.assertEqual(response.status_code,400);self.assertFalse(Product.objects.filter(provider_id=self.foreign.pk).exists())
 def test_cancellation_policy_is_scoped_to_selected_company(self):
  foreign=PoliticaCancelacion.objects.create(perfil_ref_id=self.foreign.pk,nombre='Foreign',descripcion='test')
  own=PoliticaCancelacion.objects.create(perfil_ref_id=self.a.pk,nombre='Own',descripcion='test')
  self.assertEqual(self.create(cancellation_policy=foreign.pk).status_code,400)
  self.assertEqual(self.create(cancellation_policy=own.pk).status_code,201)
 def test_conflicting_invalid_and_foreign_selectors_are_rejected(self):
  cases=[('?provider_id=bad',{},400),('?provider_id='+str(self.foreign.pk),{},403),('?provider_id='+str(self.a.pk),{'HTTP_X_TENANT_ID':str(self.b.pk)},400)]
  for query,headers,status in cases:self.assertEqual(self.call(ProductViewSet,'list',self.owner,query=query,headers=headers).status_code,status)
 def test_header_context_does_not_grant_foreign_access(self):
  target='apps.prestadores.mi_negocio.gestion_operativa.modulos_genericos.permissions.get_current_tenant'
  with patch(target,return_value=self.foreign):self.assertEqual(self.call(ProductViewSet,'list',self.owner).status_code,403)
 def test_inactive_company_user_and_agent_are_denied(self):
  self.a.is_active=False;self.a.save();self.assertEqual(self.create().status_code,403)
  self.a.is_active=True;self.a.save()
  self.owner.is_active=False;self.owner.save();self.assertEqual(self.create().status_code,403)
  self.owner.is_active=True;self.owner.is_agent=True;self.owner.save();self.assertEqual(self.create().status_code,403)
 def test_superuser_role_does_not_grant_business_ownership(self):
  self.other.is_superuser=True;self.other.save()
  self.assertEqual(self.call(ProductViewSet,'list',self.other,query='?provider_id='+str(self.a.pk)).status_code,403)
 def test_crm_uses_identical_owned_company_selection(self):
  created=self.call(ClienteViewSet,'create',self.owner,'post',{'nombre':'Synthetic client','email':'client@example.test'},query='?provider_id='+str(self.b.pk));self.assertEqual(created.status_code,201,created.data)
  self.assertEqual(self.call(ClienteViewSet,'retrieve',self.owner,pk=created.data['id'],query='?provider_id='+str(self.a.pk)).status_code,404)
 def test_company_options_are_private_owned_and_do_not_grant_sso_or_financial_access(self):
  from apps.prestadores.mi_negocio.gestion_comercial.quote_views import CompanyScopeOptions
  request=APIRequestFactory().get('/scopes/')
  self.assertIn(CompanyScopeOptions.as_view()(request).status_code,(401,403))
  request=APIRequestFactory().get('/scopes/');force_authenticate(request,user=self.owner)
  response=CompanyScopeOptions.as_view()(request);self.assertEqual(response.status_code,200)
  self.assertEqual({row['provider_id'] for row in response.data['companies']},{str(self.a.pk),str(self.b.pk)})
  self.assertFalse(response.data['cross_system_sso_enabled']);self.assertFalse(response.data['financial_permissions_granted']);self.assertEqual(response['Cache-Control'],'no-store')
 def test_product_price_serialization_and_negative_price_validation(self):
  created=self.create();self.assertEqual(created.status_code,201,created.data);self.assertEqual(str(created.data['base_price']),'10.00')
  self.assertEqual(self.create(base_price='-1.00').status_code,400)
 def test_cookie_access_requires_erp_session_and_current_factor_version(self):
  import sys,types,secrets
  from django.test import override_settings
  from django.urls import path
  from django.contrib.sessions.models import Session
  from allauth.mfa.models import Authenticator
  from allauth.account.models import EmailAddress
  from apps.core_erp.models import EventAuditLog
  from apps.prestadores.mi_negocio.web_session import SessionStatus,SessionLogin
  from rest_framework.test import APIClient
  for model in (Session,Authenticator,EmailAddress,EventAuditLog):fixture['fixture']['create'](model)
  module=types.ModuleType('scope_cookie_fixture');module.urlpatterns=[path('api/session/',SessionStatus.as_view()),path('api/login/',SessionLogin.as_view()),path('api/catalog/',ProductViewSet.as_view({'get':'list','post':'create'}))];sys.modules[module.__name__]=module
  password=secrets.token_urlsafe(24);self.owner.set_password(password);self.owner.save(update_fields=['password'])
  try:
   with override_settings(ROOT_URLCONF=module.__name__,ERP_WEB_SESSION_ENABLED=True,SESSION_COOKIE_SECURE=False,CSRF_COOKIE_SECURE=False,MIDDLEWARE=['django.contrib.sessions.middleware.SessionMiddleware','django.middleware.csrf.CsrfViewMiddleware','django.contrib.auth.middleware.AuthenticationMiddleware']):
    client=APIClient(enforce_csrf_checks=True,HTTP_HOST='localhost');csrf=client.get('/api/session/').json()['data']['csrf_token']
    logged=client.post('/api/login/',{'username':self.owner.username,'password':password},format='json',HTTP_X_CSRFTOKEN=csrf);self.assertEqual(logged.status_code,200,logged.content)
    self.assertEqual(client.get('/api/catalog/?provider_id='+str(self.a.pk)).status_code,200)
    self.assertEqual(client.post('/api/catalog/?provider_id='+str(self.a.pk),{'nombre':'No CSRF','base_price':'1'},format='json').status_code,403)
    legacy=APIClient(enforce_csrf_checks=True,HTTP_HOST='localhost');legacy.force_login(self.owner,backend='django.contrib.auth.backends.ModelBackend')
    self.assertIn(legacy.get('/api/catalog/?provider_id='+str(self.a.pk)).status_code,(401,403))
    Authenticator.objects.create(user=self.owner,type='webauthn',data={})
    self.assertIn(client.get('/api/catalog/?provider_id='+str(self.a.pk)).status_code,(401,403))
  finally:sys.modules.pop(module.__name__,None)
if __name__=='__main__':unittest.main()
