"""Password + server session + CSRF using real Django middleware, no forced auth."""
import runpy,unittest,secrets,types,sys
from pathlib import Path
fixture=runpy.run_path(str(Path(__file__).with_name('provider_security_check.py')),run_name='session_fixture')
fixture['ProviderChecks'].setUpClass()
from apps.turismo.models import ErpSecurityEvent,ErpLoginChallenge,ErpTotpUsage,ErpTotpEnrollment
from django.contrib.sessions.models import Session
from allauth.account.models import EmailAddress
from allauth.mfa.models import Authenticator
from django.test import override_settings
from django.urls import path
from django.core.cache import cache
from rest_framework.test import APIClient
from apps.prestadores.mi_negocio.web_session import SessionStatus,SessionLogin,SessionLogout,SessionMfa,SessionRecovery,RecoveryIssue,SessionSecurityEvents,EnrollmentStart,EnrollmentConfirm,EnrollmentCancel
for model in (ErpSecurityEvent,Session,Authenticator,EmailAddress,ErpTotpUsage,ErpLoginChallenge,ErpTotpEnrollment):fixture['create'](model)
module=types.ModuleType('erp_session_fixture_urls')
module.urlpatterns=[path('api/v1/erp-session/',SessionStatus.as_view()),path('api/v1/erp-session/login/',SessionLogin.as_view()),path('api/v1/erp-session/logout/',SessionLogout.as_view()),path('api/v1/erp-session/security-events/',SessionSecurityEvents.as_view()),path('api/v1/erp-session/recovery/issue/',RecoveryIssue.as_view()),path('api/v1/erp-session/recovery/',SessionRecovery.as_view()),path('api/v1/erp-session/mfa/',SessionMfa.as_view()),path('api/v1/erp-session/enrollment/start/',EnrollmentStart.as_view()),path('api/v1/erp-session/enrollment/confirm/',EnrollmentConfirm.as_view()),path('api/v1/erp-session/enrollment/cancel/',EnrollmentCancel.as_view())]
sys.modules[module.__name__]=module
class SessionChecks(unittest.TestCase):
 def setUp(self):
  override=override_settings(ROOT_URLCONF=module.__name__,ERP_WEB_SESSION_ENABLED=True,ERP_TOTP_ENROLLMENT_ENABLED=True,MIDDLEWARE=['django.contrib.sessions.middleware.SessionMiddleware','django.middleware.csrf.CsrfViewMiddleware','django.contrib.auth.middleware.AuthenticationMiddleware'],SESSION_COOKIE_HTTPONLY=True,CSRF_COOKIE_HTTPONLY=True,SESSION_COOKIE_SECURE=False,CSRF_COOKIE_SECURE=False)
  override.enable();self.addCleanup(override.disable);cache.clear()
  self.owner=fixture['ProviderChecks'].owner;self.password=secrets.token_urlsafe(24);self.owner.set_password(self.password);self.owner.save(update_fields=['password']);Authenticator.objects.filter(user=self.owner).delete();ErpTotpEnrollment.objects.filter(user=self.owner).delete()
  self.client=APIClient(enforce_csrf_checks=True,HTTP_HOST='localhost')
 def status(self):return self.client.get('/api/v1/erp-session/').json()['data']
 def login(self,csrf=None,password=None):return self.client.post('/api/v1/erp-session/login/',{'username':self.owner.username,'password':password or self.password},format='json',HTTP_X_CSRFTOKEN=csrf or '')
 def test_feature_is_closed_by_default(self):
  with override_settings(ERP_WEB_SESSION_ENABLED=False):self.assertEqual(self.client.get('/api/v1/erp-session/').status_code,503)
 def test_login_requires_csrf_even_before_authentication(self):
  self.assertEqual(self.login().status_code,403);self.assertEqual(self.login(csrf='wrong').status_code,403);self.assertFalse(self.status()['authenticated'])
 def test_password_login_and_httponly_session(self):
  csrf=self.status()['csrf_token'];response=self.login(csrf);self.assertEqual(response.status_code,200,response.content);data=response.json()['data'];self.assertTrue(data['authenticated']);self.assertEqual(data['user']['id'],self.owner.pk);self.assertNotIn('access',data);self.assertNotIn('refresh',data)
  from django.conf import settings
  self.assertTrue(response.cookies[settings.SESSION_COOKIE_NAME]['httponly']);self.assertEqual(response.cookies[settings.SESSION_COOKIE_NAME]['path'],'/api/');self.assertTrue(self.status()['authenticated']);self.assertLessEqual(self.client.session.get_expiry_age(),900)
 def test_bad_password_does_not_create_authenticated_session(self):
  self.assertIn(self.login(self.status()['csrf_token'],password='synthetic-wrong-password').status_code,(401,403));self.assertFalse(self.status()['authenticated'])
 def test_mfa_enrollment_cannot_be_bypassed(self):
  Authenticator.objects.create(user=self.owner,type='webauthn',data={})
  self.assertEqual(self.login(self.status()['csrf_token']).status_code,403);self.assertFalse(self.status()['authenticated'])
 def test_logout_requires_csrf_and_invalidates_session(self):
  self.assertEqual(self.login(self.status()['csrf_token']).status_code,200)
  self.assertEqual(self.client.post('/api/v1/erp-session/logout/',{},format='json').status_code,403)
  csrf=self.status()['csrf_token'];result=self.client.post('/api/v1/erp-session/logout/',{},format='json',HTTP_X_CSRFTOKEN=csrf)
  self.assertEqual(result.status_code,200,result.content);self.assertFalse(self.status()['authenticated'])
 def test_login_rotates_csrf_and_old_session_identifier(self):
  from django.conf import settings
  initial=self.status();old_csrf=self.client.cookies[settings.CSRF_COOKIE_NAME].value
  anonymous=self.client.session;anonymous.save();old_session=anonymous.session_key
  self.assertEqual(self.login(initial['csrf_token']).status_code,200)
  self.assertNotEqual(self.client.cookies[settings.CSRF_COOKIE_NAME].value,old_csrf)
  self.assertNotEqual(self.client.cookies[settings.SESSION_COOKIE_NAME].value,old_session)
  other=APIClient(enforce_csrf_checks=True,HTTP_HOST='localhost');other.cookies[settings.SESSION_COOKIE_NAME]=old_session
  self.assertFalse(other.get('/api/v1/erp-session/').json()['data']['authenticated'])
 def test_cross_origin_login_is_rejected_even_with_csrf_token(self):
  csrf=self.status()['csrf_token']
  response=self.client.post('/api/v1/erp-session/login/',{'username':self.owner.username,'password':self.password},format='json',HTTP_X_CSRFTOKEN=csrf,HTTP_ORIGIN='https://untrusted.example')
  self.assertEqual(response.status_code,403);self.assertFalse(self.status()['authenticated'])
 def test_new_mfa_enrollment_invalidates_this_web_access(self):
  self.assertEqual(self.login(self.status()['csrf_token']).status_code,200)
  Authenticator.objects.create(user=self.owner,type='webauthn',data={})
  self.assertFalse(self.status()['authenticated'])
 def test_password_failures_are_throttled(self):
  csrf=self.status()['csrf_token']
  for attempt in range(5):
   response=self.client.post('/api/v1/erp-session/login/',{'username':self.owner.username,'password':'synthetic-invalid-password'},format='json',HTTP_X_CSRFTOKEN=csrf,HTTP_X_FORWARDED_FOR='203.0.113.'+str(attempt))
   self.assertIn(response.status_code,(401,403))
  self.assertEqual(self.login(csrf,password='synthetic-invalid-password').status_code,429)
 # RFC test material, never a production enrollment or user credential.
 TEST_SECRET='GEZDGNBVGY3TQOJQGEZDGNBVGY3TQOJQ'
 TEST_TIME=1700000000
 def enroll_totp(self):
  from allauth.mfa.totp.internal.auth import TOTP
  return TOTP.activate(self.owner,self.TEST_SECRET).instance
 def code(self,offset=0):
  from allauth.mfa.totp.internal.auth import hotp_value,format_hotp_value
  return format_hotp_value(hotp_value(self.TEST_SECRET,self.TEST_TIME//30+offset))
 def challenge(self):
  result=self.login(self.status()['csrf_token']);self.assertEqual(result.status_code,202,result.content)
  body=result.json()['data'];self.assertFalse(body['authenticated']);self.assertTrue(body['mfa_required']);return body
 def verify_mfa(self,pending,code=None,client=None):
  return (client or self.client).post('/api/v1/erp-session/mfa/',{'challenge_id':pending['challenge_id'],'code':self.code() if code is None else code},format='json',HTTP_X_CSRFTOKEN=pending['csrf_token'])
 def test_totp_is_encrypted_and_password_is_only_first_factor(self):
  import json
  from apps.common.mfa_adapter import PREFIX
  factor=self.enroll_totp();self.assertTrue(factor.data['secret'].startswith(PREFIX));self.assertNotIn(self.TEST_SECRET,json.dumps(factor.data))
  pending=self.challenge();self.assertFalse(self.status()['authenticated']);self.assertEqual(self.status()['challenge_id'],pending['challenge_id'])
 def test_totp_completes_real_session_and_cannot_reuse_challenge(self):
  from unittest.mock import patch
  self.enroll_totp();pending=self.challenge()
  with patch('apps.prestadores.mi_negocio.web_mfa.time.time',return_value=self.TEST_TIME):response=self.verify_mfa(pending)
  self.assertEqual(response.status_code,200,response.content);self.assertTrue(self.status()['authenticated']);self.assertFalse(self.status()['mfa_required'])
  pending['csrf_token']=self.status()['csrf_token']
  with patch('apps.prestadores.mi_negocio.web_mfa.time.time',return_value=self.TEST_TIME):self.assertIn(self.verify_mfa(pending).status_code,(401,403))
 def test_incorrect_totp_persists_failure_but_does_not_authenticate(self):
  from unittest.mock import patch
  factor=self.enroll_totp();pending=self.challenge()
  with patch('apps.prestadores.mi_negocio.web_mfa.time.time',return_value=self.TEST_TIME):self.assertIn(self.verify_mfa(pending,code='000000').status_code,(401,403))
  self.assertEqual(ErpLoginChallenge.objects.get(pk=pending['challenge_id']).attempts,1);self.assertEqual(ErpTotpUsage.objects.get(factor=factor).failures,1);self.assertFalse(self.status()['authenticated'])
 def test_expired_challenge_and_old_code_are_rejected(self):
  from unittest.mock import patch
  from datetime import timedelta
  from django.utils import timezone
  self.enroll_totp();pending=self.challenge()
  with patch('apps.prestadores.mi_negocio.web_mfa.time.time',return_value=self.TEST_TIME):self.assertIn(self.verify_mfa(pending,self.code(-3)).status_code,(401,403))
  ErpLoginChallenge.objects.filter(pk=pending['challenge_id']).update(expires_at=timezone.now()-timedelta(seconds=1))
  with patch('apps.prestadores.mi_negocio.web_mfa.time.time',return_value=self.TEST_TIME):self.assertIn(self.verify_mfa(pending).status_code,(401,403))
  self.assertFalse(self.status()['authenticated'])
 def test_code_replay_is_rejected_after_cache_restart(self):
  from unittest.mock import patch
  self.enroll_totp();pending=self.challenge()
  with patch('apps.prestadores.mi_negocio.web_mfa.time.time',return_value=self.TEST_TIME):self.assertEqual(self.verify_mfa(pending).status_code,200)
  csrf=self.status()['csrf_token'];self.assertEqual(self.client.post('/api/v1/erp-session/logout/',{},format='json',HTTP_X_CSRFTOKEN=csrf).status_code,200)
  cache.clear();pending=self.challenge()
  with patch('apps.prestadores.mi_negocio.web_mfa.time.time',return_value=self.TEST_TIME):self.assertIn(self.verify_mfa(pending).status_code,(401,403))
 def test_totp_lock_applies_across_password_challenges(self):
  from unittest.mock import patch
  factor=self.enroll_totp();pending=self.challenge()
  with patch('apps.prestadores.mi_negocio.web_mfa.time.time',return_value=self.TEST_TIME):
   for attempt in range(5):self.assertIn(self.verify_mfa(pending,code='000000').status_code,(401,403))
  self.assertEqual(ErpTotpUsage.objects.get(factor=factor).failures,5)
  cache.clear();self.assertEqual(self.login(self.status()['csrf_token']).status_code,429)
 def test_challenge_cannot_move_to_another_browser_session(self):
  self.enroll_totp();pending=self.challenge();other=APIClient(enforce_csrf_checks=True,HTTP_HOST='localhost')
  pending['csrf_token']=other.get('/api/v1/erp-session/').json()['data']['csrf_token']
  self.assertIn(self.verify_mfa(pending,client=other).status_code,(401,403));self.assertFalse(self.status()['authenticated'])
 def test_password_and_factor_changes_invalidate_pending_challenge(self):
  from unittest.mock import patch
  factor=self.enroll_totp();pending=self.challenge();self.owner.set_password(secrets.token_urlsafe(24));self.owner.save(update_fields=['password'])
  with patch('apps.prestadores.mi_negocio.web_mfa.time.time',return_value=self.TEST_TIME):self.assertIn(self.verify_mfa(pending).status_code,(401,403))
  self.owner.set_password(self.password);self.owner.save(update_fields=['password']);pending=self.challenge()
  factor.data={**factor.data,'changed':True};factor.save(update_fields=['data'])
  with patch('apps.prestadores.mi_negocio.web_mfa.time.time',return_value=self.TEST_TIME):self.assertIn(self.verify_mfa(pending).status_code,(401,403))
 def test_configured_test_bypass_does_not_bypass_totp(self):
  from unittest.mock import patch
  self.enroll_totp();pending=self.challenge()
  with override_settings(MFA_TOTP_INSECURE_BYPASS_CODE='000000'),patch('apps.prestadores.mi_negocio.web_mfa.time.time',return_value=self.TEST_TIME):self.assertIn(self.verify_mfa(pending,code='000000').status_code,(401,403))
 def test_legacy_secret_conversion_is_explicit_and_repeat_safe(self):
  from django.core.management import call_command
  from apps.common.mfa_adapter import EncryptedMFAAdapter,PREFIX
  from io import StringIO
  factor=Authenticator.objects.create(user=self.owner,type='totp',data={'secret':self.TEST_SECRET})
  self.assertEqual(self.login(self.status()['csrf_token']).status_code,403)
  output=StringIO();call_command('encrypt_mfa_secrets',stdout=output);factor.refresh_from_db();self.assertEqual(factor.data['secret'],self.TEST_SECRET)
  call_command('encrypt_mfa_secrets',apply=True,stdout=output);factor.refresh_from_db();self.assertTrue(factor.data['secret'].startswith(PREFIX));self.assertEqual(EncryptedMFAAdapter().decrypt(factor.data['secret']),self.TEST_SECRET)
  sealed=factor.data['secret'];call_command('encrypt_mfa_secrets',apply=True,stdout=output);factor.refresh_from_db();self.assertEqual(factor.data['secret'],sealed);self.assertNotIn(self.TEST_SECRET,output.getvalue());self.challenge()
 def test_cancelling_pending_mfa_does_not_leave_a_usable_challenge(self):
  from unittest.mock import patch
  self.enroll_totp();pending=self.challenge()
  self.assertEqual(self.client.post('/api/v1/erp-session/logout/',{},format='json',HTTP_X_CSRFTOKEN=pending['csrf_token']).status_code,200)
  pending['csrf_token']=self.status()['csrf_token']
  with patch('apps.prestadores.mi_negocio.web_mfa.time.time',return_value=self.TEST_TIME):self.assertIn(self.verify_mfa(pending).status_code,(401,403))
  self.assertFalse(self.status()['authenticated'])
 def test_totp_completion_also_requires_csrf(self):
  self.enroll_totp();pending=self.challenge()
  result=self.client.post('/api/v1/erp-session/mfa/',{'challenge_id':pending['challenge_id'],'code':self.code()},format='json')
  self.assertEqual(result.status_code,403);self.assertEqual(ErpLoginChallenge.objects.get(pk=pending['challenge_id']).attempts,0)
 def test_eight_digit_totp_and_cooldown_recovery(self):
  from unittest.mock import patch
  from datetime import timedelta
  from django.utils import timezone
  factor=self.enroll_totp();pending=self.challenge()
  with patch('apps.prestadores.mi_negocio.web_mfa.time.time',return_value=self.TEST_TIME):
   for attempt in range(5):self.verify_mfa(pending,'000000')
  usage=ErpTotpUsage.objects.get(factor=factor);usage.locked_until=timezone.now()-timedelta(seconds=1);usage.save()
  cache.clear()
  with override_settings(MFA_TOTP_DIGITS=8):
   pending=self.challenge()
   with patch('apps.prestadores.mi_negocio.web_mfa.time.time',return_value=self.TEST_TIME+30):result=self.verify_mfa(pending,self.code(1))
   self.assertEqual(result.status_code,200,result.content);self.assertTrue(self.status()['authenticated'])
  usage.refresh_from_db();self.assertEqual(usage.failures,0)
 def test_secret_conversion_rolls_back_if_any_record_is_invalid(self):
  from django.core.management import call_command
  from django.core.management.base import CommandError
  from io import StringIO
  first=Authenticator.objects.create(user=self.owner,type='totp',data={'secret':self.TEST_SECRET})
  other=fixture['ProviderChecks'].other
  bad=Authenticator.objects.create(user=other,type='totp',data={'secret':'invalid secret'})
  self.addCleanup(lambda:Authenticator.objects.filter(pk=bad.pk).delete())
  with self.assertRaises(CommandError):call_command('encrypt_mfa_secrets',apply=True,stdout=StringIO())
  first.refresh_from_db();self.assertEqual(first.data['secret'],self.TEST_SECRET)
 def test_other_factors_cannot_fall_back_to_totp(self):
  self.enroll_totp()
  for kind in ('webauthn','unknown_future_factor'):
   extra=Authenticator.objects.create(user=self.owner,type=kind,data={})
   self.assertEqual(self.login(self.status()['csrf_token']).status_code,403)
   self.assertFalse(self.status()['authenticated']);extra.delete()
 def setup_enrollment(self):
  self.assertEqual(self.login(self.status()['csrf_token']).status_code,200)
  response=self.client.post('/api/v1/erp-session/enrollment/start/',{'password':self.password},format='json',HTTP_X_CSRFTOKEN=self.status()['csrf_token'])
  self.assertEqual(response.status_code,201,response.content);return response.json()['data']
 def confirm_enrollment(self,proposal,code=None,client=None):
  from allauth.mfa.totp.internal.auth import hotp_value,format_hotp_value
  target=client or self.client
  csrf=target.get('/api/v1/erp-session/').json()['data']['csrf_token']
  valid=format_hotp_value(hotp_value(proposal['secret'],self.TEST_TIME//30))
  return target.post('/api/v1/erp-session/enrollment/confirm/',{'id':proposal['id'],'code':valid if code is None else code},format='json',HTTP_X_CSRFTOKEN=csrf)
 def test_enrollment_requires_auth_csrf_reauthentication_and_opt_in(self):
  path='/api/v1/erp-session/enrollment/start/'
  self.assertIn(self.client.post(path,{'password':self.password},format='json').status_code,(401,403))
  self.assertEqual(self.login(self.status()['csrf_token']).status_code,200)
  self.assertEqual(self.client.post(path,{'password':self.password},format='json').status_code,403)
  csrf=self.status()['csrf_token']
  self.assertIn(self.client.post(path,{'password':'incorrect'},format='json',HTTP_X_CSRFTOKEN=csrf).status_code,(401,403))
  with override_settings(ERP_TOTP_ENROLLMENT_ENABLED=False):self.assertEqual(self.client.post(path,{'password':self.password},format='json',HTTP_X_CSRFTOKEN=csrf).status_code,503)
  self.assertFalse(ErpTotpEnrollment.objects.filter(user=self.owner).exists())
 def test_enrollment_secret_is_ciphered_before_confirmation(self):
  import json
  proposal=self.setup_enrollment();stored=ErpTotpEnrollment.objects.get(pk=proposal['id'])
  self.assertNotIn(proposal['secret'],stored.sealed_secret);self.assertNotIn(proposal['secret'],json.dumps(dict(self.client.session)));self.assertFalse(Authenticator.objects.filter(user=self.owner).exists())
 def test_enrollment_activation_requires_code_and_rotates_session(self):
  from unittest.mock import patch
  from django.conf import settings
  from apps.common.mfa_adapter import EncryptedMFAAdapter
  proposal=self.setup_enrollment();old_key=self.client.cookies[settings.SESSION_COOKIE_NAME].value
  with patch('apps.prestadores.mi_negocio.web_enrollment.time.time',return_value=self.TEST_TIME):result=self.confirm_enrollment(proposal)
  self.assertEqual(result.status_code,200,result.content);self.assertTrue(result.json()['data']['mfa_enabled']);self.assertFalse(result.json()['data']['totp_enrollment_allowed'])
  factor=Authenticator.objects.get(user=self.owner,type='totp');self.assertEqual(EncryptedMFAAdapter().decrypt(factor.data['secret']),proposal['secret'])
  stored=ErpTotpEnrollment.objects.get(pk=proposal['id']);self.assertIsNotNone(stored.consumed_at);self.assertEqual(stored.sealed_secret,'');self.assertNotEqual(old_key,self.client.cookies[settings.SESSION_COOKIE_NAME].value)
  other=APIClient(enforce_csrf_checks=True,HTTP_HOST='localhost');other.cookies[settings.SESSION_COOKIE_NAME]=old_key;self.assertFalse(other.get('/api/v1/erp-session/').json()['data']['authenticated'])
  self.assertTrue(self.status()['authenticated'])
 def test_enrollment_wrong_code_does_not_create_factor(self):
  from unittest.mock import patch
  from allauth.mfa.totp.internal.auth import hotp_value,format_hotp_value
  proposal=self.setup_enrollment();valid=int(format_hotp_value(hotp_value(proposal['secret'],self.TEST_TIME//30)));wrong=str((valid+1)%1000000).zfill(6)
  with patch('apps.prestadores.mi_negocio.web_enrollment.time.time',return_value=self.TEST_TIME):self.assertIn(self.confirm_enrollment(proposal,wrong).status_code,(401,403))
  self.assertFalse(Authenticator.objects.filter(user=self.owner).exists());self.assertEqual(ErpTotpEnrollment.objects.get(pk=proposal['id']).attempts,1)
 def test_expired_enrollment_cannot_activate_and_discards_key(self):
  from unittest.mock import patch
  from datetime import timedelta
  from django.utils import timezone
  proposal=self.setup_enrollment();ErpTotpEnrollment.objects.filter(pk=proposal['id']).update(expires_at=timezone.now()-timedelta(seconds=1))
  with patch('apps.prestadores.mi_negocio.web_enrollment.time.time',return_value=self.TEST_TIME):self.assertIn(self.confirm_enrollment(proposal).status_code,(401,403))
  self.assertEqual(ErpTotpEnrollment.objects.get(pk=proposal['id']).sealed_secret,'');self.assertFalse(Authenticator.objects.filter(user=self.owner).exists())
 def test_cancel_enrollment_is_repeat_safe_and_never_deletes_factors(self):
  proposal=self.setup_enrollment();path='/api/v1/erp-session/enrollment/cancel/';csrf=self.status()['csrf_token']
  for attempt in range(2):self.assertEqual(self.client.post(path,{'id':proposal['id']},format='json',HTTP_X_CSRFTOKEN=csrf).status_code,200)
  self.assertEqual(ErpTotpEnrollment.objects.get(pk=proposal['id']).sealed_secret,'');self.assertFalse(Authenticator.objects.filter(user=self.owner).exists())
  self.assertIn(self.confirm_enrollment(proposal).status_code,(401,403))
 def test_enrollment_cannot_move_to_another_session_of_same_user(self):
  proposal=self.setup_enrollment();other=APIClient(enforce_csrf_checks=True,HTTP_HOST='localhost');csrf=other.get('/api/v1/erp-session/').json()['data']['csrf_token']
  self.assertEqual(other.post('/api/v1/erp-session/login/',{'username':self.owner.username,'password':self.password},format='json',HTTP_X_CSRFTOKEN=csrf).status_code,200)
  self.assertIn(self.confirm_enrollment(proposal,client=other).status_code,(401,403));self.assertEqual(ErpTotpEnrollment.objects.get(pk=proposal['id']).attempts,0)
 def test_enrollment_never_replaces_an_existing_factor(self):
  from unittest.mock import patch
  factor=self.enroll_totp();pending=self.challenge()
  with patch('apps.prestadores.mi_negocio.web_mfa.time.time',return_value=self.TEST_TIME):self.assertEqual(self.verify_mfa(pending).status_code,200)
  before=factor.data.copy();csrf=self.status()['csrf_token']
  result=self.client.post('/api/v1/erp-session/enrollment/start/',{'password':self.password},format='json',HTTP_X_CSRFTOKEN=csrf)
  self.assertEqual(result.status_code,403);factor.refresh_from_db();self.assertEqual(factor.data,before)
 def test_new_enrollment_discards_previous_pending_key(self):
  first=self.setup_enrollment();csrf=self.status()['csrf_token']
  second=self.client.post('/api/v1/erp-session/enrollment/start/',{'password':self.password},format='json',HTTP_X_CSRFTOKEN=csrf)
  self.assertEqual(second.status_code,201);old=ErpTotpEnrollment.objects.get(pk=first['id']);self.assertIsNotNone(old.consumed_at);self.assertEqual(old.sealed_secret,'');self.assertNotEqual(first['id'],second.json()['data']['id'])
 def cleanup_fixture(self):
  from datetime import timedelta
  from django.utils import timezone
  now=timezone.now()
  def create(**changes):
   values=dict(user=self.owner,binding_digest='b'*64,password_version='p'*64,factor_version='f'*64,sealed_secret='synthetic-ciphertext',expires_at=now+timedelta(minutes=2))
   values.update(changes);return ErpTotpEnrollment.objects.create(**values)
  return create(expires_at=now-timedelta(seconds=1)),create(consumed_at=now),create()
 def test_cleanup_dry_run_never_erases_keys_or_prints_material(self):
  from django.core.management import call_command
  from io import StringIO
  expired,consumed,valid=self.cleanup_fixture();output=StringIO()
  call_command('purge_totp_enrollments',stdout=output)
  self.assertEqual(output.getvalue(),'ELIGIBLE_NO_WRITE 2\n')
  for proposal in (expired,consumed,valid):
   proposal.refresh_from_db();self.assertEqual(proposal.sealed_secret,'synthetic-ciphertext')
 def test_cleanup_erases_only_unusable_material_in_bounded_repeat_safe_batches(self):
  from django.core.management import call_command
  from io import StringIO
  expired,consumed,valid=self.cleanup_fixture();factor=self.enroll_totp();before=factor.data.copy()
  output=StringIO();call_command('purge_totp_enrollments',apply=True,batch_size=1,stdout=output)
  self.assertEqual(output.getvalue(),'ERASED 1\n')
  self.assertEqual(ErpTotpEnrollment.objects.filter(sealed_secret='').count(),1)
  for expected in (1,0):
   output=StringIO();call_command('purge_totp_enrollments',apply=True,stdout=output)
   self.assertEqual(output.getvalue(),f'ERASED {expected}\n')
  for proposal in (expired,consumed):
   proposal.refresh_from_db();self.assertEqual(proposal.sealed_secret,'');self.assertEqual(proposal.binding_digest,'b'*64)
  valid.refresh_from_db();self.assertEqual(valid.sealed_secret,'synthetic-ciphertext')
  factor.refresh_from_db();self.assertEqual(factor.data,before)
 def test_cleanup_rejects_invalid_batch_size_without_changes(self):
  from django.core.management import call_command
  from django.core.management.base import CommandError
  from io import StringIO
  self.cleanup_fixture()
  for size in (0,-1,10001):
   with self.assertRaises(CommandError):call_command('purge_totp_enrollments',apply=True,batch_size=size,stdout=StringIO())
  self.assertEqual(ErpTotpEnrollment.objects.exclude(sealed_secret='').count(),3)
 def recovery_fixture(self):
  from allauth.mfa.recovery_codes.internal.auth import RecoveryCodes
  self.enroll_totp();backup=RecoveryCodes.activate(self.owner)
  return backup,backup.get_unused_codes()[0]
 def recover(self,pending,code,client=None):
  return (client or self.client).post('/api/v1/erp-session/recovery/',{'challenge_id':pending['challenge_id'],'code':code},format='json',HTTP_X_CSRFTOKEN=pending['csrf_token'])
 @override_settings(ERP_RECOVERY_CODES_ENABLED=True)
 def test_recovery_code_completes_session_once_without_removing_totp(self):
  backup,code=self.recovery_fixture();pending=self.challenge();self.assertTrue(pending['recovery_available'])
  self.assertEqual(self.recover(pending,code).status_code,200);self.assertTrue(self.status()['authenticated'])
  self.assertTrue(Authenticator.objects.filter(user=self.owner,type='totp').exists())
  next_challenge=self.challenge();self.assertIn(self.recover(next_challenge,code).status_code,(401,403));self.assertFalse(self.status()['authenticated'])
 @override_settings(ERP_RECOVERY_CODES_ENABLED=True)
 def test_recovery_requires_password_csrf_and_same_browser(self):
  backup,code=self.recovery_fixture();pending=self.challenge()
  self.assertEqual(self.client.post('/api/v1/erp-session/recovery/',{'challenge_id':pending['challenge_id'],'code':code},format='json').status_code,403)
  other=APIClient(enforce_csrf_checks=True,HTTP_HOST='localhost');csrf=other.get('/api/v1/erp-session/').json()['data']['csrf_token']
  moved=dict(pending,csrf_token=csrf);self.assertIn(self.recover(moved,code,other).status_code,(401,403))
  self.assertEqual(self.recover(pending,code).status_code,200)
 @override_settings(ERP_RECOVERY_CODES_ENABLED=True)
 def test_recovery_failures_share_totp_persistent_lock(self):
  backup,code=self.recovery_fixture();pending=self.challenge()
  for attempt in range(5):self.assertIn(self.recover(pending,'0'*len(code)).status_code,(401,403))
  cache.clear();self.assertEqual(self.login(self.status()['csrf_token']).status_code,429)
  backup.instance.refresh_from_db();self.assertEqual(backup.instance.data['used_mask'],0)
 def test_recovery_disabled_by_default_and_never_falls_back_to_plaintext(self):
  backup,code=self.recovery_fixture();pending=self.challenge();self.assertFalse(pending['recovery_available'])
  self.assertEqual(self.recover(pending,code).status_code,503)
  from apps.common.mfa_adapter import EncryptedMFAAdapter
  backup.instance.data['seed']=EncryptedMFAAdapter().decrypt(backup.instance.data['seed']);backup.instance.save()
  with override_settings(ERP_RECOVERY_CODES_ENABLED=True):
   pending=self.challenge();self.assertFalse(pending['recovery_available']);self.assertIn(self.recover(pending,code).status_code,(401,403))
 @override_settings(ERP_RECOVERY_CODES_ENABLED=True)
 def test_expired_recovery_does_not_consume_backup(self):
  from django.utils import timezone
  from datetime import timedelta
  backup,code=self.recovery_fixture();pending=self.challenge()
  ErpLoginChallenge.objects.filter(pk=pending['challenge_id']).update(expires_at=timezone.now()-timedelta(seconds=1))
  self.assertIn(self.recover(pending,code).status_code,(401,403));backup.instance.refresh_from_db();self.assertEqual(backup.instance.data['used_mask'],0)
 @override_settings(ERP_RECOVERY_CODES_ENABLED=True)
 def test_recovery_rejects_weak_code_policy_without_consumption(self):
  backup,code=self.recovery_fixture()
  with override_settings(MFA_RECOVERY_CODE_DIGITS=4):
   pending=self.challenge();self.assertFalse(pending['recovery_available'])
   self.assertIn(self.recover(pending,code).status_code,(401,403))
  backup.instance.refresh_from_db();self.assertEqual(backup.instance.data['used_mask'],0)
 def issue_fixture(self):
  from unittest.mock import patch
  self.enroll_totp();pending=self.challenge()
  with patch('apps.prestadores.mi_negocio.web_mfa.time.time',return_value=self.TEST_TIME):self.assertEqual(self.verify_mfa(pending).status_code,200)
 def issue_backup(self,code=None,password=None):
  return self.client.post('/api/v1/erp-session/recovery/issue/',{'password':self.password if password is None else password,'code':self.code(1) if code is None else code},format='json',HTTP_X_CSRFTOKEN=self.status()['csrf_token'])
 @override_settings(ERP_RECOVERY_CODES_ENABLED=True,ERP_RECOVERY_ISSUANCE_ENABLED=True)
 def test_issue_requires_fresh_totp_and_rotates_current_session(self):
  from unittest.mock import patch
  from django.conf import settings
  self.issue_fixture();before=self.client.cookies[settings.SESSION_COOKIE_NAME].value
  with patch('apps.prestadores.mi_negocio.web_recovery.time.time',return_value=self.TEST_TIME):self.assertIn(self.issue_backup(self.code()).status_code,(401,403))
  with patch('apps.prestadores.mi_negocio.web_recovery.time.time',return_value=self.TEST_TIME+30):result=self.issue_backup()
  self.assertEqual(result.status_code,201,result.content);body=result.json()['data'];self.assertEqual(len(body['codes']),10);self.assertTrue(body['session']['authenticated'])
  self.assertNotEqual(before,self.client.cookies[settings.SESSION_COOKIE_NAME].value);self.assertTrue(self.status()['authenticated'])
  from apps.common.mfa_adapter import PREFIX
  factor=Authenticator.objects.get(user=self.owner,type='recovery_codes');self.assertTrue(factor.data['seed'].startswith(PREFIX))
  self.assertNotIn(body['codes'][0],str(dict(self.client.session)))
 @override_settings(ERP_RECOVERY_CODES_ENABLED=True,ERP_RECOVERY_ISSUANCE_ENABLED=True)
 def test_rotation_invalidates_previous_recovery_codes(self):
  from unittest.mock import patch
  from allauth.mfa.recovery_codes.internal.auth import RecoveryCodes
  self.issue_fixture()
  with patch('apps.prestadores.mi_negocio.web_recovery.time.time',return_value=self.TEST_TIME+30):first=self.issue_backup().json()['data']['codes']
  with patch('apps.prestadores.mi_negocio.web_recovery.time.time',return_value=self.TEST_TIME+60):second=self.issue_backup(self.code(2))
  self.assertEqual(second.status_code,201)
  backup=RecoveryCodes(Authenticator.objects.get(user=self.owner,type='recovery_codes'))
  self.assertNotEqual(first,backup.get_unused_codes());self.assertFalse(backup.validate_code(first[0]))
 @override_settings(ERP_RECOVERY_CODES_ENABLED=True,ERP_RECOVERY_ISSUANCE_ENABLED=True)
 def test_issue_wrong_password_or_csrf_does_not_create_codes(self):
  self.issue_fixture();self.assertIn(self.issue_backup(password='wrong').status_code,(401,403))
  result=self.client.post('/api/v1/erp-session/recovery/issue/',{'password':self.password,'code':self.code(1)},format='json');self.assertEqual(result.status_code,403)
  self.assertFalse(Authenticator.objects.filter(user=self.owner,type='recovery_codes').exists())
 @override_settings(ERP_RECOVERY_CODES_ENABLED=True,ERP_RECOVERY_ISSUANCE_ENABLED=True)
 def test_issue_failures_share_persistent_factor_lock(self):
  self.issue_fixture()
  for attempt in range(5):self.assertIn(self.issue_backup(code='000000').status_code,(401,403))
  usage=ErpTotpUsage.objects.get(factor__user=self.owner);self.assertIsNotNone(usage.locked_until)
  self.assertFalse(Authenticator.objects.filter(user=self.owner,type='recovery_codes').exists())
 def test_issue_disabled_by_default(self):
  self.issue_fixture();self.assertEqual(self.issue_backup().status_code,503)
 @override_settings(ERP_RECOVERY_CODES_ENABLED=True,ERP_RECOVERY_ISSUANCE_ENABLED=True)
 def test_recovery_audits_issue_rotation_and_use_without_secrets(self):
  from unittest.mock import patch
  self.issue_fixture()
  before=ErpSecurityEvent.objects.filter(actor_id=self.owner.pk).count()
  with patch('apps.prestadores.mi_negocio.web_recovery.time.time',return_value=self.TEST_TIME+30):first=self.issue_backup()
  self.assertEqual(first.status_code,201)
  with patch('apps.prestadores.mi_negocio.web_recovery.time.time',return_value=self.TEST_TIME+60):second=self.issue_backup(self.code(2))
  self.assertEqual(second.status_code,201)
  pending=self.challenge();code=second.json()['data']['codes'][0];self.assertEqual(self.recover(pending,code).status_code,200)
  events=list(ErpSecurityEvent.objects.filter(actor_id=self.owner.pk).order_by('occurred_at'))[before:]
  self.assertEqual([event.kind for event in events],['recovery_issued','recovery_rotated','recovery_used'])
  self.assertEqual(str(events[-1].challenge_id),pending['challenge_id'])
  self.assertEqual({field.name for field in ErpSecurityEvent._meta.fields},{'id','actor_id','kind','occurred_at','challenge_id','factor_id'})
 @override_settings(ERP_RECOVERY_CODES_ENABLED=True,ERP_RECOVERY_ISSUANCE_ENABLED=True)
 def test_issue_audit_failure_rolls_back_seed_and_counter(self):
  from unittest.mock import patch
  self.issue_fixture();usage=ErpTotpUsage.objects.get(factor__user=self.owner);old_counter=usage.last_counter
  with patch('apps.prestadores.mi_negocio.web_recovery.time.time',return_value=self.TEST_TIME+30),patch.object(ErpSecurityEvent.objects,'create',side_effect=RuntimeError('synthetic audit unavailable')):
   with self.assertRaises(RuntimeError):self.issue_backup()
  usage.refresh_from_db();self.assertEqual(usage.last_counter,old_counter)
  self.assertFalse(Authenticator.objects.filter(user=self.owner,type='recovery_codes').exists())
 @override_settings(ERP_RECOVERY_CODES_ENABLED=True)
 def test_recovery_audit_failure_does_not_consume_code_or_challenge(self):
  from unittest.mock import patch
  backup,code=self.recovery_fixture();pending=self.challenge()
  with patch.object(ErpSecurityEvent.objects,'create',side_effect=RuntimeError('synthetic audit unavailable')):
   with self.assertRaises(RuntimeError):self.recover(pending,code)
  backup.instance.refresh_from_db();self.assertEqual(backup.instance.data['used_mask'],0)
  self.assertIsNone(ErpLoginChallenge.objects.get(pk=pending['challenge_id']).consumed_at)
  self.assertEqual(self.recover(pending,code).status_code,200)
 def test_audit_application_guards_reject_updates_and_deletions(self):
  event=ErpSecurityEvent.objects.create(actor_id=self.owner.pk,kind='recovery_used')
  with self.assertRaises(ValueError):event.save()
  with self.assertRaises(ValueError):event.delete()
  with self.assertRaises(ValueError):ErpSecurityEvent.objects.filter(pk=event.pk).update(kind='recovery_issued')
  with self.assertRaises(ValueError):ErpSecurityEvent.objects.filter(pk=event.pk).delete()
  event.refresh_from_db();self.assertEqual(event.kind,'recovery_used')
 def test_security_history_requires_session_and_only_returns_own_bounded_events(self):
  path='/api/v1/erp-session/security-events/'
  self.assertIn(self.client.get(path).status_code,(401,403))
  self.assertEqual(self.login(self.status()['csrf_token']).status_code,200)
  other=fixture['ProviderChecks'].other
  foreign=ErpSecurityEvent.objects.create(actor_id=other.pk,kind='recovery_used')
  for _ in range(25):ErpSecurityEvent.objects.create(actor_id=self.owner.pk,kind='recovery_issued')
  result=self.client.get(path);self.assertEqual(result.status_code,200)
  events=result.json()['data']['events'];self.assertEqual(len(events),20)
  self.assertNotIn(str(foreign.pk),[event['id'] for event in events])
  self.assertEqual(set(events[0]),{'id','kind','occurred_at'})
  self.assertEqual(result['Cache-Control'],'no-store')
if __name__=='__main__':unittest.main()
