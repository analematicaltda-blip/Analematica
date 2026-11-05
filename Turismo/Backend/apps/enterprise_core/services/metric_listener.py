import logging
from apps.core_erp.event_bus import EventBus
from .decision_engine import DecisionEngine

logger = logging.getLogger(__name__)

class MetricListener:
    """
    Subscribes to system events to feed the Decision Engine.
    Part of the Metric Intake Layer.
    """

    @staticmethod
    def start_listening():
        EventBus.subscribe("METRIC_COLLECTED", MetricListener.on_metric_received)
        EventBus.subscribe("JOURNAL_ENTRY_POSTED", MetricListener.on_accounting_event)
        EventBus.subscribe("SUBSCRIPTION_ACTIVATED", MetricListener.on_commercial_event)
        logger.info("EOS DECISION ENGINE: Metric Listener active.")

    @staticmethod
    def on_metric_received(payload: dict):
        DecisionEngine.process_metric_update(
            payload.get('name'),
            payload.get('value'),
            payload
        )

    @staticmethod
    def on_accounting_event(payload: dict):
        # Infer metrics from accounting events if necessary
        return {"status": "success", "executed": True}

    @staticmethod
    def on_commercial_event(payload: dict):
        # Infer metrics from commercial events
        return {"status": "success", "executed": True}
