import logging
from datetime import date, timedelta
from ..models import Subscription
from ..models import Plan
from apps.admin_plataforma.models import GovernanceAuditLog

logger = logging.getLogger(__name__)

class SubscriptionEngine:
    """
    Motor de ciclo de vida de suscripciones.
    """

    @staticmethod
    def create_subscription(tenant_id, plan: Plan, cycle: str = Subscription.BillingCycle.MONTHLY) -> Subscription:
        start_date = date.today()
        trial_days = 15

        subscription = Subscription.objects.create(
            tenant_id=tenant_id,
            plan=plan,
            status=Subscription.Status.TRIAL,
            billing_cycle=cycle,
            trial_end_date=start_date + timedelta(days=trial_days),
            next_billing_date=start_date + timedelta(days=trial_days),
            is_active=True
        )

        SubscriptionEngine._log_event(subscription, "SUBSCRIPTION_CREATED", f"Iniciada suscripción para plan {plan.code}")
        return subscription

    @staticmethod
    def upgrade_plan(subscription: Subscription, new_plan: Plan):
        old_plan = subscription.plan
        subscription.plan = new_plan
        subscription.save()

        SubscriptionEngine._log_event(subscription, "SUBSCRIPTION_UPGRADE", f"Upgrade: {old_plan.code} -> {new_plan.code}")
        return subscription

    @staticmethod
    def cancel_subscription(subscription: Subscription, immediate: bool = False):
        if immediate:
            subscription.status = Subscription.Status.CANCELED
            subscription.is_active = False
        else:
            subscription.auto_renew = False

        subscription.save()
        SubscriptionEngine._log_event(subscription, "SUBSCRIPTION_CANCELED", f"Inmediata: {immediate}")
        return subscription

    @staticmethod
    def _log_event(subscription, intention, details):
        GovernanceAuditLog.objects.create(
            intencion=intention,
            parametros={
                "subscription_id": str(subscription.id),
                "tenant_id": str(subscription.tenant_id),
                "plan_code": subscription.plan.code
            },
            resultado={"status": "SUCCESS", "message": details},
            success=True
        )
