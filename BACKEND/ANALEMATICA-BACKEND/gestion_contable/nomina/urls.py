from rest_framework.routers import DefaultRouter
from .views import (
    EmployeeViewSet, EmploymentContractViewSet,
    PayrollRunViewSet, PayrollConceptViewSet
)

router = DefaultRouter()
router.register(r'employees', EmployeeViewSet, basename='employee')
router.register(r'contracts', EmploymentContractViewSet, basename='contract')
router.register(r'payroll-runs', PayrollRunViewSet, basename='payroll-run')
router.register(r'concepts', PayrollConceptViewSet, basename='payroll-concept')

urlpatterns = router.urls
