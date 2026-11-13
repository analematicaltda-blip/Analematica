"""Own authenticated CRM API. No identity, financial or delivery authority is inferred."""
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError,MethodNotAllowed,APIException
from apps.core_erp.tenancy.models import Tenant
from apps.turismo.models import TourismProvider
from .api import Pool08View
from .identity import resolve_access
from .access_protocol import AccessFault
from .crm import CRM,CRMError
from .crm_store import Store

class CRMView(Pool08View):
    def service(self,request):
        allowed={'provider_id'} | ({'q','offset','limit','stage'} if request.method=='GET' else set())
        if set(request.query_params)-allowed or any(len(request.query_params.getlist(k))!=1 for k in request.query_params) or 'provider_id' not in request.query_params:
            raise ValidationError('Selecciona una sola empresa verificada.')
        provider=request.query_params['provider_id']
        def current():
            access=resolve_access(request.user,provider)
            if not access.session()['capability_permissions'].get('crm.prospect.manage'):
                raise CRMError('CRM_PERMISSION_REQUIRED',403)
            return access
        access=current()
        def member(ref):
            fresh=current()
            if ref is None:
                rows,truncated=fresh.team()
                from django.contrib.auth import get_user_model
                users=get_user_model().objects.in_bulk([int(r['actor_ref']) for r in rows])
                return [{'actor_ref':r['actor_ref'],'display_name':(users[int(r['actor_ref'])].get_full_name() or users[int(r['actor_ref'])].get_username()),'local_roles':r['local_roles']} for r in rows]
            try:return bool(fresh.subject(str(ref)))
            except AccessFault:return False
        store=Store(Tenant.objects.get(pk=access.tenant),TourismProvider.objects.get(pk=provider),request.user)
        return CRM(store,actor=access.actor,authorize=current,member=member)
    def handle_exception(self,exception):
        if isinstance(exception,(CRMError,AccessFault)):
            return Response({'code':str(exception),**getattr(exception,'safe',{})},status=exception.status)
        return super().handle_exception(exception)
    def get(self,request,contact_id=None,section='contacts'):
        if section=='commands':raise MethodNotAllowed('GET')
        service=self.service(request)
        if section=='context':return Response(service.context())
        if section=='receipt':return Response(service.receipt(contact_id))
        try:offset=int(request.query_params.get('offset','0'));limit=int(request.query_params.get('limit','50'))
        except ValueError:raise CRMError('INVALID_PAGE') from None
        if section=='history':return Response(service.history(contact_id,offset))
        if contact_id:return Response(service.get(contact_id))
        return Response(service.list(request.query_params.get('q',''),offset,limit))
    def post(self,request,section='commands',**kwargs):
        if section!='commands':raise MethodNotAllowed('POST')
        return Response(self.service(request).command(request.data))

class CRMCompaniesView(Pool08View):
    def get(self,request):
        from api.models import BusinessUserProfile
        from apps.turismo.models import VerifiedCompanyLink
        from django.db.models import Q
        providers=BusinessUserProfile.objects.filter(user_id=request.user.pk).values_list('provider_id',flat=True)
        rows=VerifiedCompanyLink.objects.filter(Q(administrator_id=request.user.pk)|Q(provider_id__in=providers)).select_related('provider').order_by('provider_id')[:101]
        result=[]
        for row in rows:
            try:
                access=resolve_access(request.user,str(row.provider_id))
                if access.session()['capability_permissions'].get('crm.prospect.manage'):
                    result.append({'provider_id':str(row.provider_id),'name':row.provider.name})
            except (AccessFault,CRMError,APIException):continue
        return Response({'companies':result[:100],'truncated':len(rows)>100,'cross_system_access_granted':False})

# Reuse the audited native password/CSRF/MFA session, with an owned route boundary.
import os
from .contract import SYSTEM
from rest_framework.exceptions import NotFound
from apps.prestadores.mi_negocio.web_session import SessionStatus,SessionLogin,SessionMfa,SessionRecovery,SessionLogout
class NativeSessionBoundary:
    def initial(self,request,*args,**kwargs):
        if os.environ.get('BACKEND_SERVICE')!=SYSTEM:raise NotFound()
        return super().initial(request,*args,**kwargs)
class CRMSessionStatus(NativeSessionBoundary,SessionStatus):pass
class CRMSessionLogin(NativeSessionBoundary,SessionLogin):pass
class CRMSessionMfa(NativeSessionBoundary,SessionMfa):pass
class CRMSessionRecovery(NativeSessionBoundary,SessionRecovery):pass
class CRMSessionLogout(NativeSessionBoundary,SessionLogout):pass

from .opportunities import Opportunities
from .opportunity_store import Store as OpportunityStore
class OpportunitiesView(CRMView):
    def opportunity_service(self,request):
        crm=self.service(request)
        return Opportunities(OpportunityStore(crm.store),crm)
    def get(self,request,opportunity_id=None,section='list'):
        if section=='commands':raise MethodNotAllowed('GET')
        service=self.opportunity_service(request)
        if section=='receipt':return Response(service.receipt(opportunity_id))
        try:offset=int(request.query_params.get('offset','0'));limit=int(request.query_params.get('limit','30'))
        except ValueError:raise CRMError('INVALID_PAGE') from None
        if section=='history':return Response(service.history(opportunity_id,offset))
        if opportunity_id:return Response(service.get(opportunity_id))
        return Response(service.list(request.query_params.get('q',''),request.query_params.get('stage',''),offset,limit))
    def post(self,request,section='commands',**kwargs):
        if section!='commands':raise MethodNotAllowed('POST')
        return Response(self.opportunity_service(request).command(request.data))

from .pricing import Pricing
from .pricing_store import Store as PriceStore
class PricesView(CRMView):
    def pricing_service(self,request):
        crm=self.service(request)
        return Pricing(PriceStore(crm.store),crm)
    def get(self,request,item_id=None,section='list'):
        if section=='commands':raise MethodNotAllowed('GET')
        service=self.pricing_service(request)
        if section=='receipt':return Response(service.receipt(item_id))
        try:offset=int(request.query_params.get('offset','0'));limit=int(request.query_params.get('limit','30'))
        except ValueError:raise CRMError('INVALID_PAGE') from None
        if section=='history':return Response(service.history(item_id,offset))
        if item_id:return Response(service.get(item_id))
        return Response(service.list(request.query_params.get('q',''),offset,limit))
    def post(self,request,section='commands',**kwargs):
        if section!='commands':raise MethodNotAllowed('POST')
        return Response(self.pricing_service(request).command(request.data))

from .quotations import Quotations
from .quotation_store import Store as QuoteStore
class QuotationsView(CRMView):
    def quotation_service(self,request):
        crm=self.service(request)
        return make_quotations(crm)
    def get(self,request,quotation_id=None,section='list'):
        if section=='commands':raise MethodNotAllowed('GET')
        service=self.quotation_service(request)
        if section=='receipt':return Response(service.receipt(quotation_id))
        try:offset=int(request.query_params.get('offset','0'));limit=int(request.query_params.get('limit','30'))
        except ValueError:raise CRMError('INVALID_PAGE') from None
        if section=='history':return Response(service.history(quotation_id,offset))
        if quotation_id:return Response(service.get(quotation_id))
        return Response(service.list(request.query_params.get('q',''),offset,limit))
    def post(self,request,section='commands',**kwargs):
        if section!='commands':raise MethodNotAllowed('POST')
        return Response(self.quotation_service(request).command(request.data))


from .pricing import Pricing
from .pricing_store import Store as PriceStore
from .quotation_capacity import Capacity
from .quotation_media import Media,MAX_MEDIA
from .quotation_models import CommercialQuotation

def make_quotations(crm):
    pricing=Pricing(PriceStore(crm.store),crm);store=QuoteStore(crm.store)
    return Quotations(store,crm,pricing,Capacity(crm),Media(store,pricing))

from rest_framework.parsers import BaseParser
from rest_framework.permissions import AllowAny
from django.http import QueryDict,HttpResponse
from types import SimpleNamespace
class QuoteMediaParser(BaseParser):
    media_type='*/*'
    def parse(self,stream,media_type=None,parser_context=None):
        data=stream.read(MAX_MEDIA+1)
        if len(data)>MAX_MEDIA:raise CRMError('QUOTE_MEDIA_LIMIT',413)
        return data
class QuoteResourcesView(CRMView):
    def get(self,request):return Response(make_quotations(self.service(request)).capacity.resources())
class QuoteMediaView(CRMView):
    parser_classes=[QuoteMediaParser]
    def get(self,request,asset_id):
        data,mime=make_quotations(self.service(request)).media.bytes(asset_id);response=HttpResponse(data,content_type=mime);response['Cache-Control']='no-store';response['X-Content-Type-Options']='nosniff';response['Content-Security-Policy']="default-src 'none'";return response
    def post(self,request,asset_id):return Response(make_quotations(self.service(request)).media.upload(asset_id,request.data,request.content_type))
class PublicQuoteView(CRMView):
    authentication_classes=[]
    permission_classes=[AllowAny]
    def scoped_service(self,request,quotation_id):
        from django.contrib.auth import get_user_model
        from .opportunities import uuid_ref
        uuid_ref(quotation_id)
        if request.query_params:raise CRMError('QUOTE_LINK_DENIED',403)
        row=CommercialQuotation.objects.filter(pk=quotation_id).first()
        if not row or row.document.get('status')=='CAPACITY_POLICY':raise CRMError('QUOTE_LINK_DENIED',403)
        user=get_user_model().objects.filter(pk=row.document.get('issuer_ref'),is_active=True).first()
        if not user:raise CRMError('QUOTE_LINK_DENIED',403)
        query=QueryDict('',mutable=True);query['provider_id']=row.provider_ref
        return make_quotations(CRMView().service(SimpleNamespace(user=user,query_params=query,method=request.method)))
    def get(self,request,quotation_id,link_id,asset_id=None):
        q=self.scoped_service(request,quotation_id);item,link,view=q.link_view(quotation_id,link_id,request.headers.get('x-quote-token'))
        if asset_id is None:return Response(view)
        if asset_id not in [x['id'] for x in item['content']['media']]:raise CRMError('QUOTE_LINK_DENIED',403)
        if q.media.get(asset_id)!=next(x for x in item['content']['media'] if x['id']==asset_id):raise CRMError('QUOTE_MEDIA_CHANGED',503)
        data,mime=q.media.bytes(asset_id);response=HttpResponse(data,content_type=mime);response['Cache-Control']='no-store';response['X-Content-Type-Options']='nosniff';response['Content-Security-Policy']="default-src 'none'";return response
    def post(self,request,quotation_id,link_id,asset_id=None):
        if asset_id:raise MethodNotAllowed('POST')
        return Response(self.scoped_service(request,quotation_id).accept_link(quotation_id,link_id,request.headers.get('x-quote-token'),request.data))

from .sales import Sales
from .sales_store import Store as SaleStore
from .sales_ledger import Ledger as SaleLedger
from .sales_operations import Operations as SaleOperations
def make_sales(crm):
    quotes=make_quotations(crm);return Sales(SaleStore(crm.store),quotes,SaleLedger(crm),SaleOperations(quotes))
class SalesView(CRMView):
    def get(self,request,sale_id=None,section='list'):
        sales=make_sales(self.service(request))
        if section=='accounts':return Response(sales.ledger.catalog())
        if section=='receipt':return Response(sales.receipt(sale_id))
        try:offset=int(request.query_params.get('offset','0'));limit=int(request.query_params.get('limit','30'))
        except ValueError:raise CRMError('INVALID_PAGE') from None
        if section=='history':return Response(sales.history(sale_id,offset))
        return Response(sales.get(sale_id) if sale_id else sales.list(request.query_params.get('q',''),offset,limit))
    def post(self,request,section='commands',**kwargs):
        if section!='commands':raise MethodNotAllowed('POST')
        try:
            engine=make_sales(self.service(request))
            if isinstance(request.data,dict) and request.data.get('sale_id'):
                source=engine.get(request.data['sale_id'])['source']
                if source.get('_external'):raise CRMError('SOURCE_SALES_WORKFLOW_REQUIRED',409)
            return Response(engine.command(request.data))
        except __import__('apps.core_erp.accounting.exceptions',fromlist=['AccountingError']).AccountingError:raise CRMError('SALE_ACCOUNTING_REVIEW_REQUIRED',409) from None

from .payments import Payments
from .payment_store import Store as PaymentStore

def make_payments(crm):return Payments(PaymentStore(crm.store),make_sales(crm))

class PaymentsView(CRMView):
    def get(self,request,payment_id=None,section='list'):
        if section=='commands':raise MethodNotAllowed('GET')
        engine=make_payments(self.service(request))
        try:offset=int(request.query_params.get('offset','0'));limit=int(request.query_params.get('limit','30'))
        except ValueError:raise CRMError('INVALID_PAGE') from None
        if section=='receipt':return Response(engine.receipt(payment_id))
        if section=='history':return Response(engine.history(payment_id,offset))
        if payment_id:return Response(engine.get(payment_id))
        return Response(engine.list(request.query_params.get('q',''),offset,limit))
    def post(self,request,payment_id=None,section='list'):
        if section!='commands':raise MethodNotAllowed('POST')
        return Response(make_payments(self.service(request)).command(request.data))

class AfterSalesView(CRMView):
    def post(self,request,operation):
        from .after_sales import execute
        return Response(execute(self.service(request),request.user,operation,request.data))

from .landings import Landings,public_html,HEADERS as LANDING_HEADERS
from .landing_store import Store as LandingStore
class LandingsView(CRMView):
    def builder(self,request):
        crm=self.service(request);return Landings(LandingStore(crm.store),crm)
    def get(self,request,item_id=None,section='list'):
        builder=self.builder(request)
        if section=='preview':
            from django.http import HttpResponse
            return HttpResponse(builder.preview(item_id),content_type='text/html; charset=utf-8',headers={**LANDING_HEADERS,'X-Robots-Tag':'noindex, nofollow'})
        if section=='history':return Response(builder.history(item_id))
        if section=='receipt':return Response(builder.receipt(item_id))
        if item_id:return Response(builder.get(item_id))
        try:offset=int(request.query_params.get('offset','0'));limit=int(request.query_params.get('limit','30'))
        except ValueError:raise CRMError('INVALID_PAGE') from None
        return Response(builder.list(offset,limit))
    def post(self,request,section='commands'):
        return Response(self.builder(request).command(request.data))
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
class PublicLandingView(APIView):
    authentication_classes=[]
    permission_classes=[AllowAny]
    def get(self,request,item_id):
        from django.http import HttpResponse
        try:return HttpResponse(public_html(LandingStore,None,item_id),content_type='text/html; charset=utf-8',headers=LANDING_HEADERS)
        except CRMError as exc:return Response({'code':str(exc)},status=exc.status,headers=LANDING_HEADERS)

from . import landing_capture_api as capture_api
class CaptureMetricsView(CRMView):
    def get(self,request,item_id):
        try:offset=int(request.query_params.get('offset','0'))
        except ValueError:raise CRMError('INVALID_PAGE') from None
        return Response(capture_api.service(self.service(request)).metrics(item_id,offset))
class PublicLandingView(PublicLandingView):
    def get(self,request,item_id,operation=None):
        from django.http import HttpResponse
        if operation is not None:return HttpResponse(capture_api.error_html('METHOD_NOT_ALLOWED'),status=405,content_type='text/html; charset=utf-8',headers={**capture_api.PUBLIC_HEADERS,'Allow':'POST'})
        try:
            origin=request.build_absolute_uri('/').rstrip('/');body,browser=capture_api.public_document(None,item_id,request.path,origin,request.COOKIES.get(capture_api.COOKIE,''),request.query_params)
            response=HttpResponse(body,content_type='text/html; charset=utf-8',headers=capture_api.PUBLIC_HEADERS)
            if browser:response.set_cookie(capture_api.COOKIE,browser,path=request.path.rstrip('/'),max_age=3600,httponly=True,secure=request.is_secure(),samesite='Lax')
            return response
        except CRMError as exc:return HttpResponse(capture_api.error_html(str(exc)),status=exc.status,content_type='text/html; charset=utf-8',headers=capture_api.PUBLIC_HEADERS)
    def post(self,request,item_id,operation=None):
        from django.http import HttpResponse
        if operation is None:return HttpResponse(capture_api.error_html('METHOD_NOT_ALLOWED'),status=405,content_type='text/html; charset=utf-8',headers={**capture_api.PUBLIC_HEADERS,'Allow':'GET'})
        try:
            capture_api.same_origin(request.headers.get('Origin'),request.build_absolute_uri('/').rstrip('/'))
            data=capture_api.parse_form(request._request.read(12001),request.content_type);handler=capture_api.service(capture_api.owner_crm(None,item_id))
            if operation=='capture':
                result=handler.submit(item_id,data,request.COOKIES.get(capture_api.COOKIE,''),request.META.get('REMOTE_ADDR',''));body=capture_api.receipt_html(item_id,result,request.path)
            elif operation=='withdraw' and set(data)=={'reference','proof'}:
                handler.withdraw(item_id,data['reference'],data['proof']);body='<!doctype html><html lang="es"><meta charset="utf-8"><body style="background:#071b34;color:white"><h1>Declaración retirada</h1><p>No se enviaron mensajes.</p></body></html>'
            else:raise CRMError('INVALID_PUBLIC_FORM')
            return HttpResponse(body,content_type='text/html; charset=utf-8',headers=capture_api.PUBLIC_HEADERS)
        except CRMError as exc:return HttpResponse(capture_api.error_html(str(exc)),status=exc.status,content_type='text/html; charset=utf-8',headers=capture_api.PUBLIC_HEADERS)

from . import library_api
class LibraryView(CRMView):
    def get(self,request,item_id=None,section='list',version=None,kind=None):
        lib=library_api.service(self.service(request))
        if section=='receipt':return Response(lib.receipt(item_id))
        if section=='bytes':
            from django.http import HttpResponse
            data,mime=lib.bytes(item_id,version,kind);return HttpResponse(data,content_type=mime,headers={**library_api.HEADERS,'Content-Disposition':'attachment; filename="original.bin"' if kind=='original' else 'inline'})
        if item_id:return Response(lib.get(item_id))
        try:offset=int(request.query_params.get('offset','0'))
        except ValueError:raise CRMError('INVALID_PAGE') from None
        return Response(lib.list(offset))
    def post(self,request,section='commands'):
        lib=library_api.service(self.service(request));lib.authority()
        if section=='upload':
            meta=library_api.upload_metadata(request.headers.get('X-Library-Metadata'));raw=request._request.read(library_api.MAX_UPLOAD+1)
            if len(raw)>library_api.MAX_UPLOAD:raise CRMError('LIBRARY_UPLOAD_LIMIT',413)
            return Response(lib.upload(meta,raw,request.content_type))
        return Response(lib.command(request.data))
class PublicLibraryView(APIView):
    authentication_classes=[]
    permission_classes=[AllowAny]
    def get(self,request,item_id,version):
        from django.http import HttpResponse
        try:
            data,mime=library_api.public_service(None,item_id).bytes(item_id,version,'delivery',public=True);return HttpResponse(data,content_type=mime,headers=library_api.HEADERS)
        except (CRMError,AccessFault):return Response({'code':'MEDIA_UNAVAILABLE'},status=404,headers=library_api.HEADERS)


from . import generation_api
class GenerationView(CRMView):
    def get(self,request,job_id=None,section='list'):
        gen=generation_api.service(self.service(request))
        if section=='profiles':return Response(gen.profiles())
        if section=='receipt':return Response(gen.receipt(job_id))
        if section=='history':return Response(gen.history(job_id))
        if section=='result':
            from django.http import HttpResponse
            data,mime=gen.bytes(job_id);return HttpResponse(data,content_type=mime,headers=generation_api.HEADERS)
        if job_id:return Response(gen.view(job_id))
        try:offset=int(request.query_params.get('offset','0'))
        except ValueError:raise CRMError('INVALID_PAGE') from None
        return Response(gen.list(offset))
    def post(self,request):return Response(generation_api.service(self.service(request)).command(request.data))

from . import email_campaign_api
class EmailCampaignView(CRMView):
    def get(self,request,campaign_id=None,contact_id=None,section='list'):
        e=email_campaign_api.service(self.service(request))
        if section=='receipt':return Response(e.receipt(campaign_id))
        if section=='preview':return Response(e.preview(campaign_id,contact_id))
        return Response(e.get(campaign_id) if campaign_id else e.list())
    def post(self,request):return Response(email_campaign_api.service(self.service(request)).command(request.data))
class PublicEmailUnsubscribeView(APIView):
    authentication_classes=[]
    permission_classes=[AllowAny]
    def get(self,request,campaign_id,contact_id,proof):
        from django.http import HttpResponse
        try:return HttpResponse(email_campaign_api.form(email_campaign_api.public(None,campaign_id),campaign_id,contact_id,proof),content_type='text/html; charset=utf-8',headers=email_campaign_api.HEADERS)
        except CRMError:return Response({'code':'UNSUBSCRIBE_UNAVAILABLE'},status=404,headers=email_campaign_api.HEADERS)
    def post(self,request,campaign_id,contact_id,proof):
        raw=request._request.read(101)
        if raw not in (b'confirm=yes',b'List-Unsubscribe=One-Click'):return Response({'code':'UNSUBSCRIBE_CONFIRM_REQUIRED'},status=422,headers=email_campaign_api.HEADERS)
        try:return Response(email_campaign_api.public(None,campaign_id).unsubscribe(campaign_id,contact_id,proof),headers=email_campaign_api.HEADERS)
        except CRMError:return Response({'code':'UNSUBSCRIBE_UNAVAILABLE'},status=404,headers=email_campaign_api.HEADERS)

class PublicEmailReceiptView(APIView):
    parser_classes=Pool08View.parser_classes
    renderer_classes=Pool08View.renderer_classes
    authentication_classes=[]
    permission_classes=[AllowAny]
    def post(self,request,campaign_id):
        try:
            if request.data.get('campaign_id')!=campaign_id:raise CRMError('EMAIL_PROVIDER_EVENT_MISMATCH')
            return Response(email_campaign_api.receipt_service(None,campaign_id).provider_receipt(request.data,request.headers.get('X-Email-Receipt-Signature','')),headers=email_campaign_api.HEADERS)
        except CRMError as exc:return Response({'code':str(exc)},status=exc.status,headers=email_campaign_api.HEADERS)

from . import mobile_message_api
class MobileMessageView(CRMView):
    def get(self,request,job_id=None,section='list'):
        e=mobile_message_api.service(self.service(request))
        if section=='receipt':return Response(e.receipt(job_id))
        if section=='history':return Response(e.history(job_id))
        return Response(e.get(job_id) if job_id else e.list())
    def post(self,request):return Response(mobile_message_api.service(self.service(request)).command(request.data))
class PublicMobileReportView(APIView):
    authentication_classes=[]
    permission_classes=[AllowAny]
    parser_classes=Pool08View.parser_classes
    renderer_classes=Pool08View.renderer_classes
    def post(self,request,job_id):
        try:
            if request.data.get('job_id')!=job_id:raise CRMError('MOBILE_PROVIDER_EVENT_MISMATCH')
            return Response(mobile_message_api.receiver(None,job_id).provider_receipt(request.data,request.headers.get('X-Mobile-Receipt-Signature','')),headers=mobile_message_api.HEADERS)
        except CRMError as exc:return Response({'code':str(exc)},status=exc.status,headers=mobile_message_api.HEADERS)

from . import publishing_api
class PublishingView(CRMView):
    def get(self,request,job_id=None,section='list'):
        e=publishing_api.service(self.service(request))
        if section=='receipt':return Response(e.receipt(job_id))
        if section=='history':return Response(e.history(job_id))
        return Response(e.get(job_id) if job_id else e.list())
    def post(self,request):return Response(publishing_api.service(self.service(request)).command(request.data))

from . import inbox_api
class InboxView(CRMView):
    def get(self,request,job_id=None,section='list'):
        e=inbox_api.service(self.service(request))
        if section=='receipt':return Response(e.receipt(job_id))
        if section=='history':return Response(e.history(job_id))
        return Response(e.get(job_id) if job_id else e.list())
    def post(self,request,section='command'):
        crm=self.service(request)
        if section=='native':return Response(inbox_api.native(crm,request.data))
        if section=='source-sync':return Response(inbox_api.source_sync(crm,request.data))
        e=inbox_api.service(crm)
        return Response(e.ingest(request.data,request.headers.get('X-Inbox-Connector-Signature','')) if section=='ingress' else e.command(request.data))

from . import ads_api
class AdsView(CRMView):
    def get(self,request,job_id=None,section='list'):
        e=ads_api.service(self.service(request))
        if section=='receipt':return Response(e.receipt(job_id))
        if section=='history':return Response(e.history(job_id))
        return Response(e.get(job_id) if job_id else e.list())
    def post(self,request):return Response(ads_api.service(self.service(request)).command(request.data))

from . import army_api
class ArmyView(CRMView):
    def get(self,request,job_id=None,section='list'):
        crm=self.service(request);e=army_api.service(crm)
        if section=='receipt':return Response(e.receipt(job_id))
        if section=='history':return Response(e.history(job_id))
        if section=='soup':return Response(army_api.soup(crm,job_id))
        return Response(e.get(job_id) if job_id else e.list())
    def post(self,request):return Response(army_api.command(self.service(request),request.data))

from . import analytics_api
class AnalyticsView(CRMView):
    def get(self,request,job_id=None,section='list'):
        e=analytics_api.service(self.service(request))
        if section=='receipt':return Response(e.receipt(job_id))
        if section=='history':return Response(e.history(job_id))
        return Response(e.get(job_id) if job_id else e.list())
    def post(self,request):return Response(analytics_api.service(self.service(request)).command(request.data))

from .operations import Operations
class OperationsView(CRMView):
    http_method_names=['get','head','options']
    def get(self,request,domain=None,record_id=None):
        engine=Operations(self.service(request))
        return Response(engine.trace(domain,str(record_id)) if domain is not None else engine.health(),headers={'Cache-Control':'no-store'})
