import hashlib
import json
import sys
from apps.core_erp.outbox_models import EventAuditLog
from apps.core_erp.accounting.ledger_engine import LedgerEngine

def verify_system_integrity():
    print("🛡️ INICIANDO AUDITORÍA CRIPTOGRÁFICA SARITA v1.0")

    # 1. Verificar EventAuditLog (Omnisciencia)
    print("\n--- Verificando EventAuditLog (Outbox Chain) ---")
    logs = EventAuditLog.objects.all().order_by('timestamp', 'id')
    previous_hash = "AUDIT_GENESIS"
    audit_errors = 0

    for log in logs:
        if log.previous_hash != previous_hash:
            print(f"❌ Ruptura en Audit Log {log.id}. Esperado: {previous_hash}, Real: {log.previous_hash}")
            audit_errors += 1

        # Recalcular hash de integridad
        content = {
            "id": str(log.id),
            "event_type": log.event_type,
            "correlation_id": log.correlation_id,
            "payload": log.payload,
            "previous_hash": log.previous_hash or ""
        }
        recalculated = hashlib.sha256(json.dumps(content, sort_keys=True).encode()).hexdigest()

        if log.integrity_hash != recalculated:
            print(f"❌ Hash inválido en Audit Log {log.id}. Posible alteración de datos.")
            audit_errors += 1

        previous_hash = log.integrity_hash

    if audit_errors == 0:
        print("✅ Cadena de auditoría de eventos íntegra.")
    else:
        print(f"⚠️ Se detectaron {audit_errors} errores en la cadena de auditoría.")

    # 2. Verificar Ledger (Journal Entries)
    print("\n--- Verificando Ledger Criptográfico (Financial Chain) ---")
    # Este proceso es por tenant
    from apps.core_erp.tenancy.models import Tenant
    tenants = Tenant.plain_objects.all()

    for tenant in tenants:
        print(f"Auditando Tenant: {tenant.name} ({tenant.id})")
        res = LedgerEngine.validate_ledger_integrity(str(tenant.id))
        if res['is_valid']:
            print(f"  ✅ Ledger íntegro ({res['entries_count']} asientos).")
        else:
            print(f"  ❌ Fallo de integridad en Ledger. Errores: {res['errors']}")

    print("\n🏁 AUDITORÍA FINALIZADA.")

if __name__ == "__main__":
    verify_system_integrity()
