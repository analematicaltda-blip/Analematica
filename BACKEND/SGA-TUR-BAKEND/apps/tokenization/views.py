from rest_framework import viewsets, permissions
from .domain.models import (
    TokenizedAsset,
    ProgrammableCapitalUnit,
    SmartGovernanceRule,
    DigitalRegistry,
    ComplianceConstraint
)
from .serializers import (
    TokenizedAssetSerializer,
    ProgrammableUnitSerializer,
    GovernanceRuleSerializer,
    DigitalRegistrySerializer,
    ComplianceConstraintSerializer
)
from apps.admin_plataforma.mixins import SystemicERPViewSetMixin
from api.permissions import IsSuperAdmin

class TokenizedAssetViewSet(SystemicERPViewSetMixin, viewsets.ModelViewSet):
    queryset = TokenizedAsset.objects.all()
    serializer_class = TokenizedAssetSerializer
    permission_classes = [permissions.IsAuthenticated, IsSuperAdmin]

class ProgrammableUnitViewSet(SystemicERPViewSetMixin, viewsets.ModelViewSet):
    queryset = ProgrammableCapitalUnit.objects.all()
    serializer_class = ProgrammableUnitSerializer
    permission_classes = [permissions.IsAuthenticated, IsSuperAdmin]

class GovernanceRuleViewSet(SystemicERPViewSetMixin, viewsets.ModelViewSet):
    queryset = SmartGovernanceRule.objects.all()
    serializer_class = GovernanceRuleSerializer
    permission_classes = [permissions.IsAuthenticated, IsSuperAdmin]

class DigitalRegistryViewSet(SystemicERPViewSetMixin, viewsets.ReadOnlyModelViewSet):
    queryset = DigitalRegistry.objects.all()
    serializer_class = DigitalRegistrySerializer
    permission_classes = [permissions.IsAuthenticated, IsSuperAdmin]

class ComplianceConstraintViewSet(SystemicERPViewSetMixin, viewsets.ModelViewSet):
    queryset = ComplianceConstraint.objects.all()
    serializer_class = ComplianceConstraintSerializer
    permission_classes = [permissions.IsAuthenticated, IsSuperAdmin]
