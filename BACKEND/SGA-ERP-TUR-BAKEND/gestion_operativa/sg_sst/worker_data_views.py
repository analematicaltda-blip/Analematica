"""Authenticated data intake and owner operational summaries, no medical files."""
from uuid import UUID
from django.db import transaction
from django.core.exceptions import ValidationError as ModelValidationError
from rest_framework import permissions,viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.authentication import JWTAuthentication
from apps.core_erp.accounting.query_parser import AccountingQueryJSONParser
from apps.core_erp.accounting.http_privacy import PrivateAccountingResponseMixin
from ...web_session import ErpSessionAuthentication
from . import worker_data_service as service
from .worker_data import ProfessionalAuthorization,PPEAssignment,WorkPeriod,WorkPeriodEnd,RestPeriod,SafetyRevocation

COMMON={'employee_id','request_id','expected_revision','evidence_digest','confirmed'}
class WorkerSafetyDataViewSet(PrivateAccountingResponseMixin,viewsets.GenericViewSet):
    permission_classes=[permissions.IsAuthenticated]
    parser_classes=[AccountingQueryJSONParser]
    authentication_classes=[JWTAuthentication,ErpSessionAuthentication]
    def provider_id(self):
        if set(self.request.query_params)!={'provider_id'} or len(self.request.query_params.getlist('provider_id'))!=1:raise ValidationError('Proveedor explícito único requerido.')
        try:return UUID(self.request.query_params['provider_id'])
        except ValueError:raise ValidationError('Proveedor inválido.') from None
    def command(self,request,operation,fields):
        if not isinstance(request.data,dict) or set(request.data)!=COMMON|fields:raise ValidationError('Contrato de registro de seguridad inválido.')
        try:return Response(getattr(service,operation)(actor_id=request.user.pk,provider_id=self.provider_id(),**request.data))
        except (ModelValidationError,ValueError,TypeError):raise ValidationError('Datos o relaciones de seguridad inválidos; no se sustituyen por valores predeterminados.') from None
    @action(detail=False,methods=['post'],url_path='trabajadores')
    @transaction.atomic
    def employees(self,request):
        from rest_framework.exceptions import PermissionDenied
        from apps.prestadores.mi_negocio.gestion_contable.nomina.models import Empleado
        if not isinstance(request.data,dict) or set(request.data)!={'after_id'}:raise ValidationError('Cursor explícito requerido.')
        try:user,provider,_=service.context(request.user.pk,self.provider_id())
        except PermissionDenied:user,provider,_=service.context(request.user.pk,self.provider_id(),True)
        query=Empleado.objects.filter(perfil_id=provider.pk).order_by('pk');cursor=request.data['after_id']
        if cursor is not None:
            try:query=query.filter(pk__gt=UUID(cursor))
            except (ValueError,TypeError):raise ValidationError('Cursor inválido.') from None
        rows=list(query.values('id','nombre','apellido','estado')[:51])
        return Response({'provider_id':str(provider.pk),'read_only':True,'employees':[{'id':str(row['id']),'name':row['nombre']+' '+row['apellido'],'state':row['estado']} for row in rows[:50]],'next_after_id':str(rows[49]['id']) if len(rows)>50 else None,'clinical_content_returned':False,'documents_returned':False})
    @action(detail=False,methods=['post'],url_path='autorizacion-profesional')
    def fitness(self,request):return self.command(request,'record_fitness',{'decision','evaluated_at','valid_from','valid_until','document_reference'})
    @action(detail=False,methods=['post'],url_path='entrega-epp')
    def ppe(self,request):return self.command(request,'record_ppe',{'equipment_code','equipment_reference','quantity','delivered_at','valid_until'})
    @action(detail=False,methods=['post'],url_path='jornada')
    def work(self,request):return self.command(request,'record_work',{'started_at','ended_at'})
    @action(detail=False,methods=['post'],url_path='jornada-operativa')
    def operational_work(self,request):return self.command(request,'record_work',{'started_at','ended_at','operation_reference'})
    @action(detail=False,methods=['post'],url_path='cerrar-jornada')
    def end_work(self,request):return self.command(request,'close_work',{'work_period_id','ended_at'})
    @action(detail=False,methods=['post'],url_path='descanso')
    def rest(self,request):return self.command(request,'record_rest',{'started_at','ended_at'})
    @action(detail=False,methods=['post'],url_path='revocar')
    def revoke(self,request):return self.command(request,'revoke_record',{'record_type','record_id'})
    @action(detail=False,methods=['post'],url_path='dossier-despacho')
    def dispatch_attestation(self,request):
        from ..dispatch_authorization import attest
        if not isinstance(request.data,dict) or set(request.data)!={'order_id','crew','expected_revision','confirmed'}:raise ValidationError('Referencias persistidas y revisión explícitas requeridas.')
        try:return Response(attest(actor_id=request.user.pk,provider_id=self.provider_id(),**request.data))
        except (ModelValidationError,ValueError,TypeError):raise ValidationError('Referencias o datos profesionales inválidos.') from None
    @action(detail=False,methods=['post'],url_path='detalle-profesional')
    @transaction.atomic
    def fitness_detail(self,request):
        from .access import require_clinical_permission
        if not isinstance(request.data,dict) or set(request.data)!={'record_id'}:raise ValidationError('Referencia única requerida.')
        user,provider,_=service.context(request.user.pk,self.provider_id(),True);require_clinical_permission(user,'retrieve')
        try:row=ProfessionalAuthorization.objects.filter(pk=UUID(str(request.data['record_id'])),provider=provider).first()
        except (ValueError,ModelValidationError):raise ValidationError('Referencia inválida o decisión no autenticable.') from None
        if row is None:raise ValidationError('Registro profesional no disponible.')
        try:decision=row.decision
        except ModelValidationError:raise ValidationError('No se puede autenticar la decisión cifrada.') from None
        return Response({'record_id':str(row.pk),'employee_id':str(row.employee_id),'decision':decision,'evaluated_at':row.evaluated_at.isoformat(),'valid_from':row.valid_from.isoformat(),'valid_until':row.valid_until.isoformat(),'revision':row.revision,'revoked':service.revoked('FITNESS',row),'clinical_content_returned':True,'medical_documents_returned':False,'ledger_written':False})
    @action(detail=False,methods=['post'],url_path='resumen-operativo')
    @transaction.atomic
    def summary(self,request):
        if not isinstance(request.data,dict) or set(request.data)!={'employee_id','kind','before_revision'}:raise ValidationError('Trabajador, tipo y cursor explícitos requeridos.')
        user,provider,_=service.context(request.user.pk,self.provider_id());worker=service.employee(provider,request.data['employee_id'])
        kind=request.data['kind'];models={'FITNESS':ProfessionalAuthorization,'PPE':PPEAssignment,'WORK':WorkPeriod,'WORK_END':WorkPeriodEnd,'REST':RestPeriod,'REVOKE':SafetyRevocation}
        if not isinstance(kind,str) or kind not in models:raise ValidationError('Tipo de registro no admitido.')
        cursor=request.data['before_revision']
        if cursor is not None and (type(cursor) is not int or cursor<1):raise ValidationError('Cursor de revisión inválido.')
        query=models[kind].objects.filter(provider=provider,employee=worker).order_by('-revision')
        if kind=='FITNESS':query=query.defer('decision')
        if cursor is not None:query=query.filter(revision__lt=cursor)
        rows=list(query[:21]);items=[]
        for row in rows[:20]:
            item={'record_id':str(row.pk),'revision':row.revision,'recorded_at':row.recorded_at.isoformat(),'recorded_by':str(row.recorded_by_id)}
            for field in ['equipment_code','quantity','delivered_at','valid_from','valid_until','started_at','ended_at','record_type','source_kind','operation_reference','record_id']:
                if field=='record_id':continue
                if hasattr(row,field):
                    value=getattr(row,field);item[field]=value.isoformat() if hasattr(value,'isoformat') else value
            if kind in {'FITNESS','PPE','REST'}:item['revoked']=service.revoked(kind,row)
            items.append(item)
        return Response({'provider_id':str(provider.pk),'employee_id':str(worker.pk),'read_only':True,'items':items,'next_before_revision':rows[19].revision if len(rows)>20 else None,'clinical_content_returned':False,'decision_returned':False,'documents_returned':False,'source_independently_verified':False,'ledger_written':False})
