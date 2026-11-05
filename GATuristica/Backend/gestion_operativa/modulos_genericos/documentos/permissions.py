from rest_framework import permissions
class IsDocumentoOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.prestador == request.user.perfil_prestador
