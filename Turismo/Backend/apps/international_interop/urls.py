from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import InternationalInteropViewSet

router = DefaultRouter()
router.register(r'diplomatic-gateway', InternationalInteropViewSet, basename='diplomatic-gateway')

urlpatterns = [
    path('', include(router.urls)),
]
