# backend/apps/core_erp/management/commands/certify_system.py
import json
from django.core.management.base import BaseCommand
from apps.core_erp.integrity.system_integrity_certifier import SystemIntegrityCertifier

class Command(BaseCommand):
    help = 'Ejecuta la Certificación de Integridad Total del Sistema (Fase 7).'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('Iniciando proceso de certificación SARITA EOS...'))

        certifier = SystemIntegrityCertifier()
        report = certifier.run_full_certification()

        level = report["certification_level"]
        score = report["integrity_score"]

        if level == 'A':
            color = self.style.SUCCESS
        elif level in ['B', 'C']:
            color = self.style.WARNING
        else:
            color = self.style.ERROR

        self.stdout.write("\n" + "="*50)
        self.stdout.write(f"ID DE CERTIFICACIÓN: {report['certification_id']}")
        self.stdout.write(f"NIVEL ALCANZADO: {color(level)}")
        self.stdout.write(f"SCORE DE INTEGRIDAD: {score}/100")
        self.stdout.write("="*50 + "\n")

        if level == 'A':
            self.stdout.write(self.style.SUCCESS("SYSTEM INTEGRITY: VERIFIED"))
        else:
            self.stdout.write(self.style.ERROR("SYSTEM INTEGRITY: BREACHED"))
            self.stdout.write(f"Verifique 'system_integrity_report.json' para detalles de las {len(report['components'])} auditorías.")

        self.stdout.write(f"\nResultado final: {report['verdict']}")
