from rest_framework.permissions import BasePermission
from rest_framework.exceptions import AuthenticationFailed
from contextvars import ContextVar
from django.core.exceptions import ObjectDoesNotExist,ValidationError
from django.http import JsonResponse

_current_provider=ContextVar('sgacd_current_provider',default=None)
def get_current_tenant():return _current_provider.get()

class TenantMiddleware:
    """Provider selection requires authenticated ownership, not just a header.

    Provider IDs are not automatically mapped to the separate core ERP Tenant ID.
    """
    def __init__(self,get_response):self.get_response=get_response
    def __call__(self,request):
        token=_current_provider.set(None)
        try:
            user=getattr(request,'user',None)
            if (not user or not user.is_authenticated) and request.headers.get('Authorization','').startswith('Bearer '):
                from rest_framework_simplejwt.authentication import JWTAuthentication
                try:principal=JWTAuthentication().authenticate(request)
                except AuthenticationFailed:return JsonResponse({'code':'invalid_domain_session'},status=401)
                if principal:user=request.user=principal[0]
            selected=request.headers.get('X-Tenant-ID');company=request.headers.get('X-Company-ID')
            if selected and company and selected!=company:return JsonResponse({'code':'conflicting_provider_selection'},status=400)
            selected=selected or company;provider=None
            if selected:
                if not user or not user.is_authenticated:return JsonResponse({'code':'provider_selection_requires_authentication'},status=401)
                from .perfil.models import ProviderProfile
                try:provider=ProviderProfile.objects.filter(pk=selected,owner_id=user.pk).first()
                except (ValidationError,ValueError,TypeError):return JsonResponse({'code':'invalid_provider_selection'},status=400)
                if provider is None or provider.owner_id!=user.pk:return JsonResponse({'code':'provider_access_denied'},status=403)
            elif user and user.is_authenticated:
                try:provider=getattr(user,'perfil_prestador',None)
                except ObjectDoesNotExist:provider=None
                if provider is not None and getattr(provider,'owner_id',None)!=user.pk:provider=None
            _current_provider.set(provider);request.tenant_id=str(provider.pk) if provider else None
            return self.get_response(request)
        finally:_current_provider.reset(token)

# --- PERMISO ORIGINAL (Referencia) ---
class IsOwner(BasePermission):
    """
    Permiso personalizado para permitir solo a los dueños de un objeto editarlo.
    Este permiso se vuelve menos crítico con el TenantManager, pero aún puede ser útil.
    """
    def has_object_permission(self, request, view, obj):
        if hasattr(obj, 'provider'):
            return obj.provider == request.user.perfil_prestador
        if hasattr(obj, 'perfil'): # Compatibilidad con modelos antiguos
            return obj.perfil == request.user.perfil_prestador
        return False
