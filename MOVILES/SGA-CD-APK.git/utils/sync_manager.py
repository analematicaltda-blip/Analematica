import flet as ft
from .api_client import ApiClient
from .database_manager import get_db_connection
from .security_shield import sanitize_input_for_flet, sanitize_dict_inputs, format_masked_error_code

class SyncManager:
    """
    El "Motor de Datos". Gestiona la sincronización entre la base de datos
    local del cliente y la base de datos central a través de la API.
    Soporta intercepción de errores 401/403, formateo de trazas enmascaradas
    y notificación en la interfaz Flet alineada al tema Dark Metallic Blue.
    """
    def __init__(self, page: ft.Page, api_client: ApiClient):
        self.page = page
        self.api_client = api_client

    def _show_security_error_banner(self, masked_code: str, message: str):
        """
        Muestra una notificación de error estandarizada con la paleta 60-30-10 Dark Metallic Blue.
        Superficie #0D1424, Acento Cyan #38BDF8 y botón táctil mínimo de 44px.
        """
        if not self.page:
            return

        def close_banner(e):
            self.page.banner.open = False
            self.page.update()

        banner = ft.Banner(
            bgcolor="#0D1424",
            leading=ft.Icon(ft.icons.SHIELD_OUTLINED, color="#38BDF8", size=36),
            title=ft.Text(f"SGA-CD — Notificación de Seguridad [{masked_code}]", color="#38BDF8", weight=ft.FontWeight.BOLD),
            content=ft.Text(sanitize_input_for_flet(message), color="#E2E8F0"),
            actions=[
                ft.TextButton(
                    "ACEPTAR",
                    on_click=close_banner,
                    style=ft.ButtonStyle(
                        color="#070B14",
                        bgcolor="#38BDF8",
                        padding=ft.padding.all(12)
                    )
                )
            ]
        )
        self.page.banner = banner
        self.page.banner.open = True
        self.page.update()

    def _detect_local_changes(self) -> dict:
        """Detecta los registros de alumnos y clases creados o modificados localmente."""
        print("Detectando cambios locales para el 'push'...")
        conn = get_db_connection(self.page)
        alumnos = conn.execute("SELECT * FROM alumnos ORDER BY id DESC LIMIT 5").fetchall()
        clases = conn.execute("SELECT * FROM clases ORDER BY id DESC LIMIT 5").fetchall()

        session_tenant_id = getattr(self.page, 'inquilino_id', None) if self.page else None
        changes = {}

        if alumnos:
            valid_alumnos = []
            for row in alumnos:
                row_dict = dict(row)
                if not row_dict.get('inquilino_id'):
                    if session_tenant_id:
                        row_dict['inquilino_id'] = session_tenant_id
                    else:
                        print(f"Retenido: Registro de alumno id={row_dict.get('id')} sin inquilino_id y sin sesión autenticada.")
                        continue
                valid_alumnos.append(row_dict)
            if valid_alumnos:
                changes["alumnos"] = valid_alumnos

        if clases:
            valid_clases = []
            for row in clases:
                row_dict = dict(row)
                if not row_dict.get('inquilino_id'):
                    if session_tenant_id:
                        row_dict['inquilino_id'] = session_tenant_id
                    else:
                        print(f"Retenido: Registro de clase id={row_dict.get('id')} sin inquilino_id y sin sesión autenticada.")
                        continue
                valid_clases.append(row_dict)
            if valid_clases:
                changes["clases"] = valid_clases

        conn.close()
        return changes

    def _apply_server_changes(self, server_data: dict):
        """Aplica los datos recibidos del servidor a la base de datos local."""
        print("Aplicando cambios del servidor a la base de datos local...")
        data = server_data.get("data", {})
        conn = get_db_connection(self.page)
        cursor = conn.cursor()

        try:
            if 'clases' in data:
                for clase in data['clases']:
                    clase_id = clase.get('id')
                    clean_nombre = sanitize_input_for_flet(clase.get('nombre_clase', ''))
                    inquilino_id = clase.get('inquilino_id')
                    area = clase.get('area', 'Deportes')
                    if inquilino_id is None:
                        print(f"Advertencia: Registro de clase id={clase_id} omitido por falta de 'inquilino_id' en servidor.")
                        continue

                    # Protección Multiinquilino: Verificar si la fila local existente pertenece a otro inquilino
                    cursor.execute("SELECT inquilino_id FROM clases WHERE id = ?", (clase_id,))
                    existing = cursor.fetchone()
                    if existing and existing['inquilino_id'] is not None and existing['inquilino_id'] != inquilino_id:
                        print(f"Rechazado: Intento de sobreescritura cross-tenant en clase id={clase_id} (Existente tenant={existing['inquilino_id']}, Entrante tenant={inquilino_id})")
                        continue

                    cursor.execute(
                        "INSERT OR REPLACE INTO clases (id, nombre_clase, inquilino_id, area) VALUES (?, ?, ?, ?)",
                        (clase_id, clean_nombre, inquilino_id, area)
                    )

            conn.commit()
            print("Cambios del servidor aplicados con éxito.")
        except Exception as e:
            print(f"Error al aplicar cambios del servidor: {e}")
            conn.rollback()
        finally:
            conn.close()

    def sync_with_server(self, last_sync_timestamp: str = None) -> bool:
        """Ejecuta el ciclo completo de sincronización: push y luego pull."""
        print("--- Iniciando ciclo de sincronización ---")

        # 1. Push: Enviar cambios locales al servidor
        local_changes = self._detect_local_changes()
        if local_changes:
            push_res = self.api_client.push_sync_data(local_changes)
            if isinstance(push_res, dict) and push_res.get("error"):
                masked_code = push_res.get("code", "STD-ERR-500-INTERNAL-ERROR")
                self._show_security_error_banner(
                    masked_code,
                    "Error de autorización o red durante la sincronización de salida. "
                    "Se ha activado el refresco silencioso o la protección de sesión."
                )
                return False
            elif push_res is False:
                self._show_security_error_banner(
                    "STD-ERR-400-PUSH-FAILED",
                    "Fallo durante la sincronización de salida."
                )
                return False
            print("Push completado con éxito.")

        # 2. Pull: Obtener cambios del servidor
        server_response = self.api_client.pull_sync_data(last_sync_timestamp)
        if isinstance(server_response, dict) and server_response.get("error"):
            masked_code = server_response.get("code", "STD-ERR-500-INTERNAL-ERROR")
            self._show_security_error_banner(
                masked_code,
                "No se pudo completar la descarga de cambios del servidor. "
                "Verifique las credenciales de la entidad o reconecte la sesión."
            )
            return False

        if server_response and server_response.get("data"):
            self._apply_server_changes(server_response)

        # 3. Sincronizar registros de asistencia PWA / Flet local
        self.sync_offline_attendance()

        print("--- Ciclo de sincronización completado ---")
        if self.page:
            self.page.snack_bar = ft.SnackBar(
                ft.Text("¡Sincronización completada en Disciplinas Deportivas y Talleres Culturales!"),
                bgcolor="#0D1424"
            )
            self.page.snack_bar.open = True
            self.page.update()
        return True

    @staticmethod
    def format_attendance_payload(actividad: str = "Disciplinas Deportivas / Talleres Culturales",
                                  ubicacion: str = "Escenario Deportivo / Centro Cultural",
                                  latitud: float = 4.6097,
                                  longitud: float = -74.0817) -> dict:
        """Modelo de serialización estandarizado para check-in de asistencia."""
        import datetime
        return {
            "actividad": sanitize_input_for_flet(actividad),
            "ubicacion": sanitize_input_for_flet(ubicacion),
            "latitud": latitud,
            "longitud": longitud,
            "timestamp": datetime.datetime.utcnow().isoformat()
        }

    def sync_offline_attendance(self) -> bool:
        """Envía los registros de asistencia locales hacia la API central /api/v1/alumno/asistencia."""
        try:
            import sqlite3
            conn = get_db_connection(self.page)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS asistencia_local (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    actividad TEXT,
                    ubicacion TEXT,
                    latitud REAL,
                    longitud REAL,
                    timestamp TEXT,
                    synced INTEGER DEFAULT 0
                )
            """)
            conn.commit()

            unsynced = cursor.execute("SELECT * FROM asistencia_local WHERE synced = 0").fetchall()
            for row in unsynced:
                payload = {
                    "actividad": row["actividad"],
                    "ubicacion": row["ubicacion"],
                    "latitud": row["latitud"],
                    "longitud": row["longitud"],
                    "timestamp": row["timestamp"]
                }
                res = self.api_client.post("/api/v1/alumno/asistencia", payload)
                if isinstance(res, dict) and not res.get("error"):
                    cursor.execute("UPDATE asistencia_local SET synced = 1 WHERE id = ?", (row["id"],))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error sincronizando asistencias locales Flet: {e}")
            return False
