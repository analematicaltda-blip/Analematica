import logging
from datetime import date, timedelta
from django.db import transaction
from django.utils import timezone
from ..models import Subscription, Plan, BillingCycle
from ..signals.commercial_events import (
    subscription_activated, subscription_renewed,
    payment_failed
)

logger = logging.getLogger(__name__)

class SubscriptionEngine:
    """
    Motor definitivo de Suscripciones (Fase 3).
    Maneja el ciclo de vida automatizado y prorrateo.
    """

    @staticmethod
    @transaction.atomic
    def activate_subscription(tenant_id, plan, billing_cycle=Subscription.BillingCycle.MONTHLY):
        """Activa una nueva suscripción."""
        subscription, created = Subscription.objects.update_or_create(
            tenant_id=tenant_id,
            defaults={
                'plan': plan,
                'status': Subscription.Status.ACTIVE,
                'billing_cycle': billing_cycle,
                'start_date': date.today(),
                'next_billing_date': date.today() + (timedelta(days=30) if billing_cycle == Subscription.BillingCycle.MONTHLY else timedelta(days=365))
            }
        )

        subscription_activated.send(sender=SubscriptionEngine, subscription=subscription)
        return subscription

    @staticmethod
    @transaction.atomic
    def process_renewal(subscription: Subscription):
        """Procesa la renovación de una suscripción."""
        if subscription.cancel_at_period_end:
            subscription.status = Subscription.Status.CANCELED
            subscription.is_active = False
            subscription.save()
            return subscription

        # Actualizar fechas
        subscription.last_billing_date = subscription.next_billing_date
        delta = timedelta(days=30) if subscription.billing_cycle == Subscription.BillingCycle.MONTHLY else timedelta(days=365)
        subscription.next_billing_date = subscription.last_billing_date + delta
        subscription.save()

        # Disparar evento de facturación (será manejado por el BillingAdapter)
        subscription_renewed.send(sender=SubscriptionEngine, subscription=subscription)
        return subscription

    @staticmethod
    def calculate_proration(current_plan_price, new_plan_price, days_remaining, total_days):
        """Calcula el monto prorrateado para cambios de plan."""
        if total_days == 0: return 0
        current_daily = current_plan_price / total_days
        new_daily = new_plan_price / total_days

        # Crédito por lo no usado del actual vs costo de lo que queda del nuevo
        return (new_daily - current_daily) * days_remaining

    @staticmethod
    @transaction.atomic
    def change_plan(subscription: Subscription, new_plan: Plan, immediate=True):
        """Cambia el plan de una suscripción."""
        if immediate:
             # Aquí se calcularía el prorrateo y se generaría una factura inmediata
             subscription.plan = new_plan
             subscription.save()
        else:
             # Programar para el final del periodo
             subscription.metadata['pending_plan_change'] = new_plan.code
             subscription.save()
        return subscription

    @staticmethod
    def handle_past_due(subscription: Subscription):
        """Maneja el estado de mora."""
        subscription.status = Subscription.Status.PAST_DUE
        subscription.save()
        # Notificar al motor de retención

    @staticmethod
    def suspend_subscription(subscription: Subscription):
        """Suspende el servicio por impago prolongado."""
        subscription.status = Subscription.Status.SUSPENDED
        subscription.save()
