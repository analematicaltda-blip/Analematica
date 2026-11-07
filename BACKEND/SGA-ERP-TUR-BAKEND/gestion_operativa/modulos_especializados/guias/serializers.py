from rest_framework import serializers
from .models import Skill, TourDetail

class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = ['id', 'nombre', 'skill_type']

class TourDetailSerializer(serializers.ModelSerializer):
    required_skills = serializers.PrimaryKeyRelatedField(
        queryset=Skill.objects.all(),
        many=True,
        required=False
    )

    class Meta:
        model = TourDetail
        fields = ['required_skills'] # Y otros campos como duration, difficulty, etc.
