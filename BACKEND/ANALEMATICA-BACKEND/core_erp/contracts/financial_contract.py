from dataclasses import dataclass
from uuid import UUID
from decimal import Decimal
from datetime import date
from typing import List

@dataclass(frozen=True)
class JournalEntryLineDTO:
    account_id: UUID
    debit: Decimal
    credit: Decimal
    description: str

@dataclass(frozen=True)
class JournalEntryDTO:
    id: UUID
    date: date
    description: str
    lines: List[JournalEntryLineDTO]
    reference: str = ""

class FinancialContract:
    """
    Contrato para integración financiera de alto nivel.
    """
    def project_cashflow(self, tenant_id, months=6):
        """
        Proyecta el flujo de caja basado en datos históricos y presupuestos.
        """
        from ..accounting.models import LedgerEntry
        from django.db.models import Sum

        # Lógica de proyección simplificada
        return LedgerEntry.objects.filter(journal_entry__tenant_id=tenant_id).aggregate(Sum('debit_amount'))
