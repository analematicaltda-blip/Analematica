from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CuentaBancariaViewSet, OrdenPagoViewSet

router = DefaultRouter()
router.register(r'cuentas-bancarias', CuentaBancariaViewSet, basename='cuenta-bancaria')
router.register(r'ordenes-pago', OrdenPagoViewSet, basename='orden-pago')

urlpatterns = [
    path('', include(router.urls)),
]
