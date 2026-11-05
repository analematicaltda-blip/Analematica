from django.test import TestCase
from ..models import Plan, Subscription, UsageMetric
from ..commercial_core.subscription_engine import SubscriptionEngine
from ..commercial_core.pricing_engine import PricingEngine
from decimal import Decimal
import uuid

class CommercialCoreTestCase(TestCase):
    def setUp(self):
        self.plan = Plan.objects.create(
            name="Plan Pro",
            code="PRO-01",
            monthly_price=Decimal('100.00'),
            storage_limit_gb=10
        )
        self.tenant_id = "tenant-test-123"

    def test_subscription_activation(self):
        sub = SubscriptionEngine.activate_subscription(self.tenant_id, self.plan)
        self.assertEqual(sub.status, Subscription.Status.ACTIVE)
        self.assertEqual(sub.plan, self.plan)

    def test_pricing_calculation(self):
        sub = SubscriptionEngine.activate_subscription(self.tenant_id, self.plan)
        total = PricingEngine.calculate_subscription_total(sub)
        self.assertEqual(total, Decimal('100.00'))

    def test_plan_change(self):
        new_plan = Plan.objects.create(
            name="Plan Enterprise",
            code="ENT-01",
            monthly_price=Decimal('500.00')
        )
        sub = SubscriptionEngine.activate_subscription(self.tenant_id, self.plan)
        SubscriptionEngine.change_plan(sub, new_plan)
        self.assertEqual(sub.plan.code, "ENT-01")
