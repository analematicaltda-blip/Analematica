# Tests para validar la consistencia del contrato de la API
import yaml
from rest_framework.test import APITestCase
from django.urls import reverse

class ContractValidationTests(APITestCase):
    """
    Valida que el comportamiento real de la API se corresponda con los
    artefactos de contrato generados (OpenAPI).
    """

    def test_schema_conforms_to_expectations(self):
        """
        Verifica el esquema OpenAPI generado para asegurar que las reglas
        de negocio clave estén correctamente documentadas.
        """
        # Obtener el esquema generado en vivo
        response = self.client.get('/api/schema/')
        self.assertEqual(response.status_code, 200)

        # Cargar el esquema YAML a un diccionario de Python
        schema = yaml.safe_load(response.content)

        # --- VALIDACIONES CLAVE DEL CONTRATO ---

        # 1. El path de facturas-venta debe existir
        facturas_path = '/api/v1/mi-negocio/comercial/facturas-venta/'
        self.assertIn(facturas_path, schema['paths'], "El endpoint de facturas no está en el esquema.")

        # 2. El método POST debe requerir 'cliente_id' y 'number'
        post_operation = schema['paths'][facturas_path]['post']
        request_body_schema = post_operation['requestBody']['content']['application/json']['schema']
        component_name = request_body_schema['$ref'].split('/')[-1]
        write_serializer_schema = schema['components']['schemas'][component_name]

        self.assertIn('cliente_id', write_serializer_schema['required'])
        self.assertIn('number', write_serializer_schema['required'])

        # 3. El método POST NO debe permitir enviar 'total' (debe ser readOnly)
        self.assertTrue(
            write_serializer_schema['properties']['total']['readOnly'],
            "El campo 'total' no está marcado como readOnly en el contrato de escritura."
        )

        # 4. El modelo debe incluir el nuevo estado 'COMERCIAL_CONFIRMADA'
        response_schema = schema['paths'][facturas_path]['get']['responses']['200']['content']['application/json']['schema']

        # Resolver paginación si existe
        if '$ref' in response_schema:
            comp_name = response_schema['$ref'].split('/')[-1]
            response_schema = schema['components']['schemas'][comp_name]

        if 'properties' in response_schema and 'results' in response_schema['properties']:
            item_schema = response_schema['properties']['results']['items']
        else:
            item_schema = response_schema

        if '$ref' in item_schema:
            comp_name = item_schema['$ref'].split('/')[-1]
            factura_detail_properties = schema['components']['schemas'][comp_name]['properties']
        else:
            factura_detail_properties = item_schema['properties']

        print(f"DEBUG: estado schema: {factura_detail_properties['estado']}")

        estado_field = factura_detail_properties['estado']
        if 'allOf' in estado_field:
            estado_field = estado_field['allOf'][0]

        if '$ref' in estado_field:
            comp_name = estado_field['$ref'].split('/')[-1]
            estado_field = schema['components']['schemas'][comp_name]

        estado_enum = estado_field['enum']
        self.assertIn(
            'COMERCIAL_CONFIRMADA',
            estado_enum,
            "El nuevo estado 'COMERCIAL_CONFIRMADA' no está documentado en el enum del contrato."
        )

        print("\n--- Verificación de Contrato Automática: OK ---")
