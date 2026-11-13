"""Disposable loopback WSGI harness, native backends only; never deploy."""
import argparse,os,sys,runpy,json,importlib
from pathlib import Path
parser=argparse.ArgumentParser();parser.add_argument('--system',choices=['analematica','erp-tur','turismo'],required=True);parser.add_argument('--directory',type=Path,required=True);args=parser.parse_args()
root=Path(__file__).resolve().parents[3]
fixture=runpy.run_path(str(Path(__file__).with_name('accounting_adapter_check.py')),run_name='army_native_http_fixture')
case=fixture['AdapterTests']();case.setUp()
from django.db import connection
from apps.core_erp.outbox_models import EventAuditLog
if EventAuditLog._meta.db_table not in connection.introspection.table_names():
 with connection.schema_editor() as editor:editor.create_model(EventAuditLog)
from django.conf import settings
from django.urls import clear_url_caches
from rest_framework_simplejwt.tokens import AccessToken
from django.utils import timezone
os.environ['BACKEND_SERVICE']=args.system
if args.system=='analematica':
 sys.path.insert(0,str(root/'BACKEND/ANALEMATICA-BACKEND'));settings.ROOT_URLCONF='deployment.army_urls'
else:
 sys.modules.pop('tourism_urls',None);settings.ROOT_URLCONF='tourism_urls'
clear_url_caches();case.post()
# CRM integration tables belong only to this disposable fixture database.
if args.system in ('analematica','erp-tur'):
 settings.ERP_WEB_SESSION_ENABLED=True
 module=importlib.import_module(('apps.admin_plataforma.gestion_comercial.pool08' if args.system=='analematica' else 'apps.prestadores.mi_negocio.gestion_comercial.pool08')+'.crm_models')
 from apps.prestadores.mi_negocio.gestion_operativa.modulos_genericos.clientes.models import Cliente
 identity=importlib.import_module(module.__package__+'.identity_models')
 from api.models import BusinessUserProfile
 quotations=importlib.import_module(('apps.admin_plataforma.gestion_comercial.pool08' if args.system=='analematica' else 'apps.prestadores.mi_negocio.gestion_comercial.pool08')+'.quotation_models')
 prices=importlib.import_module(('apps.admin_plataforma.gestion_comercial.pool08' if args.system=='analematica' else 'apps.prestadores.mi_negocio.gestion_comercial.pool08')+'.pricing_models')
 opportunities=importlib.import_module(('apps.admin_plataforma.gestion_comercial.pool08' if args.system=='analematica' else 'apps.prestadores.mi_negocio.gestion_comercial.pool08')+'.opportunity_models')
 payments=importlib.import_module(('apps.admin_plataforma.gestion_comercial.pool08' if args.system=='analematica' else 'apps.prestadores.mi_negocio.gestion_comercial.pool08')+'.payment_models')
 sales=importlib.import_module(('apps.admin_plataforma.gestion_comercial.pool08' if args.system=='analematica' else 'apps.prestadores.mi_negocio.gestion_comercial.pool08')+'.sales_models')
 from apps.turismo.models import TourismService,Reservation,AvailabilityHold
 legacy=[TourismService,Reservation,AvailabilityHold]
 if args.system=='erp-tur':
  from apps.prestadores.mi_negocio.gestion_comercial.sales.models import Opportunity,StageHistory
  legacy.extend([Opportunity,StageHistory])
 with connection.schema_editor() as editor:
  for model in (identity.CommercialGrant,identity.CommercialConsent,identity.CommercialIdentityAlias,identity.CommercialPolicyEvent,Cliente,BusinessUserProfile,module.CRMContact,module.CRMEvent,opportunities.CommercialOpportunity,opportunities.OpportunityEvent,prices.CommercialPrice,prices.PriceEvent,quotations.CommercialQuotation,quotations.QuotationEvent,quotations.QuotationAsset,sales.CommercialSale,sales.SaleEvent,sales.SaleSourceBinding,payments.CommercialPayment,payments.PaymentEvent,*legacy):
   if model._meta.db_table not in connection.introspection.table_names():editor.create_model(model)

if args.system in ('analematica','erp-tur'):
 landings=importlib.import_module(('apps.admin_plataforma.gestion_comercial.pool08' if args.system=='analematica' else 'apps.prestadores.mi_negocio.gestion_comercial.pool08')+'.landing_models')
 with connection.schema_editor() as editor:
  for model in (landings.CommercialLanding,landings.LandingEvent):
   if model._meta.db_table not in connection.introspection.table_names():editor.create_model(model)

if args.system in ('analematica','erp-tur'):
 captures=importlib.import_module(('apps.admin_plataforma.gestion_comercial.pool08' if args.system=='analematica' else 'apps.prestadores.mi_negocio.gestion_comercial.pool08')+'.capture_models')
 with connection.schema_editor() as editor:
  for model in (captures.LandingCapture,captures.CaptureEvent):
   if model._meta.db_table not in connection.introspection.table_names():editor.create_model(model)

if args.system in ('analematica','erp-tur'):
 library=importlib.import_module(('apps.admin_plataforma.gestion_comercial.pool08' if args.system=='analematica' else 'apps.prestadores.mi_negocio.gestion_comercial.pool08')+'.library_models')
 with connection.schema_editor() as editor:
  for model in (library.LibraryItem,library.LibraryEvent,library.LibraryBlob):
   if model._meta.db_table not in connection.introspection.table_names():editor.create_model(model)

if args.system in ('analematica','erp-tur'):
 generation=importlib.import_module(('apps.admin_plataforma.gestion_comercial.pool08' if args.system=='analematica' else 'apps.prestadores.mi_negocio.gestion_comercial.pool08')+'.generation_models')
 with connection.schema_editor() as editor:
  for model in (generation.GenerationJob,generation.GenerationEvent,generation.GenerationResult):
   if model._meta.db_table not in connection.introspection.table_names():editor.create_model(model)

if args.system in ('analematica','erp-tur'):
 email_models=importlib.import_module(('apps.admin_plataforma.gestion_comercial.pool08' if args.system=='analematica' else 'apps.prestadores.mi_negocio.gestion_comercial.pool08')+'.email_campaign_models')
 with connection.schema_editor() as editor:
  for model in (email_models.EmailCampaignRecord,email_models.EmailCampaignEvent):
   if model._meta.db_table not in connection.introspection.table_names():editor.create_model(model)

if args.system in ('analematica','erp-tur'):
 mobile_models=importlib.import_module(('apps.admin_plataforma.gestion_comercial.pool08' if args.system=='analematica' else 'apps.prestadores.mi_negocio.gestion_comercial.pool08')+'.mobile_message_models')
 with connection.schema_editor() as editor:
  for model in (mobile_models.MobileMessageRecord,mobile_models.MobileMessageEvent):
   if model._meta.db_table not in connection.introspection.table_names():editor.create_model(model)

if args.system in ('analematica','erp-tur'):
 publication_models=importlib.import_module(('apps.admin_plataforma.gestion_comercial.pool08' if args.system=='analematica' else 'apps.prestadores.mi_negocio.gestion_comercial.pool08')+'.publishing_models')
 with connection.schema_editor() as editor:
  for model in (publication_models.PublishingRecord,publication_models.PublishingEvent):
   if model._meta.db_table not in connection.introspection.table_names():editor.create_model(model)

if args.system in ('analematica','erp-tur'):
 inbox_models=importlib.import_module(('apps.admin_plataforma.gestion_comercial.pool08' if args.system=='analematica' else 'apps.prestadores.mi_negocio.gestion_comercial.pool08')+'.inbox_models')
 with connection.schema_editor() as editor:
  for model in (inbox_models.InboxRecord,inbox_models.InboxEvent):
   if model._meta.db_table not in connection.introspection.table_names():editor.create_model(model)

if args.system in ('analematica','erp-tur'):
 ads_models=importlib.import_module(('apps.admin_plataforma.gestion_comercial.pool08' if args.system=='analematica' else 'apps.prestadores.mi_negocio.gestion_comercial.pool08')+'.ads_models')
 with connection.schema_editor() as editor:
  for model in (ads_models.AdsRecord,ads_models.AdsEvent):
   if model._meta.db_table not in connection.introspection.table_names():editor.create_model(model)

if args.system in ('analematica','erp-tur'):
 commercial_army_models=importlib.import_module(('apps.admin_plataforma.gestion_comercial.pool08' if args.system=='analematica' else 'apps.prestadores.mi_negocio.gestion_comercial.pool08')+'.army_models')
 with connection.schema_editor() as editor:
  for model in (commercial_army_models.ArmyRecord,commercial_army_models.ArmyEvent):
   if model._meta.db_table not in connection.introspection.table_names():editor.create_model(model)

if args.system in ('analematica','erp-tur'):
 analytics_models=importlib.import_module(('apps.admin_plataforma.gestion_comercial.pool08' if args.system=='analematica' else 'apps.prestadores.mi_negocio.gestion_comercial.pool08')+'.analytics_models')
 with connection.schema_editor() as editor:
  for model in (analytics_models.AnalyticsRecord,analytics_models.AnalyticsEvent):
   if model._meta.db_table not in connection.introspection.table_names():editor.create_model(model)

# Cancellation sources belong to this disposable commercial fixture, not production.
if args.system in ('analematica','erp-tur'):
 from apps.prestadores.mi_negocio.gestion_operativa.modulos_genericos.reservas.models import PoliticaCancelacion
 from apps.domain_business.operativa.models import Reservation as CoreReservation
 visiting=set()
 def after_model(model):
  model=model._meta.concrete_model
  if model in visiting or model._meta.db_table in connection.introspection.table_names():return
  visiting.add(model)
  for field in model._meta.local_fields:
   if field.is_relation and field.remote_field and field.remote_field.model is not model:after_model(field.remote_field.model)
  for field in model._meta.local_many_to_many:after_model(field.remote_field.model)
  with connection.schema_editor() as editor:editor.create_model(model)
  visiting.remove(model)
 for model in (PoliticaCancelacion,CoreReservation):after_model(model)

credentials={'actor_ref':str(case.user.pk),'token':str(AccessToken.for_user(case.user)),'other_token':str(AccessToken.for_user(case.other)),
 'provider_id':str(case.provider.pk),'company_id':str(case.tenant.pk),'day':timezone.localdate().isoformat(),
 'sgacd_modules_loaded':any(name.startswith('app.services') or name.startswith('app.agents') for name in sys.modules)}
if args.system in ('analematica','erp-tur'):
 from django.contrib.auth import get_user_model
 staff=get_user_model()(username='commercial-access-synthetic-staff',role='BUSINESS_EMPLOYEE',is_active=True)
 get_user_model().objects.bulk_create([staff]);BusinessUserProfile.objects.create(user=staff,provider=case.provider,position='Synthetic test only',is_admin=False)
 credentials.update(staff_token=str(AccessToken.for_user(staff)),staff_ref=str(staff.pk))
if args.system in ('analematica','erp-tur'):
 from apps.core_erp.accounting.models import Account
 from datetime import timedelta
 ar=Account.plain_objects.create(tenant=case.tenant,chart_of_accounts=case.chart,code='1305-SALES-TEST',name='Cartera sintética revisada',type='ASSET')
 liability=Account.plain_objects.create(tenant=case.tenant,chart_of_accounts=case.chart,code='2805-SALES-TEST',name='Obligación sintética revisada',type='LIABILITY')
 tax=Account.plain_objects.create(tenant=case.tenant,chart_of_accounts=case.chart,code='2408-SALES-TEST',name='Impuesto sintético revisado',type='LIABILITY')
 settings.COMMERCIAL_SALE_ACCOUNT_POLICIES={str(case.tenant.pk):{'version':'synthetic-http-only','valid_from':(timezone.now()-timedelta(days=1)).isoformat(),'valid_until':(timezone.now()+timedelta(days=1)).isoformat(),'reviewer_ref':str(case.link.reviewed_by_id),'support_digest':'a'*64,'roles':{'receivable':[str(ar.pk)],'revenue':[str(case.b.pk)],'contract_liability':[str(liability.pk)],'tax_liability':[str(tax.pk)]}}}
 credentials['sale_accounts']={'receivable':str(ar.pk),'contra':str(case.b.pk),'tax_liability':str(tax.pk)}
if os.environ.get('GC014_VIDEO_FIXTURE')=='1' and args.system in ('analematica','erp-tur'):
 owned='apps.admin_plataforma.gestion_comercial.pool08' if args.system=='analematica' else 'apps.prestadores.mi_negocio.gestion_comercial.pool08'
 video=importlib.import_module(owned+'.video_composition')
 key=args.system+':'+str(case.tenant.pk)+':'+str(case.provider.pk)
 os.environ['COMMERCIAL_GENERATION_PROFILES']=json.dumps({key:{'video':{'adapter':'ffmpeg-composition','model':'ffmpeg-composition-v1','model_digest':video.fingerprint(),'rights_note':'Synthetic HTTP fixture only','cost_units':100,'max_output_tokens':64}}})
if os.environ.get('GC016_EMAIL_FIXTURE')=='1' and args.system in ('analematica','erp-tur'):
    email_key=args.system+':'+str(case.tenant.pk)+':'+str(case.provider.pk)
    os.environ['COMMERCIAL_EMAIL_POLICIES']=json.dumps({email_key:{'version':'fixture-1','sender_email':'owner@example.test','sender_name':'Empresa sintética','postal_address':'Dirección de laboratorio','public_base_url':'http://localhost','daily_limit':10,'consent_reviewed':True,'allow_dispatch':False,'smtp_host':'127.0.0.1','smtp_port':1025}})
    os.environ['COMMERCIAL_EMAIL_LINK_KEYS']=json.dumps({email_key:'synthetic-email-fixture-key-only-32'})
if os.environ.get('GC017_MOBILE_FIXTURE')=='1' and args.system in ('analematica','erp-tur'):
 from mobile_message_fixture import configure
 configure(args.system,case.tenant.pk,case.provider.pk)
if os.environ.get('GC018_PUBLISH_FIXTURE')=='1' and args.system in ('analematica','erp-tur'):
 from publishing_fixture import configure
 configure(args.system,case.tenant.pk,case.provider.pk)
if os.environ.get('GC019_INBOX_FIXTURE')=='1' and args.system in ('analematica','erp-tur'):
 from inbox_fixture import configure
 configure(args.system,case.tenant.pk,case.provider.pk)
if os.environ.get('GC020_ADS_FIXTURE')=='1' and args.system in ('analematica','erp-tur'):
 from ads_fixture import configure
 configure(args.system,case.tenant.pk,case.provider.pk)
with open(args.directory/'native.json','x',opener=lambda p,f:os.open(p,f,0o600)) as stream:json.dump(credentials,stream)
from django.core.wsgi import get_wsgi_application
from wsgiref.simple_server import make_server,WSGIRequestHandler
class Quiet(WSGIRequestHandler):
 def log_message(self,*args):pass
server=make_server('127.0.0.1',0,get_wsgi_application(),handler_class=Quiet)
print('READY '+str(server.server_port),flush=True);server.serve_forever()
