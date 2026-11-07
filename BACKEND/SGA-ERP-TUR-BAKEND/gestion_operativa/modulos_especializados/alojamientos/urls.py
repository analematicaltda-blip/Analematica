from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    TipoAlojamientoViewSet,
    AlojamientoViewSet,
    HabitacionViewSet,
    TarifaViewSet,
    CalendarioDisponibilidadView
)

router = DefaultRouter()
router.register(r'tipos', TipoAlojamientoViewSet, basename='tipo-alojamiento')
router.register(r'alojamientos', AlojamientoViewSet, basename='alojamiento')
router.register(r'habitaciones', HabitacionViewSet, basename='habitacion')
router.register(r'tarifas', TarifaViewSet, basename='tarifa')

urlpatterns = [
    path('', include(router.urls)),
    path('calendario-disponibilidad/', CalendarioDisponibilidadView.as_view(), name='calendario-disponibilidad'),
]
