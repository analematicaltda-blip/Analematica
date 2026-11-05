import flet as ft
import sqlite3

def instructor_gestion_elementos(page: ft.Page, tenant_id: int, user_id: int):
    # This view is functionally identical to the one for 'almacenista'
    # In a real app, this could be a single reusable component.

    def get_elementos():
        conn = sqlite3.connect("formacion.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id, codigo, descripcion, area FROM elementos WHERE inquilino_id = ?", (tenant_id,))
        items = cursor.fetchall()
        conn.close()
        return items

    def crear_dialogo_elemento(elemento=None):
        is_edit = elemento is not None

        codigo_input = ft.TextField(label="Código", value=elemento[1] if is_edit else "")
        desc_input = ft.TextField(label="Descripción", value=elemento[2] if is_edit else "")
        area_dropdown = ft.Dropdown(
            label="Área",
            options=[ft.dropdown.Option("Cultura"), ft.dropdown.Option("Deportes")],
            value=elemento[3] if is_edit else None
        )

        def guardar_elemento(e):
            if not all([codigo_input.value, desc_input.value, area_dropdown.value]):
                return

            conn = sqlite3.connect("formacion.db")
            cursor = conn.cursor()
            try:
                if is_edit:
                    cursor.execute("""
                        UPDATE elementos SET codigo = ?, descripcion = ?, area = ?
                        WHERE id = ? AND inquilino_id = ?
                    """, (codigo_input.value, desc_input.value, area_dropdown.value, elemento[0], tenant_id))
                else:
                    cursor.execute("""
                        INSERT INTO elementos (inquilino_id, codigo, descripcion, area)
                        VALUES (?, ?, ?, ?)
                    """, (tenant_id, codigo_input.value, desc_input.value, area_dropdown.value))
                conn.commit()
                page.dialog.open = False
                cargar_elementos()
            except Exception as ex:
                print(f"Error saving element: {ex}")
            finally:
                conn.close()
                page.update()

        return ft.AlertDialog(
            modal=True,
            title=ft.Text("Editar Elemento" if is_edit else "Nuevo Elemento"),
            content=ft.Column([codigo_input, desc_input, area_dropdown]),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: setattr(page.dialog, 'open', False) or page.update()),
                ft.ElevatedButton("Guardar", on_click=guardar_elemento),
            ]
        )

    def handle_open_dialog(e, elemento=None):
        page.dialog = crear_dialogo_elemento(elemento)
        page.dialog.open = True
        page.update()

    tabla_elementos = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("Código")),
            ft.DataColumn(ft.Text("Descripción")),
            ft.DataColumn(ft.Text("Área")),
            ft.DataColumn(ft.Text("Acciones")),
        ],
        rows=[]
    )

    def cargar_elementos():
        tabla_elementos.rows.clear()
        for item in get_elementos():
            tabla_elementos.rows.append(
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text(item[1])),
                    ft.DataCell(ft.Text(item[2])),
                    ft.DataCell(ft.Text(item[3])),
                    ft.DataCell(ft.IconButton(icon=ft.icons.EDIT, on_click=lambda e, el=item: handle_open_dialog(e, el))),
                ])
            )
        page.update()

    cargar_elementos()

    return ft.View(
        "/instructor/elementos",
        [
            ft.AppBar(title=ft.Text("Gestión de Elementos de Inventario (Instructor)")),
            ft.Container(
                padding=20,
                expand=True,
                content=ft.Column([
                    ft.Row([
                        ft.Text("Inventario", size=22, weight="bold"),
                        ft.ElevatedButton("Añadir Elemento", icon=ft.icons.ADD, on_click=handle_open_dialog)
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    ft.Divider(),
                    ft.Row([tabla_elementos], scroll=ft.ScrollMode.ALWAYS, expand=True),
                ], expand=True)
            )
        ]
    )
