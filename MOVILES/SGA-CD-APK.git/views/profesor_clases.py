import flet as ft
import sqlite3
from datetime import datetime

def profesor_clases(page: ft.Page, tenant_id: int, user_id: int):

    def get_profesor_area():
        conn = sqlite3.connect("formacion.db")
        cursor = conn.cursor()
        cursor.execute("SELECT area FROM profesores WHERE usuario_id = ?", (user_id,))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else None

    profesor_area = get_profesor_area()

    nombre_clase_input = ft.TextField(label="Nombre de la Clase")
    proceso_dropdown = ft.Dropdown(label="Proceso de Formación")
    escenario_dropdown = ft.Dropdown(label="Escenario")
    fecha_picker = ft.DatePicker(
        on_change=lambda e: print(f"Date changed: {e.control.value}"),
        on_dismiss=lambda e: print("DatePicker dismissed"),
    )
    page.overlay.append(fecha_picker)
    fecha_button = ft.ElevatedButton("Seleccionar Fecha", icon=ft.icons.CALENDAR_MONTH, on_click=lambda _: fecha_picker.pick_date())

    def cargar_dropdowns():
        conn = sqlite3.connect("formacion.db")
        procesos = conn.execute("SELECT id, nombre_proceso FROM procesos_formacion WHERE inquilino_id = ? AND area = ?", (tenant_id, profesor_area)).fetchall()
        escenarios = conn.execute("SELECT id, nombre FROM escenarios WHERE inquilino_id = ? AND area = ?", (tenant_id, profesor_area)).fetchall()
        conn.close()
        proceso_dropdown.options = [ft.dropdown.Option(key=p[0], text=p[1]) for p in procesos]
        escenario_dropdown.options = [ft.dropdown.Option(key=e[0], text=e[1]) for e in escenarios]
        page.update()

    def handle_crear_clase(e):
        # Validation
        if not all([nombre_clase_input.value, proceso_dropdown.value, fecha_picker.value]):
            # Show error
            return

        conn = sqlite3.connect("formacion.db")
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO clases (inquilino_id, nombre_clase, proceso_id, instructor_id, fecha, area)
                VALUES (?, ?, ?, ?, ?, ?)
            """,(
                tenant_id,
                nombre_clase_input.value,
                proceso_dropdown.value,
                user_id,
                fecha_picker.value.strftime("%Y-%m-%d"),
                profesor_area
            ))
            conn.commit()
            page.snack_bar = ft.SnackBar(ft.Text("Clase creada con éxito"), bgcolor="green")
        except Exception as ex:
            page.snack_bar = ft.SnackBar(ft.Text(f"Error al crear clase: {ex}"), bgcolor="red")
        finally:
            conn.close()
            page.snack_bar.open = True
            page.update()

    cargar_dropdowns()

    return ft.View(
        "/profesor_clases",
        [
            ft.AppBar(title=ft.Text("Crear Nueva Clase")),
            ft.Container(
                padding=20,
                expand=True,
                content=ft.Column([
                    ft.Text("Detalles de la Nueva Clase", size=22, weight="bold"),
                    nombre_clase_input,
                    proceso_dropdown,
                    escenario_dropdown,
                    fecha_button,
                    ft.ElevatedButton("Crear Clase", icon=ft.icons.ADD, on_click=handle_crear_clase)
                ])
            )
        ]
    )
