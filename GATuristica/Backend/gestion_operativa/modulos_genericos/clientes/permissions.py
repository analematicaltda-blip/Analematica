from rest_framework import permissions

class IsClienteOwner(permissions.BasePermission):
    """
    Permiso para asegurar que el prestador solo acceda a sus propios clientes.
    """
    def has_object_permission(self, request, view, obj):
        return obj.perfil == request.user.perfil_prestador
