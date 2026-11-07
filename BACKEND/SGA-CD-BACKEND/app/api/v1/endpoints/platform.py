from fastapi import APIRouter,Depends
from app.api.v1.endpoints.assistance_control import administrator,PrivateRoute
from app.services.platform.registry import describe
router=APIRouter(route_class=PrivateRoute)

@router.get('/manifest')
def manifest(who=Depends(administrator)):
 return describe(who)
