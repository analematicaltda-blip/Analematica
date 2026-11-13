"""Native cookie/CSRF/TOTP CRM integration on an explicitly disposable fresh DB.
All synthetic users, companies, sessions and contacts are rolled back.
"""
import argparse,sys,unittest,uuid,secrets,os,types,time
from pathlib import Path
from datetime import timedelta
from unittest.mock import patch
parser=argparse.ArgumentParser();parser.add_argument('--directory',required=True);args=parser.parse_args()
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from fresh_local import configure
configure(args.directory,'erp-tur')
import django
django.setup()
from django.test import override_settings,Client
from django.db import transaction
from django.urls import path,include,clear_url_caches
from django.utils import timezone
from django.core.cache import cache
from api.models import CustomUser
from apps.turismo.models import TourismProvider,BusinessProfile
from apps.turismo.services.company_identity import review_link
from apps.core_erp.tenancy.models import Tenant
from allauth.mfa.totp.internal.auth import TOTP,generate_totp_secret,hotp_value,format_hotp_value
from allauth.mfa import app_settings
from django.conf import settings

def cases(system,package):
 class Checks(unittest.TestCase):
  def setUp(self):
   self.atomic=transaction.atomic();self.atomic.__enter__();self.addCleanup(lambda: (transaction.set_rollback(True),self.atomic.__exit__(None,None,None)))
   module=types.ModuleType('crm_session_'+system.replace('-','_'));module.urlpatterns=[path('api/v1/crm-test/',include(package+'.urls'))];sys.modules[module.__name__]=module
   env=patch.dict(os.environ,{'BACKEND_SERVICE':system});env.start();self.addCleanup(env.stop)
   configured=override_settings(ROOT_URLCONF=module.__name__,ERP_WEB_SESSION_ENABLED=True,SESSION_COOKIE_NAME=system+'_test_session',CSRF_COOKIE_NAME=system+'_test_csrf',SESSION_COOKIE_SECURE=True,CSRF_COOKIE_SECURE=True)
   configured.enable();self.addCleanup(configured.disable);clear_url_caches();cache.clear()
   suffix=uuid.uuid4().hex;self.password=secrets.token_urlsafe(24)
   self.owner=CustomUser(username='crm-session-'+suffix,role='BUSINESS_OWNER',is_active=True);self.owner.set_password(self.password)
   reviewer=CustomUser(username='reviewer-'+suffix,is_superuser=True,is_active=True);CustomUser.objects.bulk_create([self.owner,reviewer])
   self.provider=TourismProvider.objects.create(owner=self.owner,name='Synthetic consented laboratory',provider_type='GUIDE')
   company=Tenant.objects.create(name='Laboratory',tax_id=suffix,state='ACTIVE')
   BusinessProfile.objects.create(provider=self.provider,legal_name='Laboratory',tax_id=suffix,business_address='Synthetic',phone='Synthetic',email='fixture@example.test')
   review_link(operator=reviewer,provider_id=self.provider.pk,tenant_id=company.pk,evidence_digest='a'*64,valid_until=timezone.now()+timedelta(days=1),apply=True)
   self.client=Client(enforce_csrf_checks=True,HTTP_HOST='localhost');self.prefix='/api/v1/crm-test/crm/'
  def get(self,tail):return self.client.get(self.prefix+tail,secure=True)
  def body(self,response):
   self.assertIn(response.status_code,(200,202));raw=response.json();return raw['data'] if raw.get('success') is True else raw
  def post(self,tail,data,csrf):return self.client.post(self.prefix+tail,data,content_type='application/json',HTTP_X_CSRFTOKEN=csrf,HTTP_ORIGIN='https://localhost',secure=True)
  def test_native_session_csrf_and_totp_gate_crm(self):
   secret=generate_totp_secret();TOTP.activate(self.owner,secret)
   state=self.body(self.get('session/status/'))
   denied=self.post('session/login/',{'username':self.owner.username,'password':self.password},'bad-csrf');self.assertEqual(denied.status_code,403)
   state=self.body(self.post('session/login/',{'username':self.owner.username,'password':self.password},state['csrf_token']))
   self.assertTrue(state['mfa_required']);self.assertFalse(state['authenticated'])
   self.assertIn(self.get('companies/').status_code,(401,403))
   code=format_hotp_value(hotp_value(secret,int(time.time())//app_settings.TOTP_PERIOD))
   state=self.body(self.post('session/mfa/',{'challenge_id':state['challenge_id'],'code':code},state['csrf_token']))
   self.assertTrue(state['authenticated']);self.assertTrue(self.body(self.get('companies/'))['companies'])
   state=self.body(self.get('session/status/'))  # Browser reload must refresh the CSRF token.
   contact=dict(request_id=str(uuid.uuid4()),operation='create',contact_id=None,expected_revision=0,data=dict(name='Cookie CRM',origin='NATIVE_SESSION',responsible_ref=str(self.owner.pk)))
   tail='commands/?provider_id='+str(self.provider.pk)
   self.assertEqual(self.post(tail,contact,'bad-csrf').status_code,403)
   self.assertEqual(self.body(self.post(tail,contact,state['csrf_token']))['revision'],1)
   state=self.body(self.post('session/logout/',{},state['csrf_token']));self.assertFalse(state['authenticated'])
   self.assertIn(self.get('companies/').status_code,(401,403))
  def test_disabled_session_and_institutional_service_remain_closed(self):
   with override_settings(ERP_WEB_SESSION_ENABLED=False):self.assertEqual(self.get('session/status/').status_code,503)
   with patch.dict(os.environ,{'BACKEND_SERVICE':'turismo'}):self.assertEqual(self.get('session/status/').status_code,404)
 return Checks
suite=unittest.TestSuite()
for system,package in [('erp-tur','apps.prestadores.mi_negocio.gestion_comercial.pool08'),('analematica','apps.admin_plataforma.gestion_comercial.pool08')]:suite.addTests(unittest.defaultTestLoader.loadTestsFromTestCase(cases(system,package)))
if __name__=='__main__':raise SystemExit(not unittest.TextTestRunner(verbosity=2).run(suite).wasSuccessful())
