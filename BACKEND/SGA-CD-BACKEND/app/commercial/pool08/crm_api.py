"""SGA-owned CRM API using its existing workspace authority and contact IDs."""
from fastapi import Depends,Request,HTTPException
from app.api import deps
from app.services.workspace_service import access_for
from .api import router
from .identity import resolve_access
from .access_protocol import AccessFault
from .contract import MAX_BYTES,decode,ContractRejected
from .crm import CRM,CRMError
from .crm_store import Store

def failure(exc):
    return HTTPException(exc.status,{'code':str(exc),**getattr(exc,'safe',{})},headers={'Cache-Control':'no-store'})
def service(request:Request,db=Depends(deps.get_db),user=Depends(deps.get_current_active_user)):
    allowed={'q','offset','limit','stage'} if request.method=='GET' else set()
    if set(request.query_params)-allowed or any(len(request.query_params.getlist(k))!=1 for k in request.query_params):raise HTTPException(400,'Contexto de empresa no permitido.')
    def current():
        access=resolve_access(db,user)
        if not access.session()['capability_permissions'].get('crm.prospect.manage'):raise CRMError('CRM_PERMISSION_REQUIRED',403)
        return access
    try:
        current()
        workspace=access_for(db,user)
        def member(ref):
            fresh=current()
            if ref is None:
                rows,truncated=fresh.team()
                from app.models.user import Usuario
                return [{'actor_ref':r['actor_ref'],'display_name':(db.get(Usuario,int(r['actor_ref'])).nombre_completo or db.get(Usuario,int(r['actor_ref'])).nombre_usuario),'local_roles':r['local_roles']} for r in rows]
            try:return bool(fresh.subject(str(ref)))
            except AccessFault:return False
        return CRM(Store(db,workspace),actor=user.id,authorize=current,member=member)
    except (CRMError,AccessFault) as exc:raise failure(exc) from None

def run(action):
    try:return action()
    except (CRMError,AccessFault) as exc:raise failure(exc) from None

@router.get('/crm/context')
def crm_context(crm=Depends(service)):return run(crm.context)
@router.get('/crm/contacts')
def crm_list(q:str='',offset:int=0,limit:int=50,crm=Depends(service)):
    return run(lambda:crm.list(q,offset,limit))
@router.get('/crm/contacts/{contact_id}')
def crm_get(contact_id:str,crm=Depends(service)):return run(lambda:crm.get(contact_id))
@router.get('/crm/contacts/{contact_id}/history')
def crm_history(contact_id:str,offset:int=0,crm=Depends(service)):return run(lambda:crm.history(contact_id,offset))
@router.post('/crm/commands')
async def crm_command(request:Request,crm=Depends(service)):
    if request.headers.get('content-type','').split(';')[0].strip().lower()!='application/json':raise HTTPException(415,'Usa application/json.')
    raw=bytearray()
    async for chunk in request.stream():
        if len(raw)+len(chunk)>MAX_BYTES:raise HTTPException(413,'BODY_LIMIT')
        raw.extend(chunk)
    try:body=decode(bytes(raw))
    except ContractRejected:raise HTTPException(400,'INVALID_JSON') from None
    return run(lambda:crm.command(body))

@router.get('/crm/receipts/{request_id}')
def crm_receipt(request_id:str,crm=Depends(service)):return run(lambda:crm.receipt(request_id))

# Opportunities retain the exact CRM identity and permission boundary.
from .opportunities import Opportunities
from .opportunity_store import Store as OpportunityStore

def opportunity_service(crm):return Opportunities(OpportunityStore(crm.store),crm)

@router.get('/crm/opportunities')
def opportunities_list(q:str='',stage:str='',offset:int=0,limit:int=30,crm=Depends(service)):
    return run(lambda:opportunity_service(crm).list(q,stage,offset,limit))
@router.get('/crm/opportunities/{opportunity_id}')
def opportunity_get(opportunity_id:str,crm=Depends(service)):
    return run(lambda:opportunity_service(crm).get(opportunity_id))
@router.get('/crm/opportunities/{opportunity_id}/history')
def opportunity_history(opportunity_id:str,offset:int=0,crm=Depends(service)):
    return run(lambda:opportunity_service(crm).history(opportunity_id,offset))
@router.get('/crm/opportunity-receipts/{request_id}')
def opportunity_receipt(request_id:str,crm=Depends(service)):
    return run(lambda:opportunity_service(crm).receipt(request_id))
@router.post('/crm/opportunity-commands')
async def opportunity_command(request:Request,crm=Depends(service)):
    if request.headers.get('content-type','').split(';')[0].strip().lower()!='application/json':raise HTTPException(415,'Usa application/json.')
    raw=bytearray()
    async for chunk in request.stream():
        if len(raw)+len(chunk)>MAX_BYTES:raise HTTPException(413,'BODY_LIMIT')
        raw.extend(chunk)
    try:body=decode(bytes(raw))
    except ContractRejected:raise HTTPException(400,'INVALID_JSON') from None
    return run(lambda:opportunity_service(crm).command(body))

from .pricing import Pricing
from .pricing_store import Store as PriceStore

def pricing_service(crm):return Pricing(PriceStore(crm.store),crm)

@router.get('/crm/prices')
def prices_list(q:str='',offset:int=0,limit:int=30,crm=Depends(service)):
    return run(lambda:pricing_service(crm).list(q,offset,limit))
@router.get('/crm/prices/{item_id}')
def price_get(item_id:str,crm=Depends(service)):
    return run(lambda:pricing_service(crm).get(item_id))
@router.get('/crm/prices/{item_id}/history')
def price_history(item_id:str,offset:int=0,crm=Depends(service)):
    return run(lambda:pricing_service(crm).history(item_id,offset))
@router.get('/crm/price-receipts/{request_id}')
def price_receipt(request_id:str,crm=Depends(service)):
    return run(lambda:pricing_service(crm).receipt(request_id))
@router.post('/crm/price-commands')
async def price_command(request:Request,crm=Depends(service)):
    if request.headers.get('content-type','').split(';')[0].strip().lower()!='application/json':raise HTTPException(415,'Usa application/json.')
    raw=bytearray()
    async for chunk in request.stream():
        if len(raw)+len(chunk)>MAX_BYTES:raise HTTPException(413,'BODY_LIMIT')
        raw.extend(chunk)
    try:body=decode(bytes(raw))
    except ContractRejected:raise HTTPException(400,'INVALID_JSON') from None
    return run(lambda:pricing_service(crm).command(body))

from .quotations import Quotations
from .quotation_store import Store as QuoteStore

def quotation_service(crm):return make_quotations(crm)

@router.get('/crm/quotations')
def quotations_list(q:str='',offset:int=0,limit:int=30,crm=Depends(service)):
    return run(lambda:quotation_service(crm).list(q,offset,limit))
@router.get('/crm/quotations/{quotation_id}')
def quotation_get(quotation_id:str,crm=Depends(service)):
    return run(lambda:quotation_service(crm).get(quotation_id))
@router.get('/crm/quotations/{quotation_id}/history')
def quotation_history(quotation_id:str,offset:int=0,crm=Depends(service)):
    return run(lambda:quotation_service(crm).history(quotation_id,offset))
@router.get('/crm/quotation-receipts/{request_id}')
def quotation_receipt(request_id:str,crm=Depends(service)):
    return run(lambda:quotation_service(crm).receipt(request_id))
@router.post('/crm/quotation-commands')
async def quotation_command(request:Request,crm=Depends(service)):
    if request.headers.get('content-type','').split(';')[0].strip().lower()!='application/json':raise HTTPException(415,'Usa application/json.')
    raw=bytearray()
    async for chunk in request.stream():
        if len(raw)+len(chunk)>MAX_BYTES:raise HTTPException(413,'BODY_LIMIT')
        raw.extend(chunk)
    try:body=decode(bytes(raw))
    except ContractRejected:raise HTTPException(400,'INVALID_JSON') from None
    return run(lambda:quotation_service(crm).command(body))


from .pricing import Pricing
from .pricing_store import Store as PriceStore
from .quotation_capacity import Capacity
from .quotation_media import Media,MAX_MEDIA
from .quotation_models import CommercialQuotation

def make_quotations(crm):
    pricing=Pricing(PriceStore(crm.store),crm);store=QuoteStore(crm.store)
    return Quotations(store,crm,pricing,Capacity(crm),Media(store,pricing))

@router.get('/crm/quotation-resources')
def quotation_resources(crm=Depends(service)):return run(lambda:make_quotations(crm).capacity.resources())
@router.post('/crm/quotation-media/{asset_id}')
async def quotation_media_upload(asset_id:str,request:Request,crm=Depends(service)):
    raw=bytearray()
    async for chunk in request.stream():
        if len(raw)+len(chunk)>MAX_MEDIA:raise HTTPException(413,'QUOTE_MEDIA_LIMIT')
        raw.extend(chunk)
    return run(lambda:make_quotations(crm).media.upload(asset_id,bytes(raw),request.headers.get('content-type','').split(';')[0]))
@router.get('/crm/quotation-media/{asset_id}')
def quotation_media_get(asset_id:str,crm=Depends(service)):
    from fastapi.responses import Response
    def get():
        data,mime=make_quotations(crm).media.bytes(asset_id);return Response(data,media_type=mime,headers={'Cache-Control':'no-store','X-Content-Type-Options':'nosniff','Content-Security-Policy':"default-src 'none'"})
    return run(get)

def public_quotation(request,db,ref):
    from app.models.user import Usuario
    uuid_ref(ref);row=db.query(CommercialQuotation).filter_by(id=ref).first()
    if not row or row.document.get('status')=='CAPACITY_POLICY':raise CRMError('QUOTE_LINK_DENIED',403)
    issuer=row.document.get('issuer_ref');user=db.get(Usuario,int(issuer)) if isinstance(issuer,str) and issuer.isdecimal() else None
    if user is None:raise CRMError('QUOTE_LINK_DENIED',403)
    return make_quotations(service(request,db,user))
from .opportunities import uuid_ref
@router.get('/quote-links/{quotation_id}/{link_id}')
def public_quote_view(quotation_id:str,link_id:str,request:Request,db=Depends(deps.get_db)):
    return run(lambda:public_quotation(request,db,quotation_id).link_view(quotation_id,link_id,request.headers.get('x-quote-token'))[2])
@router.post('/quote-links/{quotation_id}/{link_id}')
async def public_quote_accept(quotation_id:str,link_id:str,request:Request,db=Depends(deps.get_db)):
    if request.headers.get('content-type','').split(';')[0].strip().lower()!='application/json':raise HTTPException(415,'Usa application/json.')
    raw=bytearray()
    async for chunk in request.stream():
        if len(raw)+len(chunk)>MAX_BYTES:raise HTTPException(413,'BODY_LIMIT')
        raw.extend(chunk)
    raw=bytes(raw)
    try:body=decode(raw)
    except ContractRejected:raise HTTPException(400,'INVALID_JSON') from None
    return run(lambda:public_quotation(request,db,quotation_id).accept_link(quotation_id,link_id,request.headers.get('x-quote-token'),body))
@router.get('/quote-links/{quotation_id}/{link_id}/media/{asset_id}')
def public_quote_media(quotation_id:str,link_id:str,asset_id:str,request:Request,db=Depends(deps.get_db)):
    from fastapi.responses import Response
    def get():
        q=public_quotation(request,db,quotation_id);item,link,view=q.link_view(quotation_id,link_id,request.headers.get('x-quote-token'))
        if asset_id not in [x['id'] for x in item['content']['media']]:raise CRMError('QUOTE_LINK_DENIED',403)
        if q.media.get(asset_id)!=next(x for x in item['content']['media'] if x['id']==asset_id):raise CRMError('QUOTE_MEDIA_CHANGED',503)
        data,mime=q.media.bytes(asset_id);return Response(data,media_type=mime,headers={'Cache-Control':'no-store','X-Content-Type-Options':'nosniff','Content-Security-Policy':"default-src 'none'"})
    return run(get)
from .sales_store import Store as SaleStore
from .sales_saga import SalesSaga
from .sales_operations import Operations as SaleOperations
from .sales_bridge import Bridge as SaleBridge

def make_sales(crm,request):
    quotes=make_quotations(crm);return SalesSaga(SaleStore(crm.store),quotes,SaleOperations(quotes),SaleBridge(crm,request))
@router.get('/crm/sales')
def sales_list(request:Request,q:str='',offset:int=0,limit:int=30,crm=Depends(service)):return run(lambda:make_sales(crm,request).list(q,offset,limit))
@router.get('/crm/sales/{sale_id}')
def sale_get(sale_id:str,request:Request,crm=Depends(service)):return run(lambda:make_sales(crm,request).get(sale_id))
@router.get('/crm/sales/{sale_id}/history')
def sale_history(sale_id:str,request:Request,offset:int=0,crm=Depends(service)):return run(lambda:make_sales(crm,request).history(sale_id,offset))
@router.get('/crm/sale-receipts/{request_id}')
def sale_receipt(request_id:str,request:Request,crm=Depends(service)):return run(lambda:make_sales(crm,request).receipt(request_id))
async def sale_body(request):
    if request.headers.get('content-type','').split(';')[0].strip().lower()!='application/json':raise HTTPException(415,'Usa application/json.')
    raw=bytearray()
    async for chunk in request.stream():
        if len(raw)+len(chunk)>MAX_BYTES:raise HTTPException(413,'BODY_LIMIT')
        raw.extend(chunk)
    try:return decode(bytes(raw))
    except ContractRejected:raise HTTPException(400,'INVALID_JSON') from None
@router.post('/crm/sale-commands')
async def sale_command(request:Request,crm=Depends(service)):
    body=await sale_body(request);return run(lambda:make_sales(crm,request).command(body))
@router.get('/crm/sale-ledger/context')
def sale_context(request:Request,crm=Depends(service)):
    from .source_protocol import wrap
    return run(lambda:wrap(SaleBridge(crm,request).context(),{}))
@router.post('/crm/sale-ledger/scopes')
async def sale_scopes(request:Request,crm=Depends(service)):
    body=await sale_body(request)
    if body!={}:raise HTTPException(422,'INVALID_SOURCE_COMMAND')
    return run(lambda:SaleBridge(crm,request).rpc('scopes',{}))
@router.post('/crm/sale-ledger/accounts')
async def sale_accounts(request:Request,crm=Depends(service)):
    body=await sale_body(request)
    if not isinstance(body,dict) or set(body)!={'provider_id'}:raise HTTPException(422,'INVALID_SOURCE_COMMAND')
    uuid_ref(body['provider_id']);return run(lambda:SaleBridge(crm,request).rpc('accounts',{},body['provider_id']))
@router.api_route('/crm/sale-ledger/session/{action}',methods=['GET','POST'])
async def sale_session(action:str,request:Request,crm=Depends(service)):
    if (request.method=='GET')!=(action=='status'):raise HTTPException(405,'METHOD_NOT_ALLOWED')
    body=await sale_body(request) if request.method=='POST' else None
    from fastapi.responses import JSONResponse
    def call():
        data,cookies=SaleBridge(crm,request).session(action,body);response=JSONResponse(data,headers={'Cache-Control':'no-store'})
        for cookie in cookies:response.headers.append('Set-Cookie',cookie)
        return response
    return run(call)

from .payments import Payments
from .payment_store import Store as PaymentStore
def make_payments(crm,request):return Payments(PaymentStore(crm.store),make_sales(crm,request))
@router.get('/crm/payments')
def payments_list(request:Request,q:str='',offset:int=0,limit:int=30,crm=Depends(service)):return run(lambda:make_payments(crm,request).list(q,offset,limit))
@router.get('/crm/payments/{payment_id}')
def payment_get(payment_id:str,request:Request,crm=Depends(service)):return run(lambda:make_payments(crm,request).get(payment_id))
@router.get('/crm/payments/{payment_id}/history')
def payment_history(payment_id:str,request:Request,offset:int=0,crm=Depends(service)):return run(lambda:make_payments(crm,request).history(payment_id,offset))
@router.get('/crm/payment-receipts/{request_id}')
def payment_receipt(request_id:str,request:Request,crm=Depends(service)):return run(lambda:make_payments(crm,request).receipt(request_id))
@router.post('/crm/payment-commands')
async def payment_command(request:Request,crm=Depends(service)):
    body=await sale_body(request);return run(lambda:make_payments(crm,request).command(body))

@router.post('/crm/after-sales/{operation}')
async def after_sales_command(operation:str,request:Request,crm=Depends(service)):
    body=await sale_body(request)
    if not isinstance(body,dict) or set(body)!={'provider_id','data'} or not isinstance(body['data'],dict):raise HTTPException(422,'INVALID_AFTER_SALES_FIELDS')
    uuid_ref(body['provider_id'])
    if operation=='followup':
        data=body['data']
        if set(data)!={'request_id','contact_id','expected_revision','reservation_id','title','due_at','responsible_ref'}:raise HTTPException(422,'INVALID_AFTER_SALES_FIELDS')
        run(lambda:SaleBridge(crm,request).rpc('after-sales',{'operation':'case_state','data':{'reservation_id':data['reservation_id']}},body['provider_id']))
        from .after_sales_followup import record_followup
        result=run(lambda:record_followup(crm,data))
        return {'result':result,'reservation_ref':data['reservation_id'],'customer_binding_verified':False,'outbound_message_sent':False}
    return run(lambda:SaleBridge(crm,request).rpc('after-sales',{'operation':operation,'data':body['data']},body['provider_id']))

from .landings import Landings,public_html,HEADERS as LANDING_HEADERS
from .landing_store import Store as LandingStore
from fastapi.responses import HTMLResponse
def make_landings(crm):return Landings(LandingStore(crm.store),crm)
@router.get('/crm/landings')
def landing_list(offset:int=0,limit:int=30,crm=Depends(service)):return run(lambda:make_landings(crm).list(offset,limit))
@router.get('/crm/landings/{item_id}')
def landing_get(item_id:str,crm=Depends(service)):return run(lambda:make_landings(crm).get(item_id))
@router.get('/crm/landings/{item_id}/history')
def landing_history(item_id:str,crm=Depends(service)):return run(lambda:make_landings(crm).history(item_id))
@router.get('/crm/landings/{item_id}/preview')
def landing_preview(item_id:str,crm=Depends(service)):return HTMLResponse(run(lambda:make_landings(crm).preview(item_id)),headers={**LANDING_HEADERS,'X-Robots-Tag':'noindex, nofollow'})
@router.get('/crm/landing-receipts/{request_id}')
def landing_receipt(request_id:str,crm=Depends(service)):return run(lambda:make_landings(crm).receipt(request_id))
@router.post('/crm/landing-commands')
async def landing_command(request:Request,crm=Depends(service)):
    body=await sale_body(request);return run(lambda:make_landings(crm).command(body))
from . import landing_capture_api as capture_api
@router.get('/landing-pages/{item_id}')
def landing_public(item_id:str,request:Request,db=Depends(deps.get_db)):
    try:
        body,browser=run(lambda:capture_api.public_document(db,item_id,request.url.path,str(request.base_url).rstrip('/'),request.cookies.get(capture_api.COOKIE,''),request.query_params))
        response=HTMLResponse(body,headers=capture_api.PUBLIC_HEADERS)
        if browser:response.set_cookie(capture_api.COOKIE,browser,path=request.url.path.rstrip('/'),max_age=3600,httponly=True,secure=request.url.scheme=='https',samesite='lax')
        return response
    except (CRMError,AccessFault,HTTPException) as exc:return HTMLResponse(capture_api.error_html(getattr(exc,'code',str(exc))),status_code=getattr(exc,'status',getattr(exc,'status_code',503)),headers=capture_api.PUBLIC_HEADERS)
@router.post('/landing-pages/{item_id}/{operation}')
async def landing_capture(item_id:str,operation:str,request:Request,db=Depends(deps.get_db)):
    try:
        run(lambda:capture_api.same_origin(request.headers.get('origin'),str(request.base_url).rstrip('/')))
        raw=bytearray()
        async for chunk in request.stream():
            if len(raw)+len(chunk)>12000:raise HTTPException(413,'PUBLIC_FORM_TOO_LARGE')
            raw.extend(chunk)
        data=run(lambda:capture_api.parse_form(bytes(raw),request.headers.get('content-type','')))
        handler=run(lambda:capture_api.service(capture_api.owner_crm(db,item_id)))
        if operation=='capture':
            result=run(lambda:handler.submit(item_id,data,request.cookies.get(capture_api.COOKIE,''),request.client.host));body=capture_api.receipt_html(item_id,result,request.url.path)
        elif operation=='withdraw' and set(data)=={'reference','proof'}:
            run(lambda:handler.withdraw(item_id,data['reference'],data['proof']));body='<!doctype html><html lang="es"><meta charset="utf-8"><body style="background:#071b34;color:white"><h1>Declaración retirada</h1><p>No se enviaron mensajes.</p></body></html>'
        else:raise HTTPException(422,'INVALID_PUBLIC_FORM')
        return HTMLResponse(body,headers=capture_api.PUBLIC_HEADERS)
    except (CRMError,AccessFault,HTTPException) as exc:return HTMLResponse(capture_api.error_html(getattr(exc,'code',str(exc))),status_code=getattr(exc,'status',getattr(exc,'status_code',503)),headers=capture_api.PUBLIC_HEADERS)
@router.get('/crm/landings/{item_id}/captures')
def landing_capture_metrics(item_id:str,offset:int=0,crm=Depends(service)):
    return run(lambda:capture_api.service(crm).metrics(item_id,offset))

from . import library_api
@router.get('/crm/library')
def library_list(offset:int=0,crm=Depends(service)):return run(lambda:library_api.service(crm).list(offset))
@router.get('/crm/library/{item_id}')
def library_get(item_id:str,crm=Depends(service)):return run(lambda:library_api.service(crm).get(item_id))
@router.get('/crm/library-receipts/{request_id}')
def library_receipt(request_id:str,crm=Depends(service)):return run(lambda:library_api.service(crm).receipt(request_id))
@router.post('/crm/library-commands')
async def library_command(request:Request,crm=Depends(service)):
    body=await sale_body(request);return run(lambda:library_api.service(crm).command(body))
@router.post('/crm/library-upload')
async def library_upload(request:Request,crm=Depends(service)):
    lib=library_api.service(crm);run(lib.authority);meta=run(lambda:library_api.upload_metadata(request.headers.get('x-library-metadata')));raw=bytearray()
    async for chunk in request.stream():
        if len(raw)+len(chunk)>library_api.MAX_UPLOAD:raise HTTPException(413,'LIBRARY_UPLOAD_LIMIT')
        raw.extend(chunk)
    return run(lambda:lib.upload(meta,bytes(raw),request.headers.get('content-type','').split(';')[0].strip()))
@router.get('/crm/library/{item_id}/versions/{version}/{kind}')
def library_bytes(item_id:str,version:int,kind:str,crm=Depends(service)):
    data,mime=run(lambda:library_api.service(crm).bytes(item_id,version,kind));return __import__('fastapi').Response(data,media_type=mime,headers={**library_api.HEADERS,'Content-Disposition':'attachment; filename="original.bin"' if kind=='original' else 'inline'})
@router.get('/media-library/{item_id}/{version}')
def library_public(item_id:str,version:int,db=Depends(deps.get_db)):
    try:
        data,mime=library_api.public_service(db,item_id).bytes(item_id,version,'delivery',public=True);return __import__('fastapi').Response(data,media_type=mime,headers=library_api.HEADERS)
    except (CRMError,AccessFault,HTTPException):raise HTTPException(404,'MEDIA_UNAVAILABLE',headers=library_api.HEADERS) from None


from . import generation_api
@router.get('/crm/generation-profiles')
def generation_profiles(crm=Depends(service)):return run(lambda:generation_api.service(crm).profiles())
@router.get('/crm/generation')
def generation_list(offset:int=0,crm=Depends(service)):return run(lambda:generation_api.service(crm).list(offset))
@router.get('/crm/generation/{job_id}')
def generation_get(job_id:str,crm=Depends(service)):return run(lambda:generation_api.service(crm).view(job_id))
@router.get('/crm/generation-receipts/{request_id}')
def generation_receipt(request_id:str,crm=Depends(service)):return run(lambda:generation_api.service(crm).receipt(request_id))
@router.get('/crm/generation/{job_id}/history')
def generation_history(job_id:str,crm=Depends(service)):return run(lambda:generation_api.service(crm).history(job_id))
@router.get('/crm/generation/{job_id}/result')
def generation_result(job_id:str,crm=Depends(service)):
    data,mime=run(lambda:generation_api.service(crm).bytes(job_id));return __import__('fastapi').Response(data,media_type=mime,headers=generation_api.HEADERS)
@router.post('/crm/generation-commands')
async def generation_command(request:Request,crm=Depends(service)):
    body=await sale_body(request);return run(lambda:generation_api.service(crm).command(body))

from . import email_campaign_api
@router.get('/crm/email-campaigns')
def email_campaign_list(crm=Depends(service)):return run(lambda:email_campaign_api.service(crm).list())
@router.get('/crm/email-campaigns/{campaign_id}')
def email_campaign_get(campaign_id:str,crm=Depends(service)):return run(lambda:email_campaign_api.service(crm).get(campaign_id))
@router.get('/crm/email-campaigns/{campaign_id}/preview/{contact_id}')
def email_campaign_preview(campaign_id:str,contact_id:str,crm=Depends(service)):return run(lambda:email_campaign_api.service(crm).preview(campaign_id,contact_id))
@router.get('/crm/email-campaign-receipts/{request_id}')
def email_campaign_receipt(request_id:str,crm=Depends(service)):return run(lambda:email_campaign_api.service(crm).receipt(request_id))
@router.post('/crm/email-campaign-commands')
async def email_campaign_command(request:Request,crm=Depends(service)):
    body=await sale_body(request);return run(lambda:email_campaign_api.service(crm).command(body))
@router.api_route('/email-unsubscribe/{campaign_id}/{contact_id}/{proof}/',methods=['GET','POST'])
async def email_unsubscribe(request:Request,campaign_id:str,contact_id:str,proof:str,db=Depends(deps.get_db)):
    from fastapi.responses import HTMLResponse,JSONResponse
    engine=run(lambda:email_campaign_api.public(db,campaign_id))
    if request.method=='GET':return HTMLResponse(run(lambda:email_campaign_api.form(engine,campaign_id,contact_id,proof)),headers=email_campaign_api.HEADERS)
    raw=bytearray()
    async for chunk in request.stream():
        if len(raw)+len(chunk)>100:raise HTTPException(413,'BODY_LIMIT')
        raw.extend(chunk)
    if bytes(raw) not in (b'confirm=yes',b'List-Unsubscribe=One-Click'):raise HTTPException(422,'UNSUBSCRIBE_CONFIRM_REQUIRED')
    return JSONResponse(run(lambda:engine.unsubscribe(campaign_id,contact_id,proof)),headers=email_campaign_api.HEADERS)

@router.post('/email-receipts/{campaign_id}/')
async def email_provider_receipt(request:Request,campaign_id:str,db=Depends(deps.get_db)):
    body=await sale_body(request)
    if body.get('campaign_id')!=campaign_id:raise HTTPException(422,'EMAIL_PROVIDER_EVENT_MISMATCH')
    return run(lambda:email_campaign_api.receipt_service(db,campaign_id).provider_receipt(body,request.headers.get('X-Email-Receipt-Signature','')))

from . import mobile_message_api
@router.get('/crm/mobile-messages')
def mobile_message_list(crm=Depends(service)):return run(lambda:mobile_message_api.service(crm).list())
@router.get('/crm/mobile-messages/{job_id}')
def mobile_message_get(job_id:str,crm=Depends(service)):return run(lambda:mobile_message_api.service(crm).get(job_id))
@router.get('/crm/mobile-message-receipts/{request_id}')
def mobile_message_receipt(request_id:str,crm=Depends(service)):return run(lambda:mobile_message_api.service(crm).receipt(request_id))
@router.post('/crm/mobile-message-commands')
async def mobile_message_command(request:Request,crm=Depends(service)):
    body=await sale_body(request);return run(lambda:mobile_message_api.service(crm).command(body))
@router.post('/mobile-message-reports/{job_id}/')
async def mobile_message_report(request:Request,job_id:str,db=Depends(deps.get_db)):
    body=await sale_body(request)
    if body.get('job_id')!=job_id:raise HTTPException(422,'MOBILE_PROVIDER_EVENT_MISMATCH')
    return run(lambda:mobile_message_api.receiver(db,job_id).provider_receipt(body,request.headers.get('X-Mobile-Receipt-Signature','')))

@router.get('/crm/mobile-messages/{job_id}/history')
def mobile_message_history(job_id:str,crm=Depends(service)):return run(lambda:mobile_message_api.service(crm).history(job_id))

from . import publishing_api
@router.get('/crm/publications')
def publication_list(crm=Depends(service)):return run(lambda:publishing_api.service(crm).list())
@router.get('/crm/publications/{job_id}')
def publication_get(job_id:str,crm=Depends(service)):return run(lambda:publishing_api.service(crm).get(job_id))
@router.get('/crm/publications/{job_id}/history')
def publication_history(job_id:str,crm=Depends(service)):return run(lambda:publishing_api.service(crm).history(job_id))
@router.get('/crm/publication-receipts/{request_id}')
def publication_receipt(request_id:str,crm=Depends(service)):return run(lambda:publishing_api.service(crm).receipt(request_id))
@router.post('/crm/publication-commands')
async def publication_command(request:Request,crm=Depends(service)):
    body=await sale_body(request);return run(lambda:publishing_api.service(crm).command(body))

from . import inbox_api
@router.get('/crm/inbox')
def inbox_list(crm=Depends(service)):return run(lambda:inbox_api.service(crm).list())
@router.get('/crm/inbox/{job_id}')
def inbox_get(job_id:str,crm=Depends(service)):return run(lambda:inbox_api.service(crm).get(job_id))
@router.get('/crm/inbox/{job_id}/history')
def inbox_history(job_id:str,crm=Depends(service)):return run(lambda:inbox_api.service(crm).history(job_id))
@router.get('/crm/inbox-receipts/{request_id}')
def inbox_receipt(request_id:str,crm=Depends(service)):return run(lambda:inbox_api.service(crm).receipt(request_id))
@router.post('/crm/inbox-commands')
async def inbox_command(request:Request,crm=Depends(service)):
    body=await sale_body(request);return run(lambda:inbox_api.service(crm).command(body))
@router.post('/crm/inbox-ingress')
async def inbox_ingress(request:Request,crm=Depends(service)):
    body=await sale_body(request);return run(lambda:inbox_api.service(crm).ingest(body,request.headers.get('X-Inbox-Connector-Signature','')))

@router.post('/crm/inbox-native-ingress')
async def inbox_native(request:Request,crm=Depends(service)):
    body=await sale_body(request);return run(lambda:inbox_api.native(crm,body))
@router.post('/crm/inbox-source-sync')
async def inbox_source_sync(request:Request,crm=Depends(service)):
    body=await sale_body(request);return run(lambda:inbox_api.source_sync(crm,body))

from . import ads_api
@router.get('/crm/ads')
def ads_list(crm=Depends(service)):return run(lambda:ads_api.service(crm).list())
@router.get('/crm/ads/{job_id}')
def ads_get(job_id:str,crm=Depends(service)):return run(lambda:ads_api.service(crm).get(job_id))
@router.get('/crm/ads/{job_id}/history')
def ads_history(job_id:str,crm=Depends(service)):return run(lambda:ads_api.service(crm).history(job_id))
@router.get('/crm/ads-receipts/{request_id}')
def ads_receipt(request_id:str,crm=Depends(service)):return run(lambda:ads_api.service(crm).receipt(request_id))
@router.post('/crm/ads-commands')
async def ads_command(request:Request,crm=Depends(service)):
    body=await sale_body(request);return run(lambda:ads_api.service(crm).command(body))

from . import army_api
@router.get('/crm/army')
def army_list(crm=Depends(service)):return run(lambda:army_api.service(crm).list())
@router.get('/crm/army/{job_id}')
def army_get(job_id:str,crm=Depends(service)):return run(lambda:army_api.service(crm).get(job_id))
@router.get('/crm/army/{job_id}/history')
def army_history(job_id:str,crm=Depends(service)):return run(lambda:army_api.service(crm).history(job_id))
@router.get('/crm/army/{job_id}/soup')
def army_soup(job_id:str,crm=Depends(service)):return run(lambda:army_api.soup(crm,job_id))
@router.get('/crm/army-receipts/{request_id}')
def army_receipt(request_id:str,crm=Depends(service)):return run(lambda:army_api.service(crm).receipt(request_id))
@router.post('/crm/army-commands')
async def army_command(request:Request,crm=Depends(service)):
    body=await sale_body(request);return run(lambda:army_api.command(crm,body))

from . import analytics_api
@router.get('/crm/analytics')
def analytics_list(crm=Depends(service)):return run(lambda:analytics_api.service(crm).list())
@router.get('/crm/analytics/{job_id}')
def analytics_get(job_id:str,crm=Depends(service)):return run(lambda:analytics_api.service(crm).get(job_id))
@router.get('/crm/analytics/{job_id}/history')
def analytics_history(job_id:str,crm=Depends(service)):return run(lambda:analytics_api.service(crm).history(job_id))
@router.get('/crm/analytics-receipts/{request_id}')
def analytics_receipt(request_id:str,crm=Depends(service)):return run(lambda:analytics_api.service(crm).receipt(request_id))
@router.post('/crm/analytics-commands')
async def analytics_command(request:Request,crm=Depends(service)):
    body=await sale_body(request);return run(lambda:analytics_api.service(crm,request).command(body))

from .operations import Operations
@router.get('/crm/operations')
def operations_health(crm=Depends(service)):
 from starlette.responses import JSONResponse
 return JSONResponse(run(lambda:Operations(crm).health()),headers={'Cache-Control':'no-store'})
@router.get('/crm/operations/{domain}/{record_id}')
def operations_trace(domain:str,record_id:str,crm=Depends(service)):
 from starlette.responses import JSONResponse
 return JSONResponse(run(lambda:Operations(crm).trace(domain,record_id)),headers={'Cache-Control':'no-store'})
