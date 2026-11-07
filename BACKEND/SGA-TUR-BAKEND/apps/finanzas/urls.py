from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import FinancialDashboardViewSet

router = DefaultRouter()
router.register(r'dashboard', FinancialDashboardViewSet, basename='financial-dashboard')

app_name = 'finanzas'

urlpatterns = [
    path('', include(router.urls)),
]
