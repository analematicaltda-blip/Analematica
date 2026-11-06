from decimal import Decimal
from django.db.models import Sum
from ..statements_models import EstadoResultados, BalanceGeneral, FlujoEfectivo, CambiosPatrimonio
from apps.prestadores.mi_negocio.gestion_contable.contabilidad.models import Cuenta, Transaccion, PeriodoContable

class FinancialStatementService:
    """
    Servicio encargado de generar los 4 estados financieros básicos a partir de la contabilidad.
    """

    @staticmethod
    def generar_estado_resultados(periodo_id: str, provider_id: str):
        """
        Calcula Ingresos, Costos y Gastos.
        """
        periodo = PeriodoContable.objects.get(id=periodo_id)

        # Ingresos (Tipo 4)
        ingresos = Transaccion.objects.filter(
            asiento__periodo=periodo,
            cuenta__tipo='INGRESOS'
        ).aggregate(total=Sum('credito'))['total'] or Decimal(0)

        # Gastos (Tipo 5)
        gastos = Transaccion.objects.filter(
            asiento__periodo=periodo,
            cuenta__tipo='GASTOS'
        ).aggregate(total=Sum('debito'))['total'] or Decimal(0)

        # Costos (Tipo 6)
        costos = Transaccion.objects.filter(
            asiento__periodo=periodo,
            cuenta__tipo='COSTOS'
        ).aggregate(total=Sum('debito'))['total'] or Decimal(0)

        utilidad = ingresos - (gastos + costos)

        reporte = EstadoResultados.objects.create(
            provider_id=provider_id,
            periodo_contable_ref_id=periodo_id,
            ingresos_totales=ingresos,
            costos_totales=costos,
            gastos_totales=gastos,
            utilidad_neta=utilidad,
            metadata_detalle={"mensaje": "Generado automáticamente por SARITA"}
        )
        return reporte

    @staticmethod
    def generar_balance_general(fecha_corte, provider_id: str):
        """
        Calcula Activos, Pasivos y Patrimonio a una fecha.
        """
        activos = Transaccion.objects.filter(
            asiento__fecha__lte=fecha_corte,
            asiento__provider_id=provider_id,
            cuenta__tipo='ACTIVO'
        ).aggregate(d=Sum('debito'), c=Sum('credito'))
        total_activos = (activos['d'] or 0) - (activos['c'] or 0)

        pasivos = Transaccion.objects.filter(
            asiento__fecha__lte=fecha_corte,
            asiento__provider_id=provider_id,
            cuenta__tipo='PASIVO'
        ).aggregate(d=Sum('debito'), c=Sum('credito'))
        total_pasivos = (pasivos['c'] or 0) - (pasivos['d'] or 0)

        patrimonio = Transaccion.objects.filter(
            asiento__fecha__lte=fecha_corte,
            asiento__provider_id=provider_id,
            cuenta__tipo='PATRIMONIO'
        ).aggregate(d=Sum('debito'), c=Sum('credito'))
        total_patrimonio = (patrimonio['c'] or 0) - (patrimonio['d'] or 0)

        reporte = BalanceGeneral.objects.create(
            provider_id=provider_id,
            fecha_corte=fecha_corte,
            total_activos=total_activos,
            total_pasivos=total_pasivos,
            total_patrimonio=total_patrimonio
        )
        return reporte
