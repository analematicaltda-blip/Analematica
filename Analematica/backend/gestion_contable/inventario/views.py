from rest_framework import viewsets, permissions
from .models import ProductCategory, Warehouse, Product, InventoryMovement
from .serializers import (
    ProductCategorySerializer, WarehouseSerializer,
    ProductSerializer, InventoryMovementSerializer
)
from apps.admin_plataforma.mixins import SystemicERPViewSetMixin
from api.permissions import IsSuperAdmin

class ProductCategoryViewSet(SystemicERPViewSetMixin, viewsets.ModelViewSet):
    queryset = ProductCategory.objects.all()
    serializer_class = ProductCategorySerializer
    permission_classes = [permissions.IsAuthenticated, IsSuperAdmin]

class WarehouseViewSet(SystemicERPViewSetMixin, viewsets.ModelViewSet):
    queryset = Warehouse.objects.all()
    serializer_class = WarehouseSerializer
    permission_classes = [permissions.IsAuthenticated, IsSuperAdmin]

class ProductViewSet(SystemicERPViewSetMixin, viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated, IsSuperAdmin]

class InventoryMovementViewSet(SystemicERPViewSetMixin, viewsets.ModelViewSet):
    queryset = InventoryMovement.objects.all()
    serializer_class = InventoryMovementSerializer
    permission_classes = [permissions.IsAuthenticated, IsSuperAdmin]
