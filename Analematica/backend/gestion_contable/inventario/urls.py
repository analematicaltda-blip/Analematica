from rest_framework.routers import DefaultRouter
from .views import (
    ProductCategoryViewSet, WarehouseViewSet,
    ProductViewSet, InventoryMovementViewSet
)

router = DefaultRouter()
router.register(r'categories', ProductCategoryViewSet, basename='product-category')
router.register(r'warehouses', WarehouseViewSet, basename='warehouse')
router.register(r'products', ProductViewSet, basename='product')
router.register(r'movements', InventoryMovementViewSet, basename='inventory-movement')

urlpatterns = router.urls
