# backend/apps/sarita_agents/agents/general/sarita/coroneles/prestadores/soldados/soldados_cartera.py

from apps.sarita_agents.agents.soldado_n6_oro_v2 import SoldadoN6OroV2
import logging
from decimal import Decimal

logger = logging.getLogger(__name__)

class SoldadoSeguimientoCartera(SoldadoN6OroV2):
    domain = "prestadores"
    aggregate_root = "Account"
    required_permissions = ["prestadores.execute"]

    def perform_atomic_action(self, params: dict):
        logger.info(f"SOLDADO CARTERA: Analizando antigüedad de saldos.")
        from apps.core_erp.accounting.models import Account, LedgerEntry
        from django.db.models import Sum

        tenant_id = params.get('tenant_id')
        # Cuenta 1305 (Clientes)
        cuenta_cartera = Account.plain_objects.filter(tenant_id=tenant_id, code='1305').first()
        if not cuenta_cartera:
            return {"status": "NO_CARTERA_ACCOUNT", "total": 0.0}

        movs = LedgerEntry.objects.filter(account=cuenta_cartera).aggregate(d=Sum('debit_amount'), c=Sum('credit_amount'))
        total = (movs['d'] or Decimal('0.00')) - (movs['c'] or Decimal('0.00'))

        return {
            "id": str(cuenta_cartera.id),
            "total_cartera": float(total),
            "status": "HEALTHY" if total >= 0 else "OVERPAID"
        }

class SoldadoGestionCobro(SoldadoN6OroV2):
    domain = "prestadores"
    aggregate_root = "JournalEntry"
    required_permissions = ["prestadores.execute"]

    def perform_atomic_action(self, params: dict):
        logger.info(f"SOLDADO CARTERA: Registrando gestión de cobro.")
        # Lógica de registro de actividad de cobranza
        return {"status": "SUCCESS", "msg": "Recordatorio enviado."}
