from rest_framework.routers import DefaultRouter
from .views import ProjectViewSet, ProjectIncomeViewSet, ProjectCostViewSet

router = DefaultRouter()
router.register(r'projects', ProjectViewSet, basename='project')
router.register(r'incomes', ProjectIncomeViewSet, basename='project-income')
router.register(r'costs', ProjectCostViewSet, basename='project-cost')

urlpatterns = router.urls
