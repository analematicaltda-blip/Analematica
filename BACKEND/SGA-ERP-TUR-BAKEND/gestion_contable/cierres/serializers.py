from rest_framework import serializers
from .models import PeriodoContable

class PeriodoContableSerializer(serializers.ModelSerializer):
    class Meta:
        model = PeriodoContable
        fields = '__all__'
