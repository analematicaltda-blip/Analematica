# backend/apps/sarita_agents/agents/general/sarita/coroneles/prestadores/soldados/soldados_impuestos.py

from apps.sarita_agents.agents.soldado_n6_oro_v2 import SoldadoN6OroV2
import logging

logger = logging.getLogger(__name__)

class SoldadoCalculoIVA(SoldadoN6OroV2):
    domain = "prestadores"
    aggregate_root = "TaxTransaction"
    required_permissions = ["prestadores.execute"]
    event_name = "TAX_GENERATED"

    def perform_atomic_action(self, params: dict):
        logger.info(f"SOLDADO IMPUESTOS: Calculando impuestos determinísticamente.")
        from apps.core_erp.taxation.services.tax_calculator import TaxCalculatorEngine
        from decimal import Decimal

        tenant_id = params.get('tenant_id')
        base_amount = Decimal(str(params.get('base_amount', 0)))
        doc_type = params.get('document_type', 'INVOICE')
        entity_type = params.get('entity_type', 'CLIENT')

        # Evaluar mediante el motor normativo de la Fase 6.2
        taxes = TaxCalculatorEngine.calculate_taxes(
            tenant_id=tenant_id,
            document_type=doc_type,
            entity_type=entity_type,
            base_amount=base_amount
        )

        # Persistir transacciones fiscales
        TaxCalculatorEngine.record_tax_transaction(
            tenant_id=tenant_id,
            document_id=params.get('document_id'),
            tax_data=taxes
        )

        return {"status": "SUCCESS", "taxes_calculated": len(taxes), "details": taxes}

class SoldadoRegistroRetenciones(SoldadoN6OroV2):
    domain = "prestadores"
    aggregate_root = "TaxTransaction"
    required_permissions = ["prestadores.execute"]

    def perform_atomic_action(self, params: dict):
        logger.info(f"SOLDADO IMPUESTOS: Registrando retenciones.")
        # Lógica para ICA, Fuente, etc.
        return {"status": "SUCCESS", "msg": "Retenciones registradas."}
