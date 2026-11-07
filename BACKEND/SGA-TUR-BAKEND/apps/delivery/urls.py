from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DeliveryCompanyViewSet, DriverViewSet, VehicleViewSet, DeliveryServiceViewSet, RutaViewSet, IndicadorLogisticoViewSet

router = DefaultRouter()
router.register(r'companies', DeliveryCompanyViewSet)
router.register(r'drivers', DriverViewSet)
router.register(r'vehicles', VehicleViewSet)
router.register(r'rutas', RutaViewSet)
router.register(r'services', DeliveryServiceViewSet, basename='delivery-service')
router.register(r'indicadores', IndicadorLogisticoViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
