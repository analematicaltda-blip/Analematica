import flet as ft
import sqlite3

class ResumenGamificacionWidget(ft.Container):
    def __init__(self, user_id: int, tenant_id: int):
        super().__init__()
        self.user_id = user_id
        self.tenant_id = tenant_id

        self.content = ft.Column(
            [
                ft.Text("Mi Progreso", style=ft.TextThemeStyle.TITLE_MEDIUM),
                ft.Divider(),
                ft.ProgressRing(),
            ],
            spacing=10
        )

        self.padding = 20
        self.bgcolor = ft.colors.AMBER_50
        self.border_radius = 10

        self.load_data()

    def load_data(self):
        conn = sqlite3.connect("formacion.db")
        cursor = conn.cursor()

        # Get points and level
        cursor.execute(
            "SELECT puntos_totales, nivel FROM alumnos WHERE usuario_id = ?",
            (self.user_id,)
        )
        gamification_data = cursor.fetchone()

        # Get recent medals
        cursor.execute("""
            SELECT m.nombre, m.icono_path
            FROM gamificacion_medallas_obtenidas mo
            JOIN gamificacion_medallas m ON mo.medalla_key = m.medalla_key AND mo.inquilino_id = m.inquilino_id
            WHERE mo.alumno_id = (SELECT id FROM alumnos WHERE usuario_id = ?)
            ORDER BY mo.fecha_obtencion DESC
            LIMIT 3
        """, (self.user_id,))
        medallas = cursor.fetchall()

        conn.close()

        self.content.controls.pop() # Remove ProgressRing

        if not gamification_data:
            self.content.controls.append(ft.Text("No se encontraron datos de progreso."))
        else:
            puntos, nivel = gamification_data
            self.content.controls.extend([
                ft.ListTile(
                    leading=ft.Icon(ft.icons.STAR, color=ft.colors.AMBER),
                    title=ft.Text(f"Nivel {nivel}"),
                ),
                ft.ListTile(
                    leading=ft.Icon(ft.icons.CONTROL_POINT, color=ft.colors.ORANGE),
                    title=ft.Text(f"{puntos} Puntos"),
                ),
                ft.Text("Últimas Medallas:", weight="bold"),
            ])

            if not medallas:
                self.content.controls.append(ft.Text("¡Aún no has ganado medallas!", italic=True))
            else:
                medallas_row = ft.Row(spacing=10)
                for nombre, icon_path in medallas:
                    medallas_row.controls.append(
                        ft.Image(src=icon_path, width=40, height=40, tooltip=nombre)
                    )
                self.content.controls.append(medallas_row)
