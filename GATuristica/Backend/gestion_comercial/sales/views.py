from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from .models import Opportunity
from .serializers import OpportunitySerializer

class OpportunityViewSet(viewsets.ModelViewSet):
    queryset = Opportunity.objects.all()
    serializer_class = OpportunitySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Opportunity.objects.filter(tenant=self.request.user.tenant)

    def perform_create(self, serializer):
        serializer.save(tenant=self.request.user.tenant, assigned_to=self.request.user)

    @action(detail=True, methods=['put'], url_path='move')
    def move_opportunity(self, request, pk=None):
        opportunity = self.get_object()
        new_stage = request.data.get('stage')

        if not new_stage:
            return Response({"error": "El campo 'stage' es requerido."}, status=status.HTTP_400_BAD_REQUEST)

        # Simplemente actualizamos la oportunidad
        opportunity.stage = new_stage
        opportunity.save()

        return Response(self.get_serializer(opportunity).data, status=status.HTTP_200_OK)
