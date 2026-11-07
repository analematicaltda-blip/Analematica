from django.urls import path, include
from rest_framework.routers import DefaultRouter

from rest_framework.routers import DefaultRouter
from .views import PlanCuentaViewSet

router = DefaultRouter()
router.register(r'cuentas', PlanCuentaViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
