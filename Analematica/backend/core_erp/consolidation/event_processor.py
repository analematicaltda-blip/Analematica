import logging
from apps.core_erp.event_bus import EventBus
from .intercompany_engine import IntercompanyEngine
from .consolidation_snapshot_engine import SnapshotGenerator

logger = logging.getLogger(__name__)

class ConsolidationEventProcessor:
    """
    Subscribes to accounting and entity events to trigger automatic consolidation.
    100% Event-Driven (EOS Activation).
    """

    @staticmethod
    def start_listening():
        """
        Registers event handlers in the EventBus.
        """
        EventBus.subscribe("JOURNAL_ENTRY_POSTED", ConsolidationEventProcessor.handle_posting)
        EventBus.subscribe("FINANCIAL_PERIOD_CLOSED", ConsolidationEventProcessor.handle_period_closure)
        EventBus.subscribe("SUBSIDIARY_CREATED", ConsolidationEventProcessor.handle_new_entity)
        logger.info("EOS CONSOLIDATION: Event handlers registered.")

    @staticmethod
    def handle_posting(event_data: dict):
        """
        Checks for intercompany transactions on every post and updates snapshots.
        """
        tenant_id = event_data.get('tenant_id')
        entry_id = event_data.get('entry_id')

        logger.info(f"EOS CONSOLIDATION: Processing posting event for tenant {tenant_id}")

        # 1. Real-time intercompany detection
        IntercompanyEngine.detect_and_match(entry_id)

        # 2. Incremental snapshot update (or queue full rebuild)
        SnapshotGenerator.trigger_incremental(tenant_id)

    @staticmethod
    def handle_period_closure(event_data: dict):
        """
        Generates final certified snapshots upon period closure.
        """
        tenant_id = event_data.get('tenant_id')
        period_id = event_data.get('period_id')

        logger.warning(f"EOS CONSOLIDATION: Period closure detected for {tenant_id}. Generating certified snapshots.")
        SnapshotGenerator.generate_full_consolidated_report(tenant_id, period_id)

    @staticmethod
    def handle_new_entity(event_data: dict):
        """
        Initializes consolidation mapping for new subsidiaries.
        """
        entity_id = event_data.get('entity_id')
        logger.info(f"EOS CONSOLIDATION: Initializing consolidation for new subsidiary {entity_id}")
        # Logic to update holding structures
