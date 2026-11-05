from apps.core_erp.event_bus import EventBus
from .strategic_service import StrategicIntelligenceService

def register_strategic_handlers():
    EventBus.subscribe("PERIOD_CLOSED", handle_period_closed_forecast)
    EventBus.subscribe("JOURNAL_POSTED", handle_journal_posted_forecast)

def handle_period_closed_forecast(payload):
    StrategicIntelligenceService.update_rolling_forecast(payload.get('tenant_id'))

def handle_journal_posted_forecast(payload):
    # Only update daily if needed, or sample
    pass
