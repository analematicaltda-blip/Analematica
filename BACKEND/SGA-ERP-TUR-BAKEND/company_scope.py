"""Request-scoped ERP ownership selection; roles and client IDs never grant ownership."""
from uuid import UUID
from rest_framework.exceptions import PermissionDenied,ValidationError
from apps.turismo.models import TourismProvider


def owned_provider(request):
    user=request.user
    if not user or not user.is_authenticated or not user.is_active or getattr(user,'is_agent',False):
        raise PermissionDenied('Se requiere un titular personal activo.')
    from .gestion_operativa.modulos_genericos.permissions import get_current_tenant
    selected=[]
    for value in (request.query_params.get('provider_id'),request.headers.get('X-Tenant-ID'),request.headers.get('X-Company-ID')):
        if value is not None:
            try:selected.append(UUID(str(value)))
            except (ValueError,TypeError,AttributeError):raise ValidationError('Selección de empresa inválida.')
    context=get_current_tenant()
    if context is not None:
        try:selected.append(UUID(str(context.pk)))
        except (ValueError,TypeError,AttributeError):raise PermissionDenied('Contexto empresarial inválido.')
    if len(set(selected))>1:raise ValidationError('La selección de empresa es contradictoria.')
    query=TourismProvider.objects.filter(owner_id=user.pk,is_active=True,status='ACTIVE')
    if selected:provider=query.filter(pk=selected[0]).first()
    else:
        matches=list(query.order_by('pk')[:2])
        if len(matches)!=1:raise PermissionDenied('Seleccione explícitamente una empresa propia activa.')
        provider=matches[0]
    if provider is None:raise PermissionDenied('No tiene acceso a esta empresa activa.')
    return provider


def company_options(request):
    user=request.user
    if not user or not user.is_authenticated or not user.is_active or getattr(user,'is_agent',False):
        raise PermissionDenied('Se requiere una cuenta personal activa.')
    rows=list(TourismProvider.objects.filter(owner_id=user.pk,is_active=True,status='ACTIVE').order_by('name','pk').values('id','name')[:101])
    return {'companies':[{'provider_id':str(row['id']),'name':row['name']} for row in rows[:100]],'truncated':len(rows)>100,'selection_policy':'OWNER_ONLY','cross_system_sso_enabled':False,'financial_permissions_granted':False}
