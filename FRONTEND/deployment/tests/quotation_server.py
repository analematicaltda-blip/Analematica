"""Loopback-only integration harness: real password, cookies, CSRF and Django WSGI.
Uses generated test users and memory database; never deploy this test harness.
"""
import argparse,importlib,ipaddress,json,os,runpy,secrets
from pathlib import Path
from wsgiref.simple_server import make_server,WSGIRequestHandler
ROOT=Path(__file__).resolve().parents[3]
parser=argparse.ArgumentParser();parser.add_argument('--assets',type=Path,required=True);parser.add_argument('--bind',default='127.0.0.1');parser.add_argument('--origin');parser.add_argument('--secure-cookie',action='store_true');args=parser.parse_args()
if not ipaddress.ip_address(args.bind).is_private or ipaddress.ip_address(args.bind).is_unspecified:raise ValueError('Private bind required')
fixture=runpy.run_path(str(ROOT/'BACKEND/deployment/tests/company_identity_check.py'),run_name='browser_fixture')
case=fixture['CompanyChecks']();case.setUp();case.draft_fixture()
from apps.turismo.models import ErpSecurityEvent,ErpLoginChallenge,ErpTotpUsage,ErpTotpEnrollment
from django.contrib.sessions.models import Session
from allauth.account.models import EmailAddress
from allauth.mfa.models import Authenticator
from api.models import Entity
from apps.core_erp.models import EventAuditLog
for model in (ErpSecurityEvent,Session,EmailAddress,Authenticator,Entity,EventAuditLog,ErpTotpUsage,ErpLoginChallenge,ErpTotpEnrollment):fixture['fixture']['create'](model)
from django.conf import settings
settings.ERP_WEB_SESSION_ENABLED=True
settings.ERP_PASSWORD_RESET_ENABLED=os.environ.get('QUOTE_RESET')=='1'
settings.ERP_PASSWORD_RESET_MAIL_READY=settings.ERP_PASSWORD_RESET_ENABLED
settings.EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend'
settings.ADMINS=[]
settings.ERP_RECOVERY_CODES_ENABLED=os.environ.get('QUOTE_RECOVERY')=='1' or os.environ.get('QUOTE_ISSUE')=='1'
settings.ERP_RECOVERY_ISSUANCE_ENABLED=os.environ.get('QUOTE_ISSUE')=='1'
settings.ERP_TOTP_ENROLLMENT_ENABLED=os.environ.get('QUOTE_ENROLL')=='1'
settings.SESSION_COOKIE_SECURE=args.secure_cookie;settings.CSRF_COOKIE_SECURE=args.secure_cookie
if args.origin:settings.CSRF_TRUSTED_ORIGINS=[args.origin]
settings.SESSION_COOKIE_NAME='sgacd_erp_tur_session';settings.CSRF_COOKIE_NAME='sgacd_erp_tur_csrf'
settings.CACHES={'default':{'BACKEND':'django.core.cache.backends.locmem.LocMemCache','LOCATION':'quote-browser'}}
settings.CHANNEL_LAYERS={'default':{'BACKEND':'channels.layers.InMemoryChannelLayer'}}
os.environ['BACKEND_SERVICE']='erp-tur'
import tourism_urls
importlib.reload(tourism_urls)
from django.urls import clear_url_caches
clear_url_caches()
owner=fixture['F'].owner;password=secrets.token_urlsafe(24);owner.set_password(password);owner.save(update_fields=['password'])
credential_file=args.assets/'fixture-credentials.json'
credentials={'username':owner.username,'password':password}
if settings.ERP_PASSWORD_RESET_ENABLED:
 owner.email=secrets.token_hex(8)+'@example.test';owner.save(update_fields=['email'])
 EmailAddress.objects.create(user=owner,email=owner.email,primary=True,verified=True)
 credentials['email']=owner.email
if os.environ.get('QUOTE_MFA')=='1':
 from allauth.mfa.totp.internal.auth import TOTP,generate_totp_secret
 secret=generate_totp_secret();TOTP.activate(owner,secret);credentials['totp_secret']=secret
if os.environ.get('QUOTE_RECOVERY')=='1':
 from allauth.mfa.recovery_codes.internal.auth import RecoveryCodes
 credentials['recovery_code']=RecoveryCodes.activate(owner).get_unused_codes()[0]
with open(credential_file,'x',opener=lambda name,flags:os.open(name,flags,0o600)) as stream:json.dump(credentials,stream)
from django.core.handlers.wsgi import WSGIHandler
django_application=WSGIHandler()
def application(environ,start_response):
 path=environ['PATH_INFO']
 if path=='/':
  body=b'<html lang="es"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Prueba de cotizaciones</title><div id="root"></div><script src="/bundle.js"></script></html>'
  start_response('200 OK',[('Content-Type','text/html'),('Cache-Control','no-store')]);return [body]
 if path=='/bundle.js':
  start_response('200 OK',[('Content-Type','text/javascript'),('Cache-Control','no-store')]);return [(args.assets/'bundle.js').read_bytes()]
 if not path.startswith('/api/'):
  start_response('404 Not Found',[('Content-Type','application/json')]);return [b'{}']
 response=django_application(environ,start_response)
 if settings.ERP_PASSWORD_RESET_ENABLED:
  from django.core import mail
  if getattr(mail,'outbox',None):
   target=args.assets/'private-reset-mail.json'
   link=next((line for line in mail.outbox[-1].body.splitlines() if line.startswith(('https://','http://'))),None)
   if link:
    with open(target,'w',opener=lambda name,flags:os.open(name,flags,0o600)) as stream:json.dump({'link':link},stream)
 return response
class QuietHandler(WSGIRequestHandler):
 def log_message(self,*args):pass
server=make_server(args.bind,0,application,handler_class=QuietHandler)
if settings.ERP_PASSWORD_RESET_ENABLED:
 settings.ERP_PASSWORD_RESET_URL=(args.origin or 'http://127.0.0.1:'+str(server.server_port))+'/'
 settings.ERP_PASSWORD_RESET_LOCAL_HTTP=not args.secure_cookie
print('READY '+str(server.server_port),flush=True)
server.serve_forever()
