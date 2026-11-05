from django.urls import path, include
from rest_framework.routers import DefaultRouter

app_name = 'mi_negocio'

from .gestion_operativa.views import (
    ProcesoOperativoViewSet,
    TareaOperativaViewSet,
    OrdenOperativaViewSet,
    IncidenteOperativoViewSet
)

router = DefaultRouter()
router.register(r'operativa/procesos', ProcesoOperativoViewSet, basename='proceso-operativo')
router.register(r'operativa/tareas', TareaOperativaViewSet, basename='tarea-operativa')
router.register(r'operativa/ordenes', OrdenOperativaViewSet, basename='orden-operativa')
router.register(r'operativa/incidencias', IncidenteOperativoViewSet, basename='incidente-operativo')

urlpatterns = [
    path('', include(router.urls)),
    # Módulos operativos genéricos y especializados
    path('operativa/', include('apps.prestadores.mi_negocio.gestion_operativa.modulos_genericos.urls')),
    path('operativa/sst/', include('apps.prestadores.mi_negocio.gestion_operativa.sg_sst.urls')),

    # Módulos comerciales y facturación electrónica DIAN
    path('comercial/', include('apps.prestadores.mi_negocio.gestion_comercial.urls')),

    # Gestión financiera y tesorería
    path('financiera/', include('apps.prestadores.mi_negocio.gestion_financiera.urls')),

    # Módulo contable (contabilidad, compras, inventario, activos fijos, nómina)
    path('contable/contabilidad/', include('apps.prestadores.mi_negocio.gestion_contable.contabilidad.urls')),
    path('contable/activos-fijos/', include('apps.prestadores.mi_negocio.gestion_contable.activos_fijos.urls')),
    path('contable/nomina/', include('apps.prestadores.mi_negocio.gestion_contable.nomina.urls')),
    path('contable/compras/', include('apps.prestadores.mi_negocio.gestion_contable.compras.urls')),
    path('contable/inventario/', include('apps.prestadores.mi_negocio.gestion_contable.inventario.urls')),
    path('contable/proyectos/', include('apps.prestadores.mi_negocio.gestion_contable.proyectos.urls')),
    path('contable/presupuesto/', include('apps.prestadores.mi_negocio.gestion_contable.presupuesto.urls')),
    path('contable/reportes/', include('apps.prestadores.mi_negocio.gestion_contable.reportes.urls')),

    # Gestión Archivística
    path('archivistica/', include('apps.prestadores.mi_negocio.gestion_archivistica.urls')),
]
