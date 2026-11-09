"""Personal owner-scoped operational planning/containment, never qualified dispatch."""
import hashlib
from django.db import transaction
from rest_framework.exceptions import ValidationError
from apps.audit.models import AuditLog
from .state_guard import _permit
from .sg_sst.sargentos import _context

ORDER={'PENDIENTE':{'PREPARACION','INCIDENCIA','CANCELADA'},'PREPARACION':{'INCIDENCIA','CANCELADA'},'EJECUCION':{'INCIDENCIA','CANCELADA'},'VALIDACION':{'INCIDENCIA','CANCELADA'},'INCIDENCIA':{'CANCELADA'},'COMPLETADA':set(),'CANCELADA':set()}
PROCESS={'PLANIFICADO':{'SUSPENDIDO','FALLIDO'},'EN_EJECUCION':{'SUSPENDIDO','FALLIDO'},'SUSPENDIDO':{'FALLIDO'},'COMPLETADO':set(),'FALLIDO':set()}

def model_for(kind):
    from .models import OrdenOperativa,ProcesoOperativo
    if kind not in {'OrdenOperativa','ProcesoOperativo'}:raise ValidationError('Tipo operativo no admitido.')
    return OrdenOperativa if kind=='OrdenOperativa' else ProcesoOperativo

def diagnosis(obj):
    return {'provider_id':str(obj.provider_id),'operation_id':str(obj.pk),'state':obj.estado,
        'read_only':True,'ready_to_dispatch':False,'medical_qualification_verified':False,
        'ppe_qualification_verified':False,'fatigue_qualification_verified':False,
        'blocking_codes':['QUALIFIED_FITNESS_CONTRACT_UNAVAILABLE','QUALIFIED_PPE_CONTRACT_UNAVAILABLE','QUALIFIED_WORK_REST_CONTRACT_UNAVAILABLE'],
        'clinical_content_returned':False,'ledger_written':False,'service_started':False,
        'service_started_by_this_call':False,'physical_service_state_verified':False}

@transaction.atomic
def transition(*,usuario_id,provider_id,kind,operation_id,expected_state,new_state,reason,confirmed,audit_action='OPERATIONAL_STATE_CHANGED'):
    user,provider=_context(usuario_id,provider_id)
    if confirmed is not True or not isinstance(expected_state,str) or not isinstance(new_state,str) or not isinstance(reason,str) or not 1<=len(reason.strip())<=2000:
        raise ValidationError('Confirma la transición exacta y su motivo acotado.')
    if audit_action not in {'OPERATIONAL_STATE_CHANGED','OPERATIONAL_SST_BLOCK'}:raise ValidationError('Tipo de auditoría no admitido.')
    model=model_for(kind);obj=model.objects.select_for_update().filter(pk=operation_id,provider_id=provider.pk,is_active=True).first()
    if obj is None:raise ValidationError('Operación no disponible para la empresa autorizada.')
    if obj.estado!=expected_state:raise ValidationError('La operación cambió; recarga su estado.')
    if new_state in {'EJECUCION','EN_EJECUCION','VALIDACION','COMPLETADA','COMPLETADO'}:
        raise ValidationError('Despacho/ejecución no cualificados: faltan controles verificables de aptitud, EPP y jornada.')
    graph=ORDER if kind=='OrdenOperativa' else PROCESS
    if new_state==obj.estado:
        if new_state not in {'SUSPENDIDO','INCIDENCIA','CANCELADA','FALLIDO'}:raise ValidationError('No se crea una transición vacía.')
        return {**diagnosis(obj),'replayed':True,'state_changed':False}
    if new_state not in graph.get(obj.estado,set()):raise ValidationError('Transición operativa no admitida.')
    before=obj.estado;obj.estado=new_state
    token=_permit.set((kind,str(obj.pk),str(provider.pk),before,new_state))
    try:obj.save(update_fields=['estado','updated_at'])
    finally:_permit.reset(token)
    audit=AuditLog.objects.create(user=user,username=user.username,action=audit_action,
        details={'provider_id':str(provider.pk),'operation_id':str(obj.pk),'kind':kind,
                 'previous_state':before,'new_state':new_state,'reason_digest':hashlib.sha256(reason.encode()).hexdigest()})
    return {**diagnosis(obj),'read_only':False,'replayed':False,'state_changed':True,'audit_id':str(audit.pk)}
