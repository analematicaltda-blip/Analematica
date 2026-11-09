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
        from .accounting.ledger_engine import LedgerEngine
        return LedgerEngine.validate_balance(entry)

    @staticmethod
    def check_period_status(date, tenant):
        """
        Verifica si el periodo para la fecha dada está abierto.
        """
        from .accounting.models import FiscalPeriod
        period = FiscalPeriod.plain_objects.filter(
            tenant=tenant,
            period_start__lte=date,
            period_end__gte=date
        ).first()

        if not period:
            return False, "No fiscal period found for date"
        return period.status == "open", "OK" if period.status == "open" else "Period closed"

    @staticmethod
    @transaction.atomic
    def post_journal_entry(entry, responsible_user=None):
        """
        Realiza la contabilización definitiva de un asiento delegando al LedgerEngine real.
        """
        from .accounting.ledger_engine import LedgerEngine
        return LedgerEngine.post_entry(entry.id,tenant_id=entry.tenant_id,actor=responsible_user)

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
            period=FiscalPeriod.plain_objects.filter(tenant=origin_tenant, is_open=True).first()
        )

        # 3. Crear Asiento en Destino
        entry_dest = JournalEntry.objects.create(
            tenant=destination_tenant,
            date=now,
            description=f"INTERCOMPANY: {concept} from {origin_tenant}",
            period=FiscalPeriod.plain_objects.filter(tenant=destination_tenant, is_open=True).first()
        )

        logger.info(f"Intercompany entries created: {entry_origin.id} and {entry_dest.id}")
        return entry_origin, entry_dest
