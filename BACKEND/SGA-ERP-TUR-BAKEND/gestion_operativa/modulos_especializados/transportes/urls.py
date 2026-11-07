from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CompaniaTransporteViewSet,
    TipoVehiculoViewSet,
    VehiculoViewSet,
    RutaViewSet,
    HorarioRutaViewSet,
)

router = DefaultRouter()
router.register(r'tipos-vehiculo', TipoVehiculoViewSet, basename='tipovehiculo')
router.register(r'companias', CompaniaTransporteViewSet, basename='compania')
router.register(r'vehiculos', VehiculoViewSet, basename='vehiculo')
router.register(r'rutas', RutaViewSet, basename='ruta')
router.register(r'horarios-ruta', HorarioRutaViewSet, basename='horarioruta')

urlpatterns = [
    path('', include(router.urls)),
]
