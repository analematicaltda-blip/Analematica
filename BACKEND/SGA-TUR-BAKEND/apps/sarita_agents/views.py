 
# backend/apps/sarita_agents/views.py
from django.db import transaction
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema
from django.db import models
from django.db.models import Count, Avg, F, ExpressionWrapper, DurationField, Q
from django.utils import timezone
from datetime import timedelta
from .models import Mision, PlanTáctico, TareaDelegada, MicroTarea, RegistroMicroTarea
from .serializers import MisionSerializer, DirectiveSerializer
from .orchestrator import sarita_orchestrator
from .tasks import ejecutar_mision_completa

class DirectiveView(APIView):
    """
    Recibe una directiva, crea una Misión y encola su ejecución asíncrona.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = DirectiveSerializer

    @extend_schema(
        request=DirectiveSerializer,
        responses={202: MisionSerializer}
    )
    def post(self, request, *args, **kwargs):
        serializer = DirectiveSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        validated_data = serializer.validated_data
        idempotency_key = validated_data.get('idempotency_key')

        try:
            # 1. Crear la Misión (esto también verifica la idempotencia)
            mision = sarita_orchestrator.start_mission(
                directive=validated_data,
                idempotency_key=idempotency_key
            )
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_409_CONFLICT)

        # 2. Encolar la ejecución de la misión DESPUÉS de que la transacción se confirme.
        transaction.on_commit(lambda: ejecutar_mision_completa.delay(mision_id=str(mision.id)))

        response_data = {
            "mission_id": mision.id,
            "status": mision.estado
        }
        return Response(response_data, status=status.HTTP_202_ACCEPTED)

class MissionStatusView(APIView):
    """
    Consulta el estado y la trazabilidad completa de una misión.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = MisionSerializer

    @extend_schema(responses={200: MisionSerializer})
    def get(self, request, id, *args, **kwargs):
        try:
            mision = Mision.objects.prefetch_related(
                'planes_tacticos',
                'planes_tacticos__tareas',
                'planes_tacticos__tareas__logs_ejecucion',
                'planes_tacticos__tareas__micro_tareas',
                'planes_tacticos__tareas__micro_tareas__logs'
            ).get(id=id)
            serializer = MisionSerializer(mision)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Mision.DoesNotExist:
            return Response(
                {"error": "Misión no encontrada."},
                status=status.HTTP_404_NOT_FOUND
            )

class ProductivityMetricsView(APIView):
    """
    Vista de alto rendimiento para métricas jerárquicas SARITA.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        # 1. Métricas de Soldados (Nivel 6)
        soldier_metrics = MicroTarea.objects.values('soldado_asignado').annotate(
            total=Count('id'),
            exitosas=Count('id', filter=Q(estado='COMPLETADA')),
            fallidas=Count('id', filter=Q(estado='FALLIDA')),
        )

        # 2. Métricas de Sargentos (Nivel 5)
        # Calculamos la eficiencia promedio de microtareas por tarea delegada
        sargento_metrics = TareaDelegada.objects.values('teniente_asignado').annotate(
            total_tareas=Count('id'),
            total_microtareas=Count('micro_tareas')
        ).annotate(
            avg_micro_per_tarea=ExpressionWrapper(F('total_microtareas') * 1.0 / F('total_tareas'), output_field=models.FloatField())
        )

        # 3. Métricas de Tenientes (Nivel 4)
        teniente_metrics = TareaDelegada.objects.values('teniente_asignado').annotate(
            total=Count('id'),
            exitosas=Count('id', filter=Q(estado='COMPLETADA')),
            tiempo_promedio=Avg(ExpressionWrapper(F('logs_ejecucion__timestamp') - F('timestamp_creacion'), output_field=DurationField()))
        )

        # 4. Métricas de Capitanes (Nivel 3)
        capitan_metrics = PlanTáctico.objects.values('capitan_responsable').annotate(
            total=Count('id'),
            exitosos=Count('id', filter=Q(estado='COMPLETADO')),
        )

        return Response({
            "timestamp": timezone.now(),
            "levels": {
                "soldados": soldier_metrics,
                "sargentos": sargento_metrics,
                "tenientes": teniente_metrics,
                "capitanes": capitan_metrics
            }
        })
 
