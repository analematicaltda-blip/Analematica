from rest_framework import serializers
from .domain.models import (
    CapitalStructure,
    DebtInstrument,
    EquityInstrument,
    MarketRating,
    StructuredDeal
)

class CapitalStructureSerializer(serializers.ModelSerializer):
    class Meta:
        model = CapitalStructure
        fields = '__all__'

class DebtInstrumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = DebtInstrument
        fields = '__all__'

class EquityInstrumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = EquityInstrument
        fields = '__all__'

class MarketRatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = MarketRating
        fields = '__all__'

class StructuredDealSerializer(serializers.ModelSerializer):
    class Meta:
        model = StructuredDeal
        fields = '__all__'
