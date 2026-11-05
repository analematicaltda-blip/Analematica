from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'kitchen-stations', views.KitchenStationViewSet, basename='kitchenstation')
router.register(r'tables', views.RestaurantTableViewSet, basename='restauranttable')

urlpatterns = router.urls
