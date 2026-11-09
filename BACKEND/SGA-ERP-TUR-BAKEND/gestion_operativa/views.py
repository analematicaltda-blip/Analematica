"""Owner-scoped operational drafts and explicit audited safe transitions."""
from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework import viewsets,permissions
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied,ValidationError
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from ..web_session import ErpSessionAuthentication
from apps.core_erp.accounting.http_privacy import PrivateAccountingResponseMixin
from ..company_scope import owned_provider
from apps.turismo.services.company_identity import resolve_company
from apps.audit.models import AuditLog
from .models import ProcesoOperativo,TareaOperativa,OrdenOperativa,IncidenteOperativo
from .serializers import ProcesoOperativoSerializer,TareaOperativaSerializer,OrdenOperativaSerializer,IncidenteOperativoSerializer
from .sg_sst.sargentos import _context

class ScopedOperationalViewSet(PrivateAccountingResponseMixin,viewsets.ModelViewSet):
    authentication_classes=[JWTAuthentication,ErpSessionAuthentication]
    permission_classes=[permissions.IsAuthenticated]
    def provider(self):
        user=get_user_model().objects.filter(pk=self.request.user.pk,is_active=True).first()
        if user is None:raise PermissionDenied('Se requiere un titular activo.')
        self.request.user=user;provider=owned_provider(self.request);resolve_company(user,provider.pk)
        return provider
    def get_queryset(self):
        provider=self.provider();model=self.serializer_class.Meta.model
        query=model.objects.filter(provider_id=provider.pk,is_active=True)
        if model is IncidenteOperativo:query=query.filter(orden__provider_id=provider.pk,orden__is_active=True)
        if model is TareaOperativa:query=query.filter(proceso__provider_id=provider.pk,proceso__is_active=True)
        return query
    def get_serializer_context(self):
        return {**super().get_serializer_context(),'operational_provider':self.provider()}
    @transaction.atomic
    def perform_create(self,serializer):
        user,provider=_context(self.request.user.pk,self.provider().pk)
        checked=self.get_serializer(data=serializer.initial_data);checked.is_valid(raise_exception=True)
        serializer.instance=checked.save(provider_id=provider.pk)
        AuditLog.objects.create(user=user,username=user.username,action='OPERATIONAL_DRAFT_CREATED',details={'provider_id':str(provider.pk),'operation_id':str(serializer.instance.pk),'kind':type(serializer.instance).__name__})
    @transaction.atomic
    def perform_update(self,serializer):
        user,provider=_context(self.request.user.pk,self.provider().pk)
        fresh=self.serializer_class.Meta.model.objects.select_for_update().filter(pk=serializer.instance.pk,provider_id=provider.pk,is_active=True).first()
        if fresh is None:raise ValidationError('La operación ya no está disponible.')
        checked=self.get_serializer(fresh,data=serializer.initial_data,partial=serializer.partial);checked.is_valid(raise_exception=True)
        serializer.instance=checked.save()
        AuditLog.objects.create(user=user,username=user.username,action='OPERATIONAL_DRAFT_UPDATED',details={'provider_id':str(provider.pk),'operation_id':str(fresh.pk),'kind':type(fresh).__name__})
    def destroy(self,request,*args,**kwargs):
        self.get_object();raise ValidationError('Conserva la historia operativa; usa cancelación o suspensión auditadas.')
    def transition(self,request):
        from .state_service import transition
        obj=self.get_object();fields={'nuevo_estado','estado_esperado','motivo','confirmado'}
        if not isinstance(request.data,dict) or set(request.data)!=fields:raise ValidationError('Revisa estado actual, destino, motivo y confirmación explícita.')
        return Response(transition(usuario_id=request.user.pk,provider_id=self.provider().pk,
            kind=type(obj).__name__,operation_id=obj.pk,expected_state=request.data['estado_esperado'],
            new_state=request.data['nuevo_estado'],reason=request.data['motivo'],confirmed=request.data['confirmado']))
    @action(detail=True,methods=['get'],url_path='historial-transiciones')
    @transaction.atomic
    def transition_history(self,request,pk=None):
        obj=self.get_object();_,provider=_context(request.user.pk,self.provider().pk)
        rows=list(AuditLog.objects.filter(details__provider_id=str(provider.pk),
            details__operation_id=str(obj.pk),details__kind=type(obj).__name__,
            action__in=['OPERATIONAL_STATE_CHANGED','OPERATIONAL_SST_BLOCK','OPERATIONAL_DISPATCH_RECORDED','OPERATIONAL_END_RECORDED'])
            .order_by('-timestamp','-pk')[:51])
        return Response({'provider_id':str(provider.pk),'operation_id':str(obj.pk),'read_only':True,
            'history':[{'id':str(row.pk),'actor_id':str(row.user_id),'known_at':row.timestamp.isoformat(),
                'previous_state':row.details.get('previous_state'),'new_state':row.details.get('new_state'),
                'action':row.action} for row in rows[:50]],'has_more':len(rows)>50,
            'clinical_content_returned':False,'service_started':False})

    @action(detail=True,methods=['get'],url_path='pre-despacho')
    def pre_dispatch(self,request,pk=None):
        from .state_service import diagnosis
        return Response(diagnosis(self.get_object()))

class OrdenOperativaViewSet(ScopedOperationalViewSet):
    serializer_class=OrdenOperativaSerializer
    def _dispatch_command(self,request,operation,fields):
        from . import dispatch_authorization
        from django.core.exceptions import ValidationError as ModelValidationError
        from apps.core_erp.accounting.exceptions import AccountingError
        obj=self.get_object()
        if not isinstance(request.data,dict) or set(request.data)!=fields:raise ValidationError('Contrato de revisión operativa inválido.')
        try:return Response(getattr(dispatch_authorization,operation)(actor_id=request.user.pk,provider_id=self.provider().pk,order_id=str(obj.pk),**request.data))
        except (ModelValidationError,AccountingError,ValueError,TypeError):raise ValidationError('Evidencia operativa inválida; no se habilitó ejecución por defecto.') from None
    @action(detail=True,methods=['post'],url_path='revisar-despacho')
    def review_dispatch(self,request,pk=None):return self._dispatch_command(request,'review_dispatch',{'confirmed'})
    @action(detail=True,methods=['post'],url_path='registrar-inicio')
    def apply_dispatch(self,request,pk=None):return self._dispatch_command(request,'apply_dispatch',{'review_id','confirmed'})
    @action(detail=True,methods=['post'],url_path='revisar-fin')
    def review_dispatch_end(self,request,pk=None):return self._dispatch_command(request,'review_end',{'actual_end','evidence_digest','confirmed'})
    @action(detail=True,methods=['post'],url_path='registrar-fin')
    def apply_dispatch_end(self,request,pk=None):return self._dispatch_command(request,'apply_end',{'review_id','confirmed'})
    @action(detail=True,methods=['post'],url_path='revocar-requisitos')
    def revoke_dispatch(self,request,pk=None):return self._dispatch_command(request,'revoke',{'attestation_id','confirmed'})
    @action(detail=True,methods=['get'],url_path='estado-despacho')
    def dispatch_state(self,request,pk=None):return self._dispatch_command(request,'dispatch_state',set())

    @action(detail=True,methods=['post'],url_path='cambiar-estado')
    def cambiar_estado(self,request,pk=None):return self.transition(request)

class ProcesoOperativoViewSet(ScopedOperationalViewSet):
    serializer_class=ProcesoOperativoSerializer
    @action(detail=True,methods=['post'])
    def avanzar_estado(self,request,pk=None):return self.transition(request)

class IncidenteOperativoViewSet(ScopedOperationalViewSet):serializer_class=IncidenteOperativoSerializer
class TareaOperativaViewSet(ScopedOperationalViewSet):serializer_class=TareaOperativaSerializer
