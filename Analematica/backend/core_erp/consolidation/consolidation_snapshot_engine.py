import logging
from .models import ConsolidatedReportSnapshot
from apps.core_erp.accounting.reports_engine import ReportsEngine
from django.utils import timezone

logger = logging.getLogger(__name__)

class SnapshotGenerator:
    """
    Generates consolidated snapshots for holding entities.
    Part of the Consolidation Snapshot Engine.
    """

    @staticmethod
    def trigger_incremental(tenant_id: str):
        """
        Updates live KPIs for the holding dashboard based on subsidiary changes.
        """
        logger.info(f"EOS SNAPSHOT: Triggering incremental update for tenant {tenant_id}")
        # Logic to update holding-level MRR, Cash, etc.

    @staticmethod
    def generate_full_consolidated_report(holding_id: str, period_id: str):
        """
        Consolidates all subsidiaries into a single financial record.
        Uses ReportsEngine (CQRS Light) for data aggregation.
        """
        logger.info(f"EOS SNAPSHOT: Generating full report for Holding {holding_id}")
        from apps.core_erp.tenancy.models import Tenant

        # 1. Fetch all subsidiaries
        holding = Tenant.plain_objects.get(id=holding_id)
        subsidiaries = holding.subsidiaries.all()

        consolidated_data = {
            "income": 0, "expenses": 0, "assets": 0, "liabilities": 0, "equity": 0
        }

        # 2. Aggregate data from subsidiaries
        for sub in subsidiaries:
            pnl = ReportsEngine.get_p_and_l(sub.id, timezone.now().date(), timezone.now().date()) # Simplified dates
            consolidated_data["income"] += pnl["income"]
            consolidated_data["expenses"] += pnl["expenses"]

        # 3. Run intercompany elimination (Subtract matched IC balances)
        # 4. Save Snapshot
        snapshot = ConsolidatedReportSnapshot.objects.create(
            tenant_id=holding_id,
            report_name=f"Consolidated Report {period_id}",
            period_start=timezone.now().date(), # Should come from period_id
            period_end=timezone.now().date(),
            consolidation_level='HOLDING',
            method_applied='FULL',
            data=consolidated_data,
            is_certified=False
        )
        logger.warning(f"EOS SNAPSHOT CREATED: {snapshot.id}")
        return snapshot
