from django.utils import timezone
from django.db import models
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Sum, Avg, Count
from api.models import CustomUser
from apps.turismo.models.provider_models import TourismProvider, Reservation
from ..models import TourismDemandForecast, TourismSeasonality, TouristBehaviorProfile, TourismEconomicImpact, ConversationalIntent, ConversationalKPI
from .serializers import (
    TourismDemandForecastSerializer, TourismSeasonalitySerializer,
    TouristBehaviorProfileSerializer, TourismEconomicImpactSerializer,
    ConversationalIntentSerializer, ConversationalKPISerializer
)
from ..services import TourismIntelligenceService, DynamicPricingService

class IntelligenceViewSet(viewsets.ViewSet):
    """
    Controlador central de Inteligencia Turística.
    """
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['get'])
    def dashboard(self, request):
        """
        Dashboard unificado para Web, Mobile y Desktop.
        Consolida métricas de Vía 1, 2 y 3 con contexto territorial.
        """
        user = request.user
        periodo_actual = timezone.now().strftime("%Y-%m")

        # Contexto Territorial
        dept_id = request.query_params.get('department')
        mun_id = request.query_params.get('municipality')

        # Filtros base para analítica consolidada
        prov_filter = models.Q()
        if mun_id:
            prov_filter &= models.Q(municipality_id=mun_id)
        elif dept_id:
            prov_filter &= models.Q(department_id=dept_id)
        elif hasattr(user, 'profile'):
            if user.role in [CustomUser.Role.DIRECTIVO_DEPARTAMENTAL]:
                prov_filter &= models.Q(department=user.profile.department)
            elif user.role in [CustomUser.Role.DIRECTIVO_MUNICIPAL, CustomUser.Role.FUNCIONARIO_PROFESIONAL]:
                prov_filter &= models.Q(municipality=user.profile.municipality)

        # 1. Métricas de Vía 3 (Conversacional - Nacional por ahora)
        total_intents = ConversationalIntent.objects.count()
        sentiment_avg = ConversationalIntent.objects.aggregate(Avg('sentiment_score'))['sentiment_score__avg'] or 0.0

        # 2. Métricas de Vía 2 (Prestadores Filtrados)
        providers_qs = TourismProvider.objects.filter(prov_filter)
        total_providers = providers_qs.count()
        total_reservations = Reservation.objects.filter(provider__in=providers_qs).count()
        avg_score = providers_qs.aggregate(Avg('puntuacion_total'))['puntuacion_total__avg'] or 0

        # 3. Predicciones (Vía 1 / SADI)
        forecast = TourismDemandForecast.objects.filter(destino='Puerto Gaitán').order_by('-fecha').first()

        # 4. Estadísticas Económicas Reales
        economic_impact = TourismEconomicImpact.objects.order_by('-periodo').first()

        # 5. Consolidación Territorial (Solo para directivos)
        territorial_summary = []
        if not mun_id:
            group_by = 'municipality__name' if dept_id or user.role == CustomUser.Role.DIRECTIVO_DEPARTAMENTAL else 'department__name'
            territorial_summary = providers_qs.values(group_by).annotate(
                count=Count('id'),
                avg_score=Avg('puntuacion_total')
            ).order_by('-count')

        return Response({
            "status": "OPERATIONAL",
            "timestamp": timezone.now(),
            "territorial_context": {"dept": dept_id, "mun": mun_id},
            "via_3": {
                "total_interacciones": total_intents,
                "sentimiento_promedio": round(sentiment_avg, 2),
                "kpis_chat": ConversationalKPISerializer(ConversationalKPI.objects.filter(period=periodo_actual)[:5], many=True).data
            },
            "via_2": {
                "prestadores_activos": total_providers,
                "reservas_totales": total_reservations,
                "puntaje_promedio": round(avg_score, 1),
                "impacto_economico": TourismEconomicImpactSerializer(economic_impact).data if economic_impact else None,
                "consolidado_territorial": territorial_summary
            },
            "via_1": {
                "prediccion_demanda": TourismDemandForecastSerializer(forecast).data if forecast else None,
                "estado_gobernanza": "ESTABLE",
                "nodos_activos": total_providers # Basado en prestadores reales
            }
        })

    @action(detail=False, methods=['get'])
    def forecast(self, request):
        destino = request.query_params.get('destino', 'Puerto Gaitán')
        categoria = request.query_params.get('categoria', 'ACCOMMODATION')
        fecha = request.query_params.get('fecha', '2026-04-01')

        forecast = TourismIntelligenceService.predict_demand(destino, categoria, fecha)
        serializer = TourismDemandForecastSerializer(forecast)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='economic-impact')
    def economic_impact(self, request):
        destino = request.query_params.get('destino', 'Puerto Gaitán')
        periodo = request.query_params.get('periodo', '2026-Q1')

        impact = TourismIntelligenceService.generate_economic_report(destino, periodo)
        serializer = TourismEconomicImpactSerializer(impact)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='suggest-price')
    def suggest_price(self, request):
        service_id = request.query_params.get('service_id')
        if not service_id:
            return Response({"error": "service_id required"}, status=status.HTTP_400_BAD_REQUEST)

        suggestion = DynamicPricingService.get_suggested_price(service_id)
        return Response(suggestion)

class TouristBehaviorViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = TouristBehaviorProfile.objects.all()
    serializer_class = TouristBehaviorProfileSerializer
    permission_classes = [permissions.IsAdminUser]

class SeasonalityViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = TourismSeasonality.objects.all()
    serializer_class = TourismSeasonalitySerializer

class ConversationalIntentViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ConversationalIntent.objects.all().order_by('-created_at')
    serializer_class = ConversationalIntentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role in ['ADMIN_NACIONAL', 'ADMIN_DEPARTAMENTAL', 'ADMIN_MUNICIPAL']:
            return ConversationalIntent.objects.all()
        return ConversationalIntent.objects.filter(tourist=user)

class ConversationalKPIViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ConversationalKPI.objects.all().order_by('-period')
    serializer_class = ConversationalKPISerializer
    permission_classes = [permissions.IsAuthenticated]
