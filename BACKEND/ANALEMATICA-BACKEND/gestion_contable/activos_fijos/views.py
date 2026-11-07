from rest_framework import viewsets, permissions
from .models import AssetCategory, FixedAsset, DepreciationCalculation
from .serializers import AssetCategorySerializer, FixedAssetSerializer, DepreciationCalculationSerializer
from apps.admin_plataforma.mixins import SystemicERPViewSetMixin
from api.permissions import IsSuperAdmin

class AssetCategoryViewSet(SystemicERPViewSetMixin, viewsets.ModelViewSet):
    queryset = AssetCategory.objects.all()
    serializer_class = AssetCategorySerializer
    permission_classes = [permissions.IsAuthenticated, IsSuperAdmin]

class FixedAssetViewSet(SystemicERPViewSetMixin, viewsets.ModelViewSet):
    queryset = FixedAsset.objects.all()
    serializer_class = FixedAssetSerializer
    permission_classes = [permissions.IsAuthenticated, IsSuperAdmin]

class DepreciationCalculationViewSet(SystemicERPViewSetMixin, viewsets.ModelViewSet):
    queryset = DepreciationCalculation.objects.all()
    serializer_class = DepreciationCalculationSerializer
    permission_classes = [permissions.IsAuthenticated, IsSuperAdmin]
