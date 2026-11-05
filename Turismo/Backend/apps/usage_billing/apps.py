from django.apps import AppConfig

class UsageBillingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.usage_billing'
    verbose_name = 'Usage Based Billing'

    def ready(self):
        from apps.core_erp.event_bus import EventBus
        from .usage_billing_engine import UsageBillingEngine

        # Escuchar cierres de ciclo para facturar
        EventBus.subscribe('USAGE_CYCLE_CLOSED', UsageBillingEngine.handle_cycle_closed)
