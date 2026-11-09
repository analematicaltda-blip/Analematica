from decimal import Decimal
from .models import (
    IndicadorSST, IncidenteLaboral, PlanAnualSST, ActividadPlanSST,
    MatrizRiesgo, AlertaSST, InspeccionSST
)
from django.utils import timezone

class SSTService:
    @staticmethod
    def calcular_indicadores(provider_id, periodo):
        """Current-month observations, not a certified occupational accident rate.

        Current staffing cannot reconstruct historical exposed worker counts.
        No fabricated denominator, target, historical backfill or metric write.
        """
        from datetime import date, datetime, time
        from decimal import localcontext, ROUND_HALF_UP
        from ...gestion_contable.nomina.models import Empleado
        today = timezone.localdate()
        if not isinstance(periodo, str) or periodo != today.strftime('%Y-%m'):
            raise ValueError('Solo se admite el mes actual; falta denominador histórico verificado.')
        start = timezone.make_aware(datetime.combine(today.replace(day=1), time.min))
        end_day = date(today.year + (today.month == 12), today.month % 12 + 1, 1)
        end = timezone.make_aware(datetime.combine(end_day, time.min))
        incidents = IncidenteLaboral.objects.filter(provider_id=provider_id, fecha_hora__gte=start, fecha_hora__lt=end, fecha_hora__lte=timezone.now())
        accidents = incidents.filter(tipo=IncidenteLaboral.TipoEvento.ACCIDENTE).count()
        workers = Empleado.objects.filter(perfil_id=provider_id, estado='ACTIVO').count()
        plans = list(PlanAnualSST.objects.filter(provider_id=provider_id, estado='ACTIVO', año=today.year)[:2])
        completion = None
        with localcontext() as ctx:
            ctx.prec = 38
            rate = format((Decimal(accidents) * 100 / workers).quantize(Decimal('.01'), rounding=ROUND_HALF_UP), '.2f') if workers else None
            if len(plans) == 1:
                activities = plans[0].actividades.all()
                total = activities.count()
                if total:
                    completion = format((Decimal(activities.filter(completada=True).count()) * 100 / total).quantize(Decimal('.01'), rounding=ROUND_HALF_UP), '.2f')
        return {'periodo': periodo, 'incidentes_periodo': incidents.count(), 'accidentes_periodo': accidents,
                'trabajadores_activos_observados': workers, 'accidentes_por_100_trabajadores_actuales': rate,
                'cumplimiento_plan': completion, 'denominador_historico_verificado': False,
                'certificacion_regulatoria': False, 'habilita_despacho': False, 'read_only': True,
                'limitaciones': ['Dotación actual; no equivale a población expuesta histórica.',
                                 'No evalúa aptitud médica, EPP ni fatiga para autorizar servicios.']}

    @staticmethod
    def generar_alerta_incidente(incidente):
        AlertaSST.objects.create(
            provider_id=incidente.provider_id,
            titulo=f"NUEVO EVENTO: {incidente.tipo}",
            mensaje=f"Se ha registrado un {incidente.tipo} de gravedad {incidente.gravedad} en {incidente.lugar}.",
            criticidad='CRITICA' if incidente.gravedad == 'MORTAL' else 'ALTA'
        )

    @staticmethod
    def registrar_hallazgo(inspeccion_id, descripcion, criticidad, plan_accion, fecha_limite, *, provider_id):
        from .models import HallazgoInspeccion
        inspeccion = InspeccionSST.objects.get(id=inspeccion_id, provider_id=provider_id)
        hallazgo = HallazgoInspeccion.objects.create(
            inspeccion=inspeccion,
            descripcion=descripcion,
            criticidad=criticidad,
            plan_accion=plan_accion,
            fecha_limite=fecha_limite
        )
        return hallazgo
