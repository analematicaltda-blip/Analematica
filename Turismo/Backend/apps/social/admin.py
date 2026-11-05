from django.contrib import admin
from .models import (
    SocialConversation,
    SocialConversationMember,
    SocialMessage,
    SocialAttachment,
    SocialProfilePreference,
    SocialGiftCatalog,
    SocialGiftTransaction,
)


@admin.register(SocialConversation)
class SocialConversationAdmin(admin.ModelAdmin):
    list_display = ("id", "conversation_type", "title", "created_by", "created_at", "updated_at")
    search_fields = ("title",)
    list_filter = ("conversation_type", "created_at")


@admin.register(SocialConversationMember)
class SocialConversationMemberAdmin(admin.ModelAdmin):
    list_display = ("id", "conversation", "user", "is_admin", "joined_at")
    search_fields = ("user__username",)
    list_filter = ("is_admin", "joined_at")


@admin.register(SocialMessage)
class SocialMessageAdmin(admin.ModelAdmin):
    list_display = ("id", "conversation", "sender", "message_type", "created_at", "is_deleted")
    search_fields = ("sender__username", "content")
    list_filter = ("message_type", "is_deleted", "created_at")


@admin.register(SocialAttachment)
class SocialAttachmentAdmin(admin.ModelAdmin):
    list_display = ("id", "message", "attachment_type", "mime_type", "size_bytes", "uploaded_at")
    list_filter = ("attachment_type", "uploaded_at")


@admin.register(SocialProfilePreference)
class SocialProfilePreferenceAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "visibility_enabled", "updated_at")
    search_fields = ("user__username",)
    list_filter = ("visibility_enabled",)


@admin.register(SocialGiftCatalog)
class SocialGiftCatalogAdmin(admin.ModelAdmin):
    list_display = ("id", "code", "name", "price", "active")
    search_fields = ("code", "name")
    list_filter = ("active",)


@admin.register(SocialGiftTransaction)
class SocialGiftTransactionAdmin(admin.ModelAdmin):
    list_display = ("id", "sender", "receiver", "gift", "amount", "status", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("sender__username", "receiver__username", "gift__name")
