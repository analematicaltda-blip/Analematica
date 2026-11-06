from django.test import TestCase
from apps.prestadores.mi_negocio.gestion_operativa.modulos_genericos.perfil.models import ProviderProfile
from apps.prestadores.mi_negocio.gestion_contable.empresa.models import Sucursal
from apps.prestadores.mi_negocio.gestion_operativa.modulos_genericos.clientes.models import Cliente
from apps.prestadores.mi_negocio.gestion_operativa.modulos_genericos.inventario.models import InventoryItem
from apps.prestadores.mi_negocio.gestion_comercial.sales.services import SalesService
from apps.prestadores.mi_negocio.facturacion.models import Factura
from apps.core_erp.accounting.models import JournalEntry, FiscalPeriod, ChartOfAccounts
from apps.domain_business.operativa.models import ProviderProfile as DomainProviderProfile
from decimal import Decimal
import uuid

class SalesFlowSimulationTest(TestCase):
    """
    Simulación completa de flujo ERP Mi Negocio (Fase 2).
    """
    databases = {'default', 'wallet_db', 'delivery_db'}

    def setUp(self):
        # 1. Setup Infraestructura
        from api.models import CustomUser
        self.user = CustomUser.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="password123",
            role="PRESTADOR"
        )
        self.provider_domain = DomainProviderProfile.objects.create(
            user=self.user,
            commercial_name="Empresa Test",
            tenant_id=uuid.uuid4()
        )
        self.provider = ProviderProfile.objects.get(id=self.provider_domain.id)

        self.sucursal = Sucursal.objects.create(
            provider=self.provider,
            nombre="Sucursal Principal",
            direccion="Calle 123",
            tenant_id=self.provider_domain.tenant_id
        )

        self.customer = Cliente.objects.create(
            perfil=self.provider,
            nombre="Cliente VIP",
            email="vip@example.com"
        )

        # 2. Setup Contabilidad (Requerido por LedgerEngine)
        self.coa = ChartOfAccounts.objects.create(tenant_id=self.provider.id, name="COA")
        self.period = FiscalPeriod.objects.create(
            tenant_id=self.provider.id,
            period_start="2026-01-01",
            period_end="2026-12-31",
            status="open"
        )

        # 3. Setup Inventario
        self.item = InventoryItem.objects.create(
            provider=self.provider,
            nombre_item="Gaseosa 500ml",
            stock_actual=100,
            stock_minimo=10,
            unidad="unidades"
        )

    def test_full_sale_cycle(self):
        """
        Simula una venta y verifica impactos en Inventario, Facturación y Ledger.
        """
        items_data = [
            {
                'producto_id': uuid.uuid4(), # Referencia operativa
                'inventory_item_id': self.item.id,
                'cantidad': 5,
                'precio_unitario': 2000.00
            }
        ]

        # Ejecutar Venta
        venta = SalesService.process_sale(
            provider=self.provider,
            sucursal=self.sucursal,
            customer=self.customer,
            items_data=items_data,
            payment_method='EFECTIVO'
        )

        # 1. Verificar Venta
        self.assertEqual(venta.estado, 'CONFIRMADA')
        self.assertEqual(venta.total, Decimal('11900.00')) # 10000 + 19% IVA

        # 2. Verificar Inventario
        self.item.refresh_from_db()
        self.assertEqual(self.item.stock_actual, 95)
        self.assertEqual(self.item.movimientos.count(), 1)

        # 3. Verificar Facturación
        factura = Factura.objects.get(venta=venta)
        self.assertTrue(factura.numero_factura.startswith('FAC-2026'))
        self.assertIsNotNone(factura.cufe)

        # 4. Verificar Ledger (Impacto Contable)
        entries = JournalEntry.objects.filter(tenant_id=self.provider.id)
        self.assertEqual(entries.count(), 1)
        entry = entries.first()
        self.assertTrue(entry.is_posted)
        self.assertEqual(entry.lines.count(), 3) # Caja, Ingresos, IVA
