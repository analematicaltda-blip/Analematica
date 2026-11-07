from rest_framework import serializers
from .models import Supplier, PurchaseInvoice

class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = ['id', 'name', 'tax_id', 'email', 'phone']

class PurchaseInvoiceSerializer(serializers.ModelSerializer):
    supplier_detail = SupplierSerializer(source='supplier', read_only=True)
    supplier_id = serializers.PrimaryKeyRelatedField(
        queryset=Supplier.objects.all(), source='supplier', write_only=True
    )

    class Meta:
        model = PurchaseInvoice
        fields = [
            'id', 'supplier_detail', 'supplier_id', 'number',
            'issue_date', 'due_date', 'status', 'total_amount', 'currency'
        ]
