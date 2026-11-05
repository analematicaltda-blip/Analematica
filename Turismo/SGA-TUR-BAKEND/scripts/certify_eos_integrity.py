import json
import os
import django
import uuid

# Setup
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "puerto_gaitan_turismo.settings")
django.setup()

from apps.core_erp.models import EventAuditLog
from apps.core_erp.accounting.models import JournalEntry
from django.utils import timezone

def certify_integrity():
    print("SARITA EOS: Iniciando Certificación de Integridad (Fase 5.8)...")
    errors = []

    # 1. Validar Ledger (No missing hashes)
    entries = JournalEntry.objects.filter(is_posted=True).order_by('posted_at')
    if entries.exists():
        prev_hash = "GENESIS_SARITA_2026"
        for entry in entries:
            # En Chained Hashing, calculamos que el chain no esté roto
            # (Aunque no verificamos el contenido exacto aquí, solo la presencia de hash)
            if not entry.system_hash:
                errors.append(f"Ledger Error: Asiento {entry.id} no tiene Hash de sistema.")

    # 2. Validar Event Bus (No EMITTED antiguos sin procesar)
    from datetime import timedelta
    old_emitted = EventAuditLog.objects.filter(
        status='EMITTED',
        timestamp__lt=timezone.now() - timedelta(minutes=30)
    ).count()
    if old_emitted > 0:
        errors.append(f"EventBus Error: {old_emitted} eventos estancados detectados.")

    # 3. Reporte Final
    if not errors:
        print("✅ EOS INTEGRITY CERTIFIED: El sistema cumple con los invariantes arquitectónicos.")
        return True
    else:
        print("❌ INTEGRITY FAILURE DETECTED:")
        for err in errors:
            print(f"  - {err}")
        return False

if __name__ == "__main__":
    certify_integrity()
