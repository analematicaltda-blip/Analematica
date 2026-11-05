from rest_framework import viewsets, permissions
from .domain.models import (
    JurisdictionConfig,
    GlobalCapitalAllocator,
    TaxStrategy,
    TreasuryPosition,
    MacroScenario
)
from .serializers import (
    JurisdictionConfigSerializer,
    GlobalCapitalAllocatorSerializer,
    TaxStrategySerializer,
    TreasuryPositionSerializer,
    MacroScenarioSerializer
)
from apps.admin_plataforma.mixins import SystemicERPViewSetMixin
from api.permissions import IsSuperAdmin

class JurisdictionViewSet(SystemicERPViewSetMixin, viewsets.ModelViewSet):
    queryset = JurisdictionConfig.objects.all()
    serializer_class = JurisdictionConfigSerializer
    permission_classes = [permissions.IsAuthenticated, IsSuperAdmin]

class CapitalAllocationViewSet(SystemicERPViewSetMixin, viewsets.ModelViewSet):
    queryset = GlobalCapitalAllocator.objects.all()
    serializer_class = GlobalCapitalAllocatorSerializer
    permission_classes = [permissions.IsAuthenticated, IsSuperAdmin]

class TaxStrategyViewSet(SystemicERPViewSetMixin, viewsets.ModelViewSet):
    queryset = TaxStrategy.objects.all()
    serializer_class = TaxStrategySerializer
    permission_classes = [permissions.IsAuthenticated, IsSuperAdmin]

class GlobalTreasuryViewSet(SystemicERPViewSetMixin, viewsets.ModelViewSet):
    queryset = TreasuryPosition.objects.all()
    serializer_class = TreasuryPositionSerializer
    permission_classes = [permissions.IsAuthenticated, IsSuperAdmin]

class MacroScenarioViewSet(SystemicERPViewSetMixin, viewsets.ModelViewSet):
    queryset = MacroScenario.objects.all()
    serializer_class = MacroScenarioSerializer
    permission_classes = [permissions.IsAuthenticated, IsSuperAdmin]
