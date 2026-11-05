from rest_framework import serializers
from .models import Project, ProjectIncome, ProjectCost

class ProjectIncomeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectIncome
        fields = ['id', 'project', 'date', 'amount', 'description']

class ProjectCostSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectCost
        fields = ['id', 'project', 'date', 'amount', 'description', 'category']

class ProjectSerializer(serializers.ModelSerializer):
    incomes = ProjectIncomeSerializer(many=True, read_only=True)
    costs = ProjectCostSerializer(many=True, read_only=True)

    class Meta:
        model = Project
        fields = [
            'id', 'name', 'description', 'start_date', 'end_date',
            'budget_allocated', 'status', 'incomes', 'costs'
        ]
