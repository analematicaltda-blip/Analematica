from rest_framework import serializers
from apps.admin_plataforma.gestion_archivistica.models import Document, DocumentVersion, Process, ProcessType, DocumentType

class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = '__all__'
        read_only_fields = ['provider']

class AdminProcessSerializer(serializers.ModelSerializer):
    class Meta:
        model = Process
        fields = '__all__'
        read_only_fields = ['provider']
