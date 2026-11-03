import sqlite3
import hashlib
import uuid

# Esta función de hashing debe ser idéntica a la usada en la aplicación principal.
def hash_password(password: str) -> str:
    """Hashes the password using SHA256."""
    return hashlib.sha256(password.encode()).hexdigest()

def create_test_users():
    """
    Crea un inquilino de prueba y una serie de usuarios de prueba con diferentes roles en la base de datos.
    """
    db_path = 'formacion.db'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    print("--- Creando Inquilino de Prueba ---")
    try:
        # Crear un inquilino de prueba si no existe uno llamado 'Inquilino de Pruebas'
        cursor.execute("SELECT id FROM inquilinos WHERE nombre_empresa = 'Inquilino de Pruebas'")
        tenant = cursor.fetchone()
        if tenant:
            tenant_id = tenant[0]
            print("Inquilino de Pruebas ya existe.")
        else:
            api_key = f"test-key-{uuid.uuid4().hex}"
            cursor.execute(
                "INSERT INTO inquilinos (nombre_empresa, plan, api_key, activo) VALUES (?, ?, ?, ?)",
                ('Inquilino de Pruebas', 'pro', api_key, 1)
            )
            tenant_id = cursor.lastrowid
            print(f"Inquilino 'Inquilino de Pruebas' creado con ID: {tenant_id}")

        # --- Definición de Usuarios de Prueba ---
        # La contraseña para todos los usuarios de prueba será 'password123'
        common_password = "password123"
        hashed_password = hash_password(common_password)

        # La lista de roles se basa en la solicitud del usuario y el análisis del sistema.
        # Se crean usuarios para los roles que pueden interactuar con la IA.
        roles_a_crear = [
            'admin_empresa', 'jefe_area', 'coordinador', 'profesor',
            'alumno', 'almacenista', 'jefe_escenarios'
        ]

        # El usuario especificó roles con distinción de área (Cultura/Deportes)
        areas = ['Cultura', 'Deportes']

        usuarios_creados = 0
        for role in roles_a_crear:
            if role in ['jefe_area', 'profesor', 'alumno']: # Roles que se duplican por área
                for area in areas:
                    username = f"{role.replace('_', '')}_{area.lower()}_test"
                    nombre_completo = f"Usuario de Prueba ({role} {area})"

                    cursor.execute("SELECT id FROM usuarios WHERE nombre_usuario = ? AND inquilino_id = ?", (username, tenant_id))
                    if cursor.fetchone():
                        print(f"Usuario '{username}' ya existe. Saltando.")
                        continue

                    cursor.execute(
                        """
                        INSERT INTO usuarios (inquilino_id, nombre_usuario, password_hash, rol, nombre_completo, correo, activo)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                        """,
                        (tenant_id, username, hashed_password, role, nombre_completo, f"{username}@test.com", 1)
                    )
                    print(f"Usuario creado: {username}")
                    usuarios_creados += 1
            else: # Roles que no se duplican por área
                username = f"{role.replace('_', '')}_test"
                nombre_completo = f"Usuario de Prueba ({role})"

                cursor.execute("SELECT id FROM usuarios WHERE nombre_usuario = ? AND inquilino_id = ?", (username, tenant_id))
                if cursor.fetchone():
                    print(f"Usuario '{username}' ya existe. Saltando.")
                    continue

                cursor.execute(
                    """
                    INSERT INTO usuarios (inquilino_id, nombre_usuario, password_hash, rol, nombre_completo, correo, activo)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (tenant_id, username, hashed_password, role, nombre_completo, f"{username}@test.com", 1)
                )
                print(f"Usuario creado: {username}")
                usuarios_creados += 1

        conn.commit()
        print(f"\n--- Proceso completado. Se crearon {usuarios_creados} nuevos usuarios. ---")
        print(f"Todos los usuarios tienen la contraseña: '{common_password}'")

    except Exception as e:
        print(f"Ocurrió un error: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    # Antes de crear usuarios, asegúrate de que la base de datos y sus tablas existan.
    # Se asume que `database_setup.py` ya ha sido ejecutado.
    create_test_users()
