"""Restricted API gateway; frontend files and upstream credentials are never served."""
import os
from contextlib import asynccontextmanager
from urllib.parse import urlsplit
import httpx
from fastapi import FastAPI,Request,HTTPException
from fastapi.responses import Response,JSONResponse

UPSTREAM=os.environ.get('SGACD_API_URL','http://sgacd:8000').rstrip('/')
parsed=urlsplit(UPSTREAM)
if parsed.scheme not in {'http','https'} or parsed.hostname not in {'sgacd','localhost','127.0.0.1','host.docker.internal'} or parsed.username or parsed.password or parsed.path or parsed.query or parsed.fragment:
    raise ValueError('SGACD_API_URL must be a configured internal API origin')

@asynccontextmanager
async def lifespan(app):
    async with httpx.AsyncClient(base_url=UPSTREAM,timeout=20,follow_redirects=False,trust_env=False) as client:
        app.state.upstream=client
        yield

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
