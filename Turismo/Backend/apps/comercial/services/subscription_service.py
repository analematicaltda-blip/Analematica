import logging
from ..models import Subscription
from ..models import Plan
from ..engines.subscription_engine import SubscriptionEngine
from ..engines.billing_engine import BillingEngine

logger = logging.getLogger(__name__)

class SubscriptionService:
    """
    Servicio de orquestación de suscripciones y monetización.
    """

    @staticmethod
    def create_subscription(tenant_id, plan: Plan):
        return SubscriptionEngine.create_subscription(tenant_id, plan)

    @staticmethod
    def activate_subscription(subscription_id):
        sub = Subscription.objects.get(id=subscription_id)
        sub.status = Subscription.Status.ACTIVE
        sub.save()
        invoice = BillingEngine.generate_invoice(sub)
        return invoice

    @staticmethod
    def renew_subscription(subscription_id):
        sub = Subscription.objects.get(id=subscription_id)
        invoice = BillingEngine.generate_invoice(sub)
        from datetime import date, timedelta
        sub.next_billing_date = date.today() + timedelta(days=30)
        sub.save()
        return invoice

    @staticmethod
    def upgrade_subscription(subscription_id, new_plan_code):
        sub = Subscription.objects.get(id=subscription_id)
        new_plan = Plan.objects.get(code=new_plan_code)
        SubscriptionEngine.upgrade_plan(sub, new_plan)
        invoice = BillingEngine.generate_invoice(sub)
        return invoice

    @staticmethod
    def cancel_subscription(subscription_id, immediate=False):
        sub = Subscription.objects.get(id=subscription_id)
        SubscriptionEngine.cancel_subscription(sub, immediate=immediate)
        return sub

    @staticmethod
    def handle_payment_failure(subscription_id):
        sub = Subscription.objects.get(id=subscription_id)
        sub.status = Subscription.Status.SUSPENDED
        sub.save()
        return sub
