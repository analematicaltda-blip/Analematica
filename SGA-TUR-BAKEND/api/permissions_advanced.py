from rest_framework import permissions

class ResourceOwnershipPermission(permissions.BasePermission):
    """
    PHASE H: Granular Resource Ownership
    Enforces that a user can only modify resources they own.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        # Check for standard ownership fields
        owner = getattr(obj, 'user', getattr(obj, 'usuario', None))
        if owner == request.user:
            return True

        # Check for multi-tenant provider ownership
        if hasattr(obj, 'provider') and hasattr(request.user, 'perfil_prestador'):
            return obj.provider == request.user.perfil_prestador

        return False
