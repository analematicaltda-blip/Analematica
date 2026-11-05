
from rest_framework.permissions import BasePermission

class IsPrestadorOwner(BasePermission):
    """
    Permiso para permitir la edición de un objeto solo al prestador
    que es propietario de ese objeto.
    """
    def has_object_permission(self, request, view, obj):
        # El permiso se concede si el perfil asociado al objeto
        # es el mismo que el perfil del usuario que hace la solicitud.
        # Esto asume que el objeto tiene un campo 'perfil'.
        if hasattr(obj, 'perfil') and hasattr(request.user, 'perfil_prestador'):
            return obj.perfil == request.user.perfil_prestador
        return False
