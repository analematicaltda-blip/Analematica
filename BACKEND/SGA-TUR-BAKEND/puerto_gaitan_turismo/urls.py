"""
URL configuration for puerto_gaitan_turismo project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    # OpenAPI Schema
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),

    path('api/auth/', include('api.auth_urls')),
    path('api/auth/registration/', include('dj_rest_auth.registration.urls')),

    # Rutas de la API de la aplicación principal
    path("api/", include("api.urls")),

    # Panel "Mi Negocio" para Prestadores
    path("api/v1/mi-negocio/", include("apps.prestadores.mi_negocio.urls")),

    # Nueva API para el panel de administración de la plataforma
    path('api/admin/plataforma/', include('apps.admin_plataforma.urls')),

    # --- DOMINIOS NORMALIZADOS (api/v1/) ---

    # Comercial
    path('api/v1/sales/', include('apps.comercial.urls')),
    path('api/v1/commercial-engine/', include('apps.commercial_engine.urls')),
    path('api/v1/web-funnel/', include('apps.web_funnel.urls')),
    path('api/v1/cart/', include('apps.cart.urls')),
    path('api/v1/payments/', include('apps.payments.urls')),

    # Finanzas
    path('api/v1/finance/wallet/', include('apps.wallet.urls')),
    path('api/v1/finance/ledger/', include('apps.prestadores.mi_negocio.gestion_contable.contabilidad.urls')),
    path('api/v1/finance/indicators/', include('apps.finanzas.urls')),

    # Operaciones y Logística
    path('api/v1/operations/delivery/', include('apps.delivery.urls')),
    path('api/v1/operations/intelligence/', include('apps.operational_intelligence.urls')),

    # Capital Humano
    path('api/v1/payroll/', include('apps.prestadores.mi_negocio.gestion_contable.nomina.urls')),

    # Inteligencia y Agentes
    path('api/v1/agents/sadi/', include('apps.sadi_agent.urls')),
    path('api/v1/agents/sarita/', include('apps.sarita_agents.urls')),

    # Gobernanza y Holding
    path('api/v1/governance/control-tower/', include('apps.admin_control_tower.urls')),
    path('api/v1/governance/intelligence/', include('apps.decision_intelligence.urls')),
    path('api/v1/governance/optimization/', include('apps.ecosystem_optimization.urls')),
    path('api/v1/governance/plataforma/', include('apps.admin_plataforma.urls')),

    # --- ALIAS DE COMPATIBILIDAD (DEPRECATED) ---
    path('api/comercial/', include('apps.comercial.urls')),
    path('api/commercial-engine/', include('apps.commercial_engine.urls')),
    path('api/web/', include('apps.web_funnel.urls')),
    path('api/cart/', include('apps.cart.urls')),
    path('api/payments/', include('apps.payments.urls')),
    path('api/wallet/', include('apps.wallet.urls')),
    path('api/delivery/', include('apps.delivery.urls')),
    path('api/sadi/', include('apps.sadi_agent.urls')),
    path('api/sarita/', include('apps.sarita_agents.urls')),
    path('api/contabilidad/', include('apps.prestadores.mi_negocio.gestion_contable.contabilidad.urls')),
    path('api/nomina/', include('apps.prestadores.mi_negocio.gestion_contable.nomina.urls')),
    path('api/admin/control-tower/', include('apps.admin_control_tower.urls')),
    path('api/admin/intelligence/', include('apps.decision_intelligence.urls')),
    path('api/admin/optimization/', include('apps.ecosystem_optimization.urls')),
    path('api/admin/finanzas/', include('apps.finanzas.urls')),

    # API para Interoperabilidad Internacional (Z-TRUST-NET)
    path('api/v1/international-interop/', include('apps.international_interop.urls')),

    # API para Peace-Net (Estabilidad Global)
    path('api/v1/peace-net/', include("apps.peace_net.urls")),

    # API para Tratados Operativos (Z-OPERATIONAL-TREATIES)
    path('api/v1/operational-treaties/', include("apps.operational_treaties.urls")),

    # API para Inteligencia Operativa (Fase 5)
    path('api/operational-intelligence/', include('apps.operational_intelligence.urls')),

    # API para Custodia de Legado (Fase Legado)
    path('api/v1/legacy/', include("legacy_custody.urls")),

    # FASE 18: Autonomous Economic Ecosystem (EOE)
    path('api/v1/economic-ecosystem/', include('apps.economic_ecosystem.urls')),

    # FASE 19: Corporate Sovereign Infrastructure (CSI)
    path('api/v1/sovereign-infrastructure/', include('apps.sovereign_infrastructure.urls')),

    # FASE 20: Meta-Economic Autonomous Network (MAN)
    path('api/v1/meta-economic-network/', include('apps.meta_economic_network.urls')),

    # FASE 21: State-Integrated Economic Infrastructure (SIEI)
    path('api/v1/state-integration/', include('apps.state_integration.urls')),

    # FASE 22: Hybrid Transnational Governance (HTG)
    path('api/v1/transnational-governance/', include('apps.transnational_governance.urls')),

    # FASE 23: Global Digital Economic Infrastructure (GDEI)
    path('api/v1/global-digital-infrastructure/', include('apps.global_digital_infrastructure.urls')),

    # FASE 24: Public-Private Macroeconomic Coordination (PPMCF)
    path('api/v1/macroeconomic-coordination/', include('apps.macroeconomic_coordination.urls')),

    # FASE 25: Global Integrated Financial Stability (GIFSA)
    path('api/v1/financial-stability/', include('apps.financial_stability.urls')),

    # EOS Activation: Enterprise Operating System Core
    path('api/v1/enterprise-core/', include('apps.enterprise_core.urls')),
    path('api/v1/governance/', include('apps.core_erp.urls')),
    path('api/enterprise/', include('apps.enterprise_core.urls')),

    # EOS Maturity & Self-Reporting
    path('api/enterprise/governance/', include('apps.enterprise_governance.urls')),

    # FASE 8: Infraestructura y Observabilidad Global
    path('api/v1/infra/', include('apps.common.observability.urls')),

    # Geointeligencia y Mapas
    path('api/v1/tourism-map/', include('apps.tourism_map.urls')),

    # Operación Móvil en Campo
    path('api/v1/operational/', include('apps.operational_mobile.urls')),
    path("api/v1/turismo/", include("apps.turismo.urls")),
    path("api/v1/marketplace/", include("apps.tourism_marketplace.urls")),
    path("api/v1/tourism/intelligence/", include("apps.tourism_intelligence.urls")),
    path("api/v1/social/", include("apps.social.urls")),
    path("api/v1/turismo/divipola/", include("apps.turismo.api.urls")),


    # Redirecciones para cumplir Directiva Frontend
    path("api/v1/providers/", include("apps.turismo.api.urls")),
    path("api/v1/reservations/", include("apps.turismo.api.urls")),

    # Triple Vía de Usuarios
    path("api/v1/", include("api.triple_via_urls")),
]

# Servir archivos multimedia y la URL del admin en modo de desarrollo
if settings.DEBUG:
    urlpatterns += [
        path('admin/', admin.site.urls),
    ]
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
