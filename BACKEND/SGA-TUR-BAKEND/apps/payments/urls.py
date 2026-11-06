
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PaymentViewSet, PaymentWebhookViewSet

router = DefaultRouter()
router.register(r'', PaymentViewSet, basename='payment')
router.register(r'webhooks', PaymentWebhookViewSet, basename='payment-webhook')

urlpatterns = router.urls
