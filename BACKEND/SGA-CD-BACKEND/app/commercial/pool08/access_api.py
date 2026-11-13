"""SGA-CD owned administrator routes, fresh local authority on every request."""
from fastapi import Depends, Request, HTTPException
from app.api import deps
from .api import router
from .identity import resolve_access
from .access_admin import AccessAdmin
from .access_protocol import AccessFault
from .crm import CRMError
from .contract import MAX_BYTES, decode, ContractRejected

def admin(request:Request,db=Depends(deps.get_db),user=Depends(deps.get_current_active_user)):
    from .crm_api import service as crm_service
    if request.query_params:raise HTTPException(400,'UNEXPECTED_CONTEXT')
    return execute(lambda:AccessAdmin(resolve_access(db,user),crm_service(request,db,user)))
def execute(action):
    try:return action()
    except CRMError as exc:
        from .crm_api import failure
        raise failure(exc) from None
    except AccessFault as exc:raise HTTPException(exc.status,{'code':exc.code},headers={'Cache-Control':'no-store'}) from None

@router.get('/crm/access/{section}')
def access_read(section:str,service=Depends(admin)):
    return execute(lambda:service.read(section))
@router.get('/crm/access/receipts/{key}')
def access_receipt(key:str,service=Depends(admin)):
    return execute(lambda:service.read('receipts',key))
@router.post('/crm/access/commands')
async def access_command(request:Request,service=Depends(admin)):
    if request.headers.get('content-type','').split(';')[0].strip().lower()!='application/json':raise HTTPException(415,'JSON_REQUIRED')
    raw=bytearray()
    async for chunk in request.stream():
        if len(raw)+len(chunk)>MAX_BYTES:raise HTTPException(413,'BODY_LIMIT')
        raw.extend(chunk)
    try:body=decode(bytes(raw))
    except ContractRejected:raise HTTPException(400,'INVALID_JSON') from None
    return execute(lambda:service.command(body))
