from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import WorkflowViewSet, AgentPersonaViewSet

router = DefaultRouter()
router.register(r'workflows', WorkflowViewSet, basename='workflow')
router.register(r'personas', AgentPersonaViewSet, basename='persona')

urlpatterns = [
    path('', include(router.urls)),
]
