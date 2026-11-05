from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import ProveedorViewSet, FacturaCompraViewSet, GenerarPagoMasivoProveedoresView

router = DefaultRouter()
router.register(r'proveedores', ProveedorViewSet, basename='proveedor')
router.register(r'facturas', FacturaCompraViewSet, basename='factura-compra')

urlpatterns = router.urls

urlpatterns += [
    path('generar-pago-masivo/', GenerarPagoMasivoProveedoresView.as_view(), name='generar-pago-masivo'),
]
