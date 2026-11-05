from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SubscriptionPortalViewSet, PublicPlanViewSet

app_name = 'comercial'

router = DefaultRouter()
router.register(r'my-subscription', SubscriptionPortalViewSet, basename='my-subscription')
router.register(r'plans', PublicPlanViewSet, basename='public-plans')

urlpatterns = [
    path('', include(router.urls)),
]
