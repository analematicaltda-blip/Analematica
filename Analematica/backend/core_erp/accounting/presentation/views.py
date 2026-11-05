from rest_framework import viewsets, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Account, JournalEntry
from .serializers import AccountSerializer, JournalEntrySerializer

class BaseAccountingViewSet(viewsets.ReadOnlyModelViewSet):
    """Base ViewSet con aislamiento Tenant obligatorio."""
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]

    def get_queryset(self):
        # GlobalTenantManager inyecta el filtro automáticamente en core_erp
        return self.model.objects.all()

class AccountViewSet(BaseAccountingViewSet):
    model = Account
    serializer_class = AccountSerializer
    filterset_fields = ['type', 'is_active', 'parent_account']
    search_fields = ['code', 'name']

class JournalEntryViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = JournalEntrySerializer
    filterset_fields = ['date', 'is_posted', 'period']
    search_fields = ['reference', 'description']

    def get_queryset(self):
        return JournalEntry.objects.all()

    @action(detail=True, methods=['post'])
    def reverse(self, request, pk=None):
        """Bloque 3.2: Reversar asiento bajo control de permisos."""
        entry = self.get_object()
        from ..ledger_engine import LedgerEngine
        try:
            reversal = LedgerEngine.reverse_entry(entry.id, reason=request.data.get('reason'))
            return Response(JournalEntrySerializer(reversal).data)
        except Exception as e:
            return Response({"error": str(e)}, status=400)
