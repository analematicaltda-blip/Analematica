import logging
import json
import uuid
from apps.core_erp.event_bus import EventBus
from .models import SaaSMetric, IntelligenceAuditLog
from django.db.models import Sum
from decimal import Decimal
from django.utils import timezone
from django.core.serializers.json import DjangoJSONEncoder

logger = logging.getLogger(__name__)

class DataCollector:
    """
    Consumes events from various modules to build the Operational Data Mart.
    """

    @staticmethod
    def initialize():
        EventBus.subscribe('SUBSCRIPTION_ACTIVATED', DataCollector.on_subscription_activated)
        EventBus.subscribe('SUBSCRIPTION_CANCELLED', DataCollector.on_subscription_cancelled)
        EventBus.subscribe('PLAN_UPGRADED', DataCollector.on_plan_upgraded)
        EventBus.subscribe('PLAN_DOWNGRADED', DataCollector.on_plan_downgraded)
        EventBus.subscribe('USAGE_BILLED', DataCollector.on_usage_billed)
        EventBus.subscribe('PAYMENT_RECONCILED', DataCollector.on_payment_reconciled)
        EventBus.subscribe('INVOICE_CREATED', DataCollector.on_invoice_created)
        EventBus.subscribe('USAGE_RECORDED', DataCollector.on_usage_recorded)
        logger.info("OPERATIONAL INTELLIGENCE: DataCollector initialized.")

    @staticmethod
    def _clean_payload(payload):
        """Ensures all values in payload are JSON serializable."""
        return json.loads(json.dumps(payload, cls=DjangoJSONEncoder))

    @staticmethod
    def on_subscription_activated(payload):
        # Extract data for MRR/ARR
        amount = payload.get('amount', 0)
        customer_id = payload.get('customer_id')
        plan_name = payload.get('plan_name')

        SaaSMetric.objects.create(
            metric_name='MRR_INFLOW',
            value=amount,
            dimension=f'Plan:{plan_name}',
            meta_data={'customer_id': str(customer_id), 'event': 'SUBSCRIPTION_ACTIVATED'}
        )
        logger.info(f"MRR Inflow recorded for customer {customer_id}")

    @staticmethod
    def on_subscription_cancelled(payload):
        amount = payload.get('amount', 0)
        customer_id = payload.get('customer_id')

        SaaSMetric.objects.create(
            metric_name='MRR_CHURN',
            value=amount,
            dimension='Cancellation',
            meta_data={'customer_id': str(customer_id), 'event': 'SUBSCRIPTION_CANCELLED'}
        )
        logger.info(f"Churn recorded for customer {customer_id}")

    @staticmethod
    def on_plan_upgraded(payload):
        amount = payload.get('expansion_amount', 0)
        customer_id = payload.get('customer_id')
        SaaSMetric.objects.create(
            metric_name='MRR_EXPANSION',
            value=amount,
            dimension='Upgrade',
            meta_data={'customer_id': str(customer_id), 'event': 'PLAN_UPGRADED'}
        )

    @staticmethod
    def on_plan_downgraded(payload):
        amount = payload.get('contraction_amount', 0)
        customer_id = payload.get('customer_id')
        SaaSMetric.objects.create(
            metric_name='MRR_CONTRACTION',
            value=amount,
            dimension='Downgrade',
            meta_data={'customer_id': str(customer_id), 'event': 'PLAN_DOWNGRADED'}
        )

    @staticmethod
    def on_usage_billed(payload):
        amount = payload.get('total_amount', 0)
        customer_id = payload.get('customer_id')

        SaaSMetric.objects.create(
            metric_name='USAGE_REVENUE',
            value=amount,
            dimension='Usage',
            meta_data={'customer_id': str(customer_id), 'event': 'USAGE_BILLED'}
        )

    @staticmethod
    def on_payment_reconciled(payload):
        amount = payload.get('amount', 0)
        SaaSMetric.objects.create(
            metric_name='CASH_COLLECTED',
            value=amount,
            dimension='Reconciliation',
            meta_data={'payload': DataCollector._clean_payload(payload)}
        )

    @staticmethod
    def on_invoice_created(payload):
        amount = payload.get('total_amount', 0)
        SaaSMetric.objects.create(
            metric_name='TOTAL_BILLING',
            value=amount,
            dimension='Invoicing',
            meta_data={'payload': DataCollector._clean_payload(payload)}
        )

    @staticmethod
    def on_usage_recorded(payload):
        units = payload.get('units', 0)
        customer_id = payload.get('customer_id')
        feature = payload.get('feature_code')

        SaaSMetric.objects.create(
            metric_name='USAGE_UNITS',
            value=Decimal(str(units)),
            dimension=f'Feature:{feature}',
            meta_data={'customer_id': str(customer_id), 'feature': feature}
        )
