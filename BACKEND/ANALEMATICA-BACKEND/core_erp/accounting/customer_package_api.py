"""Customer-operated service, independent of ERP auth/database and client KEKs.

Run as core_erp.accounting.customer_package_api:create_app with --factory,
CUSTOMER_PACKAGE_CONFIG pointing to the customer's private deployment config.
Schema initialization is explicit via this module's --initialize CLI.
"""
import hashlib,hmac,json,os,re,stat
from pathlib import Path
from datetime import datetime,timezone,timedelta
from urllib.parse import urlsplit
from uuid import UUID
from fastapi import FastAPI,HTTPException,Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.concurrency import run_in_threadpool
from django.db import DatabaseError
from .customer_package_store import CustomerPackageStore,StorageConflict,StorageOutcomeUnknown,package_receipt,initialize_customer_packages

MAX=1500000

def private_json(path):
    p=Path(path)
    if p.is_symlink() or not p.is_file() or p.stat().st_mode&0o077 or p.stat().st_size>16384:raise ValueError('Private bounded configuration file required.')
    return json.loads(p.read_text())

def origin(value,allow_loopback=False):
    if not isinstance(value,str):raise ValueError('Explicit origin required.')
    u=urlsplit(value)
    if u.username or u.password or u.path or u.query or u.fragment or not u.hostname or u.scheme!='https' and not (allow_loopback and u.scheme=='http' and u.hostname in {'127.0.0.1','localhost'}):raise ValueError('Explicit HTTPS origin required.')
    if value!=u.scheme+'://'+u.netloc or u.port is not None and not 1<=u.port<=65535:raise ValueError('Canonical origin required.')
    return value

def grant(path,now,allow_loopback=False):
    g=private_json(path)
    if not isinstance(g,dict) or set(g)!={'company_id','token_sha256','expires_at','permissions','allowed_origins'}:raise ValueError('Invalid customer grant.')
    if str(UUID(g['company_id']))!=g['company_id'] or not isinstance(g['token_sha256'],str) or len(g['token_sha256'])!=64 or any(c not in '0123456789abcdef' for c in g['token_sha256']):raise ValueError('Invalid grant identity.')
    expires=datetime.fromisoformat(g['expires_at'])
    if expires.tzinfo is None or expires>now+timedelta(days=1):raise ValueError('Bounded timezone-aware grant expiry required.')
    if not isinstance(g['permissions'],list) or not g['permissions'] or len(g['permissions'])!=len(set(g['permissions'])) or set(g['permissions'])-{'read','append'}:raise ValueError('Invalid grant permissions.')
    if not isinstance(g['allowed_origins'],list) or not 1<=len(g['allowed_origins'])<=5:raise ValueError('Explicit origin list required.')
    for value in g['allowed_origins']:origin(value,allow_loopback)
    return g,expires

def strict_json(raw):
    def pairs(values):
        result={}
        for key,value in values:
            if key in result:raise ValueError('Duplicate package key.')
            result[key]=value
        return result
    def nonfinite(value):raise ValueError('Nonfinite JSON value.')
    return json.loads(raw.decode('utf-8'),object_pairs_hook=pairs,parse_constant=nonfinite)

def build_app(store_factory,grant_path,*,allow_loopback_test_origins=False,clock=lambda:datetime.now(timezone.utc)):
    startup,_=grant(grant_path,clock(),allow_loopback_test_origins)
    app=FastAPI(title='Customer encrypted package store',docs_url=None,redoc_url=None,openapi_url=None)
    app.add_middleware(CORSMiddleware,allow_origins=startup['allowed_origins'],allow_methods=['GET','POST'],allow_headers=['Authorization','Content-Type'],allow_credentials=False,max_age=0)
    @app.middleware('http')
    async def privacy(request,call_next):
        response=await call_next(request);response.headers['Cache-Control']='private, no-store';response.headers['X-Content-Type-Options']='nosniff';return response
    def authorize(request,permission):
        try:g,expires=grant(grant_path,clock(),allow_loopback_test_origins)
        except (ValueError,KeyError,TypeError,AttributeError,OSError):raise HTTPException(503,'Configuración de cliente no disponible.') from None
        token=request.headers.get('authorization','')
        if not token.startswith('Bearer ') or not re.fullmatch('byos_[A-Za-z0-9_-]{43}',token[7:]) or expires<=clock() or not hmac.compare_digest(hashlib.sha256(token[7:].encode()).hexdigest(),g['token_sha256']):raise HTTPException(401,'Autorización del cliente no vigente.')
        if permission not in g['permissions'] or request.headers.get('origin') not in (None,*g['allowed_origins']):raise HTTPException(403,'Permiso u origen no autorizado.')
        return g
    def work(request,permission,operation):
        g=authorize(request,permission)
        try:
            with store_factory() as store:
                if store.company_id!=g['company_id']:raise ValueError('Customer company binding mismatch.')
                return operation(store)
        except StorageOutcomeUnknown:raise HTTPException(503,{'code':'PACKAGE_WRITE_OUTCOME_UNKNOWN','action':'READ_EXACT_VERSION_THEN_RETRY_IDENTICAL_PACKAGE'}) from None
        except StorageConflict:raise HTTPException(409,'Versión o padre en conflicto; consulta el estado del cliente.') from None
        except LookupError:raise HTTPException(404,'Documento del cliente no disponible.') from None
        except ValueError:raise HTTPException(400,'Paquete o vínculo de cliente inválido.') from None
        except DatabaseError:raise HTTPException(503,'Almacenamiento no confirmado; consulta y reintenta la misma versión.') from None
    @app.get('/v1/identity')
    async def identity(request:Request):
        return await run_in_threadpool(work,request,'read',lambda store:{'schema':'sgacd-customer-store-v1','company_id':store.company_id,'destination':'explicit_customer_postgresql','authenticated_ciphertext_verified':False,'ownership_independently_verified':False,'fiscal_accepted':False,'ledger_written':False})
    @app.get('/v1/packages/{document_id}')
    async def retrieve(request:Request,document_id:str,revision:int|None=None):
        return await run_in_threadpool(work,request,'read',lambda store:store.get(document_id,revision))
    @app.get('/v1/receipts/{document_id}')
    async def receipt(request:Request,document_id:str,revision:int,package_digest:str):
        if set(request.query_params)!={'revision','package_digest'} or any(len(request.query_params.getlist(k))!=1 for k in request.query_params) or request.query_params['revision']!=str(revision):raise HTTPException(422,'Versión y huella únicas y canónicas requeridas.')
        return await run_in_threadpool(work,request,'read',lambda store:package_receipt(store,document_id,revision,package_digest))
    @app.post('/v1/packages')
    async def append(request:Request):
        authorize(request,'append')
        if request.headers.get('content-encoding','identity')!='identity' or request.headers.get('content-type','').split(';')[0]!='application/json':raise HTTPException(415,'JSON sin compresión requerido.')
        data=bytearray()
        async for chunk in request.stream():
            if len(data)+len(chunk)>MAX:raise HTTPException(413,'Paquete demasiado grande.')
            data.extend(chunk)
        try:value=strict_json(data)
        except (ValueError,UnicodeError,RecursionError):raise HTTPException(400,'Contrato JSON inválido.') from None
        return await run_in_threadpool(work,request,'append',lambda store:store.put(value))
    return app

def deployment():
    config=private_json(os.environ['CUSTOMER_PACKAGE_CONFIG'])
    if set(config)!={'company_id','database','grant_file'} or config['database'].get('ENGINE')!='django.db.backends.postgresql':raise ValueError('Explicit customer PostgreSQL configuration required.')
    from django.conf import settings
    if not settings.configured:settings.configure(USE_TZ=True,DATABASES={'default':{}})
    from django.db.utils import ConnectionHandler
    company=str(UUID(config['company_id']))
    from contextlib import contextmanager
    @contextmanager
    def factory():
        handler=ConnectionHandler({'default':{},'customer_documents':config['database']});connection=handler['customer_documents']
        try:yield CustomerPackageStore(connection,company)
        finally:connection.close()
    return config,factory

def create_app():
    config,factory=deployment();return build_app(factory,config['grant_file'])

if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser();parser.add_argument('--initialize',action='store_true',required=True);args=parser.parse_args()
    config,_=deployment()
    from django.db.utils import ConnectionHandler
    handler=ConnectionHandler({'default':{},'customer_documents':config['database']});connection=handler['customer_documents']
    try:initialize_customer_packages(connection,config['company_id'])
    finally:connection.close()
    print('Customer package schema initialized explicitly; no document imported.')
