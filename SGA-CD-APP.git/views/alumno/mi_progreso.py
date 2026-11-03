import flet as ft
import sqlite3

def mi_progreso_view(page: ft.Page, tenant_id: int, user_id: int):

    def get_progreso_data():
        conn = sqlite3.connect("formacion.db")
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # Get points and level
        cursor.execute("SELECT puntos_totales, nivel FROM alumnos WHERE usuario_id = ?", (user_id,))
        progreso = cursor.fetchone()

        # Get medals
        cursor.execute("""
            SELECT m.nombre, m.descripcion, m.icono_path
            FROM gamificacion_medallas_obtenidas mo
            JOIN gamificacion_medallas m ON mo.medalla_key = m.medalla_key AND mo.inquilino_id = m.inquilino_id
            WHERE mo.alumno_id = ? AND mo.inquilino_id = ?
        """, (user_id, tenant_id))
        medallas = cursor.fetchall()

        conn.close()
        return progreso, medallas

    progreso_data, medallas_data = get_progreso_data()

    puntos_text = ft.Text(f"Puntos Totales: {progreso_data['puntos_totales'] if progreso_data else 0}", size=20, weight="bold")
    nivel_text = ft.Text(f"Nivel: {progreso_data['nivel'] if progreso_data else 1}", size=20, weight="bold")

    medallas_grid = ft.GridView(expand=True, max_extent=150, child_aspect_ratio=1)
    for medalla in medallas_data:
        medallas_grid.controls.append(
            ft.Card(
                content=ft.Container(
                    padding=10,
                    content=ft.Column([
                        ft.Image(src=medalla['icono_path'], width=60, height=60),
                        ft.Text(medalla['nombre'], weight="bold", text_align=ft.TextAlign.CENTER),
                        ft.Text(medalla['descripcion'], size=12, text_align=ft.TextAlign.CENTER),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
                )
            )
        )

    return ft.View(
        "/alumno/progreso",
        [
            ft.AppBar(title=ft.Text("Mi Progreso (SIGA)")),
            ft.Container(
                padding=20,
                expand=True,
                content=ft.Column([
                    ft.Text("Tu Progreso de Gamificación", size=22, weight="bold"),
                    ft.Row([puntos_text, nivel_text], alignment=ft.MainAxisAlignment.SPACE_AROUND),
                    ft.Divider(height=20),
                    ft.Text("Mis Medallas", size=18, weight="bold"),
                    medallas_grid
                ])
            )
        ]
    )
