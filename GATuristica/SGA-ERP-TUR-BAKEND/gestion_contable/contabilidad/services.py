from apps.core_erp.accounting.journal_service import JournalService
from apps.core_erp.accounting.ledger_engine import LedgerEngine

class ContabilidadService:
    @staticmethod
    def crear_asiento_completo(provider, date, description, periodo, creado_por, transacciones_data):
        # Wrapper for core functionality
        lines_data = []
        for t in transacciones_data:
            lines_data.append({
                'account': t.get('cuenta_id'),
                'debit': t.get('debit', 0),
                'credit': t.get('credit', 0),
                'description': t.get('description', description)
            })

        entry = JournalService.create_entry(
            tenant_id=str(provider.id),
            entry_date=date,
            description=description,
            lines_data=lines_data
        )
        return LedgerEngine.post_entry(entry.id)
