from rest_framework import viewsets, permissions
from .models import WebPage, Section, ContentBlock, MediaAsset
from .serializers import (
    WebPageSerializer, WebPageDetailSerializer, SectionSerializer,
    ContentBlockSerializer, MediaAssetSerializer
)

# --- Vistas para el Panel de Administración ---

class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Permiso personalizado para permitir solo a los administradores crear/editar/eliminar,
    pero permitir a cualquiera leer.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_staff

class WebPageViewSet(viewsets.ModelViewSet):
    """
    API endpoint para que los administradores gestionen las páginas web.
    """
    queryset = WebPage.objects.all()
    serializer_class = WebPageSerializer
    permission_classes = [permissions.IsAdminUser]

class SectionViewSet(viewsets.ModelViewSet):
    """
    API endpoint para que los administradores gestionen las secciones de una página.
    """
    queryset = Section.objects.all()
    serializer_class = SectionSerializer
    permission_classes = [permissions.IsAdminUser]

class ContentBlockViewSet(viewsets.ModelViewSet):
    """
    API endpoint para que los administradores gestionen los bloques de contenido.
    """
    queryset = ContentBlock.objects.all()
    serializer_class = ContentBlockSerializer
    permission_classes = [permissions.IsAdminUser]

class MediaAssetViewSet(viewsets.ModelViewSet):
    """
    API endpoint para que los administradores gestionen los activos multimedia.
    """
    queryset = MediaAsset.objects.all()
    serializer_class = MediaAssetSerializer
    permission_classes = [permissions.IsAdminUser]


# --- Vistas para la API Pública ---

class PublicWebPageViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint público para obtener el contenido de una página por su slug.
    Solo muestra las páginas que están marcadas como 'is_published'.
    """
    queryset = WebPage.objects.filter(is_published=True)
    serializer_class = WebPageDetailSerializer
    lookup_field = 'slug'
    permission_classes = [permissions.AllowAny]
