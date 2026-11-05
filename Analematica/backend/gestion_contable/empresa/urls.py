from rest_framework.routers import DefaultRouter
from .views import AdminCompanyViewSet

router = DefaultRouter()
router.register(r'profile', AdminCompanyViewSet, basename='admin-company')

urlpatterns = router.urls
