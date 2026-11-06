from django.test import TestCase
from django.contrib.auth import get_user_model
from decimal import Decimal
import datetime

from apps.prestadores.mi_negocio.gestion_operativa.modulos_genericos.perfil.models import ProviderProfile
from apps.company.models import Company, CompanyEncryptionKey
from apps.prestadores.mi_negocio.gestion_comercial.domain.models import OperacionComercial, ItemOperacionComercial
from apps.prestadores.mi_negocio.gestion_comercial.services import FacturacionService
from apps.prestadores.mi_negocio.gestion_contable.contabilidad.models import ChartOfAccount, JournalEntry
from apps.prestadores.mi_negocio.gestion_operativa.modulos_genericos.clientes.models import Cliente
from apps.prestadores.mi_negocio.gestion_operativa.modulos_genericos.productos_servicios.models import Product
from ..cierres.models import PeriodoContable
from django.urls import reverse
from rest_framework.test import APITestCase

User = get_user_model()

class ContabilidadIntegrationTest(APITestCase):
    def setUp(self):
        self.company = Company.objects.create(name="Test Co", code="TC02")
        self.user = User.objects.create_user('prestador2@test.com', 'password', role='PRESTADOR')
        self.profile = ProviderProfile.objects.create(usuario=self.user, company=self.company)
        self.client.force_authenticate(user=self.user)

        # Crear cuentas contables básicas
        ChartOfAccount.objects.create(perfil=self.profile, code='1305', name='CXC')
        ChartOfAccount.objects.create(perfil=self.profile, code='4135', name='Ingresos')
        ChartOfAccount.objects.create(perfil=self.profile, code='2408', name='IVA')

    def test_venta_genera_asiento_contable_balanceado(self):
        """Verifica que al confirmar una venta se crea un asiento contable y está balanceado."""
        cliente = Cliente.objects.create(perfil=self.profile, nombre='Cliente de Prueba')
        producto = Product.objects.create(provider=self.profile, nombre='Servicio de Consultoría', precio=Decimal('1000.00'))

        operacion = OperacionComercial.objects.create(
            perfil=self.profile,
            cliente=cliente,
            subtotal=Decimal('1000.00'),
            total=Decimal('1190.00'),
            impuestos=Decimal('190.00'),
            creado_por=self.user
        )
        ItemOperacionComercial.objects.create(operacion=operacion, producto=producto, cantidad=1, precio_unitario=Decimal('1000.00'))

        # Actuar: Confirmar la operación
        FacturacionService.facturar_operacion_confirmada(operacion)

        # Afirmar: Verificar que el asiento contable se creó
        self.assertTrue(JournalEntry.objects.filter(perfil=self.profile).exists())
        journal_entry = JournalEntry.objects.get(perfil=self.profile)

        # Afirmar: Verificar que el asiento está balanceado
        self.assertGreater(journal_entry.total_debits, 0)
        self.assertEqual(journal_entry.total_debits, journal_entry.total_credits)
        self.assertEqual(journal_entry.total_credits, operacion.total)

    def test_reporte_falla_si_periodo_esta_abierto(self):
        """Verifica que el endpoint de reporte devuelve un error si el período no está cerrado."""
        periodo = PeriodoContable.objects.create(
            perfil=self.profile,
            nombre="Enero 2024 Abierto",
            fecha_inicio=datetime.date(2024, 1, 1),
            fecha_fin=datetime.date(2024, 1, 31),
            estado=PeriodoContable.Estado.ABIERTO
        )
        url = reverse('balance-general') + f'?periodo_id={periodo.id}'

        response = self.client.get(url)

        self.assertEqual(response.status_code, 400)
        self.assertIn("debe estar cerrado", response.data['error'])
