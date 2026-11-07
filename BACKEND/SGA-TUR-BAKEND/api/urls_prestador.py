from django.urls import path, include
from rest_framework_nested import routers

from apps.prestadores.mi_negocio.views import productos as productos_views, clientes as clientes_views

# Este archivo se poblará a medida que se refactoricen las vistas.

router = routers.DefaultRouter()
router.register(r'productos', productos_views.ProductoViewSet, basename='productos')
router.register(r'clientes', clientes_views.ClienteViewSet, basename='clientes')

urlpatterns = [
    path('', include(router.urls)),
]