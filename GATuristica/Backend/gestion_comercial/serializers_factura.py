from rest_framework import serializers
from .models.FacturaElectronica import FacturaElectronica

class FacturaSerializer(serializers.ModelSerializer):
    class Meta:
        model = FacturaElectronica
        fields = ['id', 'cufe', 'xml_content', 'pdf_url', 'estado_dian', 'fecha_envio_dian', 'prestador_email']

class FacturaPreviewSerializer(serializers.Serializer):
    cufe = serializers.CharField()
    pdf_url = serializers.URLField()
    total = serializers.DecimalField(max_digits=12, decimal_places=2)
