import logging
import hashlib
import json
from decimal import Decimal
from django.db import transaction
from django.utils import timezone
from .models import JournalEntry, LedgerEntry, Account, FiscalPeriod
from .exceptions import (
    UnbalancedEntryError, InactiveAccountError,
    FiscalPeriodClosedError, TenantMismatchError, DuplicateReversalError
)
from .posting_rules import PostingRules
from .journal_service import JournalService
from apps.common.db_resilience import db_retry

logger = logging.getLogger(__name__)

class LedgerEngine:
    """
    Motor Contable Soberano del Core ERP.
    Único componente autorizado para crear asientos, validar doble partida e impactar balances.
    """

    @staticmethod
    def calculate_hash(entry: JournalEntry, previous_hash: str = None):
        """
        Calcula un hash SHA-256 de los datos del asiento para garantizar integridad.
        Fase 3.6: hash_actual = SHA256(id + fecha + referencia + total + hash_anterior)
        """
        total_debit = sum(line.debit_amount for line in entry.lines.all())

        # Estructura obligatoria Fase 3.6
        payload = (
            f"{entry.id}"
            f"{entry.date}"
            f"{entry.reference or ''}"
            f"{total_debit}"
            f"{previous_hash or 'GENESIS_SARITA_2026'}"
        )

        return hashlib.sha256(payload.encode()).hexdigest()

    @staticmethod
    def validate_balance(entry: JournalEntry):
        """
        Garantiza el principio de partida doble (Débitos = Créditos).
        """
        lines = entry.lines.all()
        if not lines:
            raise UnbalancedEntryError("Journal entry has no lines.")

        total_debit = sum(line.debit_amount for line in lines)
        total_credit = sum(line.credit_amount for line in lines)

        if abs(total_debit - total_credit) > Decimal('0.001'):
            raise UnbalancedEntryError(
                f"Asiento descuadrado {entry.id}. Débito: {total_debit}, Crédito: {total_credit}."
            )
        return True

    @staticmethod
    @transaction.atomic
    def post_event(event_type: str, payload: dict):
        """
        Método Central: Procesa un evento de negocio y genera el impacto contable real.
        Garantiza idempotencia y atomicidad estricta.
        Incluye monitoreo de performance (Fase 6.6).
        """
        import time
        start_time = time.time()
        logger.info(f"LedgerEngine: Procesando evento {event_type}")

        tenant_id = payload.get("tenant_id") or payload.get("organization_id")
        if not tenant_id:
             raise ValueError("tenant_id es obligatorio en el payload del evento contable.")

        # 1. Verificación de Idempotencia (Fase 6.1.2)
        financial_event_id = payload.get("financial_event_id") or payload.get("reference")
        if financial_event_id:
            existing = JournalEntry.objects.filter(
                tenant_id=tenant_id,
                financial_event_id=financial_event_id
            ).first()
            if existing:
                logger.warning(f"Evento {financial_event_id} ya procesado. Omitiendo duplicado.")
                return existing

        # 2. Obtener regla desde posting_rules
        lines_data = PostingRules.get_rule_for_event(event_type, payload)
        if not lines_data:
            logger.info(f"No hay reglas contables definidas para el evento {event_type}. Saltando.")
            return None

        # 3. Generar JournalEntry y Líneas LedgerEntry vía JournalService
        from ..observability.middleware import get_correlation_id

        entry = JournalService.create_entry(
            tenant_id=str(tenant_id),
            entry_date=timezone.now().date(),
            description=f"Impacto automático: {event_type}",
            lines_data=lines_data,
            reference=str(payload.get("reference", ""))
        )

        entry.event_type = event_type
        entry.financial_event_id = financial_event_id
        entry.correlation_id = payload.get('_correlation_id') or get_correlation_id()
        entry.rule_version = PostingRules.VERSION
        entry.save()

        # 4. Validar y Postear definitivamente
        result = LedgerEngine.post_entry(entry.id)

        duration = time.time() - start_time
        logger.info(f"LedgerEngine: Evento {event_type} procesado en {duration:.4f}s")
        return result

    @staticmethod
    @db_retry(max_retries=3)
    @transaction.atomic
    def post_entry(entry_id):
        """
        Realiza la contabilización definitiva de un asiento.
        Implementa protección contra race conditions bloqueando filas críticas.
        Supports both ID and object (handles conversion).
        """
        if hasattr(entry_id, 'id'):
            entry_id = entry_id.id

        entry = JournalEntry.objects.select_for_update().get(id=entry_id)
        if entry.is_posted:
            return entry

        if entry.period.status != 'open':
            raise FiscalPeriodClosedError(f"Periodo fiscal {entry.period.id} está cerrado.")

        # 1. Bloqueo de Cuentas para consistencia (Fase 6.1.3)
        account_ids = entry.lines.values_list('account_id', flat=True)
        # Forzar select_for_update en cuentas involucradas
        list(Account.plain_objects.select_for_update().filter(id__in=account_ids))

        # 2. Validaciones de Integridad
        LedgerEngine.validate_balance(entry)

        # Verificar que todas las cuentas estén activas
        for line in entry.lines.all():
            if not line.account.is_active:
                raise InactiveAccountError(f"La cuenta {line.account.code} está inactiva.")
            if str(line.account.tenant_id) != str(entry.tenant_id):
                raise TenantMismatchError(f"Cuenta {line.account.code} no pertenece al tenant {entry.tenant_id}")

        # 3. Multi-Currency Logic (Phase B)
        # Standardize transaction vs base amounts using FXEngine
        from ..fx.fx_engine import FXEngine

        exchange_rate = getattr(entry, 'exchange_rate', Decimal('1.0'))
        # Si no se especificó tasa manual, intentar resolver vía motor
        if exchange_rate == Decimal('1.0') and entry.currency != entry.base_currency:
            try:
                exchange_rate = FXEngine.get_rate(entry.currency, entry.base_currency)
            except ValueError:
                logger.warning(f"FX Engine: No se encontró tasa para {entry.currency}/{entry.base_currency}. Usando 1.0")

        for line in entry.lines.all():
            # If not explicitly set, use debit/credit as transaction amount
            if not line.amount_transaction:
                line.amount_transaction = line.debit_amount if line.debit_amount > 0 else line.credit_amount

            # Convert to base currency for financial reporting
            line.amount_base = (line.amount_transaction * exchange_rate).quantize(Decimal('1.00'))
            line.save()

        # 4. Audit Integrity Hardening (Phase B) - Chained Hashing
        # Obtener el hash del último asiento posteado para este tenant
        last_entry = JournalEntry.objects.filter(
            tenant_id=entry.tenant_id,
            is_posted=True
        ).exclude(id=entry.id).order_by('-posted_at', '-id').first()

        previous_hash = last_entry.system_hash if last_entry else "GENESIS_SARITA_2026"
        entry.previous_hash = previous_hash

        entry.system_hash = LedgerEngine.calculate_hash(entry, previous_hash=previous_hash)
        entry.immutable_signature = f"LEDGER-SIG-CHAIN-{entry.system_hash[:16]}-{timezone.now().timestamp()}"
        entry.posted_at = timezone.now()

        # 5. Posteo Final
        entry.is_posted = True
        entry.save()

        # 5.1 Registro en Auditoría Inmutable (Fase 3.11)
        from .models import AccountingAuditLog
        from django.contrib.auth import get_user_model

        system_user = get_user_model().objects.filter(is_superuser=True).first()
        user_to_log = entry.created_by if entry.created_by else system_user

        audit_payload = f"{entry.id}{user_to_log.id if user_to_log else 'system'}{entry.system_hash}"
        AccountingAuditLog.objects.create(
            tenant_id=entry.tenant_id,
            user=user_to_log,
            action="POST",
            reference_entry=entry,
            integrity_hash=hashlib.sha256(audit_payload.encode()).hexdigest()
        )

        logger.info(f"JournalEntry {entry.id} posteado exitosamente con Hash: {entry.system_hash}")

        # 6. Emisión de Evento de Omnisciencia (Fase 4)
        from apps.core_erp.event_bus import EventBus
        EventBus.emit(
            "AsientoGenerado",
            {
                "entity_id": str(entry.tenant_id),
                "entry_id": str(entry.id),
                "description": entry.description,
                "total_debit": float(sum(line.debit_amount for line in entry.lines.all())),
                "system_hash": entry.system_hash
            },
            severity="info"
        )

        return entry

    @staticmethod
    @transaction.atomic
    def reverse_entry(journal_entry_id: str, reason: str = "Reversión automática"):
        """
        Genera un contra-asiento para anular una operación. Inmutabilidad total (Fase 3.5.2).
        """
        original = JournalEntry.objects.select_for_update().get(id=journal_entry_id)

        if not original.is_posted:
             raise ValueError("No se puede reversar un asiento que no ha sido posteado.")

        if original.is_reversal:
            raise DuplicateReversalError("No se puede reversar un asiento que ya es una reversión.")

        if JournalEntry.objects.filter(reversed_entry_id=journal_entry_id).exists():
            raise DuplicateReversalError("Este asiento ya ha sido reversado previamente.")

        # Crear nuevo JournalEntry de reversión
        reversal = JournalEntry.objects.create(
            tenant_id=original.tenant_id,
            period=original.period,
            date=timezone.now().date(),
            description=f"REVERSIÓN de {original.id}: {reason}",
            reference=f"REV-{original.reference or original.id}",
            event_type=f"REVERSAL_{original.event_type}",
            is_reversal=True,
            reversed_entry_id=original.id,
            created_by=original.created_by
        )

        # Invertir Débitos y Créditos de las líneas
        for line in original.lines.all():
            LedgerEntry.objects.create(
                tenant_id=original.tenant_id,
                journal_entry=reversal,
                account=line.account,
                debit_amount=line.credit_amount,
                credit_amount=line.debit_amount,
                amount_transaction=line.amount_transaction,
                currency=line.currency,
                description=f"Rev: {line.description}"
            )

        # Registro en Auditoría
        from .models import AccountingAuditLog
        audit_payload = f"{reversal.id}{original.id}REVERSE"
        AccountingAuditLog.objects.create(
            tenant_id=reversal.tenant_id,
            user=original.created_by,
            action="REVERSE",
            reference_entry=reversal,
            integrity_hash=hashlib.sha256(audit_payload.encode()).hexdigest()
        )

        return LedgerEngine.post_entry(reversal.id)

    @staticmethod
    def validate_ledger_integrity(tenant_id: str):
        """
        Fase 3.7: Script de Validación Automática de Integridad.
        Recorre todos los asientos, recalcula hashes y verifica la cadena.
        """
        entries = JournalEntry.objects.filter(tenant_id=tenant_id, is_posted=True).order_by('posted_at', 'id')

        previous_hash = "GENESIS_SARITA_2026"
        errors = []

        for entry in entries:
            # 1. Verificar cadena
            if entry.previous_hash != previous_hash:
                errors.append(f"Ruptura de cadena en asiento {entry.id}. Esperado: {previous_hash}, Real: {entry.previous_hash}")

            # 2. Recalcular hash
            recalculated = LedgerEngine.calculate_hash(entry, previous_hash=entry.previous_hash)
            if entry.system_hash != recalculated:
                errors.append(f"Hash inválido en asiento {entry.id}. Datos alterados.")

            # 3. Verificar balance
            try:
                LedgerEngine.validate_balance(entry)
            except Exception as e:
                errors.append(f"Desbalance en asiento {entry.id}: {str(e)}")

            previous_hash = entry.system_hash

        return {
            "is_valid": len(errors) == 0,
            "errors": errors,
            "entries_count": entries.count()
        }

    @staticmethod
    def get_trial_balance(tenant_id: str, cutoff_date=None):
        """
        Genera un balance de prueba consolidando saldos de cuentas.
        """
        if cutoff_date is None:
            cutoff_date = timezone.now().date()
        from .reports_engine import ReportsEngine
        return ReportsEngine.get_trial_balance(tenant_id, cutoff_date)
