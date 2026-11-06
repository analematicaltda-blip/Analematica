from django.core.management.base import BaseCommand
from django.apps import apps

class Command(BaseCommand):
    help = 'Seed demo comercial data'

    def handle(self, *args, **options):
        Cliente = apps.get_model('prestadores.mi_negocio.gestion_comercial.domain', 'Cliente')
        Producto = apps.get_model('prestadores.mi_negocio.gestion_comercial.domain', 'Producto')
        OperacionComercial = apps.get_model('prestadores.mi_negocio.gestion_comercial.domain', 'OperacionComercial')

        # Demo data
        cliente = Cliente.objects.create(perfil_ref_id='demo-tenant', nombre='Turista Demo', email='demo@test.com')
        producto = Producto.objects.create(perfil_ref_id='demo-tenant', nombre='Tour Cascada', precio=50000, stock=10)

        op = OperacionComercial.objects.create(
            perfil_ref_id='demo-tenant',
            tipo_operacion='VENTA',
            total=50000,
            estado='COMPLETADA',
            cliente=cliente
        )

        self.stdout.write(self.style.SUCCESS('Demo comercial seeded'))

