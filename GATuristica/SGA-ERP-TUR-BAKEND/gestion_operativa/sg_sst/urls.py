from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    MatrizRiesgoViewSet, IncidenteLaboralViewSet, SaludOcupacionalViewSet,
    CapacitacionSSTViewSet, PlanAnualSSTViewSet, ActividadPlanSSTViewSet,
    InspeccionSSTViewSet, IndicadorSSTViewSet, AlertaSSTViewSet, DashboardSSTViewSet
)

router = DefaultRouter()
router.register(r'riesgos', MatrizRiesgoViewSet, basename='sgsst-riesgos')
router.register(r'incidentes', IncidenteLaboralViewSet, basename='sgsst-incidentes')
router.register(r'salud', SaludOcupacionalViewSet, basename='sgsst-salud')
router.register(r'capacitaciones', CapacitacionSSTViewSet, basename='sgsst-capacitaciones')
router.register(r'plan-anual', PlanAnualSSTViewSet, basename='sgsst-plan-anual')
router.register(r'actividades-plan', ActividadPlanSSTViewSet, basename='sgsst-actividades')
router.register(r'inspecciones', InspeccionSSTViewSet, basename='sgsst-inspecciones')
router.register(r'indicadores', IndicadorSSTViewSet, basename='sgsst-indicadores')
router.register(r'alertas', AlertaSSTViewSet, basename='sgsst-alertas')
router.register(r'dashboard', DashboardSSTViewSet, basename='sgsst-dashboard')

urlpatterns = [
    path('', include(router.urls)),
]
