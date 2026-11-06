from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# ==============================================================================
# El DefaultRouter de DRF genera automáticamente las URLs estándar para los ViewSets.
# Por ejemplo, para `DocumentViewSet` generará:
# /gestion-archivistica/documents/       (GET para listar, POST para crear)
# /gestion-archivistica/documents/{pk}/  (GET para detalle)
# ==============================================================================

router = DefaultRouter()

# --- Registro de Endpoints de Catálogos ---
router.register(r'process-types', views.ProcessTypeViewSet, basename='processtype')
router.register(r'processes', views.ProcessViewSet, basename='process')
router.register(r'document-types', views.DocumentTypeViewSet, basename='documenttype')

# --- Registro del Endpoint Principal de Documentos ---
# Se registra con `basename='document'` para poder crear URLs personalizadas si fuera necesario.
router.register(r'documents', views.DocumentViewSet, basename='document')

# `urlpatterns` es la variable que Django busca en este archivo.
# Incluimos todas las URLs generadas por el router.
urlpatterns = [
    path('', include(router.urls)),
]

# El resultado final son endpoints como (asumiendo que este router se monta bajo 'gestion-archivistica/'):
# GET, POST /api/v1/mi-negocio/gestion-archivistica/documents/
# GET      /api/v1/mi-negocio/gestion-archivistica/documents/{id}/
# POST     /api/v1/mi-negocio/gestion-archivistica/documents/{id}/versions/
# GET      /api/v1/mi-negocio/gestion-archivistica/processes/
