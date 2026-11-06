# backend/apps/sarita_agents/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('directive/', views.DirectiveView.as_view(), name='sarita_directive'),
    path('missions/<uuid:id>/', views.MissionStatusView.as_view(), name='sarita_mission_status'),
    path('metrics/productivity/', views.ProductivityMetricsView.as_view(), name='sarita_productivity_metrics'),
]
