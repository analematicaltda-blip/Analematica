from rest_framework import serializers
from .models import Document, DocumentVersion, Process, ProcessType, DocumentType
from api.models import CustomUser
from apps.companies.models import Company

# ==========================================================
# Serializers Anidados (para lectura)
# ==========================================================
class CompanyNestedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ['id', 'name', 'code']

class UserNestedSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username']

class ProcessNestedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Process
        fields = ['id', 'name', 'code']

class DocumentTypeNestedSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentType
        fields = ['id', 'name', 'code']

# ==========================================================
# Serializers de Versiones de Documento
# ==========================================================
class DocumentVersionSerializer(serializers.ModelSerializer):
    uploaded_by = UserNestedSerializer(read_only=True)
    class Meta:
        model = DocumentVersion
        fields = [
            'id', 'version_number', 'title', 'uploaded_at', 'uploaded_by',
            'status', 'file_hash_sha256', 'blockchain_transaction', 'blockchain_timestamp'
        ]

class DocumentVersionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentVersion
        fields = ['title', 'validity_year']

# ==========================================================
# Serializers de Documentos (Contenedores)
# ==========================================================
class DocumentListSerializer(serializers.ModelSerializer):
    process = ProcessNestedSerializer(read_only=True)
    latest_version = serializers.SerializerMethodField()

    class Meta:
        model = Document
        fields = ['id', 'document_code', 'process', 'latest_version']

    def get_latest_version(self, obj):
        latest = obj.versions.first()
        if latest:
            return DocumentVersionSerializer(latest).data
        return None

class DocumentDetailSerializer(serializers.ModelSerializer):
    process = ProcessNestedSerializer(read_only=True)
    document_type = DocumentTypeNestedSerializer(read_only=True)
    created_by = UserNestedSerializer(read_only=True)
    versions = DocumentVersionSerializer(many=True, read_only=True)

    class Meta:
        model = Document
        fields = [
            'id', 'document_code', 'created_at', 'process',
            'document_type', 'created_by', 'versions'
        ]

class DocumentCreateSerializer(serializers.ModelSerializer):
    process = serializers.PrimaryKeyRelatedField(queryset=Process.objects.all(), write_only=True)
    document_type = serializers.PrimaryKeyRelatedField(queryset=DocumentType.objects.all(), write_only=True)
    title = serializers.CharField(write_only=True, max_length=200)
    validity_year = serializers.IntegerField(write_only=True)

    class Meta:
        model = Document
        fields = ['process', 'document_type', 'title', 'validity_year']

    def validate(self, data):
        # Asegurarse de que los catálogos pertenezcan a la compañía del usuario
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            company = request.user.company
            if data['process'].company != company or data['document_type'].company != company:
                raise serializers.ValidationError("Los catálogos seleccionados no son válidos.")
        return data


# ==========================================================
# Serializers de Catálogos (Solo Lectura)
# ==========================================================
class ProcessTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProcessType
        fields = '__all__'

class ProcessSerializer(serializers.ModelSerializer):
    class Meta:
        model = Process
        fields = '__all__'

class DocumentTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentType
        fields = '__all__'
