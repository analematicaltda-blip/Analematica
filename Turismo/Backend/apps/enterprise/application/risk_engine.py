import logging
from decimal import Decimal
from django.utils import timezone
from ..domain.decision_engine import RiskExposure
from apps.core_erp.accounting.reports_engine import ReportsEngine

logger = logging.getLogger(__name__)

class RiskEngine:
    """
    Integrated Risk Engine of EOS.
    Monitors financial, FX, and concentration risks in real-time.
    """

    @staticmethod
    def evaluate_all_risks(tenant_id):
        """
        Runs the full risk assessment suite for a tenant.
        """
        RiskEngine._evaluate_liquidity_risk(tenant_id)
        RiskEngine._evaluate_concentration_risk(tenant_id)
        RiskEngine._evaluate_fx_risk(tenant_id)

    @staticmethod
    def _evaluate_liquidity_risk(tenant_id):
        """
        Measures Current Ratio and Runway.
        """
        balance = ReportsEngine.get_balance_sheet(tenant_id, timezone.now().date())
        assets = balance['assets']
        liabilities = balance['liabilities']

        ratio = assets / liabilities if liabilities > 0 else Decimal('99.0')
        level = 'LOW'
        if ratio < 1.2: level = 'MEDIUM'
        if ratio < 1.0: level = 'HIGH'

        RiskExposure.objects.create(
            tenant_id=tenant_id,
            risk_type=RiskExposure.RiskType.FINANCIAL,
            exposure_value=ratio,
            risk_level=level,
            factors={"current_ratio": str(ratio), "total_assets": str(assets)}
        )

    @staticmethod
    def _evaluate_concentration_risk(tenant_id):
        """
        Measures revenue concentration.
        Simplified: checks if a single country or entity exceeds thresholds.
        """
        # In a real system, we'd slice P&L by country dimension
        concentration = Decimal('0.65') # Simulated 65% from one source
        level = 'HIGH' if concentration > 0.6 else 'LOW'

        RiskExposure.objects.create(
            tenant_id=tenant_id,
            risk_type=RiskExposure.RiskType.CONCENTRATION,
            exposure_value=concentration,
            risk_level=level,
            factors={"top_source_pct": str(concentration)}
        )

    @staticmethod
    def _evaluate_fx_risk(tenant_id):
        """
        Measures exposure to currency variations.
        """
        exposure = Decimal('50000.00') # Simulated USD exposure
        RiskExposure.objects.create(
            tenant_id=tenant_id,
            risk_type=RiskExposure.RiskType.FX,
            exposure_value=exposure,
            risk_level='MEDIUM',
            factors={"currency": "USD", "exposure_amount": str(exposure)}
        )
