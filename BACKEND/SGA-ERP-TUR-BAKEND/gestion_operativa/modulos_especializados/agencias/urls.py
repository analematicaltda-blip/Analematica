# backend/apps/prestadores/mi_negocio/gestion_operativa/modulos_especializados/agencias/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter

router = DefaultRouter()

urlpatterns = [
    path('', include(router.urls)),
]
