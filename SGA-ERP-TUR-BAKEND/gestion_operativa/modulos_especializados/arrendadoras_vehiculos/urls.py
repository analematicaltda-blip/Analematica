# backend/apps/prestadores/mi_negocio/gestion_operativa/modulos_especializados/arrendadoras_vehiculos/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import VehiculoDeAlquilerViewSet, AlquilerViewSet

router = DefaultRouter()
router.register(r'flota', VehiculoDeAlquilerViewSet, basename='vehiculo-alquiler')
router.register(r'alquileres', AlquilerViewSet, basename='alquiler')

urlpatterns = [
    path('', include(router.urls)),
]
