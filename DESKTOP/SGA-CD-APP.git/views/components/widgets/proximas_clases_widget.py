import flet as ft
import sqlite3
from datetime import datetime

class ProximasClasesWidget(ft.Container):
    def __init__(self, user_id: int, user_role: str, tenant_id: int):
        super().__init__()
        self.user_id = user_id
        self.user_role = user_role
        self.tenant_id = tenant_id

        self.content = ft.Column(
            [
                ft.Text("Próximas Clases", style=ft.TextThemeStyle.TITLE_MEDIUM),
                ft.Divider(),
                ft.ProgressRing(), # Placeholder while loading
            ],
            spacing=10
        )

        self.padding = 20
        self.bgcolor = ft.colors.BLUE_GREY_50
        self.border_radius = 10

        self.load_data()

    def load_data(self):
        conn = sqlite3.connect("formacion.db")
        cursor = conn.cursor()

        today_iso = datetime.now().strftime("%Y-%m-%d")

        if self.user_role == 'profesor':
            query = """
                SELECT c.nombre_clase, c.fecha, c.hora_inicio
                FROM clases c
                WHERE c.instructor_id = ? AND c.inquilino_id = ? AND c.fecha >= ?
                ORDER BY c.fecha, c.hora_inicio
                LIMIT 5
            """
            params = (self.user_id, self.tenant_id, today_iso)
        elif self.user_role == 'alumno':
            query = """
                SELECT c.nombre_clase, c.fecha, c.hora_inicio
                FROM clases c
                JOIN inscripciones i ON c.id = i.clase_id
                WHERE i.alumno_id = ? AND c.inquilino_id = ? AND c.fecha >= ?
                ORDER BY c.fecha, c.hora_inicio
                LIMIT 5
            """
            params = (self.user_id, self.tenant_id, today_iso)
        else:
            # No classes to show for other roles
            self.content.controls = [
                ft.Text("Próximas Clases", style=ft.TextThemeStyle.TITLE_MEDIUM),
                ft.Divider(),
                ft.Text("No aplicable para este rol.")
            ]
            conn.close()
            return

        cursor.execute(query, params)
        clases = cursor.fetchall()
        conn.close()

        # Clear placeholder and add data
        self.content.controls.pop() # Remove ProgressRing
        if not clases:
            self.content.controls.append(ft.Text("No tienes clases programadas."))
        else:
            for nombre, fecha, hora in clases:
                self.content.controls.append(
                    ft.ListTile(
                        leading=ft.Icon(ft.icons.CALENDAR_MONTH),
                        title=ft.Text(nombre or "Clase sin nombre"),
                        subtitle=ft.Text(f"{fecha} a las {hora}")
                    )
                )
