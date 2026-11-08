from rest_framework_simplejwt.authentication import JWTAuthentication
from ....web_session import ErpSessionAuthentication
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Product
from .serializers import ProductSerializer
from ....company_scope import owned_provider
import uuid

class ProductViewSet(viewsets.ModelViewSet):
    authentication_classes=[JWTAuthentication,ErpSessionAuthentication]
    queryset=Product.objects.all()
    serializer_class=ProductSerializer
    permission_classes=[IsAuthenticated]

    def get_provider(self):return owned_provider(self.request)

    def get_queryset(self):
        return self.queryset.filter(provider_id=self.get_provider().pk)

    def perform_create(self,serializer):
        from ..perfil.models import ProviderProfile
        serializer.save(provider=ProviderProfile.objects.get(pk=self.get_provider().pk),id_publico=uuid.uuid4())
