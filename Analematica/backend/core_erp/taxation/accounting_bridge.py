import logging
from django.db import transaction
from .models import TaxAccountMapping, TaxTransaction
from apps.core_erp.accounting.ledger_engine import LedgerEngine

logger = logging.getLogger(__name__)

class TaxLedgerBridge:
    """
    Bloque 2.2: Puente de Integración Contable.
    Traduce transacciones fiscales en asientos del libro mayor.
    """

    @staticmethod
    @transaction.atomic
    def post_taxes_to_accounting(document_id: str, tenant_id: str):
        """
        Consulta las transacciones fiscales del documento y dispara el LedgerEngine.
        """
        tax_txs = TaxTransaction.objects.filter(document_id=document_id, tenant_id=tenant_id)

        for tx in tax_txs:
            # Obtener Mapeo Contable (Bloque 6)
            mapping = TaxAccountMapping.objects.filter(tax=tx.tax, tenant_id=tenant_id).first()

            if not mapping:
                logger.error(f"FISCAL LOCK: No existe mapeo contable para el impuesto {tx.tax.code}.")
                raise ValueError(f"Falta parametrización contable para {tx.tax.code}")

            # Construir Payload para Ledger
            ledger_payload = {
                "tenant_id": tenant_id,
                "reference": str(document_id),
                "amount": float(tx.tax_amount),
                "description": f"Causación de {tx.tax.name} - Doc: {document_id}",
                "lines": [
                    {"account": mapping.debit_account, "debit": float(tx.tax_amount), "credit": 0},
                    {"account": mapping.credit_account, "debit": 0, "credit": float(tx.tax_amount)}
                ]
            }

            # Ejecutar Impacto Contable Real
            LedgerEngine.post_event("TAX_RECOGNITION", ledger_payload)

        logger.info(f"TAX BRIDGE: Integración contable finalizada para documento {document_id}")
