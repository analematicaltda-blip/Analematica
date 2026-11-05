from django.urls import path
from .views import GlobalDashboardView, RiskPanelView

app_name = 'admin_control_tower'

urlpatterns = [
    path('dashboard/', GlobalDashboardView.as_view(), name='global-dashboard'),
    path('risk-panel/', RiskPanelView.as_view(), name='risk-panel'),
]
