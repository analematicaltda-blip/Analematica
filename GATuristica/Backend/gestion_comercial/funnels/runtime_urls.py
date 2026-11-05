# funnels/runtime_urls.py
from django.urls import path
from .runtime_views import FunnelEventView, LeadDetailView

urlpatterns = [
    path('events/', FunnelEventView.as_view(), name='runtime-event'),
    path('leads/<uuid:lead_id>/', LeadDetailView.as_view(), name='runtime-lead-detail'),
]
