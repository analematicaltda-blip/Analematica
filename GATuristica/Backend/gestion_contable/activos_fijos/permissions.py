
from rest_framework.permissions import BasePermission
from django.contrib.contenttypes.models import ContentType

class CanAssignOwnerPermission(BasePermission):
    """
    Permiso para verificar si un usuario puede asignar un objeto como 'owner'.

    Por ahora, la lógica es simple: solo los superusuarios pueden asignar owners.
    Esta clase se puede extender en el futuro para lógicas más complejas
    (ej. un manager puede asignar objetos de su propia compañía).
    """
    def has_permission(self, request, view):
        owner_data = request.data.get('owner')

        # Si no se está intentando asignar un owner, el permiso no se aplica.
        if not owner_data:
            return True

        # Solo los administradores pueden asignar owners.
        return request.user and request.user.is_superuser
