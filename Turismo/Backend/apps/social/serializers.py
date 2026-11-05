from rest_framework import serializers
from .models import (
    SocialConversation,
    SocialConversationMember,
    SocialMessage,
    SocialAttachment,
    SocialProfilePreference,
    SocialGiftCatalog,
    SocialGiftTransaction,
    SocialProfileMedia,
)


class SocialAttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = SocialAttachment
        fields = [
            "id",
            "attachment_type",
            "file_url",
            "mime_type",
            "size_bytes",
            "uploaded_at",
        ]


class SocialMessageSerializer(serializers.ModelSerializer):
    attachments = SocialAttachmentSerializer(many=True, read_only=True)

    class Meta:
        model = SocialMessage
        fields = [
            "id",
            "conversation",
            "sender",
            "message_type",
            "content",
            "is_deleted",
            "created_at",
            "attachments",
        ]
        read_only_fields = ["sender", "created_at", "attachments"]


class SocialConversationMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = SocialConversationMember
        fields = ["id", "conversation", "user", "is_admin", "joined_at", "last_seen_at"]
        read_only_fields = ["joined_at"]


class SocialConversationSerializer(serializers.ModelSerializer):
    memberships = SocialConversationMemberSerializer(many=True, read_only=True)

    class Meta:
        model = SocialConversation
        fields = [
            "id",
            "conversation_type",
            "title",
            "entry_fee",
            "is_adult_only",
            "created_by",
            "created_at",
            "updated_at",
            "memberships",
        ]
        read_only_fields = ["created_by", "created_at", "updated_at", "memberships"]

    def validate(self, attrs):
        title = attrs.get("title")
        if not title or not str(title).strip():
            raise serializers.ValidationError({"title": "El título es obligatorio."})
        return attrs


class SocialProfileMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = SocialProfileMedia
        fields = ["id", "media_type", "media_url", "order", "created_at"]

class SocialProfilePreferenceSerializer(serializers.ModelSerializer):
    media_gallery = SocialProfileMediaSerializer(many=True, read_only=True)

    class Meta:
        model = SocialProfilePreference
        fields = [
            "id",
            "user",
            "bio",
            "interests",
            "preferred_languages",
            "preferred_destinations",
            "is_dating_active",
            "presentation_photo",
            "presentation_video",
            "media_gallery",
            "visibility_enabled",
            "updated_at",
        ]
        read_only_fields = ["user", "updated_at", "media_gallery"]

    def validate_interests(self, value):
        if not isinstance(value, list):
            raise serializers.ValidationError("Debe ser una lista.")
        return value

    def validate_preferred_languages(self, value):
        if not isinstance(value, list):
            raise serializers.ValidationError("Debe ser una lista.")
        return value

    def validate_preferred_destinations(self, value):
        if not isinstance(value, list):
            raise serializers.ValidationError("Debe ser una lista.")
        return value


class SocialGiftCatalogSerializer(serializers.ModelSerializer):
    class Meta:
        model = SocialGiftCatalog
        fields = ["id", "code", "name", "description", "price", "icon_url", "active"]


class SocialGiftTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = SocialGiftTransaction
        fields = [
            "id",
            "sender",
            "receiver",
            "gift",
            "conversation",
            "amount",
            "status",
            "external_reference",
            "created_at",
            "processed_at",
        ]
        read_only_fields = ["sender", "amount", "status", "created_at", "processed_at"]


class SendGiftSerializer(serializers.Serializer):
    receiver_id = serializers.UUIDField()
    gift_id = serializers.UUIDField()
    conversation_id = serializers.UUIDField(required=False)
