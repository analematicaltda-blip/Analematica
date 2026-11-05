
import pytest
from decimal import Decimal
from django.core.exceptions import ValidationError
from django.test import TestCase
from unittest.mock import patch
from django.db.models import Sum

from api.models import CustomUser, ProviderProfile
from apps.companies.models import Company
from apps.prestadores.mi_negocio.gestion_operativa.modulos_genericos.clientes.models import Cliente
from apps.prestadores.mi_negocio.gestion_operativa.modulos_genericos.productos_servicios.models import Product
from apps.prestadores.mi_negocio.gestion_comercial.domain.models import OperacionComercial, FacturaVenta
from apps.prestadores.mi_negocio.gestion_contable.contabilidad.models import ChartOfAccount, JournalEntry, Transaction
from apps.prestadores.mi_negocio.gestion_comercial.services import FacturacionService
from apps.prestadores.mi_negocio.gestion_contable.services import FacturaVentaAccountingService

@pytest.mark.django_db
class ServiceIntegrationTests(TestCase):

    def setUp(self):
        self.user = CustomUser.objects.create_user(email='prestador_service@test.com', username='prestador_service', password='pw', role='PRESTADOR')
        self.company = Company.objects.create(name='Empresa Service', code='SERVICE')
        self.profile = ProviderProfile.objects.create(usuario=self.user, nombre_comercial='Negocio Service', company=self.company)
        self.cliente = Cliente.objects.create(perfil=self.profile, nombre='Cliente Service', email='cliente_s@test.com')
        self.producto = Product.objects.create(provider=self.profile, nombre='Producto Service', tipo=Product.Tipo.PRODUCTO, es_inventariable=False, base_price=100)

        # Cuentas Contables
        ChartOfAccount.objects.create(perfil=self.profile, code='1305', name='CXC', nature='DEBITO')
        ChartOfAccount.objects.create(perfil=self.profile, code='4135', name='Ingresos', nature='CREDITO')
        ChartOfAccount.objects.create(perfil=self.profile, code='2408', name='IVA', nature='CREDITO')

    def test_flujo_completo_con_llamada_a_servicio(self):
        """
        Prueba el flujo completo llamando a FacturacionService directamente.
        """
        # 1. Crear la OperacionComercial
        operacion = OperacionComercial.objects.create(
            perfil=self.profile,
            cliente=self.cliente,
            creado_por=self.user,
            subtotal=Decimal('200.00'),
            impuestos=Decimal('38.00'),
            total=Decimal('238.00')
        )
        operacion.items.create(producto=self.producto, descripcion="Test", cantidad=2, precio_unitario=Decimal('100.00'), subtotal=Decimal('200.00'))

        # 2. Llamar al servicio de facturación
        with patch('apps.prestadores.mi_negocio.gestion_comercial.dian_services.DianService.enviar_factura') as mock_dian:
            mock_dian.return_value = {"success": True, "cufe": "test-cufe"}
            factura = FacturacionService.facturar_operacion_confirmada(operacion)

        # 3. Validar los resultados
        operacion.refresh_from_db()
        self.assertEqual(operacion.estado, OperacionComercial.Estado.FACTURADA)

        self.assertIsNotNone(factura)
        self.assertEqual(factura.operacion, operacion)
        self.assertEqual(factura.estado, FacturaVenta.Estado.EMITIDA)
        self.assertEqual(factura.total, Decimal('238.00'))

        self.assertEqual(JournalEntry.objects.count(), 1)
        journal_entry = JournalEntry.objects.first()

        # Validar partida doble
        totals = journal_entry.transactions.aggregate(total_debit=Sum('debit'), total_credit=Sum('credit'))
        self.assertEqual(totals['total_debit'], totals['total_credit'])
        self.assertEqual(totals['total_debit'], Decimal('238.00'))

    def test_rollback_si_contabilidad_falla(self):
        """
        Verifica que si el servicio de contabilidad falla, la operación no se factura.
        """
        operacion = OperacionComercial.objects.create(perfil=self.profile, cliente=self.cliente, creado_por=self.user)

        with patch.object(FacturaVentaAccountingService, 'registrar_factura_venta', side_effect=ValidationError("Error contable simulado")):
            with self.assertRaises(ValidationError):
                FacturacionService.facturar_operacion_confirmada(operacion)

        operacion.refresh_from_db()
        self.assertEqual(operacion.estado, OperacionComercial.Estado.BORRADOR)
        self.assertEqual(FacturaVenta.objects.count(), 0)
        self.assertEqual(JournalEntry.objects.count(), 0)
