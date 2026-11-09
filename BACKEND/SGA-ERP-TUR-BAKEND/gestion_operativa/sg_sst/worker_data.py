"""Minimal immutable worker safety evidence, no diagnoses or medical documents.

Medical decisions are encrypted using the existing configured field encryption.
Sources remain explicit human evidence; database records are not physical proof.
"""
import uuid
from django.conf import settings
from django.db import models
from django.core.exceptions import ValidationError
from django.db.models import Q,F
from api.fields import EncryptedTextField,fernet
from cryptography.fernet import InvalidToken

class StrictEncryptedDecisionField(EncryptedTextField):
    def from_db_value(self,value,expression,connection):
        try:
            result=fernet.decrypt(value.encode('utf-8')).decode('utf-8')
        except (InvalidToken,AttributeError,UnicodeError):
            raise ValidationError('No se pudo autenticar la autorización cifrada.') from None
        if result not in {'FIT','FIT_RESTRICTED','UNFIT'}:raise ValidationError('Decisión cifrada incompatible.')
        return result
    def to_python(self,value):
        if not isinstance(value,str) or value not in {'FIT','FIT_RESTRICTED','UNFIT'}:raise ValidationError('Decisión estructurada requerida.')
        return value

class SafetyQuerySet(models.QuerySet):
    def update(self,**kwargs):raise ValidationError('Evidencia inmutable; registra una nueva versión o revocación.')
    def delete(self):raise ValidationError('No se borra evidencia de seguridad laboral.')
    def bulk_update(self,*args,**kwargs):raise ValidationError('No se sobrescribe evidencia en lote.')
    def bulk_create(self,*args,**kwargs):raise ValidationError('Usa el servicio validado de registro, no altas masivas.')

class SafetyEvidence(models.Model):
    id=models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    provider=models.ForeignKey('turismo.TourismProvider',on_delete=models.PROTECT,related_name='+')
    employee=models.ForeignKey('nomina.Empleado',on_delete=models.PROTECT,related_name='+')
    recorded_by=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT,related_name='+')
    recorded_at=models.DateTimeField(auto_now_add=True)
    revision=models.PositiveIntegerField()
    evidence_digest=models.CharField(max_length=64)
    objects=SafetyQuerySet.as_manager()
    class Meta:
        abstract=True
    def clean(self):
        import re
        if not self.employee_id or not self.provider_id or self.employee.perfil_id!=self.provider_id:raise ValidationError('Trabajador y evidencia deben pertenecer a la misma empresa.')
        if not re.fullmatch('[0-9a-f]{64}',self.evidence_digest or '') or not self.revision:raise ValidationError('Soporte y revisión positiva requeridos.')
    def save(self,*args,**kwargs):
        if not self._state.adding or type(self).objects.filter(pk=self.pk).exists():raise ValidationError('No se actualiza evidencia histórica.')
        self.full_clean();return super().save(*args,**kwargs)
    def delete(self,*args,**kwargs):raise ValidationError('No se borra evidencia histórica.')

class ProfessionalAuthorization(SafetyEvidence):
    decision=StrictEncryptedDecisionField(choices=[('FIT','Apto'),('FIT_RESTRICTED','Requiere condiciones adicionales'),('UNFIT','No autorizado')])
    evaluated_at=models.DateTimeField()
    valid_from=models.DateTimeField()
    valid_until=models.DateTimeField()
    document_reference=models.UUIDField()
    class Meta:
        app_label='sg_sst'
        constraints=[models.UniqueConstraint(fields=['provider','employee','revision'],name='safety_fitness_revision'),models.CheckConstraint(condition=Q(valid_until__gt=F('valid_from'),valid_from__gte=F('evaluated_at')),name='safety_fitness_dates')]

class PPEAssignment(SafetyEvidence):
    equipment_code=models.CharField(max_length=30)
    equipment_reference=models.UUIDField()
    quantity=models.PositiveIntegerField()
    delivered_at=models.DateTimeField()
    valid_until=models.DateTimeField()
    class Meta:
        app_label='sg_sst'
        constraints=[models.UniqueConstraint(fields=['provider','employee','revision'],name='safety_ppe_revision'),models.CheckConstraint(condition=Q(quantity__gte=1,valid_until__gt=F('delivered_at')),name='safety_ppe_dates_qty')]

class WorkPeriod(SafetyEvidence):
    started_at=models.DateTimeField()
    ended_at=models.DateTimeField(null=True,blank=True)
    operation_reference=models.UUIDField(null=True,blank=True)
    source_kind=models.CharField(max_length=20,choices=[('MANUAL','Declarado por titular'),('DISPATCH','Inicio/fin operativo registrado')])
    class Meta:
        app_label='sg_sst'
        constraints=[models.UniqueConstraint(fields=['provider','employee','revision'],name='safety_work_revision'),models.CheckConstraint(condition=Q(ended_at__isnull=True)|Q(ended_at__gt=F('started_at')),name='safety_work_dates')]

class WorkPeriodEnd(SafetyEvidence):
    work_period=models.OneToOneField(WorkPeriod,on_delete=models.PROTECT,related_name='closing')
    ended_at=models.DateTimeField()
    class Meta:
        app_label='sg_sst'
        constraints=[models.UniqueConstraint(fields=['provider','employee','revision'],name='safety_work_end_revision')]
    def clean(self):
        super().clean()
        if self.work_period.provider_id!=self.provider_id or self.work_period.employee_id!=self.employee_id or self.work_period.ended_at is not None or self.ended_at<=self.work_period.started_at:raise ValidationError('Cierre incompatible con la jornada original.')

class RestPeriod(SafetyEvidence):
    started_at=models.DateTimeField()
    ended_at=models.DateTimeField()
    class Meta:
        app_label='sg_sst'
        constraints=[models.UniqueConstraint(fields=['provider','employee','revision'],name='safety_rest_revision'),models.CheckConstraint(condition=Q(ended_at__gt=F('started_at')),name='safety_rest_dates')]

class SafetyRevocation(SafetyEvidence):
    record_type=models.CharField(max_length=12,choices=[('FITNESS','Autorización'),('PPE','Entrega EPP'),('REST','Descanso declarado')])
    record_id=models.UUIDField()
    class Meta:
        app_label='sg_sst'
        constraints=[models.UniqueConstraint(fields=['record_type','record_id'],name='safety_revocation_once'),models.UniqueConstraint(fields=['provider','employee','revision'],name='safety_revoke_revision')]
