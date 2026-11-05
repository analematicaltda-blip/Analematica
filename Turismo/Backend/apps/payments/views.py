
from rest_framework import viewsets, status, permissions, serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from .models import Payment
from .serializers import PaymentSerializer, InitiatePaymentSerializer
from .services import PaymentService
from apps.cart.models import Cart

class PaymentViewSet(viewsets.GenericViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Payment.objects.filter(user=self.request.user)

    @action(detail=False, methods=['post'], url_path='init')
    def initiate_payment(self, request):
        serializer = InitiatePaymentSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            cart = Cart.objects.get(user=request.user)
        except Cart.DoesNotExist:
            return Response({'error': 'No se encontró un carro para este usuario.'}, status=status.HTTP_404_NOT_FOUND)

        provider = serializer.validated_data['provider']

        try:
            payment = PaymentService.initiate_payment(cart=cart, provider=provider)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        response_serializer = self.get_serializer(payment)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['get'], url_path='status')
    def get_status(self, request, pk=None):
        try:
            payment = self.get_object()
            return Response({'status': payment.status})
        except Payment.DoesNotExist:
            return Response({'error': 'Pago no encontrado.'}, status=status.HTTP_404_NOT_FOUND)

class PaymentWebhookViewSet(viewsets.ViewSet):
    permission_classes = [permissions.AllowAny]

    @extend_schema(responses={200: serializers.JSONField()})
    @action(detail=False, methods=['post'], url_path='confirm')
    def confirm_payment(self, request):
        transaction_id = request.data.get('transaction_id')
        if not transaction_id:
            return Response({'error': 'transaction_id es requerido'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            PaymentService.confirm_payment(transaction_id)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)

        return Response(status=status.HTTP_200_OK)
