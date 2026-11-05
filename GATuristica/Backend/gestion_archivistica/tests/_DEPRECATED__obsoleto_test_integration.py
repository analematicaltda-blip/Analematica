# backend/apps/prestadores/mi_negocio/gestion_archivistica/tests/test_integration.py
import json
import hashlib
from decimal import Decimal
from django.test import TestCase
from django.contrib.auth import get_user_model

from apps.companies.models import Company
from api.models import ProviderProfile
from apps.prestadores.mi_negocio.gestion_operativa.modulos_genericos.clientes.models import Cliente
from apps.prestadores.mi_negocio.gestion_operativa.modulos_genericos.productos_servicios.models import Product
from apps.prestadores.mi_negocio.gestion_comercial.domain.models import OperacionComercial, ItemOperacionComercial, FacturaVenta
from apps.prestadores.mi_negocio.gestion_comercial.services import FacturacionService
from apps.prestadores.mi_negocio.gestion_contable.contabilidad.models import ChartOfAccount
from ..models import ProcessType, Process, DocumentType, Document

User = get_user_model()

class ArchivingIntegrationTest(TestCase):
    def setUp(self):
        # 1. Crear la infraestructura básica
        self.user = User.objects.create_user(username='test_integration', email='test@integracion.com', password='password')
        self.company = Company.objects.create(name='Empresa de Integración', code='INT')
        self.provider_profile = ProviderProfile.objects.create(usuario=self.user, company=self.company, nombre_comercial='Hotel de Prueba')

        # 2. Crear la taxonomía del SGA
        self.process_type = ProcessType.objects.create(company=self.company, name='Contabilidad', code='CONT')
        self.process = Process.objects.create(company=self.company, process_type=self.process_type, name='Facturación', code='FACT')
        self.doc_type = DocumentType.objects.create(company=self.company, name='Factura de Venta', code='FV')

        # 3. Crear cuentas contables necesarias
        ChartOfAccount.objects.create(perfil=self.provider_profile, code='1305', name='Cuentas por Cobrar')
        ChartOfAccount.objects.create(perfil=self.provider_profile, code='4135', name='Ingresos Operacionales')
        ChartOfAccount.objects.create(perfil=self.provider_profile, code='2408', name='IVA por Pagar')

        # 4. Crear datos para la operación comercial
        self.cliente = Cliente.objects.create(perfil=self.provider_profile, nombre='Cliente de Prueba')
        self.producto = Product.objects.create(
            provider=self.provider_profile,
            nombre='Servicio de Consultoría',
            tipo='SERVICIO',
            base_price=Decimal('1000.00')
        )

    def test_facturacion_flow_triggers_archiving(self):
        """
        Verifica que la ejecución del FacturacionService crea correctamente
        un registro de archivo y lo vincula a la factura.
        """
        # 1. Crear una OperacionComercial confirmada
        operacion = OperacionComercial.objects.create(
            perfil=self.provider_profile,
            cliente=self.cliente,
            estado=OperacionComercial.Estado.CONFIRMADA,
            creado_por=self.user,
            subtotal=Decimal('1000.00'),
            impuestos=Decimal('190.00'),
            total=Decimal('1190.00')
        )
        ItemOperacionComercial.objects.create(
            operacion=operacion,
            producto=self.producto,
            descripcion='Consultoría',
            cantidad=1,
            precio_unitario=Decimal('1000.00')
        )

        # 2. Ejecutar el servicio de facturación
        factura = FacturacionService.facturar_operacion_confirmada(operacion)

        # 3. VERIFICACIONES
        self.assertIsNotNone(factura)
        self.assertEqual(factura.estado, FacturaVenta.Estado.EMITIDA)

        # 3.1 Verificar que la factura está vinculada a un documento del SGA
        self.assertIsNotNone(factura.documento_archivistico)
        self.assertIsInstance(factura.documento_archivistico, Document)

        # 3.2 Verificar los detalles del documento archivado
        doc_archivado = factura.documento_archivistico
        self.assertEqual(doc_archivado.company, self.company)
        self.assertEqual(doc_archivado.document_type, self.doc_type)
        self.assertEqual(doc_archivado.document_code, f"FV-{factura.id}")

        # 3.3 Verificar que se creó la versión del documento
        self.assertEqual(doc_archivado.versions.count(), 1)
        doc_version = doc_archivado.versions.first()
        self.assertEqual(doc_version.version_number, 1)
        self.assertEqual(doc_version.status, 'PENDING_CONFIRMATION')

        # 3.4 Verificar el hash del contenido
        factura_content = {
            "number": factura.number,
            "cliente": factura.cliente.nombre,
            "total": str(factura.total),
            "cufe": factura.cufe
        }
        factura_bytes = json.dumps(factura_content, indent=2).encode('utf-8')
        expected_hash = hashlib.sha256(factura_bytes).hexdigest()

        self.assertEqual(doc_version.file_hash_sha256, expected_hash)

        print("\nPrueba de integración de archivado completada con éxito.")
