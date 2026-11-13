"""SGA-CD-owned commercial protocol, protected by existing CRM authority."""
from fastapi import APIRouter, Depends, Request, HTTPException, Response
from fastapi.routing import APIRoute
from app.api import deps
from app.services.workspace_service import access_for
from .contract import (CURRENT_VERSION, MAX_BYTES, ContractRejected, capabilities,
                       contract_document, decode, http_status, validate_intent)

class PrivateRoute(APIRoute):
    async def handle(self, scope, receive, send):
        from starlette.exceptions import HTTPException as StarletteHTTPException
        try:
            return await super().handle(scope, receive, send)
        except StarletteHTTPException as exc:
            exc.headers={**(exc.headers or {}),'Cache-Control':'no-store'}
            raise
    def get_route_handler(self):
        original = super().get_route_handler()
        async def private(request):
            try:
                response = await original(request)
                response.headers['Cache-Control'] = 'no-store'
                return response
            except HTTPException as exc:
                exc.headers = {**(exc.headers or {}), 'Cache-Control': 'no-store', 'X-POOL08-Contract-Version': CURRENT_VERSION}
                raise
        return private

router = APIRouter(route_class=PrivateRoute)

def context(request: Request, db=Depends(deps.get_db), user=Depends(deps.get_current_active_user)):
    current = access_for(db, user)
    current.require('crm')
    if request.query_params:
        raise HTTPException(400, 'La empresa procede de la sesión verificada, no de parámetros de consulta.')
    return {'tenant_ref': current.scope, 'actor_ref': str(current.user.id)}

def failure(error):
    code = str(error)
    return HTTPException(http_status(error), {'code': code, 'detail': 'Contrato no válido; no se ejecutó ninguna operación.'},
                         headers={'Cache-Control': 'no-store', 'X-POOL08-Error-Code': code})

def version_header(request):
    values = request.headers.getlist('x-pool08-contract-version')
    if len(values) > 1:
        raise failure(ContractRejected('UNSUPPORTED_VERSION'))
    return values[0] if values else None

def document(request, response, reader, authority):
    try:
        result = reader(version_header(request))
    except ContractRejected as exc:
        raise failure(exc) from None
    response.headers['X-POOL08-Contract-Version'] = result['schema_version']
    return {**result, 'context': authority}

@router.get('/capabilities')
def catalog(request: Request, response: Response, authority=Depends(context)):
    return document(request, response, capabilities, authority)

@router.get('/contract')
def contract(request: Request, response: Response, authority=Depends(context)):
    return document(request, response, contract_document, authority)

@router.post('/intents/validate')
async def validate(request: Request, response: Response, authority=Depends(context)):
    if request.headers.get('content-type', '').split(';', 1)[0].strip().lower() != 'application/json':
        raise HTTPException(415, 'Usa application/json.')
    raw = bytearray()
    async for chunk in request.stream():
        if len(raw) + len(chunk) > MAX_BYTES:
            raise failure(ContractRejected('BODY_LIMIT'))
        raw.extend(chunk)
    try:
        result = validate_intent(decode(bytes(raw)), **authority, requested_version=version_header(request))
    except ContractRejected as exc:
        raise failure(exc) from None
    response.headers['X-POOL08-Contract-Version'] = result['schema_version']
    return result

# Register own CRM routes after the shared private router exists.
from . import crm_api

from . import access_api
