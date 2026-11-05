from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import (
    Empleado, Contrato, Planilla, ConceptoNomina, DetalleLiquidacion,
    NovedadNomina, IncapacidadLaboral, Ausencia, ProvisionNomina, IndicadorLaboral
)
from .serializers import *
from .services import NominaService

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

class PlanillaViewSet(BaseNominaViewSet):
    model = Planilla
    serializer_class = PlanillaSerializer
    def get_queryset(self):
        return Planilla.objects.filter(perfil=self.request.user.perfil_prestador)

    @action(detail=True, methods=['post'])
    def liquidar(self, request, pk=None):
        try:
            planilla = NominaService.liquidar_periodo(pk, request.user.id)
            return Response(PlanillaSerializer(planilla).data)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def contabilizar(self, request, pk=None):
        try:
            asiento = NominaService.contabilizar_nomina(pk, request.user.id)
            return Response({"status": "SUCCESS", "asiento_id": str(asiento.id)})
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

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
