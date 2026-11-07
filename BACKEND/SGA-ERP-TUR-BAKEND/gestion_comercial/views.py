from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .domain.models import OperacionComercial
from apps.prestadores.mi_negocio.gestion_operativa.modulos_genericos.clientes.models import Cliente
from .serializers import OperacionSerializer, ClienteSerializer
from rest_framework.views import APIView
from django.db.models import Sum

class OperacionComercialViewSet(viewsets.ModelViewSet):
    queryset = OperacionComercial.objects.all()
    serializer_class = OperacionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['estado', 'tipo_operacion', 'fecha']

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(perfil_ref_id=self.request.tenant.id)

    @action(detail=False)
    def stats(self, request):
        total_ventas = self.get_queryset().filter(tipo_operacion='VENTA').aggregate(total=Sum('total'))['total'] or 0
        return Response({'total_ventas': total_ventas})

class ClienteViewSet(viewsets.ModelViewSet):
    queryset = Cliente.objects.all()
    serializer_class = ClienteSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return super().get_queryset().filter(perfil_ref_id=self.request.tenant.id)

class POSView(APIView):
    def post(self, request):
        # Quick sale
        data = request.data
        op = OperacionComercial.objects.create(
            perfil_ref_id=request.tenant.id,
            tipo_operacion='VENTA_RAPIDA',
            total=data['total'],
            cliente_id=data.get('cliente_id'),
            estado='COMPLETADA'
        )
        return Response({'id': op.id, 'factura': f'FAC-{op.id}'})

