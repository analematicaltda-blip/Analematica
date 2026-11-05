from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'skills', views.SkillViewSet, basename='skill')
router.register(r'tours', views.TourProductViewSet, basename='tour')

urlpatterns = router.urls
