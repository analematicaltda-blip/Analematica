from rest_framework import serializers
from .models import AgentExecution
from api.serializers import CustomUserDetailSerializer

class AgentExecutionCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating a new agent execution.
    Only the 'objective' is required from the user.
    """
    class Meta:
        model = AgentExecution
        fields = ['objective']


class AgentExecutionSerializer(serializers.ModelSerializer):
    """
    Serializer for retrieving agent execution details.
    Provides a read-only, comprehensive view of the execution.
    """
    user = CustomUserDetailSerializer(read_only=True)

    class Meta:
        model = AgentExecution
        fields = [
            'id',
            'user',
            'objective',
            'plan',
            'execution_history',
            'logs',
            'final_result',
            'status',
            'created_at',
            'updated_at',
        ]
        read_only_fields = fields
