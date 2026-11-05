from rest_framework.routers import DefaultRouter
from .views import ProyectoViewSet, IngresoProyectoViewSet, CostoProyectoViewSet

router = DefaultRouter()
router.register(r'proyectos', ProyectoViewSet, basename='proyecto')
router.register(r'ingresos', IngresoProyectoViewSet, basename='ingreso-proyecto')
router.register(r'costos', CostoProyectoViewSet, basename='costo-proyecto')

urlpatterns = router.urls
