import logging
from .journal_service import JournalService
from .ledger_engine import LedgerEngine
from .models import FiscalPeriod

logger = logging.getLogger(__name__)

class DomainSargentoContable:
    """
    Consolidated Sargento for Accounting Operations.
    """

    @staticmethod
    def generar_asiento_partida_doble(tenant_id, date, description, movimientos, user_id=None):
        try:
            from django.contrib.auth import get_user_model
            from .validation import current_actor
            actor=current_actor(get_user_model().objects.filter(pk=user_id).first())
            # Mapping legacy format to core format
            lines_data = []
            for mov in movimientos:
                lines_data.append({
                    'account': mov.get('cuenta_id') or mov.get('cuenta_code') or mov.get('account_code'),
                    'debit': mov.get('debit', 0),
                    'credit': mov.get('credit', 0),
                    'description': mov.get('description', description)
                })

            # Create Entry
            entry = JournalService.create_entry(
                tenant_id=tenant_id,
                entry_date=date,
                description=description,
                lines_data=lines_data, created_by=actor
            )

            # Post Entry
            return LedgerEngine.post_entry(entry.id,tenant_id=tenant_id,actor=actor)

        except Exception as e:
            logger.error(f"DOMAIN SARGENTO: Error generating entry: {e}")
            raise e
