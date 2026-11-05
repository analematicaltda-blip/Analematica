import flet as ft
import sqlite3
from gamification.engine import grant_manual_badge

LOGO_PATH = "../../assets/logo.png"
COLOR1_HEX = "#FFD700"
COLOR2_HEX = "#00A651"

def gamificacion_dashboard_view(page: ft.Page, tenant_id: int, profesor_id: int):

    def show_award_dialog(e, student_user_id: int, student_name: str):

        manual_medals_dropdown = ft.Dropdown(label="Seleccionar Medalla")

        # Load manually-awardable medals
        conn = sqlite3.connect("formacion.db")
        cursor = conn.cursor()
        cursor.execute(
            "SELECT medalla_key, nombre FROM gamificacion_medallas WHERE inquilino_id = ? AND es_manual = 1",
            (tenant_id,)
        )
        manual_medals_dropdown.options = [ft.dropdown.Option(key, name) for key, name in cursor.fetchall()]
        conn.close()

        def award_badge(e):
            medal_key = manual_medals_dropdown.value
            if not medal_key:
                return

            result = grant_manual_badge(
                tenant_id=tenant_id,
                actor_user_id=profesor_id,
                target_alumno_user_id=student_user_id,
                medalla_key=medal_key,
                pubsub_instance=page.pubsub
            )

            page.dialog.open = False
            page.snack_bar = ft.SnackBar(ft.Text(result["message"]), bgcolor="green" if result["status"] == "success" else "orange")
            page.snack_bar.open = True
            page.update()

        page.dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(f"Otorgar Medalla a {student_name}"),
            content=ft.Column([
                ft.Text("Selecciona la medalla que deseas otorgar por un logro destacado:"),
                manual_medals_dropdown,
            ]),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: setattr(page.dialog, 'open', False) or page.update()),
                ft.ElevatedButton("Otorgar", on_click=award_badge),
            ]
        )
        page.dialog.open = True
        page.update()


    alumnos_table = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("Alumno")),
            ft.DataColumn(ft.Text("Nivel")),
            ft.DataColumn(ft.Text("Puntos Totales")),
            ft.DataColumn(ft.Text("Acciones")),
        ],
        rows=[]
    )

    def load_alumnos_progreso():
        try:
            conn = sqlite3.connect("formacion.db")
            cursor = conn.cursor()

            query = """
                SELECT DISTINCT
                    u.nombre_completo,
                    al.nivel,
                    al.puntos_totales,
                    al.usuario_id
                FROM alumnos al
                JOIN usuarios u ON al.usuario_id = u.id
                JOIN inscripciones i ON i.alumno_id = al.id
                JOIN clases c ON i.clase_id = c.id
                WHERE c.instructor_id = ? AND c.inquilino_id = ?
                ORDER BY al.puntos_totales DESC
            """

            cursor.execute(query, (profesor_id, tenant_id))
            alumnos = cursor.fetchall()
            conn.close()

            alumnos_table.rows = []
            for nombre, nivel, puntos, alumno_user_id in alumnos:
                actions = ft.Row([
                    ft.IconButton(
                        icon=ft.icons.EMOJI_EVENTS,
                        tooltip="Otorgar Medalla Manualmente",
                        on_click=lambda e, uid=alumno_user_id, uname=nombre: show_award_dialog(e, uid, uname)
                    )
                ])

                alumnos_table.rows.append(
                    ft.DataRow(cells=[
                        ft.DataCell(ft.Text(nombre)),
                        ft.DataCell(ft.Text(str(nivel))),
                        ft.DataCell(ft.Text(str(puntos))),
                        ft.DataCell(actions),
                    ])
                )
            page.update()
        except Exception as e:
            print(f"Error loading student progress for instructor: {e}")

    # Initial load
    load_alumnos_progreso()

    return ft.View(
        "/profesor/gamificacion",
        [
            ft.AppBar(title=ft.Text("Dashboard de Gamificación")),
            ft.Container(
                padding=20,
                expand=True,
                content=ft.Column([
                    ft.Text("Progreso de mis Alumnos", size=22, weight="bold"),
                    ft.Text("Supervisa el avance y otorga medallas por logros destacados."),
                    ft.Divider(),
                    ft.Container(content=alumnos_table, expand=True)
                ], scroll=ft.ScrollMode.ALWAYS)
            )
        ]
    )
