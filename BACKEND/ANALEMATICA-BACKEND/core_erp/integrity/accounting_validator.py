# backend/apps/core_erp/integrity/accounting_validator.py
import hashlib
import json
import logging
from typing import Dict, List
from django.db.models import Sum
from django.core.serializers.json import DjangoJSONEncoder

logger = logging.getLogger(__name__)

class AccountingValidator:
    """
    Regla 3: Toda transacción económica debe generar asiento contable.
    Valida integridad del hash y continuidad de la cadena (SHA-256).
    """

    def validate(self) -> Dict:
        logger.info("Iniciando auditoría de integridad contable...")

        try:
            from apps.prestadores.mi_negocio.gestion_contable.contabilidad.models import AsientoContable
            from apps.core_erp.models import EventAuditLog

            violations = []

            # 1. Verificar integridad de la cadena de hashes
            chain_status = self._verify_hash_chain()
            if not chain_status["success"]:
                violations.append({
                    "type": "HashChainBreach",
                    "message": f"Fallo de integridad en el bloque: {chain_status['error_block']}"
                })

            # 2. Verificar correspondencia Evento -> Asiento (Muestreo)
            # Buscamos eventos SALE_CREATED que no tengan reflejo contable
            missing_postings = self._check_event_accounting_mapping()
            if missing_postings > 0:
                violations.append({
                    "type": "MissingAccountingReflex",
                    "count": missing_postings,
                    "message": f"Se detectaron {missing_postings} eventos económicos sin asiento contable."
                })

            status = "PASSED" if not violations else "FAILED"
            score = 100 if not violations else max(0, 100 - (len(violations) * 20))

            return {
                "component": "AccountingIntegrity",
                "status": status,
                "score": score,
                "violations": violations,
                "metrics": {
                    "ledger_blocks_verified": chain_status["blocks_verified"],
                    "integrity_hash": chain_status["last_hash"]
                }
            }
        except Exception as e:
            logger.error(f"Error en validación contable: {e}", exc_info=True)
            return {"component": "AccountingIntegrity", "status": "ERROR", "score": 0, "message": str(e)}

    def _verify_hash_chain(self) -> Dict:
        """
        Re-calcula todos los hashes del Ledger para validar la inmutabilidad.
        """
        from apps.prestadores.mi_negocio.gestion_contable.contabilidad.models import AsientoContable

        # En esta implementación, el hash está en JournalEntry del Ledger central
        from apps.core_erp.accounting.models import JournalEntry

        entries = JournalEntry.objects.filter(is_posted=True).order_by('posted_at', 'id')
        previous_hash = "GENESIS_SARITA_2026"
        blocks_verified = 0

        for entry in entries:
            # Reconstruir payload para verificación
            # (Debe coincidir EXACTAMENTE con la lógica en LedgerEngine.post_event)
            payload = {
                "id": str(entry.id),
                "event_type": entry.event_type,
                "timestamp": entry.posted_at.isoformat() if entry.posted_at else "",
                "previous_hash": previous_hash
            }
            payload_str = json.dumps(payload, sort_keys=True, cls=DjangoJSONEncoder)
            calculated_hash = hashlib.sha256(payload_str.encode()).hexdigest()

            if entry.system_hash and entry.system_hash != calculated_hash:
                return {
                    "success": False,
                    "error_block": str(entry.id),
                    "blocks_verified": blocks_verified,
                    "last_hash": previous_hash
                }

            previous_hash = entry.system_hash or calculated_hash
            blocks_verified += 1

        return {
            "success": True,
            "blocks_verified": blocks_verified,
            "last_hash": previous_hash
        }

    def _check_event_accounting_mapping(self) -> int:
        """
        Busca eventos económicos (SALE_CREATED) en EventAuditLog que no estén marcados como PROCESSED.
        """
        from apps.core_erp.models import EventAuditLog
        return EventAuditLog.objects.filter(
            event_type='SALE_CREATED',
            status__in=['EMITTED', 'PARTIAL_FAILURE']
        ).count()
