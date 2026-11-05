from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TourismLocationViewSet

router = DefaultRouter()
router.register(r'locations', TourismLocationViewSet, basename='tourism-location')

urlpatterns = [
    path('', include(router.urls)),
]
