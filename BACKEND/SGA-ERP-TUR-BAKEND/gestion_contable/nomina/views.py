from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import (
    Empleado, Contrato, Planilla, ConceptoNomina, DetalleLiquidacion,
    NovedadNomina, IncapacidadLaboral, Ausencia, ProvisionNomina, IndicadorLaboral
)
from .serializers import *
from .services import NominaService
from django.db import transaction
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.authentication import JWTAuthentication
from apps.prestadores.mi_negocio.web_session import ErpSessionAuthentication
from apps.core_erp.accounting.http_privacy import PrivateAccountingResponseMixin
from apps.prestadores.mi_negocio.gestion_operativa.sg_sst.access import company_context


class IsNominaOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # Manejar diferentes tipos de objetos (Empleado, Planilla, etc.)
        profile_attr = 'perfil'
        if hasattr(obj, 'empleado'): profile_attr = 'empleado.perfil'

        target = obj
        for attr in profile_attr.split('.'):
            target = getattr(target, attr)

        return target == request.user.perfil_prestador

class BaseNominaViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated, IsNominaOwner]

    def perform_create(self, serializer):
        if hasattr(self.model, 'perfil'):
            serializer.save(perfil=self.request.user.perfil_prestador)
        else:
            serializer.save()

class EmpleadoViewSet(BaseNominaViewSet):
    model = Empleado
    serializer_class = EmpleadoSerializer
    def get_queryset(self):
        return Empleado.objects.filter(perfil=self.request.user.perfil_prestador)

class ContratoViewSet(BaseNominaViewSet):
    model = Contrato
    serializer_class = ContratoSerializer
    def get_queryset(self):
        return Contrato.objects.filter(empleado__perfil=self.request.user.perfil_prestador)

class PlanillaViewSet(PrivateAccountingResponseMixin, BaseNominaViewSet):
    authentication_classes = [JWTAuthentication, ErpSessionAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    model = Planilla
    serializer_class = PlanillaSerializer
    def get_queryset(self):
        provider = company_context(self.request)
        return Planilla.objects.filter(perfil_id=provider.pk).order_by('-periodo_fin', 'pk')

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['payroll_provider'] = company_context(self.request)
        return context

    @transaction.atomic
    def perform_create(self, serializer):
        provider = company_context(self.request, lock=True)
        serializer.save(perfil_id=provider.pk, estado='BORRADOR')

    @transaction.atomic
    def perform_update(self, serializer):
        company_context(self.request, lock=True)
        row = self.get_queryset().select_for_update().get(pk=serializer.instance.pk)
        if row.estado != 'BORRADOR' or row.asiento_contable_ref_id or row.orden_pago_ref_id:
            raise ValidationError('No se modifica una planilla con estado o efectos financieros previos.')
        serializer.save(perfil_id=row.perfil_id)

    @transaction.atomic
    def perform_destroy(self, instance):
        company_context(self.request, lock=True)
        row = self.get_queryset().select_for_update().get(pk=instance.pk)
        if row.estado != 'BORRADOR' or row.asiento_contable_ref_id or row.orden_pago_ref_id:
            raise ValidationError('No se elimina historia laboral o contable mediante esta ruta.')
        row.delete()

    @action(detail=True, methods=['post'])
    def liquidar(self, request, pk=None):
        planilla = self.get_object()
        NominaService.liquidar_periodo(planilla.pk, request.user.pk)

    @action(detail=True, methods=['post'])
    def contabilizar(self, request, pk=None):
        planilla = self.get_object()
        NominaService.contabilizar_nomina(planilla.pk, request.user.pk)

class ConceptoNominaViewSet(viewsets.ModelViewSet):
    queryset = ConceptoNomina.objects.all()
    serializer_class = ConceptoNominaSerializer
    permission_classes = [permissions.IsAuthenticated]

class NovedadNominaViewSet(BaseNominaViewSet):
    model = NovedadNomina
    serializer_class = NovedadNominaSerializer
    def get_queryset(self):
        return NovedadNomina.objects.filter(empleado__perfil=self.request.user.perfil_prestador)

class IncapacidadLaboralViewSet(BaseNominaViewSet):
    model = IncapacidadLaboral
    serializer_class = IncapacidadLaboralSerializer
    def get_queryset(self):
        return IncapacidadLaboral.objects.filter(empleado__perfil=self.request.user.perfil_prestador)

class AusenciaViewSet(BaseNominaViewSet):
    model = Ausencia
    serializer_class = AusenciaSerializer
    def get_queryset(self):
        return Ausencia.objects.filter(empleado__perfil=self.request.user.perfil_prestador)

class IndicadorLaboralViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = IndicadorLaboralSerializer
    permission_classes = [permissions.IsAuthenticated]
    def get_queryset(self):
        return IndicadorLaboral.objects.filter(perfil=self.request.user.perfil_prestador)

class DashboardNominaViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]
    def list(self, request):
        perfil = request.user.perfil_prestador

        # Hallazgo March 2026: Cálculo automático del próximo vencimiento
        proximo_vencimiento = None
        ultima_planilla = Planilla.objects.filter(perfil=perfil).order_by('-periodo_fin').first()

        if ultima_planilla:
            # Asumimos periodicidad mensual por defecto si no se especifica en el perfil
            from datetime import timedelta
            proximo_vencimiento = ultima_planilla.periodo_fin + timedelta(days=30)

        # Alerta de vencimientos de contratos fijos
        contrato_por_vencer = Contrato.objects.filter(
            empleado__perfil=perfil,
            activo=True,
            tipo_contrato='TERMINO_FIJO',
            fecha_fin__isnull=False
        ).order_by('fecha_fin').first()

        return Response({
            "total_empleados": Empleado.objects.filter(perfil=perfil, estado='ACTIVO').count(),
            "ultima_nomina": PlanillaSerializer(ultima_planilla).data if ultima_planilla else None,
            "indicadores": IndicadorLaboralSerializer(IndicadorLaboral.objects.filter(perfil=perfil), many=True).data,
            "proximo_vencimiento": proximo_vencimiento,
            "alerta_contrato": {
                "fecha": contrato_por_vencer.fecha_fin,
                "empleado": f"{contrato_por_vencer.empleado.nombre} {contrato_por_vencer.empleado.apellido}"
            } if contrato_por_vencer else None
        })
