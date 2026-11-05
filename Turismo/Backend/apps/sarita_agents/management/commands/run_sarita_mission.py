# backend/apps/sarita_agents/management/commands/run_sarita_mission.py
import json
from django.core.management.base import BaseCommand, CommandError
from apps.sarita_agents.orchestrator import sarita_orchestrator

class Command(BaseCommand):
    help = 'Ejecuta una misión SARITA directamente a través del orquestador.'

    def add_arguments(self, parser):
        parser.add_argument(
            'directive_json',
            type=str,
            help='La directiva de la misión en formato JSON (string).'
        )

    def handle(self, *args, **options):
        directive_json_str = options['directive_json']

        try:
            directive = json.loads(directive_json_str)
        except json.JSONDecodeError:
            raise CommandError('Error: La directiva proporcionada no es un JSON válido.')

        self.stdout.write(self.style.SUCCESS('--- INICIANDO MISIÓN SARITA ---'))
        self.stdout.write(f"Directiva recibida: {json.dumps(directive, indent=2)}")
        self.stdout.write(self.style.SUCCESS('----------------------------------'))

        # Invocar al orquestador
        final_report = sarita_orchestrator.handle_directive(directive)

        self.stdout.write(self.style.SUCCESS('--- MISIÓN FINALIZADA ---'))
        self.stdout.write(f"Reporte final: {json.dumps(final_report, indent=2, ensure_ascii=False)}")
        self.stdout.write(self.style.SUCCESS('-------------------------'))
