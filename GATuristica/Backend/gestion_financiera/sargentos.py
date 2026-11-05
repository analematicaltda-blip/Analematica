import logging
from decimal import Decimal
from django.db import transaction
from .models import OrdenPago, CuentaBancaria, TesoreriaCentral
from apps.prestadores.mi_negocio.gestion_contable.contabilidad.models import AsientoContable, Transaccion, PeriodoContable
from apps.audit.models import AuditLog

logger = logging.getLogger(__name__)

class SargentoFinanciero:
    """
    Sargento Atómico: Ejecuta acciones financieras indivisibles con respaldo contable.
    """

    @staticmethod
    def ejecutar_pago(orden_pago_id: str, usuario_id: int):
        """
        Ejecuta una transferencia de fondos y genera el asiento contable.
        """
        with transaction.atomic():
            orden = OrdenPago.objects.get(id=orden_pago_id)
            cuenta = CuentaBancaria.objects.get(id=orden.cuenta_bancaria_ref_id)

            if cuenta.saldo_actual < orden.monto:
                raise ValueError("Saldo insuficiente en la cuenta para ejecutar el pago.")

            # 1. Movimiento de Dinero (Finanzas)
            cuenta.saldo_actual -= orden.monto
            cuenta.save()

            # 2. Respaldo Contable (Contabilidad)
            # Buscamos el periodo abierto
            periodo = PeriodoContable.objects.filter(provider_id=orden.perfil_ref_id, cerrado=False).first()
            if not periodo:
                raise ValueError("No hay un periodo contable abierto para registrar el pago.")

            asiento = AsientoContable.objects.create(
                periodo=periodo,
                fecha=orden.fecha_pago,
                descripcion=f"Pago: {orden.concepto} - Ref: {orden.referencia_pago}",
                creado_por_id=usuario_id,
                provider_id=orden.perfil_ref_id
            )

            # Transacción: Salida de Bancos (Crédito)
            Transaccion.objects.create(
                asiento=asiento,
                cuenta_id=cuenta.cuenta_contable_ref_id,
                credito=orden.monto,
                debito=0,
                descripcion="Salida de fondos bancarios"
            )

            # Transacción: Disminución de Pasivo (Débito) - Simplificado
            # En un flujo real buscaríamos la cuenta por pagar
            # Transaccion.objects.create(...)

            # 3. Actualización de Estado
            orden.estado = OrdenPago.EstadoPago.PAGADA
            orden.save()

            # 4. Auditoría
            AuditLog.objects.create(
                user_id=usuario_id,
                action="FINANCIAL_PAYMENT_EXECUTED",
                details=f"Pago ejecutado por {orden.monto}. Orden ID: {orden.id}"
            )

            logger.info(f"SARGENTO FINANCIERO: Pago ejecutado exitosamente. Orden {orden_pago_id}")
            return {"status": "SUCCESS", "monto": orden.monto}

    @staticmethod
    def bloquear_fondos(monto: Decimal, perfil_id: str, motivo: str):
        """
        Bloquea fondos de la liquidez disponible para reservas o provisiones.
        """
        with transaction.atomic():
            tesoreria = TesoreriaCentral.objects.get(provider_id=perfil_id)
            if tesoreria.liquidez_disponible < monto:
                raise ValueError("Liquidez insuficiente para bloquear fondos.")

            tesoreria.liquidez_disponible -= monto
            tesoreria.reservas_totales += monto
            tesoreria.save()

            logger.info(f"SARGENTO FINANCIERO: Fondos bloqueados: {monto}. Motivo: {motivo}")
            return {"status": "BLOCKED", "monto": monto}

    @staticmethod
    def liberar_fondos(monto: Decimal, perfil_id: str, motivo: str):
        """
        Libera fondos de reserva a liquidez disponible.
        """
        with transaction.atomic():
            tesoreria = TesoreriaCentral.objects.get(provider_id=perfil_id)
            if tesoreria.reservas_totales < monto:
                raise ValueError("Reservas insuficientes para liberar fondos.")

            tesoreria.reservas_totales -= monto
            tesoreria.liquidez_disponible += monto
            tesoreria.save()

            logger.info(f"SARGENTO FINANCIERO: Fondos liberados: {monto}. Motivo: {motivo}")
            return {"status": "RELEASED", "monto": monto}
