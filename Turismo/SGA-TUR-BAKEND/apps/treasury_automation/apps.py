from django.apps import AppConfig

class TreasuryAutomationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.treasury_automation'
    verbose_name = 'Treasury Automation'

    def ready(self):
        from apps.core_erp.event_bus import EventBus
        from .reconciliation_engine import ReconciliationEngine
        from .cashflow_engine import CashflowEngine
        from .anomaly_detector import AnomalyDetector

        # 1. Al importar una transacción -> Intentar Conciliar
        EventBus.subscribe('BANK_TRANSACTION_IMPORTED', ReconciliationEngine.handle_transaction_imported)

        # 2. Al importar una transacción -> Detectar Anomalías
        EventBus.subscribe('BANK_TRANSACTION_IMPORTED', AnomalyDetector.handle_transaction_imported)

        # 3. Cualquier movimiento bancario -> Actualizar Cashflow
        EventBus.subscribe('BANK_TRANSACTION_IMPORTED', CashflowEngine.handle_transaction)
        EventBus.subscribe('PAYMENT_RECONCILED', CashflowEngine.handle_transaction)

        import logging
        logger = logging.getLogger(__name__)
        logger.info("TREASURY AUTOMATION: Orquestación de eventos configurada.")
