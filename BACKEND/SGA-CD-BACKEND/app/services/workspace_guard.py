"""Keep the legacy commercial endpoints from bypassing delegated panel access."""
from fastapi import HTTPException
from jose import jwt,JWTError
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from starlette.concurrency import run_in_threadpool
from app.core.config import settings
from app.db.session import SessionLocal
from app.models.user import Usuario
from app.services.workspace_service import access_for

class WorkspaceLegacyGuard(BaseHTTPMiddleware):
    def __init__(self,app,session_factory=None):super().__init__(app);self.factory=session_factory or SessionLocal
    def authorize(self,authorization,path):
        if not authorization.startswith('Bearer '):raise HTTPException(401,'Inicia sesión para continuar.')
        try:
            claims=jwt.decode(authorization[7:],settings.SECRET_KEY,algorithms=[settings.ALGORITHM])
            if claims.get('type')!='access':raise JWTError()
            user_id=int(claims['sub'])
        except (JWTError,ValueError,KeyError):raise HTTPException(401,'Sesión no válida.') from None
        with self.factory() as db:
            user=db.query(Usuario).filter(Usuario.id==user_id).first()
            if not user:raise HTTPException(401,'Sesión no válida.')
            access=access_for(db,user)
            access.require('media' if '/crm/' in path else 'publish')
            if path.endswith('/video_distribution/publish') and not access.owner:
                raise HTTPException(409,'Publica desde el estudio de tu empresa para usar exclusivamente sus canales autorizados.')
    async def dispatch(self,request,call_next):
        paths={settings.API_V1_STR+'/admin_general/crm/generate_predis_media',settings.API_V1_STR+'/video_distribution/publish'}
        if request.url.path in paths:
            try:await run_in_threadpool(self.authorize,request.headers.get('Authorization',''),request.url.path)
            except HTTPException as error:return JSONResponse(status_code=error.status_code,content={'detail':error.detail})
        return await call_next(request)
