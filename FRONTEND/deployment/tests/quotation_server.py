"""Loopback-only integration harness: real password, cookies, CSRF and Django WSGI.
Uses generated test users and memory database; never deploy this test harness.
"""
import argparse,importlib,ipaddress,json,os,runpy,secrets
from pathlib import Path
from wsgiref.simple_server import make_server,WSGIRequestHandler
ROOT=Path(__file__).resolve().parents[3]
parser=argparse.ArgumentParser();parser.add_argument('--assets',type=Path,required=True);parser.add_argument('--bind',default='127.0.0.1');parser.add_argument('--origin');parser.add_argument('--secure-cookie',action='store_true');args=parser.parse_args()
if not ipaddress.ip_address(args.bind).is_private or ipaddress.ip_address(args.bind).is_unspecified:raise ValueError('Private bind required')
if os.environ.get('LEDGER_BROWSER')=='1':
 ledger=runpy.run_path(str(ROOT/'BACKEND/deployment/tests/accounting_adapter_check.py'),run_name='ledger_browser_fixture')
 case=ledger['AdapterTests']();case.setUp()
 if os.environ.get('NATIVE_PURCHASE_FIXTURE')=='1':
  from django.db import connection
  from apps.prestadores.mi_negocio.gestion_contable.compras.models import Proveedor,FacturaCompra
  for model in [Proveedor,FacturaCompra]:
   if model._meta.db_table not in connection.introspection.table_names():
    with connection.schema_editor() as editor:editor.create_model(model)
  from apps.core_erp.accounting.models import Account
  from apps.core_erp.accounting import tax_policies
  from django.utils import timezone
  native_accounts={}
  for role,code,kind in [('basis','510072','EXPENSE'),('input','135572','ASSET'),('retention','236572','LIABILITY'),('settlement','220572','LIABILITY')]:
   native_accounts[role]=str(Account.plain_objects.create(tenant=case.tenant,chart_of_accounts=case.chart,code=code,name='Synthetic native UI '+role,type=kind).pk)
  native_day=timezone.localdate()
  native_policy={'code':'NATIVE_UI72','jurisdiction':'CO','currency':'COP','valid_from':native_day.replace(month=1,day=1).isoformat(),'valid_until':native_day.replace(month=12,day=31).isoformat(),'rounding':'PER_COMPONENT_HALF_UP','components':[{'code':'INPUT','kind':'INPUT_TAX','rate_bps':1900,'applies_to':['TAXABLE']},{'code':'RET','kind':'WITHHOLDING','rate_bps':250,'applies_to':['TAXABLE']}]}
  native_review=tax_policies.review_policy(case.tenant.pk,actor=case.user,policy=native_policy,evidence_digest='a'*64,expected_revision=0,confirmed=True)
  tax_policies.record_policy(case.tenant.pk,actor=case.user,review_id=native_review['review_id'],confirmed=True)


 if os.environ.get('OPENING_BROWSER')=='1':
  from apps.core_erp.accounting.models import Account
  Account.plain_objects.filter(pk=case.a.pk).update(initial_balance='100.00')
  opening_equity=Account.plain_objects.create(tenant=case.tenant,chart_of_accounts=case.chart,code='310505',name='Synthetic opening equity',type='EQUITY',initial_balance='100.00')
  if os.environ.get('OPENING_LINK_BROWSER')=='1':
   from django.utils import timezone
   from apps.core_erp.accounting.ledger_engine import LedgerEngine
   opening_existing=LedgerEngine.post_lines(tenant_id=case.tenant.pk,entry_date=timezone.localdate(),description='Previously recorded opening fixture',lines_data=[{'account':case.a,'debit':'100.00'},{'account':opening_equity,'credit':'100.00'}],actor=case.user,idempotency_key='existing-opening-fixture',period_id=case.period.pk)
 else:case.post()
 mapping=case.ratio_mapping()
 assert case.configure_ratio(mapping).status_code==201
 from apps.core_erp.accounting.models import Account
 from apps.core_erp.accounting.ledger_engine import LedgerEngine
 from django.utils import timezone
 liability=Account.plain_objects.get(pk=mapping['current_liabilities'][0])
 if os.environ.get('OPENING_BROWSER')!='1':
  LedgerEngine.post_lines(tenant_id=case.tenant.pk,entry_date=timezone.localdate(),description='Synthetic liquidity funding',
   lines_data=[{'account':case.a,'debit':'5.00'},{'account':liability,'credit':'5.00'}],actor=case.user,idempotency_key='browser-liquidity')
 fixture=ledger['fixture']['fixture']['fixture']
 from apps.domain_business.operativa.models import Reservation
 from apps.domain_business.operativa.sargentos import DomainSargentoReservas
 from django.contrib.contenttypes.models import ContentType
 from datetime import timedelta
 import uuid
 ledger['fixture']['fixture']['fixture']['fixture']['create'](Reservation)
 if os.environ.get('CANCELLATION_POLICY_FIXTURE')=='1':
  from django.db import connection
  from apps.prestadores.mi_negocio.gestion_operativa.modulos_genericos.reservas.models import PoliticaCancelacion
  if PoliticaCancelacion._meta.db_table not in connection.introspection.table_names():
   with connection.schema_editor() as editor:editor.create_model(PoliticaCancelacion)
 billing_reservation=Reservation.plain_objects.create(tenant=case.tenant,customer_id=uuid.uuid4(),content_type=ContentType.objects.get_for_model(Reservation),object_id=uuid.uuid4(),start_date=timezone.now()-timedelta(days=2),end_date=timezone.now()-timedelta(days=1),total_price='100.00')
 if os.environ.get('CANCELLATION_TIMING_FIXTURE')=='1':
  Reservation.plain_objects.filter(pk=billing_reservation.pk).update(start_date=timezone.now()+timedelta(days=15),end_date=timezone.now()+timedelta(days=16));billing_reservation.refresh_from_db()
 DomainSargentoReservas.confirm_reservation(billing_reservation.pk,actor=case.user,provider_id=case.provider.pk)
 if os.environ.get('WALLET_REFUND_LIFECYCLE_FIXTURE')=='1':
  from wallet_lifecycle_fixture import apply
  apply(case,billing_reservation,ledger['fixture']['fixture']['fixture']['fixture']['create'])
 recognition_receivable=Account.plain_objects.create(tenant=case.tenant,chart_of_accounts=case.chart,code='130505',name='Synthetic reviewed receivable',type='ASSET')

 if os.environ.get('LARGE_LEDGER_CATALOG')=='1':
  from apps.domain_business.comercial.services.reservation_fiscal import review_reservation
  account_max=max(Account.plain_objects.filter(tenant=case.tenant).values_list('pk',flat=True),key=lambda value:value.int).int
  Account.plain_objects.bulk_create([Account(id=uuid.UUID(int=account_max+1+i),tenant=case.tenant,chart_of_accounts=case.chart,code='BROWSER-PAGE-'+str(i),name='Synthetic paged account '+str(i),type='ASSET') for i in range(530)])
  for i in range(45):
   extra=Reservation.plain_objects.create(id=uuid.UUID(int=billing_reservation.pk.int+1+i),tenant=case.tenant,customer_id=uuid.uuid4(),content_type_id=billing_reservation.content_type_id,object_id=uuid.uuid4(),start_date=billing_reservation.start_date,end_date=billing_reservation.end_date,status='CONFIRMED',total_price='1.00')
   review_reservation(actor=case.user,provider_id=case.provider.pk,reservation_id=extra.pk,items=[{'item_id':str(uuid.uuid4()),'net':'1.00','tax':'0.00','tax_category':'EXCLUDED','policy_reference':'synthetic-page:1'}],evidence_digest='b'*64,confirmed=True,expected_revision=0)

else:
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
if os.environ.get('NATIVE_PURCHASE_FIXTURE')=='1':credentials['native_template']=native_accounts
if os.environ.get('LEDGER_BROWSER')=='1':credentials.update(ledger_date=timezone.localdate().isoformat(),provider_id=str(case.provider.pk),reservation_id=str(billing_reservation.pk),recognition_receivable_id=str(recognition_receivable.pk),recognition_revenue_id=str(case.b.pk))
if os.environ.get('OPENING_LINK_BROWSER')=='1':credentials.update(opening_existing_journal_id=str(opening_existing.pk),opening_existing_hash=opening_existing.system_hash)
if os.environ.get('PAYROLL_BROWSER')=='1':
 helper=runpy.run_path(str(ROOT/'BACKEND/deployment/tests/payroll_fixture.py'))
 credentials['payroll']=helper['install'](case,fixture['fixture']['create'])
if os.environ.get('OPERATIONAL_COST_FIXTURE')=='1':
 helper=runpy.run_path(str(ROOT/'BACKEND/deployment/tests/operational_cost_fixture.py'))
 credentials['payroll_cost']=helper['install'](case,fixture['fixture']['create'],credentials['payroll'])
if os.environ.get('HOTEL_BROWSER')=='1':
 helper=runpy.run_path(str(ROOT/'BACKEND/deployment/tests/hotel_metrics_fixture.py'))
 credentials['hotel']=helper['install'](case,fixture['fixture']['create'])
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
