
from rest_framework import serializers
from .models import WebPage, Section, ContentBlock, MediaAsset

class MediaAssetSerializer(serializers.ModelSerializer):
    class Meta:
        model = MediaAsset
        fields = ['id', 'nombre', 'archivo', 'tipo', 'uploaded_at']

class ContentBlockSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContentBlock
        fields = ['id', 'section', 'content_type', 'content', 'link', 'order']

class SectionSerializer(serializers.ModelSerializer):
    content_blocks = ContentBlockSerializer(many=True, read_only=True)

    class Meta:
        model = Section
        fields = ['id', 'web_page', 'title', 'order', 'content_blocks']

class WebPageSerializer(serializers.ModelSerializer):
    sections = SectionSerializer(many=True, read_only=True)

    class Meta:
        model = WebPage
        fields = ['id', 'title', 'slug', 'is_published', 'sections']

class WebPageDetailSerializer(WebPageSerializer):
    """Serializer para el detalle de una página, incluye el contenido completo."""
    sections = SectionSerializer(many=True, read_only=True)

    class Meta(WebPageSerializer.Meta):
        fields = WebPageSerializer.Meta.fields
