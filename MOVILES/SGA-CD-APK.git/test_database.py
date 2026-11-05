import unittest
import os
import sqlite3
from unittest.mock import Mock

# --- Importar los módulos a probar ---
# Asegurarse de que la ruta de importación sea correcta
from utils.database_manager import get_db_path, initialize_local_database, get_db_connection
from database.database_setup import setup_database_with_conn

class TestDatabaseManager(unittest.TestCase):

    def setUp(self):
        """
        Configura un entorno de prueba limpio antes de cada test.
        """
        # Crear un mock del objeto 'page' de Flet
        self.mock_page = Mock()

        # Usar un directorio de prueba temporal para no interferir con datos reales
        test_dir = os.path.join(os.getcwd(), "test_user_data")
        self.mock_page.user_data_path = test_dir

        # Limpiar el directorio de prueba antes de cada ejecución
        self.db_path = get_db_path(self.mock_page)
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
        if not os.path.exists(test_dir):
            os.makedirs(test_dir)

    def tearDown(self):
        """
        Limpia el entorno de prueba después de cada test.
        """
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
        if os.path.exists(os.path.dirname(self.db_path)):
            # De forma simple, se podría borrar el directorio, pero es más seguro
            # dejarlo para evitar borrados accidentales si la ruta es incorrecta.
            pass

    def test_01_initialize_local_database_creates_db_file(self):
        """
        Verifica que `initialize_local_database` crea el fichero de la base de datos
        si no existe.
        """
        # Pre-condición: La base de datos no debe existir
        self.assertFalse(os.path.exists(self.db_path))

        # Acción: Inicializar la base de datos
        initialize_local_database(self.mock_page)

        # Verificación: El fichero de la base de datos ahora debe existir
        self.assertTrue(os.path.exists(self.db_path))
        print("\n[TEST PASSED] initialize_local_database_creates_db_file")

    def test_02_database_has_correct_schema(self):
        """
        Verifica que la base de datos creada tiene las tablas esperadas.
        """
        # Acción: Crear la base de datos
        initialize_local_database(self.mock_page)

        # Verificación: Conectar y comprobar la existencia de una tabla clave (p.ej. 'usuarios')
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='usuarios'")
        result = cursor.fetchone()
        conn.close()

        self.assertIsNotNone(result)
        self.assertEqual(result[0], 'usuarios')
        print("[TEST PASSED] database_has_correct_schema")

    def test_03_get_db_connection_works(self):
        """
        Verifica que `get_db_connection` devuelve un objeto de conexión válido
        y se puede usar para ejecutar una consulta.
        """
        # Preparación: Asegurarse de que la DB exista
        initialize_local_database(self.mock_page)

        try:
            # Acción: Obtener una conexión
            conn = get_db_connection(self.mock_page)
            self.assertIsInstance(conn, sqlite3.Connection)

            # Verificación: Ejecutar una consulta simple
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            self.assertEqual(result[0], 1)

            conn.close()
            print("[TEST PASSED] get_db_connection_works")

        except Exception as e:
            self.fail(f"`get_db_connection` falló con una excepción: {e}")

if __name__ == '__main__':
    print("--- Ejecutando Pruebas del Gestor de Base de Datos Local ---")
    unittest.main(verbosity=0)
