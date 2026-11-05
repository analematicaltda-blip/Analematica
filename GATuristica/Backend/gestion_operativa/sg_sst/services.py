from decimal import Decimal
from .models import (
    IndicadorSST, IncidenteLaboral, PlanAnualSST, ActividadPlanSST,
    MatrizRiesgo, AlertaSST, InspeccionSST
)
from django.utils import timezone
from django.db.models import Count, Sum

class SSTService:
    @staticmethod
    def calcular_indicadores(provider_id, periodo):
        """
        Calcula indicadores clave de SST para un periodo dado.
        """
        # 1. Tasa de accidentalidad
        # Nota: En un sistema real, Nro de trabajadores vendría de Nómina.
        n_trabajadores = 10
        n_accidentes = IncidenteLaboral.objects.filter(
            provider_id=provider_id,
            tipo=IncidenteLaboral.TipoEvento.ACCIDENTE
        ).count()

        tasa_acc = (Decimal(n_accidentes) / Decimal(n_trabajadores)) * 100 if n_trabajadores > 0 else 0

        IndicadorSST.objects.update_or_create(
            provider_id=provider_id,
            nombre="Tasa de Accidentalidad",
            periodo=periodo,
            defaults={'valor': tasa_acc, 'meta': 2.0, 'tipo': 'Accidentalidad'}
        )

        # 2. Cumplimiento Plan Anual
        plan = PlanAnualSST.objects.filter(provider_id=provider_id, estado='ACTIVO').first()
        if plan:
            total = plan.actividades.count()
            completadas = plan.actividades.filter(completada=True).count()
            cumplimiento = (Decimal(completadas) / Decimal(total)) * 100 if total > 0 else 0
            plan.porcentaje_cumplimiento = cumplimiento
            plan.save()

            IndicadorSST.objects.update_or_create(
                provider_id=provider_id,
                nombre="Cumplimiento Plan Anual",
                periodo=periodo,
                defaults={'valor': cumplimiento, 'meta': 90.0, 'tipo': 'Cumplimiento'}
            )

        return True

    @staticmethod
    def generar_alerta_incidente(incidente):
        AlertaSST.objects.create(
            provider_id=incidente.provider_id,
            titulo=f"NUEVO EVENTO: {incidente.tipo}",
            mensaje=f"Se ha registrado un {incidente.tipo} de gravedad {incidente.gravedad} en {incidente.lugar}.",
            criticidad='CRITICA' if incidente.gravedad == 'MORTAL' else 'ALTA'
        )

    @staticmethod
    def registrar_hallazgo(inspeccion_id, descripcion, criticidad, plan_accion, fecha_limite):
        from .models import HallazgoInspeccion
        inspeccion = InspeccionSST.objects.get(id=inspeccion_id)
        hallazgo = HallazgoInspeccion.objects.create(
            inspeccion=inspeccion,
            descripcion=descripcion,
            criticidad=criticidad,
            plan_accion=plan_accion,
            fecha_limite=fecha_limite
        )
        return hallazgo
