# backend/apps/prestadores/mi_negocio/gestion_operativa/modulos_especializados/agencias_de_viajes/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PaqueteTuristicoViewSet, ReservaPaqueteViewSet

router = DefaultRouter()
router.register(r'paquetes', PaqueteTuristicoViewSet, basename='paquete-turistico')
router.register(r'reservas', ReservaPaqueteViewSet, basename='reserva-paquete')

urlpatterns = [
    path('', include(router.urls)),
]
