import logging
from decimal import Decimal
from django.utils import timezone
from ..domain.intelligence import ScenarioSimulation, RollingForecast
from ..domain.budget import CorporateBudget

logger = logging.getLogger(__name__)

class StrategicIntelligenceService:
    """
    Strategic Intelligence Layer of EOS.
    Provides simulation, continuous forecasting, and high-level projections.
    """

    @staticmethod
    def run_simulation(tenant_id, name, growth_rate, fx_var, inflation):
        """
        Simulates a financial scenario based on growth and macro variables.
        """
        # Fetch current year budget as baseline
        current_year = timezone.now().year
        budget = CorporateBudget.objects.filter(tenant_id=tenant_id, fiscal_year=current_year).first()

        if not budget:
            raise ValueError(f"No budget found for year {current_year}")

        # Basic Simulation Logic
        projected_revenue = budget.revenue_target * (1 + growth_rate)
        projected_expenses = budget.expense_limit * (1 + inflation)

        # FX impact on revenue (assumed 50% international)
        fx_impact = (projected_revenue * Decimal('0.5')) * fx_var
        projected_revenue += fx_impact

        ebitda = projected_revenue - projected_expenses

        simulation = ScenarioSimulation.objects.create(
            tenant_id=tenant_id,
            name=name,
            revenue_growth_rate=growth_rate,
            fx_variation=fx_var,
            cost_inflation=inflation,
            projected_ebitda=ebitda,
            projected_cash_position=ebitda * Decimal('0.8') # Simplified conversion
        )

        logger.info(f"EOS Strategic: Simulation '{name}' completed for tenant {tenant_id}")
        return simulation

    @staticmethod
    def update_rolling_forecast(tenant_id):
        """
        Recalculates the monthly rolling forecast based on Ledger actuals.
        """
        from apps.core_erp.accounting.reports_engine import ReportsEngine

        today = timezone.now()
        current_year = today.year
        current_month = today.month

        # 1. Fetch Actuals from Ledger
        pnl = ReportsEngine.get_p_and_l(
            tenant_id,
            timezone.datetime(current_year, current_month, 1).date(),
            today.date()
        )

        # 2. Fetch Budget
        budget = CorporateBudget.objects.filter(tenant_id=tenant_id, fiscal_year=current_year).first()
        if not budget: return

        monthly_target = budget.revenue_target / Decimal('12.0')
        variance = pnl['income'] - monthly_target

        forecast, _ = RollingForecast.objects.update_or_create(
            tenant_id=tenant_id,
            fiscal_year=current_year,
            month=current_month,
            defaults={
                "base_budget_revenue": monthly_target,
                "actual_revenue_mtd": pnl['income'],
                "projected_variance": variance
            }
        )

        logger.info(f"EOS Strategic: Rolling forecast updated for M{current_month} Y{current_year}")
        return forecast
