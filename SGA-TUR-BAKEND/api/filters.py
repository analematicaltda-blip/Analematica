import django_filters
from .models import AuditLog, CustomUser

class AuditLogFilter(django_filters.FilterSet):
    """
    FilterSet para el modelo AuditLog.
    Permite filtrar por el ID del usuario y por el tipo de acción.
    """
    # Filtro por el ID del usuario. El campo en el modelo es 'user'.
    user = django_filters.ModelChoiceFilter(
        queryset=CustomUser.objects.all(),
        field_name='user__id',
        to_field_name='id',
        label='User ID'
    )

    # Filtro por el tipo de acción. Permite búsqueda exacta (insensible a mayúsculas/minúsculas).
    action = django_filters.ChoiceFilter(
        choices=AuditLog.Action.choices,
        field_name='action',
        lookup_expr='iexact',
        label='Action Type'
    )

    class Meta:
        model = AuditLog
        fields = ['user', 'action']