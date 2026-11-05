import flet as ft
import sqlite3
import datetime

def get_jefe_area_info(user_id):
    """
    Fetches the tenant ID and area of responsibility for a given Area Head user ID.
    """
    conn = sqlite3.connect("formacion.db")
    cursor = conn.cursor()

    cursor.execute("SELECT inquilino_id FROM usuarios WHERE id = ?", (user_id,))
    inquilino_result = cursor.fetchone()
    if not inquilino_result:
        conn.close()
        return None, None

    inquilino_id = inquilino_result[0]

    cursor.execute("SELECT area_responsabilidad FROM jefes_area WHERE usuario_id = ?", (user_id,))
    area_result = cursor.fetchone()
    if not area_result:
        conn.close()
        return inquilino_id, None

    area = area_result[0]
    conn.close()
    return inquilino_id, area

def gestion_salidas_view(page: ft.Page, user_id: int):

    inquilino_id, area = get_jefe_area_info(user_id)

    if not inquilino_id or not area:
        return ft.View(
            "/gestion_salidas",
            [
                ft.AppBar(title=ft.Text("Error"), bgcolor=ft.colors.ERROR),
                ft.Text("No se pudo cargar la información del Jefe de Área.", size=20)
            ]
        )

    def load_salidas():
        conn = sqlite3.connect("formacion.db")
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, nombre, alcance, fecha_inicio, lugar FROM eventos WHERE inquilino_id = ? AND area = ? AND tipo = 'salida' ORDER BY fecha_inicio DESC",
            (inquilino_id, area)
        )
        salidas = cursor.fetchall()
        conn.close()
        return salidas

    salidas_datatable = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("Nombre")),
            ft.DataColumn(ft.Text("Alcance")),
            ft.DataColumn(ft.Text("Fecha Inicio")),
            ft.DataColumn(ft.Text("Lugar")),
            ft.DataColumn(ft.Text("Acciones")),
        ],
        rows=[]
    )

    def populate_datatable():
        salidas_datatable.rows.clear()
        salidas_list = load_salidas()
        if not salidas_list:
            salidas_datatable.rows.append(ft.DataRow(cells=[ft.DataCell(ft.Text("No hay salidas creadas en esta área."), colspan=5)]))
        else:
            for salida in salidas_list:
                salidas_datatable.rows.append(
                    ft.DataRow(
                        cells=[
                            ft.DataCell(ft.Text(salida[1])),
                            ft.DataCell(ft.Text(salida[2])),
                            ft.DataCell(ft.Text(salida[3])),
                            ft.DataCell(ft.Text(salida[4])),
                            ft.DataCell(
                                ft.Row([
                                    ft.IconButton(icon=ft.icons.EDIT, on_click=lambda e, salida_id=salida[0]: open_edit_dialog(salida_id), tooltip="Editar Salida"),
                                    ft.IconButton(icon=ft.icons.PEOPLE, on_click=lambda e, salida_id=salida[0]: manage_participants(salida_id), tooltip="Gestionar Participantes"),
                                    ft.IconButton(icon=ft.icons.DELETE, on_click=lambda e, salida_id=salida[0]: open_delete_dialog(salida_id), tooltip="Eliminar Salida"),
                                ])
                            ),
                        ]
                    )
                )
        page.update()

    def save_edited_salida(e, salida_id):
        if not nombre_field.value or not alcance_dropdown.value or not start_date_picker.value:
            page.snack_bar = ft.SnackBar(ft.Text("Nombre, Alcance y Fecha de Inicio son obligatorios."), bgcolor="red")
            page.snack_bar.open = True
            page.update()
            return

        try:
            conn = sqlite3.connect("formacion.db")
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE eventos
                SET nombre = ?, descripcion = ?, alcance = ?, fecha_inicio = ?, fecha_fin = ?, lugar = ?
                WHERE id = ?
                """,
                (
                    nombre_field.value,
                    desc_field.value,
                    alcance_dropdown.value,
                    start_date_picker.value.strftime('%Y-%m-%d'),
                    end_date_picker.value.strftime('%Y-%m-%d') if end_date_picker.value else None,
                    lugar_field.value,
                    salida_id
                )
            )
            conn.commit()
            conn.close()

            dialog.open = False
            page.snack_bar = ft.SnackBar(ft.Text("¡Salida actualizada exitosamente!"), bgcolor="green")
            page.snack_bar.open = True
            populate_datatable()
            page.update()

        except Exception as ex:
            page.snack_bar = ft.SnackBar(ft.Text(f"Error al actualizar: {ex}"), bgcolor="red")
            page.snack_bar.open = True
            page.update()

    def open_edit_dialog(salida_id):
        conn = sqlite3.connect("formacion.db")
        cursor = conn.cursor()
        cursor.execute("SELECT nombre, descripcion, alcance, fecha_inicio, fecha_fin, lugar FROM eventos WHERE id = ?", (salida_id,))
        salida_data = cursor.fetchone()
        conn.close()

        if not salida_data:
            page.snack_bar = ft.SnackBar(ft.Text("No se encontró la salida."), bgcolor="red")
            page.snack_bar.open = True
            page.update()
            return

        nombre_field.value = salida_data[0]
        desc_field.value = salida_data[1]
        alcance_dropdown.value = salida_data[2]
        lugar_field.value = salida_data[5]

        if salida_data[3]:
            start_date_picker.value = datetime.datetime.strptime(salida_data[3], '%Y-%m-%d')
            start_date_text.value = f"Fecha de Inicio: {salida_data[3]}"
        else:
            start_date_picker.value = None
            start_date_text.value = ""

        if salida_data[4]:
            end_date_picker.value = datetime.datetime.strptime(salida_data[4], '%Y-%m-%d')
            end_date_text.value = f"Fecha de Fin: {salida_data[4]}"
        else:
            end_date_picker.value = None
            end_date_text.value = ""

        dialog.title = ft.Text("Editar Salida")
        dialog.actions = [
            ft.TextButton("Cancelar", on_click=close_dialog),
            ft.FilledButton("Guardar Cambios", on_click=lambda e: save_edited_salida(e, salida_id)),
        ]

        page.dialog = dialog
        dialog.open = True
        page.update()

    participants_list_view = ft.ListView(expand=True, spacing=10)
    add_participant_dropdown = ft.Dropdown(label="Añadir Usuario", expand=True)

    def add_participant_to_salida(e):
        salida_id = participants_dialog.data
        user_to_add_id = add_participant_dropdown.value
        if not salida_id or not user_to_add_id:
            return

        try:
            conn = sqlite3.connect("formacion.db")
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM evento_participantes WHERE evento_id = ? AND usuario_id = ?", (salida_id, user_to_add_id))
            if cursor.fetchone():
                page.snack_bar = ft.SnackBar(ft.Text("Este usuario ya es un participante."), bgcolor="orange")
            else:
                cursor.execute(
                    "INSERT INTO evento_participantes (inquilino_id, evento_id, usuario_id) VALUES (?, ?, ?)",
                    (inquilino_id, salida_id, user_to_add_id)
                )
                conn.commit()
                page.snack_bar = ft.SnackBar(ft.Text("Participante añadido."), bgcolor="green")

            conn.close()
            populate_participants_list(salida_id)

        except Exception as ex:
            page.snack_bar = ft.SnackBar(ft.Text(f"Error al añadir participante: {ex}"), bgcolor="red")
            page.snack_bar.open = True
            page.update()

    def remove_participant_from_salida(e, participant_id):
        salida_id = participants_dialog.data
        try:
            conn = sqlite3.connect("formacion.db")
            cursor = conn.cursor()
            cursor.execute("DELETE FROM evento_participantes WHERE evento_id = ? AND usuario_id = ?", (salida_id, participant_id))
            conn.commit()
            conn.close()
            page.snack_bar = ft.SnackBar(ft.Text("Participante eliminado."), bgcolor="green")
            populate_participants_list(salida_id)
        except Exception as ex:
            page.snack_bar = ft.SnackBar(ft.Text(f"Error al eliminar participante: {ex}"), bgcolor="red")
            page.snack_bar.open = True
            page.update()

    def populate_participants_list(salida_id):
        participants_list_view.controls.clear()
        conn = sqlite3.connect("formacion.db")
        cursor = conn.cursor()
        cursor.execute("SELECT u.id, u.nombre_completo FROM evento_participantes ep JOIN usuarios u ON ep.usuario_id = u.id WHERE ep.evento_id = ?", (salida_id,))
        participants = cursor.fetchall()
        conn.close()

        if not participants:
            participants_list_view.controls.append(ft.Text("No hay participantes en esta salida."))
        else:
            for p_id, p_name in participants:
                participants_list_view.controls.append(
                    ft.Row([
                        ft.Text(p_name, expand=True),
                        ft.IconButton(icon=ft.icons.REMOVE_CIRCLE_OUTLINE, on_click=lambda e, p_id=p_id: remove_participant_from_salida(e, p_id), tooltip="Quitar")
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
                )
        page.update()

    def close_participants_dialog(e):
        participants_dialog.open = False
        page.update()

    participants_dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("Gestionar Participantes"),
        content=ft.Column([
            ft.Row([add_participant_dropdown, ft.IconButton(icon=ft.icons.ADD_CIRCLE, on_click=add_participant_to_salida, tooltip="Añadir Participante")]),
            ft.Divider(),
            ft.Container(content=participants_list_view, height=300, border=ft.border.all(1, ft.colors.BLACK26), border_radius=5, padding=10)
        ], height=400, width=500),
        actions=[ft.TextButton("Cerrar", on_click=close_participants_dialog)],
    )

    def manage_participants(salida_id):
        participants_dialog.data = salida_id
        conn = sqlite3.connect("formacion.db")
        cursor = conn.cursor()
        cursor.execute("""
            SELECT u.id, u.nombre_completo || ' (' || u.rol || ')' as display_name
            FROM usuarios u
            LEFT JOIN profesores p ON u.id = p.usuario_id AND u.rol = 'profesor'
            WHERE u.inquilino_id = ? AND (p.area = ? OR u.rol = 'alumno')
            AND u.id NOT IN (SELECT usuario_id FROM evento_participantes WHERE evento_id = ?)
            ORDER BY u.nombre_completo
        """, (inquilino_id, area, salida_id))
        users = cursor.fetchall()
        conn.close()

        add_participant_dropdown.options = [ft.dropdown.Option(key=user[0], text=user[1]) for user in users]
        add_participant_dropdown.value = None
        populate_participants_list(salida_id)
        page.dialog = participants_dialog
        participants_dialog.open = True
        page.update()

    delete_dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("Confirmar Eliminación"),
        content=ft.Text("¿Está seguro de que desea eliminar esta salida? Esta acción no se puede deshacer."),
        actions=[],
        actions_alignment=ft.MainAxisAlignment.END,
    )

    def delete_salida(salida_id):
        try:
            conn = sqlite3.connect("formacion.db")
            cursor = conn.cursor()
            cursor.execute("DELETE FROM evento_participantes WHERE evento_id = ?", (salida_id,))
            cursor.execute("DELETE FROM eventos WHERE id = ?", (salida_id,))
            conn.commit()
            conn.close()
            delete_dialog.open = False
            page.snack_bar = ft.SnackBar(ft.Text("Salida eliminada exitosamente."), bgcolor="green")
            populate_datatable()
        except Exception as ex:
            page.snack_bar = ft.SnackBar(ft.Text(f"Error al eliminar: {ex}"), bgcolor="red")
        page.snack_bar.open = True
        page.update()

    def open_delete_dialog(salida_id):
        def on_confirm_delete(e):
            delete_salida(salida_id)

        delete_dialog.actions = [
            ft.TextButton("Cancelar", on_click=lambda e: close_delete_dialog(e)),
            ft.FilledButton("Eliminar", on_click=on_confirm_delete, bgcolor=ft.colors.RED),
        ]
        page.dialog = delete_dialog
        delete_dialog.open = True
        page.update()

    def close_delete_dialog(e):
        delete_dialog.open = False
        page.update()

    nombre_field = ft.TextField(label="Nombre de la Salida")
    desc_field = ft.TextField(label="Descripción", multiline=True)
    lugar_field = ft.TextField(label="Lugar/Destino")
    alcance_dropdown = ft.Dropdown(label="Alcance", options=[ft.dropdown.Option("nacional"), ft.dropdown.Option("regional"), ft.dropdown.Option("internacional")])

    def change_start_date(e):
        start_date_text.value = f"Fecha de Inicio: {start_date_picker.value.strftime('%Y-%m-%d')}"
        page.update()

    def change_end_date(e):
        end_date_text.value = f"Fecha de Fin: {end_date_picker.value.strftime('%Y-%m-%d')}"
        page.update()

    start_date_picker = ft.DatePicker(on_change=change_start_date)
    end_date_picker = ft.DatePicker(on_change=change_end_date)
    page.overlay.extend([start_date_picker, end_date_picker])

    start_date_button = ft.ElevatedButton("Seleccionar Inicio", icon=ft.icons.CALENDAR_MONTH, on_click=lambda _: start_date_picker.pick_date())
    start_date_text = ft.Text()
    end_date_button = ft.ElevatedButton("Seleccionar Fin", icon=ft.icons.CALENDAR_MONTH, on_click=lambda _: end_date_picker.pick_date())
    end_date_text = ft.Text()

    dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("Crear Nueva Salida"),
        content=ft.Column([
            nombre_field, desc_field, lugar_field, alcance_dropdown,
            ft.Row([start_date_button, start_date_text]),
            ft.Row([end_date_button, end_date_text]),
        ], scroll=ft.ScrollMode.AUTO, spacing=10, height=400),
        actions=[ft.TextButton("Cancelar", on_click=lambda e: close_dialog(e)), ft.FilledButton("Guardar", on_click=lambda e: save_new_salida(e))],
        actions_alignment=ft.MainAxisAlignment.END,
    )

    def close_dialog(e):
        dialog.open = False
        page.update()

    def save_new_salida(e):
        if not nombre_field.value or not alcance_dropdown.value or not start_date_picker.value:
            page.snack_bar = ft.SnackBar(ft.Text("Nombre, Alcance y Fecha de Inicio son obligatorios."), bgcolor="red")
            page.snack_bar.open = True
            page.update()
            return

        try:
            conn = sqlite3.connect("formacion.db")
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO eventos (inquilino_id, nombre, descripcion, tipo, alcance, area, fecha_inicio, fecha_fin, lugar, creado_por_usuario_id) VALUES (?, ?, ?, 'salida', ?, ?, ?, ?, ?, ?)",
                (inquilino_id, nombre_field.value, desc_field.value, alcance_dropdown.value, area, start_date_picker.value.strftime('%Y-%m-%d'), end_date_picker.value.strftime('%Y-%m-%d') if end_date_picker.value else None, lugar_field.value, user_id)
            )
            conn.commit()
            conn.close()

            dialog.open = False
            page.snack_bar = ft.SnackBar(ft.Text("¡Salida creada exitosamente!"), bgcolor="green")
            populate_datatable()
        except Exception as ex:
            page.snack_bar = ft.SnackBar(ft.Text(f"Error al guardar: {ex}"), bgcolor="red")
        page.snack_bar.open = True
        page.update()

    def open_add_dialog(e):
        nombre_field.value = ""
        desc_field.value = ""
        lugar_field.value = ""
        alcance_dropdown.value = None
        start_date_picker.value = None
        end_date_picker.value = None
        start_date_text.value = ""
        end_date_text.value = ""

        dialog.title = ft.Text("Crear Nueva Salida")
        dialog.actions = [
            ft.TextButton("Cancelar", on_click=close_dialog),
            ft.FilledButton("Guardar", on_click=save_new_salida),
        ]
        page.dialog = dialog
        dialog.open = True
        page.update()

    add_salida_button = ft.ElevatedButton("Crear Nueva Salida", icon=ft.icons.ADD, on_click=open_add_dialog)

    populate_datatable()

    return ft.View(
        "/gestion_salidas",
        [
            ft.AppBar(title=ft.Text(f"Gestión de Salidas - Área {area}"), bgcolor=ft.colors.SURFACE_VARIANT),
            ft.Container(
                content=ft.Column(
                    [
                        add_salida_button,
                        ft.Divider(),
                        ft.Text("Salidas Existentes", style=ft.TextThemeStyle.HEADLINE_SMALL),
                        salidas_datatable,
                    ],
                    scroll=ft.ScrollMode.AUTO,
                ),
                padding=20,
                expand=True
            )
        ]
    )
