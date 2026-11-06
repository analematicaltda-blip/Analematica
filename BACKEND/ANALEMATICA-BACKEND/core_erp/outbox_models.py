from django.db import models
import uuid

class OutboxEvent(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    event_type = models.CharField(max_length=100, db_index=True)
    domain = models.CharField(max_length=100, db_index=True)
    aggregate_root = models.CharField(max_length=100)
    payload = models.JSONField()
    version = models.IntegerField(default=1)
    status = models.CharField(max_length=20, default='PENDING') # PENDING, PROCESSED, ERROR
    created_at = models.DateTimeField(auto_now_add=True)
    published_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        app_label = 'core_erp'


class EventAuditLog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    event_type = models.CharField(max_length=100, db_index=True)
    correlation_id = models.CharField(max_length=100, db_index=True, null=True, blank=True)
    tenant_id = models.CharField(max_length=100, db_index=True, null=True, blank=True)
    payload = models.JSONField()
    status = models.CharField(max_length=20, default='EMITTED') # EMITTED, PROCESSED, PARTIAL_FAILURE, QUEUED_COMPLETED
    severity = models.CharField(max_length=20, default='info') # info, warning, critical, fatal
    retry_count = models.IntegerField(default=0)
    error_details = models.TextField(null=True, blank=True)
    # Phase 3.12: Cryptographic Chaining for Audit Logs
    previous_hash = models.CharField(max_length=64, null=True, blank=True)
    integrity_hash = models.CharField(max_length=64, null=True, blank=True, db_index=True)

    timestamp = models.DateTimeField(auto_now_add=True)

    def compute_integrity_hash(self):
        import hashlib
        import json
        content = {
            "id": str(self.id),
            "event_type": self.event_type,
            "correlation_id": self.correlation_id,
            "payload": self.payload,
            "previous_hash": self.previous_hash or ""
        }
        content_str = json.dumps(content, sort_keys=True)
        return hashlib.sha256(content_str.encode()).hexdigest()

    def save(self, *args, **kwargs):
        if not self.integrity_hash:
            last_log = EventAuditLog.objects.order_by('-timestamp', '-id').first()
            if last_log:
                self.previous_hash = last_log.integrity_hash
            else:
                self.previous_hash = "AUDIT_GENESIS"
            self.integrity_hash = self.compute_integrity_hash()
        super().save(*args, **kwargs)

    class Meta:
        app_label = 'core_erp'
        ordering = ['-timestamp']
