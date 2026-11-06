from rest_framework import serializers
from .models import AssetCategory, FixedAsset, DepreciationCalculation

class AssetCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = AssetCategory
        fields = ['id', 'name', 'useful_life_months']

class FixedAssetSerializer(serializers.ModelSerializer):
    category_detail = AssetCategorySerializer(source='category', read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=AssetCategory.objects.all(), source='category', write_only=True
    )

    class Meta:
        model = FixedAsset
        fields = [
            'id', 'category_detail', 'category_id', 'name',
            'acquisition_date', 'acquisition_value', 'current_value'
        ]

class DepreciationCalculationSerializer(serializers.ModelSerializer):
    class Meta:
        model = DepreciationCalculation
        fields = ['id', 'asset', 'calculation_date', 'amount', 'accumulated_depreciation']
