from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import WalletAccountViewSet, WalletTransactionViewSet

router = DefaultRouter()
router.register(r'accounts', WalletAccountViewSet, basename='wallet-account')
router.register(r'transactions', WalletTransactionViewSet, basename='wallet-transaction')

urlpatterns = [
    path('', include(router.urls)),
]
