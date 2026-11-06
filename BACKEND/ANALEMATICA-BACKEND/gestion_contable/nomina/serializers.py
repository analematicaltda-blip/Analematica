from rest_framework import serializers
from decimal import Decimal
from apps.admin_plataforma.gestion_contable.nomina.models import (
    Employee, EmploymentContract, PayrollRun, PayrollNews, PayrollConcept
)

class EmploymentContractSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmploymentContract
        fields = ['id', 'start_date', 'end_date', 'base_salary', 'position', 'is_active']

class EmployeeSerializer(serializers.ModelSerializer):
    contracts = EmploymentContractSerializer(many=True, read_only=True)

    class Meta:
        model = Employee
        fields = [
            'id', 'first_name', 'last_name', 'tax_id', 'birth_date',
            'address', 'phone', 'email', 'contracts'
        ]

class PayrollConceptSerializer(serializers.ModelSerializer):
    class Meta:
        model = PayrollConcept
        fields = ['id', 'code', 'name', 'description', 'type']

class PayrollNewsSerializer(serializers.ModelSerializer):
    concept_detail = PayrollConceptSerializer(source='concept', read_only=True)
    concept_id = serializers.PrimaryKeyRelatedField(
        queryset=PayrollConcept.objects.all(), source='concept', write_only=True
    )

    class Meta:
        model = PayrollNews
        fields = ['id', 'employee', 'concept_detail', 'concept_id', 'amount', 'description']

class PayrollRunSerializer(serializers.ModelSerializer):
    news = PayrollNewsSerializer(many=True, required=False)

    class Meta:
        model = PayrollRun
        fields = [
            'id', 'period_start', 'period_end', 'month', 'year',
            'total_earnings', 'total_deductions', 'net_total', 'news'
        ]
        read_only_fields = ('total_earnings', 'total_deductions', 'net_total')

    def create(self, validated_data):
        news_data = validated_data.pop('news', [])
        payroll_run = PayrollRun.objects.create(**validated_data)

        total_earnings = Decimal('0.00')
        total_deductions = Decimal('0.00')

        for n_data in news_data:
            news_item = PayrollNews.objects.create(payroll_run=payroll_run, **n_data)
            if news_item.concept.type == PayrollConcept.Type.EARNING:
                total_earnings += news_item.amount
            else:
                total_deductions += news_item.amount

        payroll_run.total_earnings = total_earnings
        payroll_run.total_deductions = total_deductions
        payroll_run.net_total = total_earnings - total_deductions
        payroll_run.save()

        return payroll_run
