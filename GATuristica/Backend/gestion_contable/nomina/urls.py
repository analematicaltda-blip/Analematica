from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    EmpleadoViewSet, ContratoViewSet, PlanillaViewSet, ConceptoNominaViewSet,
    NovedadNominaViewSet, IncapacidadLaboralViewSet, AusenciaViewSet,
    IndicadorLaboralViewSet, DashboardNominaViewSet
)

router = DefaultRouter()
router.register(r'empleados', EmpleadoViewSet, basename='nomina-empleados')
router.register(r'contratos', ContratoViewSet, basename='nomina-contratos')
router.register(r'planillas', PlanillaViewSet, basename='nomina-planillas')
router.register(r'conceptos', ConceptoNominaViewSet, basename='nomina-conceptos')
router.register(r'novedades', NovedadNominaViewSet, basename='nomina-novedades')
router.register(r'incapacidades', IncapacidadLaboralViewSet, basename='nomina-incapacidades')
router.register(r'ausencias', AusenciaViewSet, basename='nomina-ausencias')
router.register(r'indicadores', IndicadorLaboralViewSet, basename='nomina-indicadores')
router.register(r'dashboard', DashboardNominaViewSet, basename='nomina-dashboard')

urlpatterns = [
    path('', include(router.urls)),
]
