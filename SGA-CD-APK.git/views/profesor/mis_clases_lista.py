import flet as ft
import sqlite3
from datetime import datetime

def mis_clases_lista_view(page: ft.Page, user_id: int, tenant_id: int):

    clases_column = ft.Column(scroll=ft.ScrollMode.ADAPTIVE, expand=True)

    def load_clases():
        clases_column.controls.clear()
        conn = sqlite3.connect("formacion.db")
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT c.id, c.nombre_clase, c.fecha, c.hora_inicio, p.nombre_proceso
                FROM clases c
                JOIN procesos_formacion p ON c.proceso_id = p.id
                WHERE c.instructor_id = ? AND c.inquilino_id = ?
                ORDER BY c.fecha DESC, c.hora_inicio
            """, (user_id, tenant_id))

            clases = cursor.fetchall()

            if not clases:
                clases_column.controls.append(ft.Text("No tienes clases asignadas."))
            else:
                for clase_id, nombre, fecha, hora, proceso in clases:
                    clases_column.controls.append(
                        ft.Card(
                            content=ft.Container(
                                content=ft.Column([
                                    ft.Text(f"Proceso: {proceso}", size=16, weight="bold"),
                                    ft.Text(f"Clase: {nombre or 'N/A'}", style=ft.TextThemeStyle.BODY_LARGE),
                                    ft.Text(f"Fecha: {fecha} a las {hora}"),
                                    ft.Row(
                                        [
                                            ft.ElevatedButton(
                                                "Ir al Foro",
                                                icon=ft.icons.FORUM,
                                                on_click=lambda e, cid=clase_id: page.go(f"/clase/{cid}/foro"),
                                                tooltip="Abrir el foro de discusión de la clase"
                                            )
                                        ],
                                        alignment=ft.MainAxisAlignment.END
                                    )
                                ]),
                                padding=15,
                            )
                        )
                    )
        except Exception as e:
            clases_column.controls.append(ft.Text(f"Error al cargar clases: {e}"))
        finally:
            conn.close()
            page.update()

    load_clases()

    return ft.View(
        "/profesor/mis_clases",
        [
            ft.AppBar(title=ft.Text("Mis Clases"), bgcolor=ft.colors.SURFACE_VARIANT),
            ft.Container(
                content=clases_column,
                padding=20,
                expand=True,
            )
        ]
    )
