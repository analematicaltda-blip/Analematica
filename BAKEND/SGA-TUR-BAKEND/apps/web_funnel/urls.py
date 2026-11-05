
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    WebPageViewSet,
    SectionViewSet,
    ContentBlockViewSet,
    MediaAssetViewSet,
    PublicWebPageViewSet,
)

# Router para la API de administración
admin_router = DefaultRouter()
admin_router.register(r'pages', WebPageViewSet)
admin_router.register(r'sections', SectionViewSet)
admin_router.register(r'content-blocks', ContentBlockViewSet)
admin_router.register(r'media-assets', MediaAssetViewSet)

# Router para la API pública
public_router = DefaultRouter()
public_router.register(r'pages', PublicWebPageViewSet, basename='public-page')

urlpatterns = [
    path('admin/', include(admin_router.urls)),
    path('public/', include(public_router.urls)),
]
