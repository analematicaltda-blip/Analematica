"""Fail-closed ORM state boundary for generic operational orders/processes.
No aptitude/EPP/fatigue clearance exists yet: never authorize service activation.
The private context is an internal code boundary, not a remote authorization token.
"""
from contextvars import ContextVar
from django.db import models,transaction
from rest_framework.exceptions import ValidationError

_permit=ContextVar('operational_audited_transition',default=None)
PROTECTED={'estado','provider','provider_id','inicio_real','fin_real'}

class OperationalQuerySet(models.QuerySet):
    def update(self,**kwargs):
        if PROTECTED&set(kwargs):raise ValidationError('Estado/empresa solo mediante transición auditada.')
        return super().update(**kwargs)
    def bulk_update(self,objs,fields,batch_size=None):
        if PROTECTED&set(fields):raise ValidationError('No se permiten transiciones masivas sin revisión.')
        return super().bulk_update(objs,fields,batch_size=batch_size)
    def bulk_create(self,objs,batch_size=None,ignore_conflicts=False,update_conflicts=False,update_fields=None,unique_fields=None):
        if update_conflicts or ignore_conflicts:raise ValidationError('No se ocultan conflictos ni se reescriben estados por alta masiva.')
        objs=list(objs)
        for obj in objs:check_initial(obj)
        return super().bulk_create(objs,batch_size=batch_size,ignore_conflicts=False,
            update_conflicts=False,update_fields=update_fields,unique_fields=unique_fields)

def check_initial(obj):
    initial='PENDIENTE' if obj.__class__.__name__=='OrdenOperativa' else 'PLANIFICADO'
    if not obj.provider_id or obj.estado!=initial or getattr(obj,'inicio_real',None) is not None or getattr(obj,'fin_real',None) is not None:
        raise ValidationError('Solo se crean borradores con empresa explícita, sin ejecución o tiempos reales.')

class OperationalStateMixin:
    @transaction.atomic
    def save(self,*args,**kwargs):
        previous=type(self).objects.select_for_update().filter(pk=self.pk).first() if self.pk else None
        if previous is None:check_initial(self)
        else:
            if self._state.adding:raise ValidationError('No se reutiliza la identidad de una operación existente.')
            if previous.provider_id!=self.provider_id:raise ValidationError('No se reasigna la empresa de una operación histórica.')
            expected=(type(self).__name__,str(self.pk),str(self.provider_id),previous.estado,self.estado)
            if previous.estado!=self.estado and _permit.get()!=expected:
                raise ValidationError('Se requiere una transición autenticada y auditada.')
            if any(getattr(previous,k,None)!=getattr(self,k,None) for k in ('inicio_real','fin_real')):
                raise ValidationError('Los tiempos reales requieren un flujo de ejecución cualificado.')
        return super().save(*args,**kwargs)
