"""Disposable work sources for loopback integration tests, never app startup."""
def install(case,create,payroll):
    from datetime import datetime,time,timedelta
    from uuid import uuid4
    from zoneinfo import ZoneInfo
    from django.db import connection
    from django.utils import timezone
    from apps.prestadores.mi_negocio.gestion_operativa.sg_sst.worker_data import ProfessionalAuthorization,PPEAssignment,WorkPeriod,WorkPeriodEnd,RestPeriod,SafetyRevocation
    from apps.prestadores.mi_negocio.gestion_operativa.sg_sst.worker_data_guards import install as guards
    from apps.prestadores.mi_negocio.gestion_operativa.sg_sst.worker_data_service import record_work
    from apps.prestadores.mi_negocio.gestion_operativa.models import OrdenOperativa
    for model in [ProfessionalAuthorization,PPEAssignment,WorkPeriod,WorkPeriodEnd,RestPeriod,SafetyRevocation,OrdenOperativa]:create(model)
    guards(connection)
    start=datetime.combine(timezone.localdate()-timedelta(days=1),time(9),ZoneInfo('America/Bogota'))
    centers={}
    for i in range(2):
        begin=start+timedelta(hours=i*2);end=begin+timedelta(hours=2)
        order=OrdenOperativa.objects.create(provider_id=case.provider.pk,contrato_ref_id=uuid4(),descripcion_servicio='Synthetic cost operation '+str(i),fecha_inicio=begin,fecha_fin_estimada=end)
        centers[str(order.pk)]='SYNTHETIC_'+str(i)
        record_work(actor_id=case.provider.owner_id,provider_id=case.provider.pk,employee_id=payroll['workers'][0]['employee_id'],request_id=str(uuid4()),expected_revision=i,evidence_digest='c'*64,started_at=begin.isoformat(),ended_at=end.isoformat(),operation_reference=str(order.pk),confirmed=True)
    return {'payroll_id':payroll['payroll_id'],'capacities':[{'employee_id':payroll['workers'][0]['employee_id'],'capacity_seconds':28800}],'operation_centers':centers,'evidence_digest':'d'*64,'reason_code':'SYNTHETIC_TEST','expected_revision':0,'confirmed':True}
