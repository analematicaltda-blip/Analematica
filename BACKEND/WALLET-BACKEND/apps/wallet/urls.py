from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import WalletAccountViewSet, WalletTransactionViewSet, WalletTransferViewSet, WalletDeviceViewSet

router = DefaultRouter()
router.register(r'accounts', WalletAccountViewSet, basename='wallet-account')
router.register(r'transactions', WalletTransactionViewSet, basename='wallet-transaction')
router.register(r'transfers', WalletTransferViewSet, basename='wallet-transfer')
router.register(r'devices', WalletDeviceViewSet, basename='wallet-device')

urlpatterns = [
    path('', include(router.urls)),
]
