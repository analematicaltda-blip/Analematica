# automation/serializers.py
from rest_framework import serializers
from .models import AgentPersona, Workflow, Node, Edge

class AgentPersonaSerializer(serializers.ModelSerializer):
    class Meta:
        model = AgentPersona
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'tenant']

class NodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Node
        fields = ['id', 'node_type', 'config_json']

class EdgeSerializer(serializers.ModelSerializer):
    source_node = serializers.PrimaryKeyRelatedField(read_only=True)
    target_node = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Edge
        fields = ['source_node', 'target_node']

class WorkflowDetailSerializer(serializers.ModelSerializer):
    nodes = NodeSerializer(many=True)
    edges = EdgeSerializer(many=True)

    class Meta:
        model = Workflow
        fields = ['id', 'name', 'is_active', 'nodes', 'edges']

class WorkflowCreateSerializer(serializers.ModelSerializer):
    nodes = serializers.ListField(child=serializers.DictField(), write_only=True)
    edges = serializers.ListField(child=serializers.DictField(), write_only=True)

    class Meta:
        model = Workflow
        fields = ['id', 'name', 'is_active', 'nodes', 'edges']

    def create(self, validated_data):
        nodes_data = validated_data.pop('nodes')
        edges_data = validated_data.pop('edges')
        workflow = Workflow.objects.create(**validated_data)

        node_map = {}
        for node_data in nodes_data:
            temp_id = node_data.pop('id', None)
            node = Node.objects.create(workflow=workflow, **node_data)
            if temp_id:
                node_map[temp_id] = node

        for edge_data in edges_data:
            source_node = node_map.get(edge_data['source_node'])
            target_node = node_map.get(edge_data['target_node'])
            if source_node and target_node:
                Edge.objects.create(workflow=workflow, source_node=source_node, target_node=target_node)

        return workflow
