from django.core.management.base import BaseCommand
from django.utils.module_loading import import_string
ProcesoOperativo = import_string('apps.prestadores.mi_negocio.gestion_operativa.models.ProcesoOperativo') # DECOUPLED
TareaOperativa = import_string('apps.prestadores.mi_negocio.gestion_operativa.models.TareaOperativa') # DECOUPLED
from api.models import CustomUser
from django.utils import timezone

class Command(BaseCommand):
    help = 'Seeds initial operational data'

    def handle(self, *args, **options):
        user = CustomUser.objects.filter(role='PRESTADOR').first()
        if not user:
            self.stdout.write(self.style.ERROR("No PRESTADOR found."))
            return

        perfil = user.perfil_prestador

        proc, _ = ProcesoOperativo.objects.get_or_create(
            provider=perfil,
            nombre="Ejecución Pack Llanero",
            defaults={
                "descripcion": "Operación de tour por el río y almuerzo.",
                "estado": "EN_EJECUCION",
                "inicio_real": timezone.now()
            }
        )

        TareaOperativa.objects.get_or_create(
            provider=perfil,
            proceso=proc,
            nombre="Preparación de Embarcación",
            defaults={
                "estado": "LISTO",
                "fecha_limite": timezone.now() + timezone.timedelta(hours=2)
            }
        )

        TareaOperativa.objects.get_or_create(
            provider=perfil,
            proceso=proc,
            nombre="Asignación de Guía",
            defaults={
                "estado": "EN_PROGRESO",
                "fecha_limite": timezone.now() + timezone.timedelta(hours=4)
            }
        )

        self.stdout.write(self.style.SUCCESS("Operational data seeded."))
