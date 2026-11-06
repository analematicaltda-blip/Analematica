from django.core.management.base import BaseCommand
from apps.core_erp.accounting.ledger_engine import LedgerEngine
from apps.companies.models import Company
import logging

class Command(BaseCommand):
    help = 'Certifica la integridad de la cadena de hashes del Ledger para todos los tenants.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.MIGRATE_HEADING("Iniciando Certificación de Ledger..."))

        tenants = Company.objects.all()
        total_errors = 0

        for tenant in tenants:
            self.stdout.write(f"Verificando integridad para: {tenant.name} ({tenant.id})")

            result = LedgerEngine.validate_ledger_integrity(str(tenant.id))

            if result['is_valid']:
                self.stdout.write(self.style.SUCCESS(f"  ✅ Integridad Certificada. {result['entries_count']} asientos verificados."))
            else:
                self.stdout.write(self.style.ERROR(f"  ❌ RUPTURA DE INTEGRIDAD DETECTADA."))
                for error in result['errors']:
                    self.stdout.write(self.style.WARNING(f"     - {error}"))
                total_errors += len(result['errors'])

        if total_errors == 0:
            self.stdout.write(self.style.SUCCESS("\nCertificación Global: EXITOSA. Todos los libros son consistentes."))
        else:
            self.stdout.write(self.style.ERROR(f"\nCertificación Global: FALLIDA. Se encontraron {total_errors} inconsistencias."))
            exit(1)
