"""Explicit company ownership and separately granted clinical permissions.
Superuser status is deliberately not an enterprise or clinical authorization.
"""
from django.contrib.auth import get_user_model
from rest_framework.exceptions import PermissionDenied
from apps.prestadores.mi_negocio.company_scope import owned_provider
from apps.turismo.services.company_identity import resolve_company


def company_context(request, *, lock=False):
    user = get_user_model().objects.filter(pk=request.user.pk, is_active=True).first()
    if user is None:
        raise PermissionDenied('Se requiere un titular activo.')
    request.user = user
    provider = owned_provider(request)
    if lock:
        # Called inside a transaction; serialize with identity/ledger changes.
        from apps.core_erp.accounting.validation import lock_company
        provider = type(provider).objects.select_for_update().get(pk=provider.pk)
        provider = owned_provider(request)
        company = resolve_company(user, provider.pk).tenant
        lock_company(company.pk)
    resolve_company(user, provider.pk)
    return provider


def require_clinical_permission(user, action):
    """Require an explicit standard Django grant, not has_perm's superuser bypass.

    Grants still need an approved provisioning workflow and real clinical-role
    qualification before production. Ownership alone does not disclose records.
    """
    operation = {'list': 'view', 'retrieve': 'view', 'create': 'add',
                 'update': 'change', 'partial_update': 'change', 'destroy': 'delete'}.get(action)
    if operation is None:
        raise PermissionDenied('Acción clínica no autorizada.')
    from django.contrib.auth.models import Permission
    from django.db.models import Q
    granted = Permission.objects.filter(
        Q(user=user) | Q(group__user=user),
        content_type__app_label='prestadores',
        content_type__model='saludocupacional',
        codename=operation + '_saludocupacional',
    ).exists()
    if not granted:
        raise PermissionDenied('Se requiere un permiso clínico explícito adicional.')
