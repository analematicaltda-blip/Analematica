from rest_framework import viewsets, permissions, serializers, response
from rest_framework.decorators import action
from .models import MaturityDomain, MaturityMetric, MaturitySnapshot
from .maturity.maturity_evaluator import MaturityEvaluator

class MaturityDomainSerializer(serializers.ModelSerializer):
    class Meta:
        model = MaturityDomain
        fields = '__all__'

class MaturityMetricSerializer(serializers.ModelSerializer):
    class Meta:
        model = MaturityMetric
        fields = '__all__'

class MaturitySnapshotSerializer(serializers.ModelSerializer):
    class Meta:
        model = MaturitySnapshot
        fields = '__all__'

class MaturityViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Provides access to the SARITA Maturity Matrix and Self-Reporting Engine.
    """
    queryset = MaturitySnapshot.objects.all()
    serializer_class = MaturitySnapshotSerializer
    permission_classes = [permissions.IsAdminUser]

    @action(detail=False, methods=['post'])
    def trigger_evaluation(self, request):
        """
        Force a self-evaluation cycle and return the new snapshot.
        """
        evaluator = MaturityEvaluator()
        snapshot = evaluator.generate_full_snapshot()
        serializer = self.get_serializer(snapshot)
        return response.Response(serializer.data)

    @action(detail=False, methods=['get'])
    def latest_radar(self, request):
        """
        Returns the data formatted for a Radar Chart in the Super Admin dashboard.
        """
        latest = MaturitySnapshot.objects.order_by('-timestamp').first()
        if not latest:
            return response.Response({"error": "No snapshots available"}, status=404)

        # Format for Radar Chart: { "Domain": score }
        radar_data = {domain: data["overall"] for domain, data in latest.domain_breakdown.items()}
        return response.Response(radar_data)
