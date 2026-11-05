from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DepartmentViewSet, MunicipalityViewSet
from .provider_views import (
    TourismProviderViewSet, BusinessProfileViewSet,
    TourismServiceViewSet, ReservationViewSet
)

router = DefaultRouter()
router.register(r'depts', DepartmentViewSet)
router.register(r'muns', MunicipalityViewSet)
router.register(r'tourism-providers', TourismProviderViewSet)
router.register(r'tourism-services', TourismServiceViewSet)
router.register(r'tourism-reservations', ReservationViewSet)

urlpatterns = [
    path('', include(router.urls)),
]

