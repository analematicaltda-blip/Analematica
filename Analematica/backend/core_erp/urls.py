# backend/apps/core_erp/urls.py
from django.urls import path
from . import views
from .accounting.presentation.balances_views import AccountBalanceView
from .accounting.presentation.reports_views import BalanceGeneralView, ProfitLossView
from .accounting.presentation.finance_views import FinancialRatiosView, CashFlowView

urlpatterns = [
    path('integrity/status/', views.SystemIntegrityStatusView.as_view(), name='integrity-status'),
    path('integrity/run/', views.RunCertificationView.as_view(), name='integrity-run'),

    # Hallazgo 14: Hidratación de saldos
    path('accounting/balances/', AccountBalanceView.as_view(), name='accounting-balances'),
    path('accounting/reports/balance-general/', BalanceGeneralView.as_view(), name='report-balance-general'),
    path('accounting/reports/p-and-l/', ProfitLossView.as_view(), name='report-p-and-l'),
    path('finance/ratios/', FinancialRatiosView.as_view(), name='finance-ratios'),
    path('finance/cashflow/', CashFlowView.as_view(), name='finance-cashflow'),
]
