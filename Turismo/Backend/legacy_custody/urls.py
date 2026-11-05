from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import LegacyDashboardViewSet, LegacyMilestoneViewSet

router = DefaultRouter()
router.register(r'milestones', LegacyMilestoneViewSet, basename='legacy-milestone')

urlpatterns = [
    path('dashboard/', LegacyDashboardViewSet.as_view({'get': 'list'}), name='legacy-dashboard'),
    path('', include(router.urls)),
]
