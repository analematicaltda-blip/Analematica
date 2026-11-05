from django.db import models
from django.utils.translation import gettext_lazy as _
import uuid
from apps.core_erp.base_models import BaseErpModel

class GlobalLedgerEntry(BaseErpModel):
    """
    Registro inmutable de transacciones económicas globales (Fase 23.2).
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    transaction_hash = models.CharField(max_length=64, unique=True)
    source_jurisdiction = models.CharField(max_length=3)
    target_jurisdiction = models.CharField(max_length=3)

    amount = models.DecimalField(max_digits=25, decimal_places=4)
    currency = models.CharField(max_length=10)

    entry_type = models.CharField(max_length=50, help_text="IFRS/Local Mapping")
    payload_snapshot = models.JSONField(default=dict)

    is_settled = models.BooleanField(default=False)
    settlement_timestamp = models.DateTimeField(null=True, blank=True)

class SchemaRegistry(BaseErpModel):
    """
    Registro unificado de esquemas de datos regulatorios y contables (Fase 23.1).
    """
    schema_name = models.CharField(max_length=100)
    version = models.CharField(max_length=20)
    jurisdiction = models.CharField(max_length=3)

    schema_definition = models.JSONField()
    is_active = models.BooleanField(default=True)

class RegulatorySyncNode(BaseErpModel):
    """
    Motor de Sincronización Regulatoria (Fase 23.3).
    """
    jurisdiction = models.CharField(max_length=3)
    active_rules = models.JSONField(default=list)
    compliance_threshold = models.DecimalField(max_digits=5, decimal_places=4, default=0.95)

    last_sync = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=20, default='SYNCED')

class DigitalIdentity(BaseErpModel):
    """
    Identidad Digital Institucional y Trust Framework (Fase 23.5).
    """
    entity_name = models.CharField(max_length=255)
    identity_did = models.CharField(max_length=255, unique=True, help_text="Decentralized Identifier")

    certificate_hash = models.CharField(max_length=64)
    is_kyb_verified = models.BooleanField(default=False)

    permission_grid = models.JSONField(default=dict)

class DataFabricRegion(BaseErpModel):
    """
    Capa de Datos Distribuida (Fase 23.4).
    """
    region_name = models.CharField(max_length=50)
    provider = models.CharField(max_length=50)
    residency_status = models.CharField(max_length=50, help_text="Local/Global data residency Compliance")

    replication_factor = models.IntegerField(default=3)
    last_health_check = models.DateTimeField(null=True, blank=True)
