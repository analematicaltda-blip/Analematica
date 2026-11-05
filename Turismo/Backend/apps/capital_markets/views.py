from rest_framework import viewsets, permissions
from .domain.models import (
    CapitalStructure,
    DebtInstrument,
    EquityInstrument,
    MarketRating,
    StructuredDeal
)
from .serializers import (
    CapitalStructureSerializer,
    DebtInstrumentSerializer,
    EquityInstrumentSerializer,
    MarketRatingSerializer,
    StructuredDealSerializer
)
from apps.admin_plataforma.mixins import SystemicERPViewSetMixin
from api.permissions import IsSuperAdmin

class CapitalStructureViewSet(SystemicERPViewSetMixin, viewsets.ModelViewSet):
    queryset = CapitalStructure.objects.all()
    serializer_class = CapitalStructureSerializer
    permission_classes = [permissions.IsAuthenticated, IsSuperAdmin]

class DebtInstrumentViewSet(SystemicERPViewSetMixin, viewsets.ModelViewSet):
    queryset = DebtInstrument.objects.all()
    serializer_class = DebtInstrumentSerializer
    permission_classes = [permissions.IsAuthenticated, IsSuperAdmin]

class EquityInstrumentViewSet(SystemicERPViewSetMixin, viewsets.ModelViewSet):
    queryset = EquityInstrument.objects.all()
    serializer_class = EquityInstrumentSerializer
    permission_classes = [permissions.IsAuthenticated, IsSuperAdmin]

class MarketRatingViewSet(SystemicERPViewSetMixin, viewsets.ModelViewSet):
    queryset = MarketRating.objects.all()
    serializer_class = MarketRatingSerializer
    permission_classes = [permissions.IsAuthenticated, IsSuperAdmin]

class StructuredDealViewSet(SystemicERPViewSetMixin, viewsets.ModelViewSet):
    queryset = StructuredDeal.objects.all()
    serializer_class = StructuredDealSerializer
    permission_classes = [permissions.IsAuthenticated, IsSuperAdmin]
