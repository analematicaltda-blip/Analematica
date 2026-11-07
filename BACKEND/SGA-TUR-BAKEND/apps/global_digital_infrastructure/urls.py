from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    GlobalLedgerViewSet, SchemaRegistryViewSet,
    RegulatorySyncViewSet, DigitalIdentityViewSet,
    DataFabricViewSet, GDEIDashboardViewSet
)

router = DefaultRouter()
router.register(r'ledger', GlobalLedgerViewSet, basename='gdei_ledger')
router.register(r'schemas', SchemaRegistryViewSet, basename='gdei_schemas')
router.register(r'regulatory-sync', RegulatorySyncViewSet, basename='gdei_sync')
router.register(r'identities', DigitalIdentityViewSet, basename='gdei_identities')
router.register(r'data-fabric', DataFabricViewSet, basename='gdei_data')
router.register(r'dashboard', GDEIDashboardViewSet, basename='gdei_dashboard')

urlpatterns = [
    path('', include(router.urls)),
]
