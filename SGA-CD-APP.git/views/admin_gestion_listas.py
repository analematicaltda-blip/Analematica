import flet as ft
import sqlite3

def admin_gestion_listas(page: ft.Page, tenant_id: int):

    TABLES = [
        "generos", "grupos_etarios", "tipos_documento", "escolaridades",
        "discapacidades", "grupos_poblacionales", "barrios", "veredas", "resguardos",
        "tipos_escenario"
    ]

    selected_table = ft.Dropdown(
        label="Seleccionar lista para gestionar",
        options=[ft.dropdown.Option(t) for t in TABLES],
        on_change=lambda e: cargar_items()
    )

    items_list = ft.ListView(expand=True, spacing=10)
    new_item_input = ft.TextField(label="Nuevo valor", expand=True)

    def cargar_items():
        if not selected_table.value:
            return
        conn = sqlite3.connect("formacion.db")
        cursor = conn.cursor()
        cursor.execute(f"SELECT id, nombre FROM {selected_table.value} WHERE inquilino_id = ?", (tenant_id,))
        items = cursor.fetchall()
        conn.close()

        items_list.controls.clear()
        for item_id, nombre in items:
            items_list.controls.append(
                ft.ListTile(
                    title=ft.Text(nombre),
                    trailing=ft.IconButton(
                        icon=ft.icons.DELETE,
                        icon_color="red",
                        tooltip="Eliminar",
                        data=(item_id, nombre),
                        on_click=handle_delete_item
                    )
                )
            )
        page.update()

    def handle_add_item(e):
        table = selected_table.value
        value = new_item_input.value
        if not table or not value:
            return

        conn = sqlite3.connect("formacion.db")
        cursor = conn.cursor()
        try:
            cursor.execute(f"INSERT INTO {table} (inquilino_id, nombre) VALUES (?, ?)", (tenant_id, value))
            conn.commit()
            new_item_input.value = ""
            cargar_items()
        except sqlite3.IntegrityError:
            page.snack_bar = ft.SnackBar(ft.Text(f"El valor '{value}' ya existe en esta lista."), bgcolor="orange")
            page.snack_bar.open = True
        except Exception as ex:
            page.snack_bar = ft.SnackBar(ft.Text(f"Error: {ex}"), bgcolor="red")
            page.snack_bar.open = True
        finally:
            conn.close()
            page.update()

    def handle_delete_item(e):
        item_id, item_name = e.control.data
        table = selected_table.value

        def on_confirm_delete(e_confirm):
            conn = sqlite3.connect("formacion.db")
            try:
                conn.execute(f"DELETE FROM {table} WHERE id = ?", (item_id,))
                conn.commit()
                cargar_items()
            except Exception as ex:
                 page.snack_bar = ft.SnackBar(ft.Text(f"Error al eliminar: {ex}"), bgcolor="red")
                 page.snack_bar.open = True
            finally:
                conn.close()
                page.dialog.open = False
                page.update()

        page.dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Confirmar Eliminación"),
            content=ft.Text(f"¿Estás seguro de que quieres eliminar '{item_name}' de la lista '{table}'?"),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: setattr(page.dialog, 'open', False) or page.update()),
                ft.ElevatedButton("Eliminar", on_click=on_confirm_delete, bgcolor="red", color="white"),
            ]
        )
        page.dialog.open = True
        page.update()

    return ft.View(
        "/admin/gestion_listas",
        [
            ft.AppBar(title=ft.Text("Gestión de Listas Desplegables")),
            ft.Container(
                padding=20,
                expand=True,
                content=ft.Column([
                    ft.Text("Gestionar Listas", size=22, weight="bold"),
                    selected_table,
                    ft.Row([
                        new_item_input,
                        ft.IconButton(icon=ft.icons.ADD, on_click=handle_add_item, tooltip="Añadir valor")
                    ]),
                    ft.Divider(),
                    items_list,
                ])
            )
        ]
    )
