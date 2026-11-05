from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import OperationalTreatyViewSet

router = DefaultRouter()
router.register(r'management', OperationalTreatyViewSet, basename='treaty-management')

urlpatterns = [
    path('', include(router.urls)),
]
