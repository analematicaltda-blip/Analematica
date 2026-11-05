# marketing/serializers.py
from rest_framework import serializers
from .models import Campaign, CampaignChannel, MarketingContent

class MarketingContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = MarketingContent
        fields = ['subject', 'body_text', 'body_html']

class CampaignChannelSerializer(serializers.ModelSerializer):
    class Meta:
        model = CampaignChannel
        fields = ['channel_type', 'is_active']

class CampaignSerializer(serializers.ModelSerializer):
    channels = CampaignChannelSerializer(many=True, required=False)
    content = MarketingContentSerializer(required=False)

    class Meta:
        model = Campaign
        fields = ['id', 'name', 'status', 'created_at', 'channels', 'content']
        read_only_fields = ['id', 'status', 'created_at']

    def create(self, validated_data):
        channels_data = validated_data.pop('channels', [])
        content_data = validated_data.pop('content', None)

        campaign = Campaign.objects.create(**validated_data)

        if content_data:
            MarketingContent.objects.create(campaign=campaign, **content_data)

        for channel_data in channels_data:
            CampaignChannel.objects.create(campaign=campaign, **channel_data)

        return campaign
