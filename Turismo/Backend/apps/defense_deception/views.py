from rest_framework import viewsets, serializers
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from .models import GhostSurface, AdversarialProfile, DeceptionInteractionLog, DisuasionMetric

class GhostSurfaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = GhostSurface
        fields = '__all__'

class AdversarialProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdversarialProfile
        fields = '__all__'

class DisuasionMetricSerializer(serializers.ModelSerializer):
    class Meta:
        model = DisuasionMetric
        fields = '__all__'

class GhostSurfaceViewSet(viewsets.ModelViewSet):
    queryset = GhostSurface.objects.all()
    serializer_class = GhostSurfaceSerializer
    permission_classes = [IsAdminUser]

class AdversarialProfileViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AdversarialProfile.objects.all()
    serializer_class = AdversarialProfileSerializer
    permission_classes = [IsAdminUser]

class DisuasionStatsView(APIView):
    permission_classes = [IsAdminUser]
    serializer_class = DisuasionMetricSerializer
    def get(self, request):
        from .services import AdversarialProfilerService
        AdversarialProfilerService.update_global_metrics()
        metric = DisuasionMetric.objects.first()
        serializer = DisuasionMetricSerializer(metric)
        return Response(serializer.data)
