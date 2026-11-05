from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.apps import apps
from . import serializers

Account = apps.get_model('core_erp', 'Account')

class PlanCuentaViewSet(viewsets.ModelViewSet):
    queryset = Account.objects.all()
    serializer_class = serializers.PlanCuentaSerializer  # Import from serializers
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['code', 'type', 'is_active']

    def get_queryset(self):
        qs = super().get_queryset()
        # En el entorno de SARITA, request.tenant_id es establecido por el middleware
        tenant_id = getattr(self.request, 'tenant_id', None)
        if tenant_id:
            return qs.filter(tenant_id=tenant_id)
        return qs.none()

    def perform_create(self, serializer):
        # Inyectar tenant_id manualmente si el middleware no lo hizo en el entorno de tests
        tenant_id = getattr(self.request, 'tenant_id', None)
        if not tenant_id and 'HTTP_X_TENANT_ID' in self.request.META:
            tenant_id = self.request.META['HTTP_X_TENANT_ID']

        serializer.save(tenant_id=tenant_id)

    @action(detail=False, methods=['get'])
    def tree(self, request):
        # Hierarchical tree
        accounts = self.get_queryset().select_related('parent_account')
        # Build tree logic here (recursive/dict)
        tree = self.build_tree(accounts)
        return Response(tree)

    def build_tree(self, accounts):
        # Simple tree builder
        account_dict = {a.id: a for a in accounts}
        roots = []
        for acc in accounts:
            if acc.parent_account_id:
                parent = account_dict.get(acc.parent_account_id)
                if parent:
                    if not hasattr(parent, 'children'):
                        parent.children = []
                    parent.children.append(acc)
            else:
                roots.append(acc)
        return [self.serialize_tree(acc) for acc in roots]

    def serialize_tree(self, acc):
        data = self.serializer_class(acc).data
        if hasattr(acc, 'children'):
            data['children'] = [self.serialize_tree(child) for child in acc.children]
        return data

