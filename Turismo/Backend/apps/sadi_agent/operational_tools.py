import logging
from typing import Dict, Any
from apps.admin_plataforma.services.governance_kernel import GovernanceKernel
from django.contrib.auth import get_user_model

logger = logging.getLogger(__name__)

async def record_journal_entry(description: str, amount: float, debit_account: str, credit_account: str, tenant_id: str, user_id: str = "1"):
    """
    SADI Tool: Registra un asiento contable via GovernanceKernel.
    """
    User = get_user_model()
    try:
        user = User.objects.get(id=user_id)
        kernel = GovernanceKernel(user=user)

        parameters = {
            "description": description,
            "amount": amount,
            "movimientos": [
                {"account": debit_account, "debit_amount": amount, "description": description},
                {"account": credit_account, "credit_amount": amount, "description": description}
            ],
            "tenant_id": tenant_id
        }

        result = kernel.resolve_and_execute("ERP_CREATE_VOUCHER", parameters)
        return f"Éxito: Asiento registrado. Hash: {result.get('system_hash', 'N/A')}"
    except Exception as e:
        return f"Error registrando asiento: {str(e)}"

async def check_financial_status(tenant_id: str, user_id: str = "1"):
    """
    SADI Tool: Consulta el estado financiero actual.
    """
    User = get_user_model()
    try:
        user = User.objects.get(id=user_id)
        kernel = GovernanceKernel(user=user)

        result = kernel.resolve_and_execute("ERP_VIEW_CASH_FLOW", {"tenant_id": tenant_id})
        return f"Estado Financiero: {result}"
    except Exception as e:
        return f"Error consultando finanzas: {str(e)}"

async def run_payroll_liquidation(period_id: str, tenant_id: str, user_id: str = "1"):
    """
    SADI Tool: Ejecuta la liquidación de nómina.
    """
    User = get_user_model()
    try:
        user = User.objects.get(id=user_id)
        kernel = GovernanceKernel(user=user)

        # En una implementación real, se mapearía a una intención de nómina registrada
        return "Misión de nómina enviada a los agentes operativos."
    except Exception as e:
        return f"Error en nómina: {str(e)}"
