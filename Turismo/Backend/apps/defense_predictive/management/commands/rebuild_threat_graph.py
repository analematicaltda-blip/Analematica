from django.core.management.base import BaseCommand
from apps.defense_predictive.services import ThreatGraphService

class Command(BaseCommand):
    help = 'S-2.1: Reconstruye el Grafo Vivo de Amenazas y exporta THREAT_GRAPH_STATE.json'

    def handle(self, *args, **options):
        self.stdout.write("PDE: Reconstruyendo Grafo de Amenazas...")
        state = ThreatGraphService.rebuild_graph()
        self.stdout.write(self.style.SUCCESS(f"Grafo reconstruido. Nodos: {state['summary']['total_surface']}"))
