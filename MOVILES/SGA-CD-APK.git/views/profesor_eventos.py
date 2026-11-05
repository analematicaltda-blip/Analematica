import flet as ft
import sqlite3

def profesor_eventos(page: ft.Page, tenant_id: int, user_id: int):

    eventos_list = ft.ListView(expand=True, spacing=10)

    def cargar_eventos():
        conn = sqlite3.connect("formacion.db")
        cursor = conn.cursor()
        # Shows events created by this user or where this user is a participant
        cursor.execute("""
            SELECT e.nombre, e.descripcion, e.fecha_inicio, e.fecha_fin, e.lugar
            FROM eventos e
            LEFT JOIN evento_participantes ep ON e.id = ep.evento_id
            WHERE e.inquilino_id = ? AND (e.creado_por_usuario_id = ? OR ep.usuario_id = ?)
            GROUP BY e.id
            ORDER BY e.fecha_inicio DESC
        """, (tenant_id, user_id, user_id))
        eventos = cursor.fetchall()
        conn.close()

        eventos_list.controls.clear()
        for e in eventos:
            eventos_list.controls.append(
                ft.Card(
                    content=ft.ListTile(
                        title=ft.Text(e[0], weight="bold"),
                        subtitle=ft.Text(f"Lugar: {e[4]} | Fechas: {e[1]} - {e[2]}\n{e[3]}"),
                        is_three_line=True,
                    )
                )
            )
        page.update()

    cargar_eventos()

    return ft.View(
        "/profesor_eventos",
        [
            ft.AppBar(title=ft.Text("Gestión de Eventos")),
            ft.Container(
                padding=20,
                expand=True,
                content=ft.Column([
                    ft.Text("Mis Eventos", size=22, weight="bold"),
                    ft.Divider(),
                    eventos_list,
                ])
            )
        ]
    )
