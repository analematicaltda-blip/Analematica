# backend/apps/prestadores/mi_negocio/gestion_operativa/modulos_especializados/sitios_turisticos/urls.py
from django.urls import path, include
from rest_framework_nested import routers
from .views import SitioTuristicoViewSet, ActividadEnSitioViewSet

# Router principal para los Sitios Turísticos
router = routers.DefaultRouter()
router.register(r'sitios', SitioTuristicoViewSet, basename='sitio-turistico')

# Router anidado para las Actividades dentro de un Sitio Turístico
# Generará URLs como: /sitios/{sitio_pk}/actividades/
sitios_router = routers.NestedSimpleRouter(router, r'sitios', lookup='sitio')
sitios_router.register(r'actividades', ActividadEnSitioViewSet, basename='sitio-actividad')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(sitios_router.urls)),
]
