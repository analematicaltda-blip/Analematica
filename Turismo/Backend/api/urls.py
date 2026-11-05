from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers
from . import views

# --- Routers ---
class NestedDefaultRouter(DefaultRouter):
    def _register_nested_router(self, nested_router):
        pass

router = NestedDefaultRouter()
prestador_resenas_router = DefaultRouter()
prestador_resenas_router.register(r'valoraciones', views.PrestadorResenaUpdateViewSet, basename='prestador-resena-update')

# Endpoints para Multi-Entity
router.register(r'entities', views.EntityViewSet, basename='entity')
router.register(r'departments', views.DepartmentViewSet, basename='department')
router.register(r'municipalities', views.MunicipalityViewSet, basename='municipality')

# Recursos de Administración y Contenido General
router.register(r'notificaciones', views.NotificacionViewSet, basename='notificacion')
router.register(r'atractivos', views.AtractivoTuristicoViewSet, basename='atractivo')
router.register(r'rutas-turisticas', views.RutaTuristicaViewSet, basename='ruta-turistica')
router.register(r'hechos-historicos', views.HechoHistoricoViewSet, basename='hecho-historico')
router.register(r'mi-viaje', views.ElementoGuardadoViewSet, basename='elemento-guardado')
router.register(r'config/menu-items', views.MenuItemViewSet, basename='menu-item')
router.register(r'contenido-municipio', views.ContenidoMunicipioViewSet, basename='contenido-municipio')
router.register(r'paginas-institucionales', views.PaginaInstitucionalViewSet, basename='pagina-institucional')
router.register(r'admin/users', views.UserViewSet, basename='user-admin')
router.register(r'admin/publicaciones', views.AdminPublicacionViewSet, basename='publicacion-admin')
router.register(r'admin/homepage-components', views.HomePageComponentViewSet, basename='homepage-component')
router.register(r'admin/audit-logs', views.AuditLogViewSet, basename='audit-log')
router.register(r'admin/scoring-rules', views.ScoringRuleViewSet, basename='scoring-rule')
router.register(r'admin/artesanos', views.AdminArtesanoViewSet, basename='adminartesano')
router.register(r'resenas', views.ResenaViewSet, basename='resena')
router.register(r'sugerencias', views.SugerenciaViewSet, basename='sugerencia')
router.register(r'admin/sugerencias', views.SugerenciaAdminViewSet, basename='sugerencia-admin')

router.register(r'documentos-verificacion/tipos', views.TipoDocumentoVerificacionViewSet, basename='tipo-documento-verificacion')

# --- Verificación de Cumplimiento ---
router.register(r'admin/plantillas-verificacion', views.PlantillaVerificacionViewSet, basename='plantilla-verificacion')
router.register(r'admin/verificaciones', views.VerificacionViewSet, basename='verificacion')


# --- Formularios Dinámicos (con rutas anidadas) ---
router.register(r'formularios', views.FormularioViewSet, basename='formulario')

# /formularios/{formulario_pk}/preguntas/
preguntas_router = routers.NestedSimpleRouter(router, r'formularios', lookup='formulario')
preguntas_router.register(r'preguntas', views.PreguntaViewSet, basename='formulario-pregunta')

# /formularios/{formulario_pk}/preguntas/{pregunta_pk}/opciones/
opciones_router = routers.NestedSimpleRouter(preguntas_router, r'preguntas', lookup='pregunta')
opciones_router.register(r'opciones', views.OpcionRespuestaViewSet, basename='pregunta-opcion')


urlpatterns = [
    # --- Configuración del Sitio (Acceso Público/Restringido) ---
    path('config/site-config/', views.SiteConfigurationView.as_view(), name='site-configuration'),

    # --- Vistas de Entidad ---
    path('entities/current/', views.CurrentEntityView.as_view(), name='current-entity'),

    # --- Vistas Privadas (Requieren Autenticación) ---
    path('admin/my-entity/', views.EntityAdminView.as_view(), name='entity-admin'),
    path('profile/artesano/', views.ArtesanoProfileView.as_view(), name='artesano-profile'),
    path('profile/feedback/', views.FeedbackProveedorView.as_view(), name='proveedor-feedback'),
    path('config/my-llm/', views.UserLLMConfigView.as_view(), name='user-llm-config'),

    # --- Rutas para galerías y documentos ---
    path('galeria/artesano/', views.ImagenArtesanoView.as_view(), name='artesano-galeria-list-create'),
    path('galeria/artesano/<int:pk>/', views.ImagenArtesanoDetailView.as_view(), name='artesano-galeria-detail'),

    # --- Rutas de Formularios Dinámicos (Respuestas) ---

# Rutas para usuarios (funcionarios y usuarios finales)
path(
    'formularios/<int:formulario_pk>/respuestas/',
    views.RespuestaUsuarioViewSet.as_view({'get': 'list', 'post': 'create'}),
    name='formulario-respuestas-usuario'
),
# Ver solo las respuestas propias de un usuario
path(
    'formularios/<int:formulario_pk>/respuestas/mias/',
    views.RespuestaUsuarioViewSet.as_view({'get': 'retrieve'}),
    name='mis-respuestas-retrieve'
),
# Funcionario ve respuestas de un usuario específico
path(
    'formularios/<int:formulario_pk>/respuestas/<int:usuario_pk>/',
    views.RespuestaUsuarioViewSet.as_view({'get': 'retrieve'}),
    name='usuario-respuesta-retrieve'
),


    # --- Incluimos las rutas de todos los routers ---
    path('', include(router.urls)),
    path('', include(preguntas_router.urls)),
    path('', include(opciones_router.urls)),

    # --- Vistas Públicas (Namespace v1/public) ---
    path('v1/public/sugerencias/felicitaciones-publicas/', views.FelicitacionesPublicasView.as_view(), name='v1-public-felicitaciones-list'),
    path('v1/public/artesanos/rubros/', views.RubroArtesanoListView.as_view(), name='v1-public-artesano-rubros-list'),
    path('v1/public/artesanos/', views.ArtesanoPublicListView.as_view(), name='v1-public-artesano-list'),
    path('v1/public/artesanos/<int:pk>/', views.ArtesanoPublicDetailView.as_view(), name='v1-public-artesano-detail'),
    path('v1/public/publicaciones/', views.PublicacionListView.as_view(), name='v1-public-publicaciones-list'),
    path('v1/public/publicaciones/<slug:slug>/', views.PublicacionDetailView.as_view(), name='v1-public-publicaciones-detail'),
    path('v1/public/consejo-consultivo/', views.ConsejoConsultivoListView.as_view(), name='v1-public-consejo-list'),
    path('v1/public/videos/', views.VideoListView.as_view(), name='v1-public-videos-list'),
    path('v1/public/locations/', views.LocationListView.as_view(), name='v1-public-locations-list'),
    path('v1/public/galeria-media/', views.GaleriaListView.as_view(), name='v1-public-galeria-list'),

    # --- Legacy aliases ---
    path('sugerencias/felicitaciones-publicas/', views.FelicitacionesPublicasView.as_view(), name='felicitaciones-publicas-list'),
    path('artesanos/rubros/', views.RubroArtesanoListView.as_view(), name='artesano-rubros-list'),
    path('artesanos/', views.ArtesanoPublicListView.as_view(), name='artesano-public-list'),
    path('artesanos/<int:pk>/', views.ArtesanoPublicDetailView.as_view(), name='artesano-public-detail'),
    path('publicaciones/', views.PublicacionListView.as_view(), name='publicaciones-list'),
    path('publicaciones/<slug:slug>/', views.PublicacionDetailView.as_view(), name='publicaciones-detail'),
    path('consejo-consultivo/', views.ConsejoConsultivoListView.as_view(), name='consejo-consultivo-list'),
    path('videos/', views.VideoListView.as_view(), name='videos-list'),
    path('locations/', views.LocationListView.as_view(), name='locations-list'),
    path('galeria-media/', views.GaleriaListView.as_view(), name='galeria-media-list'),

    # --- v1 compatibility aliases for public tourism flows (Web/Mobile/Desktop parity) ---
    path('v1/atractivos/', views.AtractivoTuristicoViewSet.as_view({'get': 'list', 'post': 'create'}), name='v1-atractivos-list'),
    path('v1/atractivos/<uuid:pk>/', views.AtractivoTuristicoViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}), name='v1-atractivos-detail'),
    path('v1/publicaciones/', views.PublicacionListView.as_view(), name='v1-publicaciones-list'),
    path('v1/publicaciones/<slug:slug>/', views.PublicacionDetailView.as_view(), name='v1-publicaciones-detail'),

    # --- Vistas para el Sistema de Agentes ---
    path('agent/tasks/<uuid:id>/', views.AgentTaskStatusView.as_view(), name='agent-task-status'),

    # --- Mapeos Directos para Frontend (Fase 1 - Gestión Comercial) ---
    path('marketing/', include(('apps.prestadores.mi_negocio.gestion_comercial.marketing.urls', 'marketing'), namespace='marketing')),
    path('funnels/', include(('apps.prestadores.mi_negocio.gestion_comercial.funnels.urls', 'funnel'), namespace='funnel')),
    path('bff/funnel-builder/', include(('apps.prestadores.mi_negocio.gestion_comercial.funnels.urls', 'funnel-builder'), namespace='funnel-builder')),

    # --- Vistas de Administración y Análisis (endpoints específicos no cubiertos por el router) ---
    path('dashboard/analytics/', views.AnalyticsDataView.as_view(), name='dashboard-analytics'),
    path('admin/statistics/detailed/', views.DetailedStatisticsView.as_view(), name='admin-detailed-statistics'),
    path('admin/usuarios/', views.AdminUsuarioListView.as_view(), name='admin-usuario-list'),
]