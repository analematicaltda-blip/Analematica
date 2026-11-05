import flet as ft
import sqlite3
from datetime import datetime

LOGO_PATH = "assets/logo.png"
COLOR1_HEX = "#FFD700"
COLOR2_HEX = "#00A651"

def profesor_horarios(page: ft.Page):
    nombre_clase = ft.TextField(label="Nombre de la Clase")
    dia_semana = ft.Dropdown(
        label="Día de la semana",
        options=[ft.dropdown.Option(d) for d in ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado"]]
    )
    # Using ft.TextField for time for simplicity, as TimePicker can be complex to manage without a full app structure
    hora_inicio = ft.TextField(label="Hora de inicio (HH:MM)")
    hora_fin = ft.TextField(label="Hora de fin (HH:MM)")
    escenario = ft.TextField(label="Escenario o Lugar")

    mensaje = ft.Text(visible=False)

    def guardar_horario(e):
        if not all([nombre_clase.value, dia_semana.value, escenario.value, hora_inicio.value, hora_fin.value]):
            mensaje.value = "Todos los campos son obligatorios."
            mensaje.color = "red"
            mensaje.visible = True
            page.update()
            return

        conn = sqlite3.connect("formacion.db")
        cursor = conn.cursor()
        # This assumes a 'clases' table exists. This will be created in the database setup script.
        cursor.execute("""
            INSERT INTO clases (nombre_clase, dia_semana, hora_inicio, hora_fin, escenario)
            VALUES (?, ?, ?, ?, ?)
        """, (
            nombre_clase.value,
            dia_semana.value,
            hora_inicio.value,
            hora_fin.value,
            escenario.value
        ))
        conn.commit()
        conn.close()

        mensaje.value = "Horario guardado correctamente."
        mensaje.color = "green"
        mensaje.visible = True

        # Clear fields
        nombre_clase.value = ""
        dia_semana.value = None
        hora_inicio.value = ""
        hora_fin.value = ""
        escenario.value = ""
        page.update()

    return ft.View("/profesor_horarios", [
        ft.AppBar(title=ft.Text("Crear Horario de Clase"), bgcolor=COLOR1_HEX),
        ft.Container(
            padding=20,
            gradient=ft.LinearGradient(
                begin=ft.alignment.top_left,
                end=ft.alignment.bottom_right,
                colors=[COLOR1_HEX, COLOR2_HEX]
            ),
            content=ft.Column([
                ft.Image(src=LOGO_PATH, width=150, height=80),
                nombre_clase,
                dia_semana,
                hora_inicio,
                hora_fin,
                escenario,
                ft.ElevatedButton("Guardar Horario", on_click=guardar_horario),
                mensaje
            ], scroll=ft.ScrollMode.AUTO)
        )
    ])
