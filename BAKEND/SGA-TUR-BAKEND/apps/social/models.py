import uuid
from django.conf import settings
from django.db import models
from django.utils import timezone


class SocialConversation(models.Model):
    class ConversationType(models.TextChoices):
        DIRECT = "direct", "Directo"
        GROUP = "group", "Grupo"
        PUBLIC_ROOM = "public_room", "Sala Pública (Video Cita)"
        PRIVATE_ROOM = "private_room", "Sala Privada (Video Cita)"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    conversation_type = models.CharField(max_length=20, choices=ConversationType.choices, default=ConversationType.DIRECT)
    title = models.CharField(max_length=255, blank=True)
    entry_fee = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, help_text="Tarifa de entrada para salas privadas.")
    is_adult_only = models.BooleanField(default=False, help_text="Restricción para mayores de 18 años.")
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="social_conversations_created",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through="SocialConversationMember",
        related_name="social_conversations",
    )

    class Meta:
        ordering = ["-updated_at"]

    def __str__(self):
        return self.title or f"Conversation {self.id}"


class SocialConversationMember(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    conversation = models.ForeignKey(SocialConversation, on_delete=models.CASCADE, related_name="memberships")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="social_memberships")
    is_admin = models.BooleanField(default=False)
    joined_at = models.DateTimeField(auto_now_add=True)
    last_seen_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ("conversation", "user")
        ordering = ["-joined_at"]

    def __str__(self):
        return f"{self.user_id} in {self.conversation_id}"


class SocialMessage(models.Model):
    class MessageType(models.TextChoices):
        TEXT = "text", "Texto"
        EMOJI = "emoji", "Emoji"
        FILE = "file", "Archivo"
        VOICE = "voice", "Voz"
        GIFT = "gift", "Regalo Económico"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    conversation = models.ForeignKey(SocialConversation, on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="social_messages_sent")
    message_type = models.CharField(max_length=20, choices=MessageType.choices, default=MessageType.TEXT)
    content = models.TextField(blank=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.message_type} by {self.sender_id}"


class SocialAttachment(models.Model):
    class AttachmentType(models.TextChoices):
        IMAGE = "image", "Imagen"
        VIDEO = "video", "Video"
        FILE = "file", "Archivo"
        AUDIO = "audio", "Audio"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    message = models.ForeignKey(SocialMessage, on_delete=models.CASCADE, related_name="attachments")
    attachment_type = models.CharField(max_length=20, choices=AttachmentType.choices, default=AttachmentType.FILE)
    file_url = models.URLField()
    mime_type = models.CharField(max_length=100, blank=True)
    size_bytes = models.PositiveBigIntegerField(default=0)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["uploaded_at"]

    def __str__(self):
        return f"{self.attachment_type} {self.id}"


class SocialProfilePreference(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="social_preference")
    bio = models.TextField(blank=True)
    interests = models.JSONField(default=list, blank=True)
    preferred_languages = models.JSONField(default=list, blank=True)
    preferred_destinations = models.JSONField(default=list, blank=True)

    # Dating Profile Enhancement
    is_dating_active = models.BooleanField(default=False)
    presentation_photo = models.URLField(blank=True, null=True, help_text="Foto principal de presentación.")
    presentation_video = models.URLField(blank=True, null=True, help_text="Video de presentación.")

    visibility_enabled = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Social Profile: {self.user.username}"


class SocialProfileMedia(models.Model):
    class MediaType(models.TextChoices):
        IMAGE = "image", "Imagen"
        VIDEO = "video", "Video"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    profile = models.ForeignKey(SocialProfilePreference, on_delete=models.CASCADE, related_name="media_gallery")
    media_type = models.CharField(max_length=20, choices=MediaType.choices)
    media_url = models.URLField()
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["order", "created_at"]


class SocialGiftCatalog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.SlugField(unique=True)
    name = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    icon_url = models.URLField(blank=True)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ["price"]

    def __str__(self):
        return f"{self.name} ({self.price})"


class SocialGiftTransaction(models.Model):
    class TransactionStatus(models.TextChoices):
        PENDING = "pending", "Pendiente"
        COMPLETED = "completed", "Completada"
        FAILED = "failed", "Fallida"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="social_gifts_sent")
    receiver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="social_gifts_received")
    gift = models.ForeignKey(SocialGiftCatalog, on_delete=models.PROTECT, related_name="transactions")
    conversation = models.ForeignKey(
        SocialConversation,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="gift_transactions",
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=20, choices=TransactionStatus.choices, default=TransactionStatus.PENDING)
    external_reference = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.sender_id} -> {self.receiver_id} ({self.amount})"
