from rest_framework.routers import DefaultRouter
from .views import SupplierViewSet, PurchaseInvoiceViewSet

router = DefaultRouter()
router.register(r'suppliers', SupplierViewSet, basename='supplier')
router.register(r'invoices', PurchaseInvoiceViewSet, basename='purchase-invoice')

urlpatterns = router.urls
