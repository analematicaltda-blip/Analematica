from django.urls import path
from .views.health import LivenessProbeView, ReadinessProbeView, MetricsEndpointView

urlpatterns = [
    path('health/liveness/', LivenessProbeView.as_view(), name='health_liveness'),
    path('health/readiness/', ReadinessProbeView.as_view(), name='health_readiness'),
    path('metrics/', MetricsEndpointView.as_view(), name='technical_metrics'),
]
