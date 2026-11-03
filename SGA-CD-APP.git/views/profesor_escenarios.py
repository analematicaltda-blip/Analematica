import flet as ft
import sqlite3

def profesor_escenarios(page: ft.Page, tenant_id: int):

    escenarios_list = ft.ListView(expand=True, spacing=10)

    def cargar_escenarios():
        conn = sqlite3.connect("formacion.db")
        cursor = conn.cursor()
        cursor.execute("SELECT nombre, descripcion, ubicacion, capacidad, tipo FROM escenarios WHERE inquilino_id = ?", (tenant_id,))
        escenarios = cursor.fetchall()
        conn.close()

        escenarios_list.controls.clear()
        for e in escenarios:
            escenarios_list.controls.append(
                ft.Card(
                    content=ft.ListTile(
                        title=ft.Text(e[0], weight="bold"),
                        subtitle=ft.Text(f"Tipo: {e[4]} | Ubicación: {e[2]} | Capacidad: {e[3]}\nDescripción: {e[1]}"),
                        is_three_line=True,
                    )
                )
            )
        page.update()

    cargar_escenarios()

    return ft.View(
        "/profesor_escenarios",
        [
            ft.AppBar(title=ft.Text("Gestión de Escenarios")),
            ft.Container(
                padding=20,
                expand=True,
                content=ft.Column([
                    ft.Text("Escenarios Disponibles", size=22, weight="bold"),
                    ft.Divider(),
                    escenarios_list,
                ])
            )
        ]
    )
