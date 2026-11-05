from rest_framework.routers import DefaultRouter
from .views import BudgetViewSet, BudgetItemViewSet, BudgetExecutionViewSet

router = DefaultRouter()
router.register(r'budgets', BudgetViewSet, basename='budget')
router.register(r'items', BudgetItemViewSet, basename='budget-item')
router.register(r'executions', BudgetExecutionViewSet, basename='budget-execution')

urlpatterns = router.urls
