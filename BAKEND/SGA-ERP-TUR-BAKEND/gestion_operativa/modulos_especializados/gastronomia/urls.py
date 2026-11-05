from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    RestauranteViewSet,
    MenuViewSet,
    CategoriaPlatoViewSet,
    PlatoViewSet,
    ZonaDeliveryViewSet,
)

router = DefaultRouter()
router.register(r'restaurantes', RestauranteViewSet, basename='restaurante')
router.register(r'menus', MenuViewSet, basename='menu')
router.register(r'categorias-plato', CategoriaPlatoViewSet, basename='categoriaplato')
router.register(r'platos', PlatoViewSet, basename='plato')
router.register(r'zonas-delivery', ZonaDeliveryViewSet, basename='zonadelivery')

urlpatterns = [
    path('', include(router.urls)),
]
