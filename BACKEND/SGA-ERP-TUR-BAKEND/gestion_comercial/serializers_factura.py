from rest_framework import serializers
from .models.FacturaElectronica import FacturaElectronica

class FacturaSerializer(serializers.ModelSerializer):
    fiscal_acceptance_verified=serializers.SerializerMethodField()

    def get_fiscal_acceptance_verified(self,obj):
        # Existing state strings are historical declarations, not verified acuses.
        return False

    class Meta:
        model = FacturaElectronica
        fields = ['id', 'cufe', 'estado_dian', 'fecha_envio_dian', 'prestador_email', 'fiscal_acceptance_verified']

class FacturaPreviewSerializer(serializers.Serializer):
    cufe = serializers.CharField()
    pdf_url = serializers.URLField()
    total = serializers.DecimalField(max_digits=12, decimal_places=2)
