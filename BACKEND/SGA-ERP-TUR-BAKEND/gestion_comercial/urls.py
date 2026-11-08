from rest_framework.routers import DefaultRouter
from .views import OperacionComercialViewSet, ClienteViewSet
from .presentation.views import BusinessReportsViewSet

router = DefaultRouter()
router.register(r'operaciones', OperacionComercialViewSet)
router.register(r'clientes', ClienteViewSet)
router.register(r'reports', BusinessReportsViewSet, basename='business-reports')

from .views_factura import FacturaViewSet
router.register(r'facturas', FacturaViewSet)
from django.urls import path
from .views import QuotationPreviewView
urlpatterns = [path('quotation-preview/',QuotationPreviewView.as_view(),name='quotation-preview'),*router.urls]

from .quote_views import QuotationDraftCollection,QuotationDraftDetail,QuotationDraftWithdraw
urlpatterns += [
 path('quotation-drafts/',QuotationDraftCollection.as_view(),name='quotation-drafts'),
 path('quotation-drafts/<uuid:pk>/',QuotationDraftDetail.as_view(),name='quotation-draft-detail'),
 path('quotation-drafts/<uuid:pk>/withdraw/',QuotationDraftWithdraw.as_view(),name='quotation-draft-withdraw'),
]

from .quote_views import QuotationOptions
urlpatterns += [path("quotation-options/",QuotationOptions.as_view(),name="quotation-options")]

from .availability_views import ServiceAvailability,CapacityHoldCreate,CapacityHoldRelease
urlpatterns += [path('service-availability/',ServiceAvailability.as_view()),path('capacity-holds/',CapacityHoldCreate.as_view()),path('capacity-holds/<uuid:pk>/release/',CapacityHoldRelease.as_view())]

from .quote_views import CompanyScopeOptions
urlpatterns += [path('company-scopes/',CompanyScopeOptions.as_view())]
