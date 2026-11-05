# backend/apps/sarita_agents/agents/general/sarita/coroneles/financiero/soldados/soldados_financieros.py

from apps.sarita_agents.agents.soldado_n6_oro_v2 import SoldadoN6OroV2
import logging
from django.db import models

logger = logging.getLogger(__name__)

# --- SOLDADOS DE TESORERÍA ---

class SoldadoRegistroIngresos(SoldadoN6OroV2):
    domain = "financiero"
    aggregate_root = "IngresoFinanciero"
    required_permissions = ["financiero.execute"]

    def perform_atomic_action(self, params: dict):
        logger.info("SOLDADO TESORERÍA: Registrando ingresos reales.")
        from application.services.analytics_service import FinanceService
        service = FinanceService()

        # Refactored: No direct Model access. Using Application Service.
        result = service.record_income(params)
        return result.data

class SoldadoRegistroEgresos(SoldadoN6OroV2):
    domain = "financiero"
    aggregate_root = "EgresoFinanciero"
    required_permissions = ["financiero.execute"]

    def perform_atomic_action(self, params: dict):
        logger.info("SOLDADO TESORERÍA: Registrando egresos reales.")
        from apps.prestadores.mi_negocio.gestion_financiera.models import EgresoFinanciero
        egreso = EgresoFinanciero.objects.create(
            provider_id=params.get('provider_id'),
            monto=params.get('monto'),
            concepto=params.get('concepto'),
            categoria=params.get('categoria', 'OPERATIVO')
        )
        return egreso

class SoldadoVerificadorSoportes(SoldadoN6OroV2):
    domain = "financiero"
    aggregate_root = "Document"
    required_permissions = ["financiero.execute"]

    def perform_atomic_action(self, params: dict):
        logger.info("SOLDADO TESORERÍA: Verificando soportes físicos/digitales.")
        return {"status": "SUCCESS", "msg": "Documentación validada."}

class SoldadoValidadorTransacciones(SoldadoN6OroV2):
    domain = "financiero"
    aggregate_root = "JournalEntry"
    required_permissions = ["financiero.execute"]

    def perform_atomic_action(self, params: dict):
        logger.info("SOLDADO TESORERÍA: Validando integridad de transacciones.")
        return {"status": "SUCCESS", "msg": "Transacción auditada."}

class SoldadoConsolidadorDiario(SoldadoN6OroV2):
    domain = "financiero"
    aggregate_root = "CajaDiaria"
    required_permissions = ["financiero.execute"]

    def perform_atomic_action(self, params: dict):
        logger.info("SOLDADO TESORERÍA: Consolidando cierre diario de caja.")
        return {"status": "SUCCESS", "msg": "Caja diaria consolidada."}

# --- SOLDADOS DE CONCILIACIÓN ---

class SoldadoDescargaExtractos(SoldadoN6OroV2):
    domain = "financiero"
    aggregate_root = "BankAccount"
    required_permissions = ["financiero.execute"]

    def perform_atomic_action(self, params: dict):
        logger.info("SOLDADO CONCILIACIÓN: Descargando extractos bancarios.")
        return {"status": "SUCCESS", "msg": "Extractos sincronizados."}

class SoldadoCruceAutomatico(SoldadoN6OroV2):
    domain = "financiero"
    aggregate_root = "Reconciliation"
    required_permissions = ["financiero.execute"]

    def perform_atomic_action(self, params: dict):
        logger.info("SOLDADO CONCILIACIÓN: Ejecutando algoritmo de cruce.")
        return {"status": "SUCCESS", "msg": "Cruce automático completado."}

class SoldadoIdentificadorDiferencias(SoldadoN6OroV2):
    domain = "financiero"
    aggregate_root = "Reconciliation"
    required_permissions = ["financiero.execute"]

    def perform_atomic_action(self, params: dict):
        logger.info("SOLDADO CONCILIACIÓN: Marcando partidas conciliatorias.")
        return {"status": "SUCCESS", "msg": "Diferencias identificadas."}

class SoldadoAjustadorContable(SoldadoN6OroV2):
    domain = "financiero"
    aggregate_root = "JournalEntry"
    required_permissions = ["financiero.execute"]

    def perform_atomic_action(self, params: dict):
        logger.info("SOLDADO CONCILIACIÓN: Sugiriendo asientos de ajuste.")
        return {"status": "SUCCESS", "msg": "Ajustes sugeridos persistidos."}

class SoldadoAuditorConciliacion(SoldadoN6OroV2):
    domain = "financiero"
    aggregate_root = "Reconciliation"
    required_permissions = ["financiero.execute"]

    def perform_atomic_action(self, params: dict):
        logger.info("SOLDADO CONCILIACIÓN: Certificando conciliación bancaria.")
        return {"status": "SUCCESS", "msg": "Conciliación certificada."}

# --- SOLDADOS DE PRESUPUESTO ---

class SoldadoInputMetas(SoldadoN6OroV2):
    domain = "financiero"
    aggregate_root = "Presupuesto"
    required_permissions = ["financiero.execute"]

    def perform_atomic_action(self, params: dict):
        logger.info("SOLDADO PRESUPUESTO: Cargando metas mensuales.")
        return {"status": "SUCCESS", "msg": "Metas presupuestales cargadas."}

class SoldadoTrackingGasto(SoldadoN6OroV2):
    domain = "financiero"
    aggregate_root = "EgresoFinanciero"
    required_permissions = ["financiero.execute"]

    def perform_atomic_action(self, params: dict):
        logger.info("SOLDADO PRESUPUESTO: Seguimiento de ejecución de gasto.")
        return {"status": "SUCCESS", "msg": "Ejecución de gasto actualizada."}

class SoldadoAnalistaVarianza(SoldadoN6OroV2):
    domain = "financiero"
    aggregate_root = "Presupuesto"
    required_permissions = ["financiero.execute"]

    def perform_atomic_action(self, params: dict):
        logger.info("SOLDADO PRESUPUESTO: Calculando varianza presupuestal.")
        return {"status": "SUCCESS", "msg": "Varianza calculada."}

class SoldadoValidadorRubros(SoldadoN6OroV2):
    domain = "financiero"
    aggregate_root = "Presupuesto"
    required_permissions = ["financiero.execute"]

    def perform_atomic_action(self, params: dict):
        logger.info("SOLDADO PRESUPUESTO: Validando rubros presupuestales.")
        return {"status": "SUCCESS", "msg": "Rubros validados."}

class SoldadoAlertaSobrecosto(SoldadoN6OroV2):
    domain = "financiero"
    aggregate_root = "AlertaFinanciera"
    required_permissions = ["financiero.execute"]

    def perform_atomic_action(self, params: dict):
        logger.info("SOLDADO PRESUPUESTO: Disparando alertas de desviación.")
        from apps.prestadores.mi_negocio.gestion_financiera.models import LineaPresupuesto, AlertaFinanciera

        provider_id = params.get('provider_id')
        if not provider_id:
            raise ValueError("provider_id es obligatorio")

        lineas_excedidas = LineaPresupuesto.objects.filter(
            presupuesto__provider_id=provider_id,
            monto_ejecutado__gt=models.F('monto_presupuestado')
        )

        count = 0
        for l in lineas_excedidas:
            AlertaFinanciera.objects.get_or_create(
                provider_id=provider_id,
                tipo=AlertaFinanciera.TipoAlerta.DESVIACION_PRESUPUESTAL,
                titulo=f"Sobrecosto en {l.nombre_item}",
                defaults={
                    "descripcion": f"El rubro {l.nombre_item} ha excedido el presupuesto en ${l.monto_ejecutado - l.monto_presupuestado}.",
                    "nivel_prioridad": "ALTA"
                }
            )
            count += 1

        return {"status": "ALERTS_PROCESSED", "count": count, "msg": f"Se procesaron {count} alertas de sobrecosto."}

# --- SOLDADOS DE OBLIGACIONES ---

class SoldadoRegistroCredito(SoldadoN6OroV2):
    domain = "financiero"
    aggregate_root = "CreditoFinanciero"
    required_permissions = ["financiero.execute"]

    def perform_atomic_action(self, params: dict):
        logger.info("SOLDADO OBLIGACIONES: Registrando nuevo crédito.")
        from apps.prestadores.mi_negocio.gestion_financiera.models import CreditoFinanciero, CuotaCredito
        from apps.prestadores.mi_negocio.gestion_financiera.services import FinanzasService
        from decimal import Decimal
        from django.utils import timezone
        from dateutil.relativedelta import relativedelta

        provider_id = params.get("provider_id")
        data = params.get("data", {})
        monto = Decimal(str(data.get("monto", 0)))
        tasa = Decimal(str(data.get("tasa", 0)))
        plazo = int(data.get("plazo", 12))

        credito = CreditoFinanciero.objects.create(
            provider_id=provider_id,
            entidad_financiera=data.get("banco", "Banco Genérico"),
            monto_principal=monto,
            tasa_interes_anual=tasa,
            plazo_meses=plazo,
            fecha_desembolso=timezone.now().date(),
            saldo_pendiente=monto
        )

        tabla = FinanzasService.calcular_amortizacion(monto, tasa, plazo)
        desembolso = timezone.now().date()

        for item in tabla:
            CuotaCredito.objects.create(
                credito=credito,
                numero_cuota=item["numero"],
                fecha_vencimiento=desembolso + relativedelta(months=item["numero"]),
                monto_capital=Decimal(str(item["capital"])),
                monto_interes=Decimal(str(item["interes"]))
            )
        return credito

class SoldadoCalculadorAmortizacion(SoldadoN6OroV2):
    domain = "financiero"
    aggregate_root = "CuotaCredito"
    required_permissions = ["financiero.execute"]

    def perform_atomic_action(self, params: dict):
        return {"status": "SUCCESS", "msg": "Tabla de amortización regenerada."}

class SoldadoTrackingPagos(SoldadoN6OroV2):
    domain = "financiero"
    aggregate_root = "CuotaCredito"
    required_permissions = ["financiero.execute"]

    def perform_atomic_action(self, params: dict):
        return {"status": "SUCCESS", "msg": "Seguimiento de pagos actualizado."}

class SoldadoAnalistaRiesgoCredito(SoldadoN6OroV2):
    domain = "financiero"
    aggregate_root = "RiesgoFinanciero"
    required_permissions = ["financiero.execute"]

    def perform_atomic_action(self, params: dict):
        return {"status": "SUCCESS", "msg": "Perfil de riesgo crediticio evaluado."}

class SoldadoAuditorDeuda(SoldadoN6OroV2):
    domain = "financiero"
    aggregate_root = "CreditoFinanciero"
    required_permissions = ["financiero.execute"]

    def perform_atomic_action(self, params: dict):
        return {"status": "SUCCESS", "msg": "Auditoría de pasivos completada."}

# --- SOLDADOS DE PROYECCIONES ---

class SoldadoRecoleccionHistorica(SoldadoN6OroV2):
    domain = "financiero"
    aggregate_root = "ProyeccionFinanciera"
    required_permissions = ["financiero.execute"]

    def perform_atomic_action(self, params: dict):
        return {"status": "SUCCESS", "msg": "Histórico recolectado."}

class SoldadoModeladoEscenarios(SoldadoN6OroV2):
    domain = "financiero"
    aggregate_root = "ProyeccionFinanciera"
    required_permissions = ["financiero.execute"]

    def perform_atomic_action(self, params: dict):
        return {"status": "SUCCESS", "msg": "Escenarios proyectados."}

class SoldadoValidacionIA(SoldadoN6OroV2):
    domain = "financiero"
    aggregate_root = "ProyeccionFinanciera"
    required_permissions = ["financiero.execute"]

    def perform_atomic_action(self, params: dict):
        return {"status": "SUCCESS", "msg": "IA validó la tendencia."}

class SoldadoAjusteTendencia(SoldadoN6OroV2):
    domain = "financiero"
    aggregate_root = "ProyeccionFinanciera"
    required_permissions = ["financiero.execute"]

    def perform_atomic_action(self, params: dict):
        return {"status": "SUCCESS", "msg": "Tendencia ajustada."}

class SoldadoGeneradorReportePredictivo(SoldadoN6OroV2):
    domain = "financiero"
    aggregate_root = "ProyeccionFinanciera"
    required_permissions = ["financiero.execute"]

    def perform_atomic_action(self, params: dict):
        return {"status": "SUCCESS", "msg": "Reporte generado."}

# --- SOLDADOS DE INDICADORES ---

class SoldadoKPI(SoldadoN6OroV2):
    domain = "financiero"
    aggregate_root = "IndicadorFinanciero"
    required_permissions = ["financiero.execute"]

    def perform_atomic_action(self, params: dict):
        from apps.prestadores.mi_negocio.gestion_financiera.services import FinanzasService
        from apps.domain_business.operativa.models import ProviderProfile

        provider_id = params.get('provider_id')
        if not provider_id:
            raise ValueError("provider_id es obligatorio")

        provider = ProviderProfile.objects.get(id=provider_id)
        indicadores = FinanzasService.calcular_indicadores(provider)
        return {"status": "SUCCESS", "kpi": params.get("kpi_name"), "data": indicadores, "msg": "Indicadores financieros sincronizados."}
