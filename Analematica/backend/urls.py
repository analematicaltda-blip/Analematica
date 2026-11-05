from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SaritaProfileView, PlanViewSet, SuscripcionViewSet, MetaStandardView, SupervisionDianViewSet
from .superadmin import SuperAdminSystemAuditViewSet
from apps.audit.views import ForensicSecurityLogViewSet

app_name = 'admin_plataforma'

router = DefaultRouter()
router.register(r'planes', PlanViewSet, basename='plan')
router.register(r'suscripciones', SuscripcionViewSet, basename='suscripcion')
router.register(r'supervision-dian', SupervisionDianViewSet, basename='supervision-dian')
router.register(r'audit/forensic-logs', ForensicSecurityLogViewSet, basename='forensic-log')
router.register(r'system-audit', SuperAdminSystemAuditViewSet, basename='system-audit')

urlpatterns = [
    path('profile/', SaritaProfileView.as_view(), name='sarita-profile'),
    path('doctrina/', MetaStandardView.as_view(), name='meta-standard'),

 
    # ERP SISTÉMICO - CONSOLIDACIÓN FASE 2
    # Los módulos clonados han sido eliminados. Se usan los dominios consolidados en domain_business.
    path('operativa/', include('apps.domain_business.operativa.urls')),
    path('comercial/', include('apps.domain_business.comercial.urls')),
    path('archivistica/', include('apps.admin_plataforma.gestion_archivistica.urls')),
    path('financiera/', include('apps.admin_plataforma.gestion_financiera.urls')),
    path('contabilidad/', include('apps.admin_plataforma.gestion_contable.contabilidad.urls')),
    path('payroll/', include('apps.admin_plataforma.gestion_contable.nomina.urls')),
    path('fixed-assets/', include('apps.admin_plataforma.gestion_contable.activos_fijos.urls')),
    path('procurement/', include('apps.admin_plataforma.gestion_contable.compras.urls')),
    path('inventory/', include('apps.admin_plataforma.gestion_contable.inventario.urls')),
    path('budget/', include('apps.admin_plataforma.gestion_contable.presupuesto.urls')),
    path('projects/', include('apps.admin_plataforma.gestion_contable.proyectos.urls')),
    path('company/', include('apps.admin_plataforma.gestion_contable.empresa.urls')),
    path('control-tower/', include('apps.control_tower.urls')),
    path('enterprise/', include('apps.enterprise.urls')),
    path('global-holding/', include('apps.global_holding.urls')),
    path('capital-markets/', include('apps.capital_markets.urls')),
    path('tokenization/', include('apps.tokenization.urls')),
    path('defense-predictive/', include('apps.defense_predictive.urls')),
    path('defense-deception/', include('apps.defense_deception.urls')),
 

    path('', include(router.urls)),
]
