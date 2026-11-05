from rest_framework import permissions
class IsValoracionesOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.provider == request.user.perfil_prestador
