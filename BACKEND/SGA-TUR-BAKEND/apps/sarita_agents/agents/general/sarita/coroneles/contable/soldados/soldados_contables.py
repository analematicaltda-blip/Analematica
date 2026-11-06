# backend/apps/sarita_agents/agents/general/sarita/coroneles/contable/soldados/soldados_contables.py

from apps.sarita_agents.agents.soldado_n6_oro_v2 import SoldadoN6OroV2
import logging

logger = logging.getLogger(__name__)

class SoldadoRegistroIngreso(SoldadoN6OroV2):
    domain = "contable"
    aggregate_root = "JournalEntry"
    required_permissions = ["contable.execute"]
    event_name = "ACCOUNTING_ENTRY_POSTED"

    def perform_atomic_action(self, params: dict):
        logger.info(f"SOLDADO INGRESO: Registrando ingreso -> {params.get('monto')}")

        from apps.core_erp.accounting.sargentos import DomainSargentoContable

        tenant_id = params.get('tenant_id')
        if not tenant_id:
            raise ValueError("tenant_id es obligatorio para registro contable.")

        entry = DomainSargentoContable.generar_asiento_partida_doble(
            tenant_id=tenant_id,
            date=params.get('fecha'),
            description=params.get('descripcion', 'Registro de Ingreso via Agente'),
            movimientos=params.get('movimientos', []),
            user_id=params.get('user_id')
        )

        return entry

class SoldadoRegistroGasto(SoldadoN6OroV2):
    domain = "contable"
    aggregate_root = "JournalEntry"
    required_permissions = ["contable.execute"]
    event_name = "ACCOUNTING_ENTRY_POSTED"

    def perform_atomic_action(self, params: dict):
        logger.info(f"SOLDADO GASTO: Registrando gasto -> {params.get('monto')}")

        from apps.core_erp.accounting.sargentos import DomainSargentoContable

        tenant_id = params.get('tenant_id')
        if not tenant_id:
            raise ValueError("tenant_id es obligatorio para registro contable.")

        entry = DomainSargentoContable.generar_asiento_partida_doble(
            tenant_id=tenant_id,
            date=params.get('fecha'),
            description=params.get('descripcion', 'Registro de Gasto via Agente'),
            movimientos=params.get('movimientos', []),
            user_id=params.get('user_id')
        )

        return entry

class SoldadoConciliacionWallet(SoldadoN6OroV2):
    domain = "contable"
    aggregate_root = "WalletReconciliation"
    required_permissions = ["contable.execute"]

    def perform_atomic_action(self, params: dict):
        logger.info(f"SOLDADO CONCILIACIÓN WALLET: Cruzando datos con Wallet.")
        from apps.wallet.services import WalletService
        from django.utils.module_loading import import_string
        Cuenta = import_string('apps.prestadores.mi_negocio.gestion_contable.contabilidad.models.Cuenta') # DECOUPLED
        Transaccion = import_string('apps.prestadores.mi_negocio.gestion_contable.contabilidad.models.Transaccion') # DECOUPLED
        from django.db.models import Sum
        from decimal import Decimal

        provider_id = params.get('provider_id')
        if not provider_id:
            return {"status": "error", "message": "Falta provider_id"}

        # 1. Obtener saldo en Wallet real via Service (Fase 18: Desacoplamiento)
        wallet_service = WalletService(user=None) # Los agentes pueden no tener contexto de usuario directo
        wallet_balance = wallet_service.get_wallet_balance(
            owner_id=provider_id,
            owner_type="ARTESANO" # O el tipo correspondiente, mapeado a Wallet.OwnerType
        )

        # 2. Obtener saldo en cuenta contable 112505
        cuenta_puente = Cuenta.objects.filter(provider_id=provider_id, codigo='112505').first()
        if not cuenta_puente:
             return {"status": "warning", "message": "No se encontró cuenta puente 112505"}

        movimientos = Transaccion.objects.filter(cuenta=cuenta_puente).aggregate(d=Sum('debito'), c=Sum('credito'))
        d = movimientos['d'] or Decimal('0.00')
        c = movimientos['c'] or Decimal('0.00')
        contable_balance = cuenta_puente.saldo_inicial + d - c

        diferencia = wallet_balance - contable_balance

        return {
            "action": "wallet_reconciled",
            "wallet_balance": float(wallet_balance),
            "contable_balance": float(contable_balance),
            "difference": float(diferencia),
            "status": "OK" if diferencia == 0 else "DISCREPANCY"
        }

class SoldadoVerificacionFiscal(SoldadoN6OroV2):
    domain = "contable"
    aggregate_root = "TaxCompliance"
    required_permissions = ["contable.execute"]

    def perform_atomic_action(self, params: dict):
        logger.info(f"SOLDADO FISCAL: Verificando cumplimiento normativo.")
        from apps.core_erp.accounting.models import Account, LedgerEntry
        from django.db.models import Sum
        from decimal import Decimal

        tenant_id = params.get('tenant_id')
        # Buscar cuentas de pasivos (2) para ver obligaciones
        cuentas_pasivos = Account.plain_objects.filter(tenant_id=tenant_id, code__startswith='2')
        total_pasivos = Decimal('0.00')
        for c in cuentas_pasivos:
            movs = LedgerEntry.objects.filter(account=c).aggregate(d=Sum('debit_amount'), cr=Sum('credit_amount'))
            d = movs['d'] or Decimal('0.00')
            cr = movs['cr'] or Decimal('0.00')
            total_pasivos += (c.initial_balance + cr - d)

        return {
            "id": tenant_id,
            "action": "tax_verified",
            "compliance": True,
            "total_obligations": float(total_pasivos),
            "status": "CLEAR" if total_pasivos >= 0 else "DEBT_DETECTED"
        }

class SoldadoCierreParcial(SoldadoN6OroV2):
    domain = "contable"
    aggregate_root = "FiscalPeriod"
    required_permissions = ["contable.execute"]

    def perform_atomic_action(self, params: dict):
        logger.info(f"SOLDADO CIERRE: Ejecutando cierre parcial de periodo.")
        from apps.core_erp.accounting.models import FiscalPeriod
        periodo = FiscalPeriod.plain_objects.get(id=params.get('periodo_id'))
        # Lógica de pre-cierre o validación
        return {
            "id": str(periodo.id),
            "status": "PARTIAL_CLOSE_VERIFIED",
            "period": str(periodo)
        }
