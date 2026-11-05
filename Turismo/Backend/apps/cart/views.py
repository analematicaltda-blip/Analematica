
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Cart
from .serializers import CartSerializer
from .services import CartService

class CartViewSet(viewsets.GenericViewSet):
    """
    API endpoint para gestionar el carro de compras.
    La lógica de negocio está delegada a CartService.
    """
    queryset = Cart.objects.all()
    serializer_class = CartSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user)

    @action(detail=False, methods=['get'], url_path='view')
    def view_cart(self, request):
        """Obtiene el contenido del carro del usuario actual."""
        cart = CartService.get_or_create_cart(request.user)
        serializer = self.get_serializer(cart)
        return Response(serializer.data)

    @action(detail=False, methods=['post'], url_path='add-item')
    def add_item(self, request):
        """Añade un plan al carro o actualiza su cantidad."""
        plan_id = request.data.get('plan_id')
        quantity = int(request.data.get('quantity', 1))

        if not plan_id:
            return Response({'error': 'plan_id es requerido'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            cart = CartService.add_item_to_cart(
                user=request.user,
                plan_id=plan_id,
                quantity=quantity
            )
            serializer = self.get_serializer(cart)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['post'], url_path='remove-item')
    def remove_item(self, request):
        """Elimina un ítem del carro."""
        item_id = request.data.get('item_id')
        if not item_id:
            return Response({'error': 'item_id es requerido'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            cart = CartService.remove_item_from_cart(
                user=request.user,
                item_id=item_id
            )
            serializer = self.get_serializer(cart)
            return Response(serializer.data)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)
