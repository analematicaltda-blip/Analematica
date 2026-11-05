from rest_framework.routers import DefaultRouter
from .views import CostoViewSet

router = DefaultRouter()
router.register(r'costos', CostoViewSet, basename='costo')

urlpatterns = router.urls
