from django.db import models
from apps.core_erp.base_models import BaseErpModel

class ReplicationLog(BaseErpModel):
    """
    EOS Infrastructure: Auditable record of multi-region replication events.
    """
    source_region = models.CharField(max_length=50)
    target_region = models.CharField(max_length=50)

    sync_status = models.CharField(max_length=20)
    records_synced = models.IntegerField()

    timestamp = models.DateTimeField(auto_now_add=True)

    __schema_version__ = "v2.1"

    class Meta:
        app_label = 'global_digital_infrastructure'

class BackupAudit(BaseErpModel):
    """
    Verification record for daily ledger and governance backups.
    """
    resource_type = models.CharField(max_length=100) # Ledger, Governance, IA Logs
    storage_path = models.CharField(max_length=512)

    integrity_hash = models.CharField(max_length=64)
    verified = models.BooleanField(default=False)

    timestamp = models.DateTimeField(auto_now_add=True)

    __schema_version__ = "v2.1"

    class Meta:
        app_label = 'global_digital_infrastructure'
