from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from api.models import CustomUser
from apps.prestadores.mi_negocio.gestion_operativa.modulos_genericos.perfil.models import CategoriaPrestador, Perfil
# from apps.prestadores.mi_negocio.gestion_operativa.modulos_genericos.productos_servicios.models import ProductoServicio
from apps.prestadores.mi_negocio.gestion_operativa.modulos_genericos.clientes.models import Cliente
# from apps.prestadores.mi_negocio.gestion_operativa.modulos_genericos.reservas.models import Reserva
# from apps.prestadores.mi_negocio.gestion_operativa.modulos_genericos.costos.models import Costo
# from apps.prestadores.mi_negocio.gestion_operativa.modulos_genericos.inventario.models import Inventario
# from apps.prestadores.mi_negocio.gestion_operativa.modulos_genericos.rat.models import RegistroActividadTuristica
# from apps.prestadores.mi_negocio.gestion_operativa.modulos_genericos.soporte.models import TicketSoporte
# from apps.prestadores.mi_negocio.gestion_operativa.modulos_genericos.configuracion.models import ConfiguracionPrestador
from rest_framework.authtoken.models import Token
import datetime

class MiNegocioAPITests(APITestCase):
    """
    Pruebas para los endpoints de la API de 'Mi Negocio'.
    """
    def setUp(self):
        self.prestador_user = CustomUser.objects.create_user(
            username='prestador_test', email='prestador@example.com', password='password123', role=CustomUser.Role.PRESTADOR
        )
        self.otro_prestador_user = CustomUser.objects.create_user(
            username='otro_prestador', email='otro@example.com', password='password123', role=CustomUser.Role.PRESTADOR
        )
        self.turista_user = CustomUser.objects.create_user(
            username='turista_test', email='turista@example.com', password='password123', role=CustomUser.Role.TURISTA
        )

        self.categoria = CategoriaPrestador.objects.create(nombre="Restaurante", slug="restaurantes")
        self.perfil = Perfil.objects.create(
            user=self.prestador_user,
            nombre_comercial="Restaurante La Delicia",
            categoria=self.categoria
        )
        self.otro_perfil = Perfil.objects.create(
            user=self.otro_prestador_user,
            nombre_comercial="Restaurante El Sabor",
            categoria=self.categoria
        )

        # self.producto = ProductoServicio.objects.create(
        #     perfil=self.perfil, nombre="Café", precio=2.50
        # )
        self.cliente_obj = Cliente.objects.create(perfil=self.perfil, nombre="Juan Perez")

        self.prestador_token = Token.objects.create(user=self.prestador_user)
        self.turista_token = Token.objects.create(user=self.turista_user)

    def _get_auth_header(self, token):
        return {'HTTP_AUTHORIZATION': f'Token {token.key}'}

    # --- Pruebas de Perfil ---
    # def test_prestador_can_retrieve_own_perfil(self):
    #     url = reverse('mi_negocio:perfil-me')
    #     response = self.client.get(url, **self._get_auth_header(self.prestador_token))
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     self.assertEqual(response.data['nombre_comercial'], self.perfil.nombre_comercial)

    # # def test_prestador_cannot_retrieve_other_perfil(self):
    # #     url = reverse('perfil-detail', kwargs={'pk': self.otro_perfil.pk})
    # #     response = self.client.get(url, **self._get_auth_header(self.prestador_token))
    # #     self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # def test_turista_cannot_access_perfil_api(self):
    #     url = reverse('mi_negocio:perfil-me')
    #     response = self.client.get(url, **self._get_auth_header(self.turista_token))
    #     self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # # --- Pruebas de Productos/Servicios ---
    # def test_prestador_can_list_own_productos(self):
    #     url = reverse('mi_negocio:producto-servicio-list')
    #     response = self.client.get(url, **self._get_auth_header(self.prestador_token))
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     self.assertEqual(len(response.data['results']), 1)
    #     self.assertEqual(response.data['results'][0]['nombre'], self.producto.nombre)

    # def test_prestador_can_create_producto(self):
    #     url = reverse('mi_negocio:producto-servicio-list')
    #     data = {'nombre': 'Jugo de Naranja', 'precio': 3.00, 'tipo': 'PRODUCTO'}
    #     response = self.client.post(url, data, **self._get_auth_header(self.prestador_token))
    #     self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    #     self.assertEqual(ProductoServicio.objects.filter(perfil=self.perfil).count(), 2)

    # def test_prestador_can_update_own_producto(self):
    #     url = reverse('mi_negocio:producto-servicio-detail', kwargs={'pk': self.producto.pk})
    #     data = {'precio': 2.75}
    #     response = self.client.patch(url, data, **self._get_auth_header(self.prestador_token))
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     self.producto.refresh_from_db()
    #     self.assertEqual(self.producto.precio, 2.75)

    # def test_prestador_cannot_update_other_producto(self):
    #     otro_producto = ProductoServicio.objects.create(
    #         perfil=self.otro_perfil, nombre="Té", precio=2.00
    #     )
    #     url = reverse('mi_negocio:producto-servicio-detail', kwargs={'pk': otro_producto.pk})
    #     data = {'precio': 2.25}
    #     response = self.client.patch(url, data, **self._get_auth_header(self.prestador_token))
    #     self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # # --- Pruebas de Clientes ---
    # def test_prestador_can_list_own_clientes(self):
    #     url = reverse('mi_negocio:cliente-list')
    #     response = self.client.get(url, **self._get_auth_header(self.prestador_token))
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     self.assertEqual(len(response.data['results']), 1)

    # def test_prestador_can_create_cliente(self):
    #     url = reverse('mi_negocio:cliente-list')
    #     data = {'nombre': 'Maria Lopez', 'email': 'maria@test.com'}
    #     response = self.client.post(url, data, **self._get_auth_header(self.prestador_token))
    #     self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    #     self.assertEqual(Cliente.objects.filter(perfil=self.perfil).count(), 2)

    # # --- Pruebas de Reservas ---
    # # def test_prestador_can_create_reserva(self):
    # #     url = reverse('reservas-list')
    # #     data = {
    # #         'cliente': self.cliente_obj.pk,
    # #         'producto_servicio': self.producto.pk,
    # #         'fecha_hora_inicio': (datetime.datetime.now() + datetime.timedelta(days=1)).isoformat()
    # #     }
    # #     response = self.client.post(url, data, **self._get_auth_header(self.prestador_token))
    # #     self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    # #     # self.assertEqual(Reserva.objects.filter(perfil=self.perfil).count(), 1)

    # # --- Pruebas de Costos ---
    # def test_prestador_can_create_costo(self):
    #     url = reverse('mi_negocio:costo-list')
    #     data = {'concepto': 'Servilletas', 'monto': 20.00, 'fecha': datetime.date.today().isoformat()}
    #     response = self.client.post(url, data, **self._get_auth_header(self.prestador_token))
    #     self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    #     self.assertEqual(Costo.objects.filter(perfil=self.perfil).count(), 1)

    # # --- Pruebas de Inventario ---
    # def test_prestador_can_create_inventario_item(self):
    #     url = reverse('mi_negocio:inventario-list')
    #     data = {'nombre_item': 'Cajas de Leche', 'cantidad': 10, 'unidad': 'unidades'}
    #     response = self.client.post(url, data, **self._get_auth_header(self.prestador_token))
    #     self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    #     self.assertEqual(Inventario.objects.filter(perfil=self.perfil).count(), 1)

    # --- Pruebas de RAT ---
    # def test_prestador_can_create_rat_document(self):
    #     url = reverse('rat-list')
    #     data = {
    #         'nombre_documento': 'RUT 2024',
    #         'fecha_presentacion': datetime.date.today().isoformat(),
    #         'entidad_reguladora': 'DIAN'
    #     }
    #     response = self.client.post(url, data, **self._get_auth_header(self.prestador_token))
    #     self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    #     # self.assertEqual(RegistroActividadTuristica.objects.filter(perfil=self.perfil).count(), 1)

    # --- Pruebas de Soporte ---
    # def test_prestador_can_create_soporte_ticket(self):
    #     url = reverse('soporte-list')
    #     data = {'asunto': 'Problema con la factura', 'mensaje': 'No puedo descargar mi factura.'}
    #     response = self.client.post(url, data, **self._get_auth_header(self.prestador_token))
    #     self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    #     # self.assertEqual(TicketSoporte.objects.filter(perfil=self.perfil).count(), 1)
    #     self.assertEqual(response.data['estado'], 'ABIERTO')

    # --- Pruebas de Configuracion ---
    # def test_prestador_can_retrieve_and_update_configuracion(self):
    #     # El ViewSet no tiene una vista de lista, por lo que no podemos usar reverse('configuracion-list')
    #     # Accedemos directamente al objeto a través de su pk.
    #     # El get_object del ViewSet se encargará de crear la configuración si no existe.
    #     # config = ConfiguracionPrestador.objects.create(perfil=self.perfil)
    #     url = reverse('configuracion-detail', kwargs={'pk': config.pk})

    #     # Probar GET
    #     response_get = self.client.get(url, **self._get_auth_header(self.prestador_token))
    #     self.assertEqual(response_get.status_code, status.HTTP_200_OK)
    #     self.assertTrue(response_get.data['recibir_notificaciones_email'])

    #     # Probar PATCH
    #     data = {'recibir_notificaciones_email': False}
    #     response_patch = self.client.patch(url, data, **self._get_auth_header(self.prestador_token))
    #     self.assertEqual(response_patch.status_code, status.HTTP_200_OK)
    #     self.assertFalse(response_patch.data['recibir_notificaciones_email'])
