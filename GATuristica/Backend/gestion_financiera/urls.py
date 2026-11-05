from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()
router.register(r'cuentas-bancarias', CuentaBancariaViewSet, basename='cuentabancaria')
router.register(r'ordenes-pago', OrdenPagoViewSet, basename='ordenpago')
router.register(r'tesoreria', TesoreriaCentralViewSet, basename='tesoreria')
router.register(r'estado-resultados', EstadoResultadosViewSet, basename='estadoresultados')
router.register(r'balance-general', BalanceGeneralViewSet, basename='balancegeneral')
router.register(r'proyecciones', ProyeccionFinancieraViewSet, basename='proyeccion')
router.register(r'riesgos', RiesgoFinancieroViewSet, basename='riesgo')
router.register(r'presupuestos', PresupuestoViewSet, basename='presupuesto')
router.register(r'creditos', CreditoFinancieroViewSet, basename='credito')
router.register(r'indicadores', IndicadorFinancieroViewSet, basename='indicador')
router.register(r'alertas', AlertaFinancieraViewSet, basename='alerta')
router.register(r'logs', LogFinancieroViewSet, basename='log-financiero')

urlpatterns = [
    path('', include(router.urls)),
]
