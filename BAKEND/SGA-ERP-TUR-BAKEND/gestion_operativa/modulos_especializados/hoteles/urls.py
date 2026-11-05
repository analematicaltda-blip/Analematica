from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'amenities', views.AmenityViewSet, basename='amenity')
router.register(r'room-types', views.RoomTypeViewSet, basename='roomtype')
router.register(r'rooms', views.RoomViewSet, basename='room')

urlpatterns = router.urls
