import flet as ft
import sqlite3
from datetime import datetime

def alumno_inscripcion(page: ft.Page, tenant_id: int, user_id: int):

    clases_disponibles_dropdown = ft.Dropdown(label="Selecciona una clase para inscribirte")
    mensaje_inscripcion = ft.Text()

    def cargar_clases_disponibles():
        conn = sqlite3.connect("formacion.db")
        # Find classes the user is NOT already enrolled in
        query = """
            SELECT c.id, c.nombre_clase || ' - ' || p.nombre_proceso
            FROM clases c
            JOIN procesos_formacion p ON c.proceso_id = p.id
            WHERE c.inquilino_id = ? AND c.id NOT IN (
                SELECT clase_id FROM inscripciones WHERE alumno_id = ?
            )
        """
        clases = conn.execute(query, (tenant_id, user_id)).fetchall()
        conn.close()
        clases_disponibles_dropdown.options = [ft.dropdown.Option(key=c[0], text=c[1]) for c in clases]
        page.update()

    def handle_inscribir(e):
        clase_id = clases_disponibles_dropdown.value
        if not clase_id:
            mensaje_inscripcion.value = "Por favor, selecciona una clase."
            mensaje_inscripcion.color = "red"
            page.update()
            return

        conn = sqlite3.connect("formacion.db")
        cursor = conn.cursor()
        try:
            # We need to get the area of the class to store it in the inscription
            cursor.execute("SELECT area FROM clases WHERE id = ?", (clase_id,))
            area_clase = cursor.fetchone()[0]

            cursor.execute("""
                INSERT INTO inscripciones (inquilino_id, alumno_id, clase_id, fecha_inscripcion, area)
                VALUES (?, ?, ?, ?, ?)
            """, (tenant_id, user_id, clase_id, datetime.now().isoformat(), area_clase))
            conn.commit()
            mensaje_inscripcion.value = "¡Inscripción exitosa!"
            mensaje_inscripcion.color = "green"
            cargar_clases_disponibles() # Refresh the list
        except Exception as ex:
            mensaje_inscripcion.value = f"Error en la inscripción: {ex}"
            mensaje_inscripcion.color = "red"
        finally:
            conn.close()
            page.update()

    cargar_clases_disponibles()

    return ft.View(
        "/alumno_inscripcion",
        [
            ft.AppBar(title=ft.Text("Inscripción a Clases")),
            ft.Container(
                padding=20,
                expand=True,
                content=ft.Column([
                    ft.Text("Inscribirse a una Nueva Clase", size=22, weight="bold"),
                    clases_disponibles_dropdown,
                    ft.ElevatedButton("Inscribirme", icon=ft.icons.CHECK, on_click=handle_inscribir),
                    mensaje_inscripcion
                ])
            )
        ]
    )
