
import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from api.models import CustomUser, ProviderProfile
from apps.companies.models import Company
from apps.prestadores.mi_negocio.gestion_operativa.modulos_genericos.clientes.models import Cliente
from apps.prestadores.mi_negocio.gestion_operativa.modulos_genericos.productos_servicios.models import Product
from apps.prestadores.mi_negocio.gestion_contable.inventario.models import Almacen, MovimientoInventario
from apps.prestadores.mi_negocio.gestion_contable.contabilidad.models import ChartOfAccount

@pytest.mark.django_db
class FacturacionIntegracionTests(APITestCase):
    def setUp(self):
        # Crear usuario y perfil de prestador
        self.user = CustomUser.objects.create_user(email='prestador3@test.com', password='password123', role='PRESTADOR', username='prestador_test_3')
        self.company = Company.objects.create(name='Empresa de Prueba 3', code='T03')
        self.profile = ProviderProfile.objects.create(usuario=self.user, nombre_comercial='Negocio de Prueba 3', company=self.company)
        self.client.force_authenticate(user=self.user)

        # Crear datos maestros
        self.cliente = Cliente.objects.create(perfil=self.profile, nombre='Cliente de Prueba', email='cliente@test.com')
        self.almacen = Almacen.objects.create(perfil=self.profile, nombre='Almacén Principal')

        # Crear cuentas contables requeridas por el ViewSet
        self.cuenta_ingresos = ChartOfAccount.objects.create(
            perfil=self.profile, code='4135', name='Ingresos Operacionales', nature=ChartOfAccount.Nature.CREDIT
        )
        self.cuenta_cxc = ChartOfAccount.objects.create(
            perfil=self.profile, code='1305', name='Cuentas por Cobrar Clientes', nature=ChartOfAccount.Nature.DEBIT
        )

        # Crear producto de servicio (no inventariable)
        self.servicio = Product.objects.create(
            provider=self.profile,
            nombre='Consulta de Negocios',
            tipo=Product.Tipo.SERVICIO,
            es_inventariable=False,
            base_price=100000
        )

        # Crear producto físico (inventariable)
        self.producto_inv = Product.objects.create(
            provider=self.profile,
            nombre='Producto Físico',
            tipo=Product.Tipo.PRODUCTO,
            es_inventariable=True,
            base_price=50000,
            stock=10
        )

    def test_factura_con_servicio_no_mueve_inventario(self):
        """
        Verifica que al facturar un servicio, NO se crea un movimiento de inventario.
        """
        url = reverse('mi_negocio:factura-venta-list')
        data = {
            'cliente_id': self.cliente.id,
            'number': 'FV-001',
            'issue_date': '2024-01-01',
            'items': [
                {
                    'producto_id': self.servicio.id,
                    'descripcion': 'Servicio de consultoría',
                    'cantidad': 1,
                    'precio_unitario': 100000,
                }
            ]
        }

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Verificar que NO se ha creado ningún movimiento de salida
        movimientos_salida = MovimientoInventario.objects.filter(
            producto=self.servicio,
            tipo_movimiento=MovimientoInventario.TipoMovimiento.SALIDA
        )
        self.assertEqual(movimientos_salida.count(), 0)

    def test_factura_con_producto_inventariable_descuenta_stock(self):
        """
        Verifica que al facturar un producto inventariable, se crea un movimiento
        de inventario de SALIDA y se descuenta el stock.
        """
        url = reverse('mi_negocio:factura-venta-list')
        data = {
            'cliente_id': self.cliente.id,
            'number': 'FV-002',
            'issue_date': '2024-01-02',
            'items': [
                {
                    'producto_id': self.producto_inv.id,
                    'descripcion': 'Venta de producto físico',
                    'cantidad': 3,
                    'precio_unitario': 50000,
                }
            ]
        }

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Verificar que SÍ se ha creado un movimiento de salida
        movimiento_salida = MovimientoInventario.objects.filter(
            producto=self.producto_inv,
            tipo_movimiento=MovimientoInventario.TipoMovimiento.SALIDA
        ).first()
        self.assertIsNotNone(movimiento_salida)
        self.assertEqual(movimiento_salida.cantidad, 3)

        # Verificar que el stock del producto se ha actualizado correctamente
        self.producto_inv.refresh_from_db()
        self.assertEqual(self.producto_inv.stock, 7) # Stock inicial 10 - 3 = 7

    def test_factura_mixta_maneja_inventario_correctamente(self):
        """
        Verifica que una factura con un servicio y un producto inventariable
        solo crea movimiento de inventario para el producto.
        """
        url = reverse('mi_negocio:factura-venta-list')
        data = {
            'cliente_id': self.cliente.id,
            'number': 'FV-003',
            'issue_date': '2024-01-03',
            'items': [
                {
                    'producto_id': self.servicio.id,
                    'descripcion': 'Servicio de consultoría',
                    'cantidad': 2,
                    'precio_unitario': 100000,
                },
                {
                    'producto_id': self.producto_inv.id,
                    'descripcion': 'Venta de producto físico',
                    'cantidad': 5,
                    'precio_unitario': 50000,
                }
            ]
        }

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Verificar que NO hay movimiento de salida para el servicio
        movimientos_salida_servicio = MovimientoInventario.objects.filter(
            producto=self.servicio,
            tipo_movimiento=MovimientoInventario.TipoMovimiento.SALIDA
        )
        self.assertEqual(movimientos_salida_servicio.count(), 0)

        # Verificar que SÍ hay un movimiento de salida para el producto
        movimiento_salida_producto = MovimientoInventario.objects.filter(
            producto=self.producto_inv,
            tipo_movimiento=MovimientoInventario.TipoMovimiento.SALIDA
        ).first()
        self.assertIsNotNone(movimiento_salida_producto)
        self.assertEqual(movimiento_salida_producto.cantidad, 5)

    def test_crear_factura_sin_stock_suficiente_falla(self):
        """
        Verifica que la creación de una factura falle con un error 400 si
        se intenta vender más stock del disponible para un producto inventariable.
        """
        # Stock inicial es 10. Intentamos vender 11.
        url = reverse('mi_negocio:factura-venta-list')
        data = {
            'cliente_id': self.cliente.id,
            'number': 'FV-004',
            'issue_date': '2024-01-04',
            'items': [
                {
                    'producto_id': self.producto_inv.id,
                    'descripcion': 'Intento de venta sin stock',
                    'cantidad': 11,
                    'precio_unitario': 50000,
                }
            ]
        }

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('STOCK_INSUFICIENTE', str(response.data))

        # Verificar que el stock no cambió
        self.producto_inv.refresh_from_db()
        self.assertEqual(self.producto_inv.stock, 10)
