"""Real Django registry and HTTP boundaries against an isolated in-memory database."""
import os,sys,unittest,base64
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'BACKEND/deployment'),str(ROOT/'BACKEND/SGA-TUR-BAKEND')]
service=os.environ.get('CHECK_SERVICE','erp-tur');assert service in {'erp-tur','turismo'}
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
import tempfile
keys=tempfile.TemporaryDirectory();key=rsa.generate_private_key(public_exponent=65537,key_size=2048)
p=Path(keys.name);(p/'private.pem').write_bytes(key.private_bytes(serialization.Encoding.PEM,serialization.PrivateFormat.PKCS8,serialization.NoEncryption()));(p/'public.pem').write_bytes(key.public_key().public_bytes(serialization.Encoding.PEM,serialization.PublicFormat.SubjectPublicKeyInfo))
os.environ.update(BACKEND_SERVICE=service,DJANGO_SETTINGS_MODULE='tourism_settings',DATABASE_URL='sqlite:///:memory:',DJANGO_ALLOWED_HOSTS='localhost,127.0.0.1,testserver',DJANGO_SECRET_KEY='isolated-check-not-a-deployed-key',DJANGO_FIELD_ENCRYPTION_KEY=Fernet.generate_key().decode(),REDIS_URL='redis://127.0.0.1:6379/15',JWT_PRIVATE_KEY_PATH=str(p/'private.pem'),JWT_PUBLIC_KEY_PATH=str(p/'public.pem'))
os.environ['DJANGO_JWT_PRIVATE_KEY_B64']=base64.b64encode((p/'private.pem').read_bytes()).decode()
os.environ['DJANGO_JWT_PUBLIC_KEY_B64']=base64.b64encode((p/'public.pem').read_bytes()).decode()
os.environ['PYTHON_DOTENV_DISABLED']='1'
os.environ.pop('OPENAI_API_KEY',None)
os.environ.pop('GEMINI_API_KEY',None);os.environ.pop('OLLAMA_ENDPOINT',None)
import django
django.setup()
from django.conf import settings
settings.EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend'
from django.core.management import call_command
from django.db import connection
from django.test import RequestFactory
from django.http import JsonResponse
from rest_framework.test import APIClient,APIRequestFactory,force_authenticate
from types import SimpleNamespace

class RuntimeChecks(unittest.TestCase):
 def test_system_checks(self):call_command('check',fail_level='WARNING')
 def test_health(self):
  r=APIClient(HTTP_HOST='localhost').get('/healthz');self.assertEqual(r.status_code,200);self.assertEqual(r.json()['service'],service)
 def test_financial_boundary_auth_and_no_writes(self):
  paths=['compras/proveedores/','compras/facturas/1/pagar/','compras/generar-pago-masivo/','proyectos/','presupuesto/','reportes/estado-resultados/']
  for path in paths:self.assertIn(APIClient(HTTP_HOST='localhost').post('/api/v1/mi-negocio/contable/'+path,{},format='json').status_code,[401,403])
  client=APIClient(HTTP_HOST='localhost');client.force_authenticate(SimpleNamespace(is_authenticated=True,pk=999,id=999))
  def refuse(*args,**kwargs):raise AssertionError('Unavailable financial endpoint issued SQL')
  with connection.execute_wrapper(refuse):
   for path in paths:
    response=client.post('/api/v1/mi-negocio/contable/'+path,{},format='json');self.assertEqual(response.status_code,503,path);self.assertEqual(response.json()['errors'][0]['code'],'module_not_enabled')
 def test_ai_optional_no_dummy(self):
  from apps.prestadores.mi_negocio.gestion_comercial.ai.services.ai_manager.ai_manager import ai_manager,AIProviderUnavailable
  self.assertEqual(ai_manager.providers,[])
  with self.assertRaises(AIProviderUnavailable):ai_manager.execute_text_generation('No external call','none')
  from apps.prestadores.mi_negocio.gestion_comercial.marketing.views import AIRewriteEmailView
  request=APIRequestFactory().post('/isolated',{'text':'Test'},format='json');force_authenticate(request,user=SimpleNamespace(is_authenticated=True,pk=999,id=999));self.assertEqual(AIRewriteEmailView.as_view()(request).status_code,503)
 def test_provider_header_cannot_authorize_anonymous(self):
  from apps.prestadores.mi_negocio.gestion_operativa.modulos_genericos.permissions import TenantMiddleware,get_current_tenant
  request=RequestFactory().get('/',HTTP_X_TENANT_ID='00000000-0000-0000-0000-000000000001');request.user=SimpleNamespace(is_authenticated=False)
  def refuse(*args,**kwargs):raise AssertionError('Anonymous selection queried tenant data')
  with connection.execute_wrapper(refuse):self.assertEqual(TenantMiddleware(lambda r:JsonResponse({}))(request).status_code,401)
  self.assertIsNone(get_current_tenant())
 def test_provider_context_cleared_on_exception_and_foreign_profile_ignored(self):
  from apps.prestadores.mi_negocio.gestion_operativa.modulos_genericos.permissions import TenantMiddleware,get_current_tenant
  provider=SimpleNamespace(pk='provider-a',owner_id=11);user=SimpleNamespace(pk=11,is_authenticated=True,perfil_prestador=provider);request=RequestFactory().get('/');request.user=user
  def fail(r):
   self.assertEqual(get_current_tenant(),provider);raise ValueError('isolated failure')
  with self.assertRaises(ValueError):TenantMiddleware(fail)(request)
  self.assertIsNone(get_current_tenant());user.perfil_prestador=SimpleNamespace(pk='foreign',owner_id=22)
  def check(r):self.assertIsNone(get_current_tenant());return JsonResponse({})
  self.assertEqual(TenantMiddleware(check)(request).status_code,200)
 def test_legacy_route_alias(self):
  if service!='turismo':return
  from django.urls import resolve
  a=resolve('/api/v1/sales/plans/');b=resolve('/api/comercial/plans/');self.assertEqual(a.func.cls,b.func.cls);self.assertNotEqual(a.namespace,b.namespace)

if __name__=='__main__':unittest.main()
