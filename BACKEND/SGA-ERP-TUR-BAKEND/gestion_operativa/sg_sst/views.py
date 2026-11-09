from django.utils import timezone
from rest_framework import viewsets, permissions
from rest_framework.response import Response
from .models import (
    MatrizRiesgo, IncidenteLaboral, SaludOcupacional, CapacitacionSST,
    PlanAnualSST, ActividadPlanSST, InspeccionSST, IndicadorSST, AlertaSST
)
from .serializers import (
    MatrizRiesgoSerializer, IncidenteLaboralSerializer, SaludOcupacionalSerializer,
    CapacitacionSSTSerializer, PlanAnualSSTSerializer, ActividadPlanSSTSerializer,
    InspeccionSSTSerializer, IndicadorSSTSerializer, AlertaSSTSerializer
)

from django.db import transaction
from rest_framework_simplejwt.authentication import JWTAuthentication
from apps.prestadores.mi_negocio.web_session import ErpSessionAuthentication
from apps.core_erp.accounting.http_privacy import PrivateAccountingResponseMixin
from .access import company_context, require_clinical_permission

class BaseSSTViewSet(PrivateAccountingResponseMixin, viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication, ErpSessionAuthentication]
    scope_field = 'provider_id'

    def get_queryset(self):
        provider = company_context(self.request)
        return self.model.objects.filter(**{self.scope_field: provider.pk}).order_by('pk')

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['sst_provider'] = company_context(self.request)
        return context

    def check_clinical(self):
        if self.model is SaludOcupacional:
            require_clinical_permission(self.request.user, self.action)

    def initial(self, request, *args, **kwargs):
        super().initial(request, *args, **kwargs)
        company_context(request)
        self.check_clinical()

    @transaction.atomic
    def perform_create(self, serializer):
        provider = company_context(self.request, lock=True)
        self.check_clinical()
        if self.model is ActividadPlanSST:
            plan = serializer.validated_data['plan']
            if not PlanAnualSST.objects.filter(pk=plan.pk, provider_id=provider.pk).exists():
                from rest_framework.exceptions import PermissionDenied
                raise PermissionDenied('Plan ajeno a la empresa.')
            serializer.save()
        else:
            serializer.save(provider_id=provider.pk)

    @transaction.atomic
    def perform_update(self, serializer):
        provider = company_context(self.request, lock=True)
        self.check_clinical()
        if not self.get_queryset().filter(pk=serializer.instance.pk).exists():
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied('El registro ya no pertenece a la empresa.')
        if self.model is ActividadPlanSST:
            plan = serializer.validated_data.get('plan', serializer.instance.plan)
            if not PlanAnualSST.objects.filter(pk=plan.pk, provider_id=provider.pk).exists():
                from rest_framework.exceptions import PermissionDenied
                raise PermissionDenied('Plan ajeno a la empresa.')
            serializer.save()
        else:
            serializer.save(provider_id=provider.pk)

    @transaction.atomic
    def perform_destroy(self, instance):
        company_context(self.request, lock=True)
        self.check_clinical()
        self.get_queryset().get(pk=instance.pk).delete()

class MatrizRiesgoViewSet(BaseSSTViewSet):
    model = MatrizRiesgo
    serializer_class = MatrizRiesgoSerializer

class IncidenteLaboralViewSet(BaseSSTViewSet):
    model = IncidenteLaboral
    serializer_class = IncidenteLaboralSerializer

class SaludOcupacionalViewSet(BaseSSTViewSet):
    model = SaludOcupacional
    serializer_class = SaludOcupacionalSerializer

class CapacitacionSSTViewSet(BaseSSTViewSet):
    model = CapacitacionSST
    serializer_class = CapacitacionSSTSerializer

class PlanAnualSSTViewSet(BaseSSTViewSet):
    model = PlanAnualSST
    serializer_class = PlanAnualSSTSerializer

class ActividadPlanSSTViewSet(BaseSSTViewSet):
    model = ActividadPlanSST
    scope_field = 'plan__provider_id'
    serializer_class = ActividadPlanSSTSerializer
    permission_classes = [permissions.IsAuthenticated]

class InspeccionSSTViewSet(BaseSSTViewSet):
    model = InspeccionSST
    serializer_class = InspeccionSSTSerializer

class IndicadorSSTViewSet(BaseSSTViewSet):
    model = IndicadorSST
    serializer_class = IndicadorSSTSerializer

class AlertaSSTViewSet(BaseSSTViewSet):
    model = AlertaSST
    serializer_class = AlertaSSTSerializer

class DashboardSSTViewSet(PrivateAccountingResponseMixin, viewsets.ViewSet):
    authentication_classes = [JWTAuthentication, ErpSessionAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request):
        from .services import SSTService
        provider = company_context(request)
        today = timezone.localdate()
        observations = SSTService.calcular_indicadores(provider.pk, today.strftime('%Y-%m'))
        return Response({
            'indicadores': [],
            'indicadores_historicos_no_verificados': IndicadorSST.objects.filter(provider_id=provider.pk).count(),
            'metricas_observadas': observations,
            'alertas_activas': AlertaSSTSerializer(AlertaSST.objects.filter(provider_id=provider.pk, leida=False).order_by('-fecha_generacion')[:100], many=True).data,
            'resumen': {'incidentes_mes': observations['incidentes_periodo'],
                        'cumplimiento_plan': observations['cumplimiento_plan']},
        })
