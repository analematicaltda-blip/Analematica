from django.utils import timezone
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
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

class IsSSTOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # Permitir si es el dueño o si es superadmin
        if request.user.is_superuser: return True
        return str(obj.provider_id) == str(request.user.perfil_prestador.id)

class BaseSSTViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated, IsSSTOwner]
    def get_queryset(self):
        if self.request.user.is_superuser:
            return self.model.objects.all()
        return self.model.objects.filter(provider_id=self.request.user.perfil_prestador.id)

    def perform_create(self, serializer):
        serializer.save(provider_id=self.request.user.perfil_prestador.id)

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

class ActividadPlanSSTViewSet(viewsets.ModelViewSet):
    queryset = ActividadPlanSST.objects.all()
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

class DashboardSSTViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request):
        provider_id = request.user.perfil_prestador.id

        # Cálculo de cumplimiento real (N6 logic)
        plan_activo = PlanAnualSST.objects.filter(provider_id=provider_id, estado='ACTIVO').first()
        cumplimiento = 0
        if plan_activo:
            total_acts = plan_activo.actividades.count()
            completadas = plan_activo.actividades.filter(completada=True).count()
            cumplimiento = (completadas / total_acts * 100) if total_acts > 0 else 0

        return Response({
            "indicadores": IndicadorSSTSerializer(IndicadorSST.objects.filter(provider_id=provider_id), many=True).data,
            "alertas_activas": AlertaSSTSerializer(AlertaSST.objects.filter(provider_id=provider_id, leida=False), many=True).data,
            "resumen": {
                "incidentes_mes": IncidenteLaboral.objects.filter(provider_id=provider_id, fecha_hora__month=timezone.now().month).count(),
                "cumplimiento_plan": round(cumplimiento, 2)
            }
        })
