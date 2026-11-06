from rest_framework import serializers
from .models import Budget, BudgetItem, BudgetExecution

class BudgetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Budget
        fields = [
            'id', 'name', 'fiscal_year',
            'total_estimated_income', 'total_estimated_expenses', 'is_active'
        ]

class BudgetItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = BudgetItem
        fields = ['id', 'budget', 'account_code', 'type', 'estimated_amount', 'executed_amount']

class BudgetExecutionSerializer(serializers.ModelSerializer):
    class Meta:
        model = BudgetExecution
        fields = ['id', 'item', 'date', 'amount', 'description', 'reference_id']
