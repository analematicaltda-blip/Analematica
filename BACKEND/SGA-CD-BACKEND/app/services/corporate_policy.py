"""Pin the corporate console to one active platform owner, never to every admin role."""
from fastapi import HTTPException
from app.models.corporate import CorporateOwner
from app.models.user import Usuario
from app.services.workspace_service import access_for,roles_of

def bootstrap_owner(db):
    if db.get(CorporateOwner,1):return
    candidates=[u for u in db.query(Usuario).filter(Usuario.activo.is_(True)).all() if 'admin_general' in roles_of(u)]
    if len(candidates)==1:
        db.add(CorporateOwner(id=1,user_id=candidates[0].id));db.commit()
        print('Consola Analemática vinculada a la única cuenta de dueño activa. No se crearon credenciales.')
    else:print('Consola Analemática cerrada: se necesita identificar inequívocamente una cuenta de dueño. No se seleccionó ninguna por orden o por nombre.')

def require_owner(db,user):
    binding=db.get(CorporateOwner,1)
    if not binding:raise HTTPException(503,'La consola todavía no tiene una cuenta de dueño vinculada.')
    actor=access_for(db,user)
    if not user.activo or not actor.owner or binding.user_id!=user.id:raise HTTPException(403,'Esta consola es exclusiva de la cuenta del dueño de Analemática.')
    return actor
