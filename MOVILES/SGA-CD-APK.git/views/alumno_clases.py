import flet as ft
import sqlite3
from datetime import datetime
import os
from gamification.engine import process_gamified_action
from views.components.chat_assistant import ChatAssistant

LOGO_PATH = "assets/logo.png"
COLOR1_HEX = "#FFD700"
COLOR2_HEX = "#00A651"

def alumno_clases(page: ft.Page, tenant_id: int, user_id: int):
    clases_column = ft.Column(scroll=ft.ScrollMode.ADAPTIVE, expand=True)
    notificaciones_column = ft.Column(scroll=ft.ScrollMode.ADAPTIVE)
    mensaje_estado = ft.Text()

    def open_chat_for_class(e, area: str, clase_id: int):
        """Creates and opens a chat assistant dialog with a specific area context."""
        # This creates a new assistant instance every time, specific to the class context.
        chat_assistant = ChatAssistant(page, user_id, tenant_id, area)
        # We manually open the dialog from the assistant instance.
        chat_assistant.open_dialog(e)
        # We can even pre-fill the chat with context.
        chat_assistant.chat_history.controls.append(
            ft.Text(f"Asistente: Hola, ¿cómo puedo ayudarte con esta clase de {area}?", italic=True)
        )
        chat_assistant.update()

    def registrar_asistencia(e, clase_id: int, file_picker: ft.FilePicker):
        def seleccionar_archivo(e: ft.FilePickerResultEvent):
            if not e.files:
                mensaje_estado.value = "No se seleccionó ningún archivo."
                mensaje_estado.color = "red"
                page.update()
                return
            try:
                archivo = e.files[0]
                ruta_destino = os.path.join("evidencias", os.path.basename(archivo.path))
                os.makedirs("evidencias", exist_ok=True)

                conn = sqlite3.connect("formacion.db")
                cursor = conn.cursor()
                cursor.execute("""
                INSERT INTO asistencias (inquilino_id, alumno_id, clase_id, fecha_hora, evidencia_path)
                VALUES (?, ?, ?, ?, ?)
                """, (tenant_id, user_id, clase_id, datetime.now().isoformat(), ruta_destino))
                conn.commit()
                conn.close()
                process_gamified_action(tenant_id, user_id, 'ASISTENCIA_CLASE', page.pubsub)
                mensaje_estado.value = "Asistencia registrada correctamente."
                mensaje_estado.color = "green"
                e.control.disabled = True
            except Exception as ex:
                mensaje_estado.value = f"Error registrando asistencia: {ex}"
                mensaje_estado.color = "red"
            page.update()

        file_picker.on_result = seleccionar_archivo
        file_picker.pick_files(allow_multiple=False, allowed_extensions=["jpg", "png", "pdf"])

    def cargar_datos():
        clases_column.controls.clear()
        conn = sqlite3.connect("formacion.db")
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        try:
            # Modified query to include the class area
            cursor.execute("""
                SELECT c.id, c.fecha, c.hora_inicio, c.hora_fin, c.espacio, c.novedad, p.nombre_proceso, c.area
                FROM clases c
                JOIN procesos_formacion p ON c.proceso_id = p.id
                JOIN inscripciones ins ON ins.clase_id = c.id
                WHERE ins.alumno_id = ? AND c.inquilino_id = ?
                ORDER BY c.fecha DESC, c.hora_inicio
            """, (user_id, tenant_id))

            hoy = datetime.now().date()
            for row in cursor.fetchall():
                clase_id = row['id']
                fecha = row['fecha']
                area_clase = row['area'] # Get the area for this class

                fecha_clase = datetime.strptime(fecha, "%Y-%m-%d").date()
                mostrar_asistencia = fecha_clase == hoy
                asistencia_control = ft.Container()
                if mostrar_asistencia:
                    file_picker = ft.FilePicker()
                    page.overlay.append(file_picker)
                    asistencia_control = ft.ElevatedButton(
                        text="Registrar Asistencia", icon=ft.icons.CAMERA_ALT,
                        on_click=lambda e, cid=clase_id, fp=file_picker: registrar_asistencia(e, cid, fp)
                    )

                clases_column.controls.append(
                    ft.Card(content=ft.Container(
                        content=ft.Column([
                            ft.Text(f"Proceso: {row['nombre_proceso']} ({area_clase})", size=16, weight="bold"),
                            ft.Text(f"Fecha: {fecha} | Hora: {row['hora_inicio']} - {row['hora_fin']}"),
                            ft.Text(f"Novedad: {row['novedad']}", italic=True) if row['novedad'] else ft.Container(),
                            ft.Row([
                                asistencia_control,
                                ft.IconButton(
                                    icon=ft.icons.MENU_BOOK,
                                    on_click=lambda _, cid=clase_id: page.go(f"/alumno/contenido/{cid}"),
                                    tooltip="Ver Material de Estudio"
                                ),
                                ft.IconButton(
                                    icon=ft.icons.FORUM,
                                    on_click=lambda _, cid=clase_id: page.go(f"/clase/{cid}/foro"),
                                    tooltip="Ir al Foro de la Clase"
                                ),
                                ft.IconButton(
                                    icon=ft.icons.ASSISTANT,
                                    on_click=lambda _, area=area_clase, cid=clase_id: open_chat_for_class(_, area, cid),
                                    tooltip=f"Preguntar al Asistente de {area_clase}"
                                )
                            ], alignment=ft.MainAxisAlignment.SPACE_AROUND)
                        ]),
                        padding=15, border_radius=10
                    ))
                )
            # ... (resto de la lógica de cargar notificaciones)
        except Exception as e:
            mensaje_estado.value = f"Error al cargar datos: {e}"
        finally:
            conn.close()
            page.update()

    cargar_datos()

    return ft.View("/alumno_clases", [
        ft.AppBar(title=ft.Text("Mis Clases y Notificaciones"), bgcolor=COLOR2_HEX),
        ft.Container(padding=20, expand=True, content=ft.Column([
            ft.Row([
                ft.Image(src=LOGO_PATH, width=140, height=70),
                ft.ElevatedButton("Ver Mi Progreso (SIGA)", icon=ft.icons.STAR, on_click=lambda _: page.go("/alumno/progreso"))
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            mensaje_estado,
            ft.Text("Clases Programadas", size=20, weight="bold"),
            clases_column,
        ]))
    ])
