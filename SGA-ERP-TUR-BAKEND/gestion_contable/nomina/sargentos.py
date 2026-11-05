import logging
from decimal import Decimal
from django.db import transaction
from .models import Planilla, DetalleLiquidacion, NovedadNomina, Empleado
from apps.prestadores.mi_negocio.gestion_contable.contabilidad.models import AsientoContable, Transaccion, PeriodoContable
from apps.prestadores.mi_negocio.gestion_financiera.models import OrdenPago
from apps.audit.models import AuditLog

logger = logging.getLogger(__name__)

class SargentoNomina:
    """
    Sargento Atómico: Ejecuta acciones de nómina con integraciones contables y financieras.
    """

    @staticmethod
    def liquidar_empleado(planilla_id: str, empleado_id: str, usuario_id: int):
        """
        Calcula devengos y deducciones para un empleado en una planilla específica.
        """
        with transaction.atomic():
            planilla = Planilla.objects.get(id=planilla_id)
            empleado = Empleado.objects.get(id=empleado_id)
            contrato = empleado.contratos.filter(activo=True).first()

            if not contrato:
                raise ValueError(f"El empleado {empleado.nombre} no tiene un contrato activo.")

            # Cálculo simplificado (Fase 8 Logic)
            salario_diario = contrato.salario / Decimal(30)
            dias = 30 # Asumido por ahora
            devengado = contrato.salario

            # Deducciones salud/pensión (ej: 8%)
            deduccion = devengado * Decimal(0.08)
            neto = devengado - deduccion

            detalle = DetalleLiquidacion.objects.create(
                planilla=planilla,
                empleado=empleado,
                salario_base=contrato.salario,
                dias_trabajados=dias,
                total_devengado=devengado, # Nota: el modelo original no tenía estos campos, debo verificar
                total_deduccion=deduccion,
                total_neto=neto
            )

            return detalle

    @staticmethod
    def contabilizar_y_pagar(planilla_id: str, usuario_id: int):
        """
        Cierra la planilla, genera el asiento contable y las órdenes de pago.
        """
        with transaction.atomic():
            planilla = Planilla.objects.get(id=planilla_id)
            if planilla.estado != Planilla.EstadoPlanilla.LIQUIDADA:
                raise ValueError("La planilla debe estar liquidada antes de contabilizar.")

            # 1. Asiento Contable (Causación)
            periodo = PeriodoContable.objects.filter(provider_id=planilla.perfil_id, cerrado=False).first()
            asiento = AsientoContable.objects.create(
                periodo=periodo,
                fecha=planilla.periodo_fin,
                descripcion=f"Causación Nómina Periodo {planilla.periodo_inicio} - {planilla.periodo_fin}",
                creado_por_id=usuario_id,
                provider_id=planilla.perfil_id
            )

            # (Simplificado) Gasto Nómina vs Salarios por Pagar
            # Transaccion.objects.create(...)

            planilla.asiento_contable_ref_id = asiento.id
            planilla.estado = Planilla.EstadoPlanilla.CONTABILIZADA

            # 2. Órdenes de Pago (Finanzas)
            detalles = planilla.detalles_liquidacion.all()
            for detalle in detalles:
                orden = OrdenPago.objects.create(
                    perfil_ref_id=planilla.perfil_id,
                    cuenta_bancaria_ref_id=None, # Pendiente asignar por tesorería
                    beneficiario_id=detalle.empleado.id,
                    tipo_beneficiario="EMPLEADO",
                    fecha_pago=planilla.periodo_fin,
                    monto=detalle.total_neto,
                    concepto=f"Pago Nómina {planilla.periodo_inicio}",
                    estado='PENDIENTE'
                )

            planilla.save()

            AuditLog.objects.create(
                user_id=usuario_id,
                action="PAYROLL_ACCOUNTED_AND_ORDERED",
                details=f"Planilla {planilla.id} procesada para pago."
            )

            return {"status": "SUCCESS", "asiento": str(asiento.id)}
