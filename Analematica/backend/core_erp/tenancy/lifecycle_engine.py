import logging
from apps.core_erp.tenancy.models import Tenant
from apps.core_erp.event_bus import EventBus
from apps.core_erp.accounting.models import ChartOfAccounts, Account, FiscalPeriod
from apps.control_tower.models import KPI
from apps.enterprise_core.models.risk_snapshot import RiskSnapshot
from django.db import transaction
from django.utils import timezone

logger = logging.getLogger(__name__)

class TenantLifecycleEngine:
    """
    Automates the full lifecycle of a tenant.
    Integrated with EventBus for asynchronous provisioning and state enforcement.
    """

    @staticmethod
    def start_listening():
        EventBus.subscribe("TENANT_PROVISIONING_REQUESTED", TenantLifecycleEngine.on_provision_request)
        EventBus.subscribe("SUBSCRIPTION_EXPIRED", TenantLifecycleEngine.on_subscription_expired)
        logger.info("TENANT LIFECYCLE ENGINE: Listening for lifecycle events.")

    @staticmethod
    def on_provision_request(payload: dict):
        tenant_name = payload.get('name')
        tenant_id = payload.get('tenant_id')

        with transaction.atomic():
            tenant = Tenant.objects.get(id=tenant_id)

            # 1. Initialize Baseline Snapshots
            TenantLifecycleEngine._initialize_ledger_baseline(tenant)
            TenantLifecycleEngine._initialize_kpi_baseline(tenant)
            TenantLifecycleEngine._initialize_risk_baseline(tenant)

            tenant.state = Tenant.State.ACTIVE
            tenant.save()

            logger.warning(f"TENANT LIFECYCLE: {tenant_name} ({tenant_id}) is now ACTIVE.")

            EventBus.emit("TENANT_PROVISIONED", {"tenant_id": str(tenant.id), "status": "ACTIVE"})

    @staticmethod
    def on_subscription_expired(payload: dict):
        tenant_id = payload.get('tenant_id')
        tenant = Tenant.objects.get(id=tenant_id)

        if tenant.state == Tenant.State.ACTIVE:
            tenant.state = Tenant.State.GRACE
            logger.warning(f"TENANT LIFECYCLE: {tenant.name} moved to GRACE period.")
        elif tenant.state == Tenant.State.GRACE:
            tenant.state = Tenant.State.SUSPENDED
            logger.critical(f"TENANT LIFECYCLE: {tenant.name} SUSPENDED due to non-payment.")

        tenant.save()

    @staticmethod
    def _initialize_ledger_baseline(tenant):
        """Creates the initial financial structure for the new tenant."""
        coa = ChartOfAccounts.objects.create(tenant=tenant, name=f"Plan de Cuentas - {tenant.name}")
        # Add basic mandatory accounts...
        Account.objects.create(chart_of_accounts=coa, tenant=tenant, code='110505', name='Caja General', type='ASSET')

        FiscalPeriod.objects.create(
            tenant=tenant,
            period_start=timezone.now().date(),
            period_end=timezone.now().date() + timezone.timedelta(days=365)
        )

    @staticmethod
    def _initialize_kpi_baseline(tenant):
        """Sets the starting KPIs at 0."""
        KPI.objects.create(tenant=tenant, name='MRR', value=0.00, category='STRATEGIC')
        KPI.objects.create(tenant=tenant, name='CHURN_RATE', value=0.00, category='STRATEGIC')

    @staticmethod
    def _initialize_risk_baseline(tenant):
        """Registers the initial risk assessment."""
        RiskSnapshot.objects.create(tenant=tenant, overall_score=0.1, risk_factors={"onboarding": "completed"})
