from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    OperadorTuristicoViewSet,
    PaqueteTuristicoViewSet,
    ItinerarioDiaViewSet,
)

router = DefaultRouter()
router.register(r'operadores', OperadorTuristicoViewSet, basename='operador')
router.register(r'paquetes', PaqueteTuristicoViewSet, basename='paquete')
router.register(r'itinerarios', ItinerarioDiaViewSet, basename='itinerario')

urlpatterns = [
    path('', include(router.urls)),
]
