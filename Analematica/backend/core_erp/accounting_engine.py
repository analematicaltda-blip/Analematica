import logging
from decimal import Decimal
from django.core.exceptions import ValidationError
from django.db import transaction

logger = logging.getLogger(__name__)

class AccountingEngine:
    """
    Motor Contable Soberano del Core ERP.
    Único punto de entrada para la creación y validación de asientos contables.
    """

    @staticmethod
    def validate_balance(entry):
        """
        Garantiza el principio de partida doble (Debe = Haber).
        """
        # Se asume que entry tiene un related_name 'lines' o 'transactions'
        lines_manager = getattr(entry, 'lines', None) or getattr(entry, 'transactions', None)
        if not lines_manager:
            raise ValidationError("El asiento no tiene líneas definidas.")

        lines = lines_manager.all()
        total_debit = sum(line.debit for line in lines)
        total_credit = sum(line.credit for line in lines)

        if abs(total_debit - total_credit) > Decimal('0.001'):
            raise ValidationError(
                f"Asiento descuadrado. Débito: {total_debit}, Crédito: {total_credit}. "
                f"Diferencia: {total_debit - total_credit}"
            )
        return True

    @staticmethod
    def check_period_status(date, tenant):
        """
        Verifica si el periodo para la fecha dada está abierto.
        """
        from .accounting.models import FiscalPeriod
        period = FiscalPeriod.objects.filter(
            tenant=tenant,
            start_date__lte=date,
            end_date__gte=date
        ).first()

        if not period:
            return False, "No fiscal period found for date"
        return period.is_open, "Period closed" if not period.is_open else "OK"

    @staticmethod
    @transaction.atomic
    def post_journal_entry(entry, responsible_user=None):
        """
        Realiza la contabilización definitiva de un asiento delegando al LedgerEngine real.
        """
        from .accounting.ledger_engine import LedgerEngine
        return LedgerEngine.post_entry(entry.id)

    @staticmethod
    def create_intercompany_entry(origin_tenant, destination_tenant, amount, currency, concept):
        """
        Genera asientos espejo para transacciones entre empresas del holding.
        """
        from .accounting.models import JournalEntry, Account, FiscalPeriod
        from django.utils import timezone

        # 1. Validar periodos abiertos en ambos tenants
        now = timezone.now().date()
        if not AccountingEngine.check_period_status(now, origin_tenant)[0]:
            raise ValidationError(f"Periodo cerrado en origen {origin_tenant}")
        if not AccountingEngine.check_period_status(now, destination_tenant)[0]:
            raise ValidationError(f"Periodo cerrado en destino {destination_tenant}")

        # 2. Crear Asiento en Origen
        entry_origin = JournalEntry.objects.create(
            tenant=origin_tenant,
            date=now,
            description=f"INTERCOMPANY: {concept} to {destination_tenant}",
            period=FiscalPeriod.objects.filter(tenant=origin_tenant, is_open=True).first()
        )

        # 3. Crear Asiento en Destino
        entry_dest = JournalEntry.objects.create(
            tenant=destination_tenant,
            date=now,
            description=f"INTERCOMPANY: {concept} from {origin_tenant}",
            period=FiscalPeriod.objects.filter(tenant=destination_tenant, is_open=True).first()
        )

        logger.info(f"Intercompany entries created: {entry_origin.id} and {entry_dest.id}")
        return entry_origin, entry_dest
