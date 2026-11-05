"""Compatibility URLs: insecure legacy OAuth writes are retired, data is retained.
New authorization starts with an authenticated POST and a browser-bound state.
"""
from fastapi import APIRouter, Depends, HTTPException, Request
from app.api import deps
router=APIRouter()

@router.get('/meta/login')
def meta_login():
    raise HTTPException(409,'Conecta Meta desde Integraciones Meta Ads en Analemática. El inicio antiguo fue sustituido por autorización con estado validado.')

@router.get('/meta/callback')
def meta_callback(request:Request):
    request.scope['query_string']=b''
    raise HTTPException(410,'Esta dirección de autorización fue retirada. Reinicia la conexión desde el panel; no se guardaron credenciales.')

@router.get('/meta/status')
def meta_status(db=Depends(deps.get_db),user=Depends(deps.get_current_active_user)):
    from app.services import meta_ads_service as ads
    actor=ads.actor_for(db,user);state=ads.status(db,actor)
    return {'connected':False,'advertising_authorized':state['authorized'],'legacy_flow_retired':True,'message':'La autorización publicitaria se gestiona en Meta Ads. Publicación orgánica y mensajes requieren sus integraciones propias.'}
