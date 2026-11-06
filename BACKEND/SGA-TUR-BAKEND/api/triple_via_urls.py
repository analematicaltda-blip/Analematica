from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    GovernmentProfileViewSet, TouristProfileViewSet, DeliveryProfileViewSet,
    BusinessProfileViewSet, BusinessStaffViewSet, UserViewSet,
    AtractivoTuristicoViewSet as TourismProviderViewSet,
    RutaTuristicaViewSet as TourismServiceViewSet
)

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='users-via-compat')
router.register(r'government', GovernmentProfileViewSet, basename='government-via')
router.register(r'tourists', TouristProfileViewSet, basename='tourists-via')
router.register(r'delivery', DeliveryProfileViewSet, basename='delivery-via')
router.register(r'business', BusinessProfileViewSet, basename='business-via')
router.register(r'business-staff', BusinessStaffViewSet, basename='business-staff-via')

urlpatterns = [
    path('', include(router.urls)),
]
