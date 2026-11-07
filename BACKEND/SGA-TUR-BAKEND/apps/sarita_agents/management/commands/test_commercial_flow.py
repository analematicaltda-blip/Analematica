# backend/apps/sarita_agents/management/commands/test_commercial_flow.py
from django.core.management.base import BaseCommand
from django.utils.module_loading import import_string
FacturacionService = import_string('apps.prestadores.mi_negocio.gestion_comercial.services.FacturacionService') # DECOUPLED
from api.models import CustomUser
from django.utils.module_loading import import_string
ProviderProfile = import_string('apps.prestadores.mi_negocio.gestion_operativa.modulos_genericos.perfil.models.ProviderProfile') # DECOUPLED
import uuid

class Command(BaseCommand):
    help = 'Prueba el flujo comercial gobernado por agentes'

    def handle(self, *args, **options):
        self.stdout.write("Iniciando prueba de flujo comercial...")

        # 1. Obtener un usuario prestador
        user = CustomUser.objects.filter(role='PRESTADOR').first()
        if not user:
            self.stdout.write(self.style.ERROR("No hay usuarios PRESTADOR."))
            return

        perfil = user.perfil_prestador
        cliente_id = uuid.uuid4() # Cliente ficticio

        items = [
            {'producto': uuid.uuid4(), 'cantidad': 2, 'precio_unitario': 150.00}
        ]

        # 2. Iniciar Intención
        self.stdout.write(f"Procesando intención para {user.username}...")
        operacion = FacturacionService.procesar_intencion_venta(
            perfil_id=perfil.id,
            cliente_id=cliente_id,
            items_data=items,
            usuario=user
        )

        self.stdout.write(self.style.SUCCESS(f"Operación Comercial {operacion.id} creada en estado {operacion.estado}"))
        self.stdout.write("Misión de contratación delegada al General SARITA.")
