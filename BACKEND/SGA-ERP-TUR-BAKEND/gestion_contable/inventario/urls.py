from rest_framework.routers import DefaultRouter
from .views import (
    AlmacenViewSet,
    MovimientoInventarioViewSet
)

router = DefaultRouter()
router.register(r'almacenes', AlmacenViewSet, basename='almacen')
router.register(r'movimientos', MovimientoInventarioViewSet, basename='movimiento-inventario')

urlpatterns = router.urls
