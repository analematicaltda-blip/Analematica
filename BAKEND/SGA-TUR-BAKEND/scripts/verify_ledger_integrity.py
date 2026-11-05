import os
import django
import sys

# Configurar entorno Django
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'puerto_gaitan_turismo.settings')
django.setup()

from apps.core_erp.accounting.ledger_engine import LedgerEngine
from apps.core_erp.tenancy.models import Tenant

def run_integrity_check():
    print("Iniciando Verificación de Integridad del Ledger Contable...")

    tenants = Tenant.objects.all()
    if not tenants.exists():
        print("No hay tenants registrados. Saltando verificación.")
        return

    all_passed = True
    for tenant in tenants:
        print(f"\nAuditando Tenant: {tenant.name} ({tenant.id})")
        result = LedgerEngine.validate_ledger_integrity(str(tenant.id))

        if result['is_valid']:
            print(f"  [OK] Integridad verificada. {result['entries_count']} asientos validados.")
        else:
            all_passed = False
            print(f"  [FAIL] Se encontraron errores de integridad:")
            for error in result['errors']:
                print(f"    - {error}")

    if all_passed:
        print("\n✅ CERTIFICACIÓN EXITOSA: La cadena de bloques contable es íntegra.")
    else:
        print("\n❌ ALERTA DE SEGURIDAD: Se detectaron rupturas en la integridad del ledger.")

if __name__ == "__main__":
    run_integrity_check()
