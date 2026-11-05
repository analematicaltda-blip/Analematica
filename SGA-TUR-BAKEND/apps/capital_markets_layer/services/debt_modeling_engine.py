from decimal import Decimal
from apps.institutional_layer.services.investor_reporting_engine import InvestorReportingEngine

class DebtModelingEngine:
    """
    Motor de modelado de deuda y apalancamiento financiero (Fase 8).
    """

    @staticmethod
    def calculate_dscr(net_income, principal_payment, interest_payment):
        """
        Debt Service Coverage Ratio.
        """
        total_service = principal_payment + interest_payment
        if total_service == 0: return 99.0
        return float(net_income / total_service)

    @staticmethod
    def model_venture_debt(amount, interest_rate, term_months):
        """
        Simula impacto de deuda en el holding.
        """
        metrics = InvestorReportingEngine.get_board_deck_metrics()

        monthly_interest = (amount * (interest_rate / 100)) / 12
        monthly_principal = amount / term_months

        dscr = DebtModelingEngine.calculate_dscr(metrics['mrr'] * Decimal('0.3'), monthly_principal, monthly_interest)

        return {
            "monthly_service": monthly_principal + monthly_interest,
            "dscr_proyectado": dscr,
            "runway_impact": "RED" if dscr < 1.2 else "GREEN",
            "covenants_monitored": ["LTV/CAC > 3", "Churn < 5%"]
        }
