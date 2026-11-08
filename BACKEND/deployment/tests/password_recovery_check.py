"""Verified-email recovery via actual Django sessions and in-memory email only."""
import runpy,unittest,types,sys,secrets
from pathlib import Path
from urllib.parse import urlsplit,parse_qs
from unittest.mock import patch
from datetime import timedelta
fixture=runpy.run_path(str(Path(__file__).with_name('erp_session_check.py')),run_name='password_fixture')
Base=fixture['SessionChecks']
from django.test import override_settings
from django.urls import path
from django.core import mail
from django.core.cache import cache
from allauth.account.models import EmailAddress
from allauth.mfa.models import Authenticator
from apps.turismo.models import ErpSecurityEvent
from apps.prestadores.mi_negocio.web_session import PasswordResetRequest,PasswordResetConfirm
from apps.prestadores.mi_negocio.web_password_reset import TOKENS
module=types.ModuleType('password_recovery_fixture_urls');module.urlpatterns=fixture['module'].urlpatterns+[path('api/v1/erp-session/password-reset/request/',PasswordResetRequest.as_view()),path('api/v1/erp-session/password-reset/confirm/',PasswordResetConfirm.as_view())];sys.modules[module.__name__]=module
class PasswordChecks(Base):
 def setUp(self):
  super().setUp();self.owner.email=secrets.token_hex(8)+'@example.test';self.owner.is_active=True;self.owner.is_agent=False;self.owner.save(update_fields=['email','is_active','is_agent'])
  EmailAddress.objects.filter(user=self.owner).update(primary=False)
  self.email=EmailAddress.objects.create(user=self.owner,email=self.owner.email,verified=True,primary=True)
  settings=override_settings(ROOT_URLCONF=module.__name__,ERP_PASSWORD_RESET_ENABLED=True,ERP_PASSWORD_RESET_MAIL_READY=True,ERP_PASSWORD_RESET_URL='https://erp.example.test/erp/cotizaciones',EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend',ADMINS=[])
  settings.enable();self.addCleanup(settings.disable);mail.outbox=[]
 def request_reset(self,email=None,csrf=True):
  return self.client.post('/api/v1/erp-session/password-reset/request/',{'email':email or self.owner.email},format='json',**({'HTTP_X_CSRFTOKEN':self.status()['csrf_token']} if csrf else {}))
 def link(self):
  response=self.request_reset();self.assertEqual(response.status_code,202,response.content);self.assertEqual(len(mail.outbox),1)
  line=next(line for line in mail.outbox[-1].body.splitlines() if line.startswith('https://'))
  parsed=urlsplit(line);self.assertEqual(parsed.netloc,'erp.example.test');self.assertFalse(parsed.query)
  values=parse_qs(parsed.fragment);return {'uid':values['reset_uid'][0],'token':values['reset_token'][0]}
 def confirm_reset(self,link,password=None,csrf=True):
  return self.client.post('/api/v1/erp-session/password-reset/confirm/',{**link,'password':password or secrets.token_urlsafe(24)},format='json',**({'HTTP_X_CSRFTOKEN':self.status()['csrf_token']} if csrf else {}))
 def test_public_response_does_not_reveal_account_or_token(self):
  known=self.request_reset();unknown=self.request_reset('missing@example.test');self.assertEqual(known.status_code,202);self.assertEqual(known.json(),unknown.json());self.assertNotIn('token',str(known.json()));self.assertEqual(len(mail.outbox),1)
 def test_unverified_inactive_and_agent_accounts_receive_no_message(self):
  self.email.verified=False;self.email.save();self.assertEqual(self.request_reset().status_code,202);self.assertEqual(len(mail.outbox),0)
  self.email.verified=True;self.email.save()
  for field in ('is_active','is_agent'):
   cache.clear();setattr(self.owner,field,False if field=='is_active' else True);self.owner.save()
   self.assertEqual(self.request_reset().status_code,202);self.assertEqual(len(mail.outbox),0)
   setattr(self.owner,field,True if field=='is_active' else False);self.owner.save()
 def test_reset_is_one_use_preserves_mfa_and_does_not_log_in(self):
  factor=self.enroll_totp();before=factor.data.copy();link=self.link();password=secrets.token_urlsafe(24)
  result=self.confirm_reset(link,password);self.assertEqual(result.status_code,200,result.content);self.assertFalse(self.status()['authenticated'])
  factor.refresh_from_db();self.assertEqual(factor.data,before)
  self.assertEqual(self.confirm_reset(link).status_code,400)
  self.password=password;self.assertEqual(self.login(self.status()['csrf_token']).status_code,202)
 def test_expiry_and_factor_change_invalidate_link(self):
  link=self.link();future=TOKENS._now()+timedelta(seconds=901)
  with patch.object(TOKENS,'_now',return_value=future):self.assertEqual(self.confirm_reset(link).status_code,400)
  self.enroll_totp();self.assertEqual(self.confirm_reset(link).status_code,400)
 def test_revoked_verification_cannot_reset(self):
  link=self.link();self.email.verified=False;self.email.save();self.assertEqual(self.confirm_reset(link).status_code,400)
 def test_weak_password_does_not_consume_valid_link(self):
  link=self.link();weak=self.confirm_reset(link,'123456789012');self.assertEqual(weak.status_code,400);self.assertNotIn('ErrorDetail',weak.content.decode());self.assertEqual(self.confirm_reset(link).status_code,200)
 def test_csrf_and_email_cooldown(self):
  self.assertEqual(self.request_reset(csrf=False).status_code,403)
  link=self.link();self.assertEqual(self.request_reset().status_code,202);self.assertEqual(len(mail.outbox),1)
  self.assertEqual(self.confirm_reset(link,csrf=False).status_code,403)
 def test_unsafe_mail_host_and_disabled_feature_are_rejected(self):
  for values in ({'EMAIL_BACKEND':'django.core.mail.backends.console.EmailBackend'},{'ERP_PASSWORD_RESET_URL':'https://trusted.example/@x?next=https://evil.test'},{'ERP_PASSWORD_RESET_ENABLED':False},{'ERP_PASSWORD_RESET_MAIL_READY':False}):
   with override_settings(**values):self.assertEqual(self.request_reset().status_code,503)
  self.assertEqual(len(mail.outbox),0)
 def test_audit_failure_rolls_back_password(self):
  link=self.link();before=self.owner.password
  with patch.object(ErpSecurityEvent.objects,'create',side_effect=RuntimeError('synthetic audit failure')):
   with self.assertRaises(RuntimeError):self.confirm_reset(link)
  self.owner.refresh_from_db();self.assertEqual(self.owner.password,before);self.assertEqual(self.confirm_reset(link).status_code,200)
 def test_existing_session_is_invalidated_after_password_reset(self):
  self.assertEqual(self.login(self.status()['csrf_token']).status_code,200);self.assertTrue(self.status()['authenticated'])
  link=self.link();self.assertEqual(self.confirm_reset(link).status_code,200);self.assertFalse(self.status()['authenticated'])
for name in vars(Base):
 if name.startswith('test_') and name not in vars(PasswordChecks):setattr(PasswordChecks,name,None)
if __name__=='__main__':unittest.main(defaultTest='PasswordChecks')
