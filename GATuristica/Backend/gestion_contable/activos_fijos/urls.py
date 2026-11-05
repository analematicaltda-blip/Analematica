from rest_framework.routers import DefaultRouter
from .views import CategoriaActivoViewSet, ActivoFijoViewSet, CalculoDepreciacionViewSet

router = DefaultRouter()
router.register(r'categorias', CategoriaActivoViewSet, basename='categoria-activo')
router.register(r'activos', ActivoFijoViewSet, basename='activo-fijo')
router.register(r'depreciaciones', CalculoDepreciacionViewSet, basename='calculo-depreciacion')

urlpatterns = router.urls
