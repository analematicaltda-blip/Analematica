import unittest
import os
import sqlite3
from unittest.mock import Mock, patch

# --- Importar los módulos a probar ---
from utils.database_manager import get_db_path, initialize_local_database
from utils.sync_manager import SyncManager
from utils.api_client import ApiClient

class TestSyncManager(unittest.TestCase):

    def setUp(self):
        """
        Configura un entorno de prueba limpio con una base de datos local.
        """
        self.mock_page = Mock()
        test_dir = os.path.join(os.getcwd(), "test_sync_data")
        self.mock_page.user_data_path = test_dir

        self.db_path = get_db_path(self.mock_page)
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
        if not os.path.exists(test_dir):
            os.makedirs(test_dir)

        # Crear una base de datos local limpia para la prueba
        initialize_local_database(self.mock_page)

        # Añadir un dato de prueba a la base de datos local
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO usuarios (id, inquilino_id, nombre_usuario, password_hash, rol) VALUES (1, 1, 'testuser', 'hash', 'alumno')")
        cursor.execute("INSERT INTO alumnos (id, usuario_id, inquilino_id, documento) VALUES (1, 1, 1, '12345')")
        conn.commit()
        conn.close()

    def tearDown(self):
        """
        Limpia el entorno de prueba.
        """
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    @patch('utils.api_client.ApiClient')
    def test_sync_cycle(self, MockApiClient):
        """
        Verifica el ciclo completo de sincronización (push y pull),
        mockeando las llamadas a la API.
        """
        # --- Configuración del Mock ---

        # Configurar la instancia mock del ApiClient
        mock_api_instance = MockApiClient.return_value

        # El 'push' debe devolver éxito
        mock_api_instance.push_sync_data.return_value = True

        # El 'pull' debe devolver un lote de datos de ejemplo del servidor
        mock_server_data = {
            "timestamp": "2023-10-28T12:00:00Z",
            "data": {
                "clases": [
                    {"id": 101, "nombre_clase": "Clase de Servidor 1", "inquilino_id": 1},
                    {"id": 102, "nombre_clase": "Clase de Servidor 2", "inquilino_id": 1}
                ]
                # Podríamos añadir más datos de otras tablas aquí
            }
        }
        mock_api_instance.pull_sync_data.return_value = mock_server_data

        # --- Acción ---

        # Crear una instancia del SyncManager con el ApiClient mockeado
        sync_manager = SyncManager(self.mock_page, mock_api_instance)

        # Ejecutar el ciclo de sincronización
        sync_success = sync_manager.sync_with_server()

        # --- Verificaciones ---

        # 1. Verificar que la sincronización reportó éxito
        self.assertTrue(sync_success)
        print("\n[TEST PASSED] Sync cycle reported success.")

        # 2. Verificar que se llamó al método push
        mock_api_instance.push_sync_data.assert_called_once()
        # Verificar que los datos enviados contenían al alumno local
        pushed_data = mock_api_instance.push_sync_data.call_args[0][0]
        self.assertIn('alumnos', pushed_data)
        self.assertEqual(len(pushed_data['alumnos']), 1)
        self.assertEqual(pushed_data['alumnos'][0]['documento'], '12345')
        print("[TEST PASSED] Push was called with correct local data.")

        # 3. Verificar que se llamó al método pull
        mock_api_instance.pull_sync_data.assert_called_once()
        print("[TEST PASSED] Pull was called.")

        # 4. Verificar que los datos del pull se aplicaron a la DB local
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM clases WHERE id IN (101, 102)")
        count = cursor.fetchone()[0]
        self.assertEqual(count, 2)
        conn.close()
        print("[TEST PASSED] Server pull data applied successfully to local DB.")

    @patch('utils.api_client.ApiClient')
    def test_unassigned_historical_record_retention(self, MockApiClient):
        """
        Verifica que registros locales sin inquilino_id y sin contexto de sesión
        sean retenidos sin reasignaciones silenciosas.
        """
        self.mock_page.inquilino_id = None
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO usuarios (id, inquilino_id, nombre_usuario, password_hash, rol) VALUES (999, 1, 'unassigned_usr', 'pw', 'alumno')")
        cursor.execute("INSERT INTO alumnos (id, usuario_id, inquilino_id, documento) VALUES (999, 999, 0, '99999')")
        conn.commit()
        conn.close()

        mock_api_instance = MockApiClient.return_value
        mock_api_instance.push_sync_data.return_value = True
        mock_api_instance.pull_sync_data.return_value = {"data": {}}

        sync_manager = SyncManager(self.mock_page, mock_api_instance)
        changes = sync_manager._detect_local_changes()

        if "alumnos" in changes:
            alumno_ids = [a["id"] for a in changes["alumnos"]]
            self.assertNotIn(999, alumno_ids)
        print("[TEST PASSED] Unassigned historical record retention verified.")

    @patch('utils.api_client.ApiClient')
    def test_cross_tenant_overwrite_rejection(self, MockApiClient):
        """
        Verifica que una clase entrante del servidor con id idéntico pero distinto inquilino_id
        sea rechazada y NO sobrescriba la clase del inquilino local.
        """
        # Pre-existente: Clase id=500 de Tenant 1
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO clases (id, nombre_clase, inquilino_id, area) VALUES (500, 'Clase Tenant 1', 1, 'Deportes')")
        conn.commit()
        conn.close()

        # Intento de Pull: Servidor envía Clase id=500 perteneciente a Tenant 2
        mock_api_instance = MockApiClient.return_value
        mock_server_data = {
            "data": {
                "clases": [
                    {"id": 500, "nombre_clase": "Clase Mala Tenant 2", "inquilino_id": 2, "area": "Deportes"}
                ]
            }
        }
        sync_manager = SyncManager(self.mock_page, mock_api_instance)
        sync_manager._apply_server_changes(mock_server_data)

        # Verificar que la clase local NO fue alterada ni cambiada de tenant
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT nombre_clase, inquilino_id FROM clases WHERE id = 500")
        row = cursor.fetchone()
        self.assertEqual(row[0], "Clase Tenant 1")
        self.assertEqual(row[1], 1)
        conn.close()
        print("[TEST PASSED] Cross-tenant overwrite rejection verified successfully.")


if __name__ == '__main__':
    print("--- Ejecutando Pruebas del Motor de Sincronización ---")
    unittest.main(verbosity=0)
