from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PeriodoContableViewSet

router = DefaultRouter()
router.register(r'periodos', PeriodoContableViewSet, basename='periodo-contable')

urlpatterns = [
    path('', include(router.urls)),
]
