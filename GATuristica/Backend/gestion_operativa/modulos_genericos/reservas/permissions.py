from rest_framework import permissions
class IsReservasOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.provider == request.user.perfil_prestador
