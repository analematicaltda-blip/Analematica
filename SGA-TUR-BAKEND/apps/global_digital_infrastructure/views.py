from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from decimal import Decimal
from .models import GlobalLedgerEntry, SchemaRegistry, RegulatorySyncNode, DigitalIdentity, DataFabricRegion
from .serializers import (
    GlobalLedgerEntrySerializer, SchemaRegistrySerializer,
    RegulatorySyncNodeSerializer, DigitalIdentitySerializer,
    DataFabricRegionSerializer, GDEIDashboardSerializer
)
from .application.interop_service import InteroperabilityLayerService
from .application.settlement_service import SettlementService
from .application.sync_engine import RegulatorySyncService
from .application.trust_service import IdentityTrustService

class GlobalLedgerViewSet(viewsets.ModelViewSet):
    queryset = GlobalLedgerEntry.objects.all()
    serializer_class = GlobalLedgerEntrySerializer

    @action(detail=True, methods=['post'], url_path='settle')
    def settle(self, request, pk=None):
        result = SettlementService.settle_transaction(pk)
        return Response({'success': result}, status=status.HTTP_200_OK)

class SchemaRegistryViewSet(viewsets.ModelViewSet):
    queryset = SchemaRegistry.objects.all()
    serializer_class = SchemaRegistrySerializer

class RegulatorySyncViewSet(viewsets.ModelViewSet):
    queryset = RegulatorySyncNode.objects.all()
    serializer_class = RegulatorySyncNodeSerializer

    @action(detail=True, methods=['post'], url_path='sync')
    def sync_jurisdiction(self, request, pk=None):
        node = self.get_object()
        rules = request.data.get('rules', [])
        RegulatorySyncService.synchronize_jurisdiction(node.jurisdiction, rules)
        return Response({'status': 'SYNCED'}, status=status.HTTP_200_OK)

class DigitalIdentityViewSet(viewsets.ModelViewSet):
    queryset = DigitalIdentity.objects.all()
    serializer_class = DigitalIdentitySerializer

    @action(detail=True, methods=['post'], url_path='verify-kyb')
    def verify_kyb(self, request, pk=None):
        result = IdentityTrustService.verify_kyb(pk)
        return Response({'verified': result}, status=status.HTTP_200_OK)

class DataFabricViewSet(viewsets.ModelViewSet):
    queryset = DataFabricRegion.objects.all()
    serializer_class = DataFabricRegionSerializer

class GDEIDashboardViewSet(viewsets.ViewSet):
    """
    Panel de Infraestructura Económica Digital Global (Fase 23.10).
    """
    def list(self, request):
        ledger_count = GlobalLedgerEntry.objects.count()
        schemas = SchemaRegistry.objects.filter(is_active=True).count()
        identities = DigitalIdentity.objects.filter(is_kyb_verified=True).count()

        # Calculate Interoperability Index (Sample metrics)
        interop_index = InteroperabilityLayerService.calculate_interoperability_index(0.95, 0.90, 0.05)

        data = {
            "interoperability_index": interop_index,
            "total_ledger_entries": ledger_count,
            "active_schemas": schemas,
            "verified_identities": identities,
            "global_health_status": "OPTIMAL"
        }

        serializer = GDEIDashboardSerializer(data)
        return Response(serializer.data)
