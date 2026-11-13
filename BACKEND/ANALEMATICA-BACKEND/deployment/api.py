"""Restricted API gateway; frontend files and upstream credentials are never served."""
import os
import re
from contextlib import asynccontextmanager, AsyncExitStack
from urllib.parse import urlsplit
import httpx
from fastapi import FastAPI,Request,HTTPException
from fastapi.responses import Response,JSONResponse

UPSTREAM=os.environ.get('SGACD_API_URL','http://sgacd:8000').rstrip('/')
parsed=urlsplit(UPSTREAM)
if parsed.scheme not in {'http','https'} or parsed.hostname not in {'sgacd','localhost','127.0.0.1','host.docker.internal'} or parsed.username or parsed.password or parsed.path or parsed.query or parsed.fragment:
    raise ValueError('SGACD_API_URL must be a configured internal API origin')

def commercial_origin(value):
    """Configured internal origin only; never selected from request data."""
    if not value:
        return None
    candidate = value.rstrip('/')
    uri = urlsplit(candidate)
    try:
        port = uri.port
    except ValueError:
        raise ValueError('Invalid native commercial port') from None
    if (uri.scheme not in {'http', 'https'} or uri.hostname not in
        {'analematica-army', 'localhost', '127.0.0.1', 'host.docker.internal'} or
        uri.username or uri.password or uri.path or uri.query or uri.fragment or
        any(ord(char) < 33 for char in candidate) or (port is not None and not 1 <= port <= 65535)):
        raise ValueError('ANALEMATICA_COMMERCIAL_API_URL must be a configured internal origin')
    return candidate

@asynccontextmanager
async def lifespan(app):
    origin = commercial_origin(os.environ.get('ANALEMATICA_COMMERCIAL_API_URL', ''))
    async with AsyncExitStack() as stack:
        app.state.upstream = await stack.enter_async_context(httpx.AsyncClient(
            base_url=UPSTREAM, timeout=20, follow_redirects=False, trust_env=False))
        app.state.commercial_upstream = None
        if origin:
            app.state.commercial_upstream = await stack.enter_async_context(httpx.AsyncClient(
                base_url=origin, timeout=20, follow_redirects=False, trust_env=False))
        yield

async def commercial_proxy(path, request):
    tail = path[len('v1/commercial-unified'):].strip('/')
    routes = {'crm/operations':'GET','crm/analytics':'GET','crm/analytics-commands':'POST','crm/army':'GET','crm/army-commands':'POST','crm/ads':'GET','crm/ads-commands':'POST','crm/inbox-native-ingress':'POST','crm/inbox-source-sync':'POST','crm/inbox':'GET','crm/inbox-commands':'POST','crm/inbox-ingress':'POST','crm/publications':'GET','crm/publication-commands':'POST','crm/mobile-messages':'GET','crm/mobile-message-commands':'POST','crm/email-campaigns':'GET','crm/email-campaign-commands':'POST','capabilities': 'GET', 'contract': 'GET', 'intents/validate': 'POST', 'crm/generation-profiles':'GET', 'crm/generation':'GET', 'crm/generation-commands':'POST'}
    if re.fullmatch(r'crm/(?:generation/[a-f0-9-]{36}(?:/(?:history|result))?|generation-receipts/[a-f0-9-]{36})',tail):routes[tail]='GET'
    if re.fullmatch(r'crm/access/(?:context|team|consents|aliases|history|receipts/[a-f0-9-]{36})',tail):routes[tail]='GET'
    if tail=='crm/access/commands':routes[tail]='POST'
    routes.update({'crm/library':'GET','crm/library-commands':'POST','crm/library-upload':'POST','crm/landings':'GET','crm/landing-commands':'POST','crm/context':'GET','crm/contacts':'GET','crm/commands':'POST','crm/opportunities':'GET','crm/opportunity-commands':'POST','crm/prices':'GET','crm/price-commands':'POST','crm/payments':'GET','crm/payment-commands':'POST','crm/sales':'GET','crm/sale-commands':'POST','crm/sale-accounts':'GET','crm/quotations':'GET','crm/quotation-commands':'POST','crm/quotation-resources':'GET','crm/companies':'GET','crm/session/status':'GET','crm/session/login':'POST','crm/session/mfa':'POST','crm/session/recovery':'POST','crm/session/logout':'POST'})
    if re.fullmatch(r'crm/(?:email-campaigns/[a-f0-9-]{36}(?:/preview/(?:[a-f0-9-]{36}|customer:[1-9][0-9]{0,17}))?|email-campaign-receipts/[a-f0-9-]{36})',tail):routes[tail]='GET'
    if re.fullmatch(r'email-unsubscribe/[a-f0-9-]{36}/(?:[a-f0-9-]{36}|customer:[1-9][0-9]{0,17})/[a-f0-9]{64}',tail):routes[tail]=request.method if request.method in ('GET','POST') else 'GET'
    if re.fullmatch(r'crm/contacts/(?:[a-f0-9-]{36}|customer:[0-9]+)(?:/history)?',tail):
        routes[tail]='GET'
    if re.fullmatch(r'crm/receipts/[a-f0-9-]{36}',tail):routes[tail]='GET'
    if re.fullmatch(r'crm/(?:payments/[a-f0-9-]{36}(?:/history)?|payment-receipts/[a-f0-9-]{36}|sales/[a-f0-9-]{36}(?:/history)?|sale-receipts/[a-f0-9-]{36}|quotations/[a-f0-9-]{36}(?:/history)?|quotation-receipts/[a-f0-9-]{36})',tail):routes[tail]='GET'
    if re.fullmatch(r'crm/quotation-media/[a-f0-9-]{36}',tail):routes[tail]=request.method if request.method in ('GET','POST') else 'GET'
    if re.fullmatch(r'quote-links/[a-f0-9-]{36}/[a-f0-9-]{36}(?:/media/[a-f0-9-]{36})?',tail):routes[tail]=request.method if request.method in ('GET','POST') and not ('/media/' in tail and request.method=='POST') else 'GET'
    if re.fullmatch(r'crm/(?:prices/[a-f0-9-]{36}(?:/history)?|price-receipts/[a-f0-9-]{36})',tail):routes[tail]='GET'
    if re.fullmatch(r'crm/(?:opportunities/[a-f0-9-]{36}(?:/history)?|opportunity-receipts/[a-f0-9-]{36})',tail):routes[tail]='GET'
    if re.fullmatch(r'crm/after-sales/[a-z_]{1,64}',tail):routes[tail]='POST'
    if re.fullmatch(r'(?:crm/landings/[a-f0-9-]{36}(?:/(?:history|preview|captures))?|crm/landing-receipts/[a-f0-9-]{36}|landing-pages/[a-f0-9-]{36})',tail):routes[tail]='GET'
    if re.fullmatch(r'landing-pages/[a-f0-9-]{36}/(?:capture|withdraw)',tail):routes[tail]='POST'
    if re.fullmatch(r'(?:crm/library/[a-f0-9-]{36}(?:/versions/[0-9]{1,2}/(?:original|delivery))?|crm/library-receipts/[a-f0-9-]{36}|media-library/[a-f0-9-]{36}/[0-9]{1,2})',tail):routes[tail]='GET'
    if re.fullmatch(r'email-receipts/[a-f0-9-]{36}',tail):routes[tail]='POST'
    if re.fullmatch(r'crm/(?:mobile-messages/[a-f0-9-]{36}(?:/history)?|mobile-message-receipts/[a-f0-9-]{36})',tail):routes[tail]='GET'
    if re.fullmatch(r'mobile-message-reports/[a-f0-9-]{36}',tail):routes[tail]='POST'
    if re.fullmatch(r'crm/(?:publications/[a-f0-9-]{36}(?:/history)?|publication-receipts/[a-f0-9-]{36})',tail):routes[tail]='GET'
    if re.fullmatch(r'crm/(?:inbox/[a-f0-9-]{36}(?:/history)?|inbox-receipts/[a-f0-9-]{36})',tail):routes[tail]='GET'
    if re.fullmatch(r'crm/(?:ads/[a-f0-9-]{36}(?:/history)?|ads-receipts/[a-f0-9-]{36})',tail):routes[tail]='GET'
    if re.fullmatch(r'crm/(?:army/[a-f0-9-]{36}(?:/(?:history|soup))?|army-receipts/[a-f0-9-]{36})',tail):routes[tail]='GET'
    if re.fullmatch(r'crm/operations/[a-z-]{1,30}/[a-f0-9-]{36}',tail):routes[tail]='GET'
    if re.fullmatch(r'crm/(?:analytics/[a-f0-9-]{36}(?:/history)?|analytics-receipts/[a-f0-9-]{36})',tail):routes[tail]='GET'
    if tail not in routes:
        return JSONResponse({'code': 'COMMERCIAL_ROUTE_NOT_FOUND'}, status_code=404,
                            headers={'Cache-Control': 'no-store'})
    if request.method != routes[tail]:
        return JSONResponse({'code': 'COMMERCIAL_METHOD_NOT_ALLOWED'}, status_code=405,
                            headers={'Cache-Control': 'no-store', 'Allow': routes[tail]})
    client = request.app.state.commercial_upstream
    if client is None:
        return JSONResponse({'code': 'NATIVE_COMMERCIAL_ROUTE_REQUIRED',
            'detail': 'Configura el canal al backend nativo de Analemática.',
            'execution_authorized': False}, status_code=503, headers={'Cache-Control': 'no-store'})
    headers = {key: value for key, value in request.headers.items() if key.lower() in
               {'x-inbox-connector-signature', 'x-mobile-receipt-signature', 'x-email-receipt-signature', 'content-type', 'x-quote-token', 'x-correlation-id', 'x-pool08-contract-version', 'x-csrftoken', 'origin', 'x-library-metadata'}}
    authorization = request.headers.get('authorization', '')
    if authorization.startswith(('Bearer ', 'Token ')):
        headers['authorization'] = authorization
    headers['cookie'] = request.headers.get('cookie', '')
    if re.fullmatch(r'landing-pages/[a-f0-9-]{36}/(?:capture|withdraw)',tail):
        if request.headers.get('origin') != str(request.base_url).rstrip('/'):
            return JSONResponse({'code':'PUBLIC_FORM_ORIGIN_REJECTED'},status_code=403,headers={'Cache-Control':'no-store'})
        # Validate the browser hop above; rewrite solely to the fixed configured native origin.
        headers['origin'] = str(client.base_url).rstrip('/')
    headers['accept'] = 'application/json'
    body = bytearray()
    async for chunk in request.stream():
        if len(body) + len(chunk) > (8388608 if tail=='crm/library-upload' else 262144 if tail.startswith('crm/quotation-media/') else 16384):
            return JSONResponse({'code': 'BODY_LIMIT'}, status_code=413,
                                headers={'Cache-Control': 'no-store', 'X-POOL08-Error-Code': 'BODY_LIMIT'})
        body.extend(chunk)
    target = '/api/v1/commercial-unified/' + tail + '/'
    if request.url.query:
        target += '?' + request.url.query
    try:
        async with client.stream(request.method, target, headers=headers, content=bytes(body)) as upstream:
            if 300 <= upstream.status_code < 400:
                return JSONResponse({'code': 'NATIVE_COMMERCIAL_REDIRECT_BLOCKED'}, status_code=502,
                                    headers={'Cache-Control': 'no-store'})
            content = bytearray()
            async for chunk in upstream.aiter_bytes():
                if len(content) + len(chunk) > (16777216 if re.fullmatch(r'(?:crm/generation/[a-f0-9-]{36}/result|crm/library/[a-f0-9-]{36}/versions/[0-9]{1,2}/(?:original|delivery)|media-library/[a-f0-9-]{36}/[0-9]{1,2})',tail) else 524288):
                    return JSONResponse({'code': 'NATIVE_COMMERCIAL_RESPONSE_LIMIT'}, status_code=502,
                                        headers={'Cache-Control': 'no-store'})
                content.extend(chunk)
            allowed = {'content-type', 'www-authenticate', 'retry-after', 'x-correlation-id',
                       'x-pool08-contract-version', 'x-pool08-error-code', 'content-security-policy', 'content-disposition', 'x-content-type-options', 'x-frame-options', 'referrer-policy', 'x-robots-tag'}
            response = Response(content=bytes(content), status_code=upstream.status_code,
                headers={key: value for key, value in upstream.headers.items() if key.lower() in allowed})
            response.headers['Cache-Control'] = 'no-store'
            for cookie in upstream.headers.get_list('set-cookie'):
                response.headers.append('set-cookie', cookie)
            return response
    except httpx.HTTPError:
        return JSONResponse({'code': 'NATIVE_COMMERCIAL_UNAVAILABLE', 'execution_authorized': False},
                            status_code=503, headers={'Cache-Control': 'no-store'})

app=FastAPI(lifespan=lifespan,docs_url=None,redoc_url=None,openapi_url=None)

@app.get('/healthz')
async def health(request:Request):
    try:
        upstream=await request.app.state.upstream.get('/healthz',headers={'cookie':''})
        if upstream.status_code==200 and upstream.json().get('status')=='ok':return {'status':'ok','service':'analematica'}
    except (httpx.HTTPError,ValueError,AttributeError):pass
    return JSONResponse({'status':'unavailable','service':'analematica'},status_code=503)

@app.api_route('/api/{path:path}',methods=['GET','POST','PUT','PATCH','DELETE','OPTIONS','HEAD'])
async def proxy(path:str,request:Request):
    # The owned commercial namespace never falls back to SGA-CD.
    if path == 'v1/commercial-unified' or path.startswith('v1/commercial-unified/'):
        return await commercial_proxy(path, request)
    headers={key:value for key,value in request.headers.items() if key.lower() in {'content-type','accept','cookie','x-correlation-id'}}
    authorization=request.headers.get('authorization','')
    if authorization.startswith(('Bearer ','Token ')):headers['authorization']=authorization
    # Each request's Cookie is explicit; a shared HTTP pool must never replay another user's cookies.
    headers['cookie']=request.headers.get('cookie','')
    chunks=[];size=0
    async for chunk in request.stream():
        size+=len(chunk)
        if size>10*1024*1024:raise HTTPException(413,'Request too large')
        chunks.append(chunk)
    target='/api/'+path
    if request.url.query:target+='?'+request.url.query
    try:
        upstream=await request.app.state.upstream.request(request.method,target,headers=headers,content=b''.join(chunks))
    except httpx.HTTPError:return JSONResponse({'detail':'API dependency unavailable'},status_code=502,headers={'Cache-Control':'no-store'})
    allowed={'content-type','content-disposition','x-correlation-id','www-authenticate','retry-after'}
    response=Response(content=upstream.content,status_code=upstream.status_code,headers={key:value for key,value in upstream.headers.items() if key.lower() in allowed})
    response.headers['Cache-Control']='no-store'
    for cookie in upstream.headers.get_list('set-cookie'):response.headers.append('set-cookie',cookie)
    return response
