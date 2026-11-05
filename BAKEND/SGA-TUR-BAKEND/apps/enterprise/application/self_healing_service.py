import logging
import uuid
from django.db import transaction
from django.utils import timezone
from ..domain.autonomous import SelfHealingAudit
from apps.core_erp.accounting.models import JournalEntry, LedgerEntry
from apps.core_erp.accounting.ledger_engine import LedgerEngine

logger = logging.getLogger(__name__)

class SelfHealingService:
    """
    Self-Healing Layer (Phase 9).
    Monitors and repairs financial data inconsistencies autonomously.
    """

    @staticmethod
    @transaction.atomic
    def run_health_audit(tenant_id):
        """
        Scans for issues and applies auto-remediation.
        """
        # 1. Audit: Unbalanced Journal Entries
        entries = JournalEntry.objects.filter(tenant_id=tenant_id, is_posted=True)

        for entry in entries:
            try:
                LedgerEngine.validate_balance(entry)
            except Exception as e:
                # Remediation: Unpost and mark for manual review
                entry.is_posted = False
                entry.save()

                SelfHealingAudit.objects.create(
                    tenant_id=tenant_id,
                    issue_type="UNBALANCED_JOURNAL",
                    target_id=entry.id,
                    action_taken="UNPOST_ENTRY",
                    result=f"Entry was unbalanced. Automated unpost applied. Error: {str(e)}"
                )
                logger.error(f"EOS Self-Healing: REPAIRED unbalanced entry {entry.id}")

        # 2. Audit: Orphaned Ledger Lines
        orphans = LedgerEntry.objects.filter(journal_entry__isnull=True)
        if orphans.exists():
            count = orphans.count()
            orphans.delete()
            SelfHealingAudit.objects.create(
                tenant_id=tenant_id,
                issue_type="ORPHANED_LINES",
                target_id=uuid.uuid4(), # Batch ID
                action_taken="DELETE_ORPHANS",
                result=f"Deleted {count} orphaned ledger lines without parent journal."
            )
            logger.warning(f"EOS Self-Healing: DELETED {count} orphaned lines.")
