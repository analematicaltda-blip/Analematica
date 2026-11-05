from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'publicaciones', views.AdminPublicacionViewSet, basename='admin-publicaciones')
router.register(r'contenido-municipio', views.ContenidoMunicipioViewSet, basename='contenido-municipio')
router.register(r'users', views.UserViewSet, basename='admin-users')
router.register(r'menu-items', views.MenuItemViewSet, basename='admin-menu-items')
router.register(r'homepage-components', views.HomePageComponentViewSet, basename='admin-homepage-components')
router.register(r'audit-logs', views.AuditLogViewSet, basename='admin-audit-logs')
router.register(r'sugerencias', views.SugerenciaAdminViewSet, basename='admin-sugerencias')
router.register(r'artesanos', views.AdminArtesanoViewSet, basename='admin-artesanos')

urlpatterns = [
    path('site-config/', views.SiteConfigurationView.as_view(), name='admin-site-config'),
    path('statistics/detailed/', views.DetailedStatisticsView.as_view(), name='admin-detailed-statistics'),
    path('export-excel/', views.ExportExcelView.as_view(), name='export-excel'),
    path('', include(router.urls)),
]