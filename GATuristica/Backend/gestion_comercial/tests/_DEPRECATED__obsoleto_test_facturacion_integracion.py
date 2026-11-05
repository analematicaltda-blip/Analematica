from django.test import TestCase
from django.contrib.auth import get_user_model
from decimal import Decimal

from apps.prestadores.mi_negocio.gestion_operativa.modulos_genericos.perfil.models import ProviderProfile
from apps.company.models import Company
from apps.prestadores.mi_negocio.gestion_comercial.domain.models import OperacionComercial, ItemOperacionComercial
from apps.prestadores.mi_negocio.gestion_comercial.services import FacturacionService
from apps.prestadores.mi_negocio.gestion_operativa.modulos_genericos.productos_servicios.models import Product
from apps.prestadores.mi_negocio.gestion_operativa.modulos_genericos.clientes.models import Cliente

User = get_user_model()

class FacturacionIntegracionTest(TestCase):
    def setUp(self):
        self.company = Company.objects.create(name="Test Co", code="TC03")
        self.user = User.objects.create_user('prestador3@test.com', 'password')
        self.profile = ProviderProfile.objects.create(usuario=self.user, company=self.company)
        self.cliente = Cliente.objects.create(perfil=self.profile, nombre='Cliente Test')
        self.producto_inventariable = Product.objects.create(
            provider=self.profile,
            nombre='Producto Inventariable',
            precio=Decimal('100.00'),
            es_inventariable=True,
            stock=10
        )

    def test_facturacion_reduce_stock(self):
        """Verifica que al facturar un producto inventariable, el stock se reduce."""
        operacion = OperacionComercial.objects.create(
            perfil=self.profile,
            cliente=self.cliente,
            total=Decimal('200.00'),
            creado_por=self.user
        )
        ItemOperacionComercial.objects.create(operacion=operacion, producto=self.producto_inventariable, cantidad=2, precio_unitario=Decimal('100.00'))

        FacturacionService.facturar_operacion_confirmada(operacion)

        self.producto_inventariable.refresh_from_db()
        self.assertEqual(self.producto_inventariable.stock, 8)
