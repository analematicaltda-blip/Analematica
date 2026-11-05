from rest_framework.permissions import BasePermission
from threading import local

# --- ALMACÉN DEL CONTEXTO DE LA PETICIÓN ---
_thread_locals = local()

def get_current_tenant():
    """
    Función global y segura para obtener el inquilino (ProviderProfile) activo
    que fue establecido por el middleware para la petición actual.
    """
    return getattr(_thread_locals, 'tenant', None)

# --- MIDDLEWARE MULTI-INQUILINO ---
class TenantMiddleware:
    """
    Middleware que se ejecuta en cada petición para identificar al inquilino (tenant).
    Establece el contexto del inquilino para la petición actual.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        from .perfil.models import ProviderProfile # Lazy import

        _thread_locals.tenant = None
        tenant = None

        # Prioridad 1: Header X-Tenant-ID (Standard Fase 3)
        tenant_id = request.headers.get('X-Tenant-ID') or request.headers.get('X-Company-ID')
        if tenant_id:
            try:
                tenant = ProviderProfile.objects.get(id=tenant_id)
            except (ProviderProfile.DoesNotExist, ValueError):
                pass

        # Prioridad 2: Usuario autenticado (Fallback)
        if not tenant and request.user and request.user.is_authenticated:
            try:
                tenant = request.user.perfil_prestador
            except ProviderProfile.DoesNotExist:
                tenant = None

        _thread_locals.tenant = tenant
        request.tenant_id = str(tenant.id) if tenant else None
        response = self.get_response(request)

        if hasattr(_thread_locals, 'tenant'):
            del _thread_locals.tenant

        return response

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
