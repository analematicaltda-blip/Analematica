from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PeaceNetViewSet

router = DefaultRouter()
router.register(r'stability', PeaceNetViewSet, basename='stability')

urlpatterns = [
    path('', include(router.urls)),
]
