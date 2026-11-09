from django.db import transaction, models
from django.utils import timezone
from .models import (
    Empleado, Contrato, Planilla, DetalleLiquidacion,
    NovedadNomina, IncapacidadLaboral, ProvisionNomina, IndicadorLaboral
)
from apps.prestadores.mi_negocio.gestion_operativa.modulos_genericos.perfil.models import ProviderProfile

from rest_framework.exceptions import APIException

class PayrollReadinessUnavailable(APIException):
    status_code = 503
    default_code = 'PAYROLL_REVIEWED_PIPELINE_UNAVAILABLE'
    default_detail = 'Nómina no habilitada: faltan reglas vigentes revisadas, doble aprobación y posteo verificable al ledger. No se liquidó ni contabilizó la planilla.'

class NominaService:
    """
    Motor Central de Nómina SARITA.
    Maneja liquidación, provisiones e integración contable.
    """

    @staticmethod
    def liquidar_periodo(planilla_id, usuario_id=None):
        # Legacy defaults were dated 2024/2025 and absences were not scoped to
        # the period. Do not mutate payroll using those unqualified rules.
        raise PayrollReadinessUnavailable()

    @staticmethod
    def contabilizar_nomina(planilla_id, usuario_id=None):
        # A draft journal is not a posted ledger entry. No fabricated success.
        raise PayrollReadinessUnavailable()

    @staticmethod
    def generar_indicadores(provider_id):
        provider = ProviderProfile.objects.get(id=provider_id)
        # Costo Laboral Total
        total_costo = DetalleLiquidacion.objects.filter(planilla__perfil=provider).aggregate(s=models.Sum('total_devengado'))['s'] or 0

        IndicadorLaboral.objects.create(
            perfil=provider,
            nombre="Costo Laboral Total",
            valor=total_costo,
            periodo=timezone.now().strftime("%Y-%m")
        )
        return True

    @staticmethod
    @transaction.atomic
    def liquidar_contrato(contrato_id, fecha_retiro, motivo, usuario_id=None):
        """
        Realiza la liquidación final de un contrato laboral.
        """
        contrato = Contrato.objects.select_for_update().get(id=contrato_id)
        if not contrato.activo:
            raise ValueError("El contrato ya está liquidado/inactivo.")

        # Marcar contrato como inactivo
        contrato.fecha_fin = fecha_retiro
        contrato.activo = False
        contrato.save()

        # Actualizar estado del empleado
        empleado = contrato.empleado
        empleado.estado = Empleado.EstadoEmpleado.RETIRADO
        empleado.save()

        # En una implementación real, se generaría un Asiento Contable por el pago de prestaciones.
        return True
