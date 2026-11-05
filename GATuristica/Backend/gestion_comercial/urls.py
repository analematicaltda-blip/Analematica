from rest_framework.routers import DefaultRouter
from .views import OperacionComercialViewSet, ClienteViewSet
from .presentation.views import BusinessReportsViewSet

router = DefaultRouter()
router.register(r'operaciones', OperacionComercialViewSet)
router.register(r'clientes', ClienteViewSet)
router.register(r'reports', BusinessReportsViewSet, basename='business-reports')

from .views_factura import FacturaViewSet
router.register(r'facturas', FacturaViewSet)
urlpatterns = router.urls
