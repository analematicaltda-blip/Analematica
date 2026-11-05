from apps.core_erp.event_bus import EventBus

class EventBusAdapter:
    """
    Standard interface for Decision Engine to interact with system-wide events.
    Part of the Execution Orchestration Layer.
    """

    @staticmethod
    def emit_decision_event(decision_id: str, status: str):
        EventBus.emit("STRATEGIC_DECISION_FINALIZED", {
            "decision_id": decision_id,
            "status": status
        })
