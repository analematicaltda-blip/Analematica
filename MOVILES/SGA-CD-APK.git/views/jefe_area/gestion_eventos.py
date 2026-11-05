import flet as ft
import sqlite3

def get_jefe_area_info(user_id):
    """
    Fetches the tenant ID and area of responsibility for a given Area Head user ID.
    """
    conn = sqlite3.connect("formacion.db")
    cursor = conn.cursor()

    # First, get the inquilino_id from the usuarios table
    cursor.execute("SELECT inquilino_id FROM usuarios WHERE id = ?", (user_id,))
    inquilino_result = cursor.fetchone()
    if not inquilino_result:
        conn.close()
        return None, None # User not found

    inquilino_id = inquilino_result[0]

    # Then, get the area_responsabilidad from the jefes_area table
    cursor.execute("SELECT area_responsabilidad FROM jefes_area WHERE usuario_id = ?", (user_id,))
    area_result = cursor.fetchone()
    if not area_result:
        conn.close()
        return inquilino_id, None # User is not an Area Head

    area = area_result[0]
    conn.close()
    return inquilino_id, area

def gestion_eventos_view(page: ft.Page, user_id: int):

    inquilino_id, area = get_jefe_area_info(user_id)

    if not inquilino_id or not area:
        # Show an error view if user info can't be retrieved
        return ft.View(
            "/gestion_eventos",
            [
                ft.AppBar(title=ft.Text("Error"), bgcolor=ft.colors.ERROR),
                ft.Text("No se pudo cargar la información del Jefe de Área.", size=20)
            ]
        )

    def load_events():
        conn = sqlite3.connect("formacion.db")
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, nombre, alcance, fecha_inicio, lugar FROM eventos WHERE inquilino_id = ? AND area = ? AND tipo = 'evento' ORDER BY fecha_inicio DESC",
            (inquilino_id, area)
        )
        events = cursor.fetchall()
        conn.close()
        return events

    events_datatable = ft.DataTable(
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
        events_datatable.rows.clear()
        events_list = load_events()
        if not events_list:
            events_datatable.rows.append(ft.DataRow(cells=[ft.DataCell(ft.Text("No hay eventos creados en esta área."), colspan=5)]))
        else:
            for event in events_list:
                events_datatable.rows.append(
                    ft.DataRow(
                        cells=[
                            ft.DataCell(ft.Text(event[1])), # nombre
                            ft.DataCell(ft.Text(event[2])), # alcance
                            ft.DataCell(ft.Text(event[3])), # fecha_inicio
                            ft.DataCell(ft.Text(event[4])), # lugar
                            ft.DataCell(
                                ft.Row([
                                    ft.IconButton(icon=ft.icons.EDIT, on_click=lambda e, event_id=event[0]: open_edit_dialog(event_id), tooltip="Editar Evento"),
                                    ft.IconButton(icon=ft.icons.PEOPLE, on_click=lambda e, event_id=event[0]: manage_participants(event_id), tooltip="Gestionar Participantes"),
                                    ft.IconButton(icon=ft.icons.DELETE, on_click=lambda e, event_id=event[0]: open_delete_dialog(event_id), tooltip="Eliminar Evento"),
                                ])
                            ),
                        ]
                    )
                )
        page.update()

    def save_edited_event(e, event_id):
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
                    event_id
                )
            )
            conn.commit()
            conn.close()

            add_dialog.open = False
            page.snack_bar = ft.SnackBar(ft.Text("¡Evento actualizado exitosamente!"), bgcolor="green")
            page.snack_bar.open = True
            populate_datatable() # Refresh the table
            page.update()

        except Exception as ex:
            page.snack_bar = ft.SnackBar(ft.Text(f"Error al actualizar: {ex}"), bgcolor="red")
            page.snack_bar.open = True
            page.update()

    def open_edit_dialog(event_id):
        # Fetch current event data
        conn = sqlite3.connect("formacion.db")
        cursor = conn.cursor()
        cursor.execute("SELECT nombre, descripcion, alcance, fecha_inicio, fecha_fin, lugar FROM eventos WHERE id = ?", (event_id,))
        event_data = cursor.fetchone()
        conn.close()

        if not event_data:
            page.snack_bar = ft.SnackBar(ft.Text("No se encontró el evento."), bgcolor="red")
            page.snack_bar.open = True
            page.update()
            return

        # Populate dialog fields
        nombre_field.value = event_data[0]
        desc_field.value = event_data[1]
        alcance_dropdown.value = event_data[2]
        lugar_field.value = event_data[5]

        # Handle dates
        if event_data[3]:
            start_date_picker.value = ft.datetime.datetime.strptime(event_data[3], '%Y-%m-%d')
            start_date_text.value = f"Fecha de Inicio: {event_data[3]}"
        else:
            start_date_picker.value = None
            start_date_text.value = ""

        if event_data[4]:
            end_date_picker.value = ft.datetime.datetime.strptime(event_data[4], '%Y-%m-%d')
            end_date_text.value = f"Fecha de Fin: {event_data[4]}"
        else:
            end_date_picker.value = None
            end_date_text.value = ""

        # Configure dialog for editing
        add_dialog.title = ft.Text("Editar Evento")
        add_dialog.actions = [
            ft.TextButton("Cancelar", on_click=close_dialog),
            ft.FilledButton("Guardar Cambios", on_click=lambda e: save_edited_event(e, event_id)),
        ]

        page.dialog = add_dialog
        add_dialog.open = True
        page.update()

    # --- Participant Management Dialog ---
    participants_list_view = ft.ListView(expand=True, spacing=10)
    add_participant_dropdown = ft.Dropdown(label="Añadir Usuario", expand=True)

    def add_participant_to_event(e):
        event_id = participants_dialog.data # Get event_id from dialog's data attribute
        user_to_add_id = add_participant_dropdown.value
        if not event_id or not user_to_add_id:
            return

        try:
            conn = sqlite3.connect("formacion.db")
            cursor = conn.cursor()
            # Check if participant already exists to avoid duplicates
            cursor.execute("SELECT id FROM evento_participantes WHERE evento_id = ? AND usuario_id = ?", (event_id, user_to_add_id))
            if cursor.fetchone():
                page.snack_bar = ft.SnackBar(ft.Text("Este usuario ya es un participante."), bgcolor="orange")
                page.snack_bar.open = True
            else:
                cursor.execute(
                    "INSERT INTO evento_participantes (inquilino_id, evento_id, usuario_id) VALUES (?, ?, ?)",
                    (inquilino_id, event_id, user_to_add_id)
                )
                conn.commit()
                page.snack_bar = ft.SnackBar(ft.Text("Participante añadido."), bgcolor="green")
                page.snack_bar.open = True

            conn.close()
            # Refresh the participant list
            populate_participants_list(event_id)

        except Exception as ex:
            page.snack_bar = ft.SnackBar(ft.Text(f"Error al añadir participante: {ex}"), bgcolor="red")
            page.snack_bar.open = True
            page.update()

    def remove_participant_from_event(e, participant_id):
        event_id = participants_dialog.data
        try:
            conn = sqlite3.connect("formacion.db")
            cursor = conn.cursor()
            cursor.execute("DELETE FROM evento_participantes WHERE evento_id = ? AND usuario_id = ?", (event_id, participant_id))
            conn.commit()
            conn.close()
            page.snack_bar = ft.SnackBar(ft.Text("Participante eliminado."), bgcolor="green")
            page.snack_bar.open = True
            populate_participants_list(event_id)
        except Exception as ex:
            page.snack_bar = ft.SnackBar(ft.Text(f"Error al eliminar participante: {ex}"), bgcolor="red")
            page.snack_bar.open = True
            page.update()

    def populate_participants_list(event_id):
        participants_list_view.controls.clear()
        conn = sqlite3.connect("formacion.db")
        cursor = conn.cursor()
        cursor.execute("""
            SELECT u.id, u.nombre_completo
            FROM evento_participantes ep
            JOIN usuarios u ON ep.usuario_id = u.id
            WHERE ep.evento_id = ?
        """, (event_id,))
        participants = cursor.fetchall()
        conn.close()

        if not participants:
            participants_list_view.controls.append(ft.Text("No hay participantes en este evento."))
        else:
            for p_id, p_name in participants:
                participants_list_view.controls.append(
                    ft.Row([
                        ft.Text(p_name, expand=True),
                        ft.IconButton(icon=ft.icons.REMOVE_CIRCLE_OUTLINE, on_click=lambda e, p_id=p_id: remove_participant_from_event(e, p_id), tooltip="Quitar")
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
            ft.Row([
                add_participant_dropdown,
                ft.IconButton(icon=ft.icons.ADD_CIRCLE, on_click=add_participant_to_event, tooltip="Añadir Participante")
            ]),
            ft.Divider(),
            ft.Container(content=participants_list_view, height=300, border=ft.border.all(1, ft.colors.BLACK26), border_radius=5, padding=10)
        ], height=400, width=500),
        actions=[
            ft.TextButton("Cerrar", on_click=close_participants_dialog),
        ],
    )

    def manage_participants(event_id):
        participants_dialog.data = event_id # Store event_id for other functions to use

        # Load all users (alumnos and profesores) from the same area and tenant
        conn = sqlite3.connect("formacion.db")
        cursor = conn.cursor()
        # This query gets all users who are not already in the event
        cursor.execute("""
            SELECT u.id, u.nombre_completo || ' (' || u.rol || ')' as display_name
            FROM usuarios u
            LEFT JOIN profesores p ON u.id = p.usuario_id AND u.rol = 'profesor'
            WHERE u.inquilino_id = ? AND (p.area = ? OR u.rol = 'alumno')
            AND u.id NOT IN (SELECT usuario_id FROM evento_participantes WHERE evento_id = ?)
            ORDER BY u.nombre_completo
        """, (inquilino_id, area, event_id))
        users = cursor.fetchall()
        conn.close()

        add_participant_dropdown.options = [ft.dropdown.Option(key=user[0], text=user[1]) for user in users]
        add_participant_dropdown.value = None

        # Populate the list of current participants
        populate_participants_list(event_id)

        page.dialog = participants_dialog
        participants_dialog.open = True
        page.update()

    # --- Delete Confirmation Dialog ---
    delete_dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("Confirmar Eliminación"),
        content=ft.Text("¿Está seguro de que desea eliminar este evento? Esta acción no se puede deshacer."),
        actions=[], # Will be populated dynamically
        actions_alignment=ft.MainAxisAlignment.END,
    )

    def delete_event(event_id):
        try:
            conn = sqlite3.connect("formacion.db")
            cursor = conn.cursor()
            # First, delete participants associated with the event
            cursor.execute("DELETE FROM evento_participantes WHERE evento_id = ?", (event_id,))
            # Then, delete the event itself
            cursor.execute("DELETE FROM eventos WHERE id = ?", (event_id,))
            conn.commit()
            conn.close()

            delete_dialog.open = False
            page.snack_bar = ft.SnackBar(ft.Text("Evento eliminado exitosamente."), bgcolor="green")
            page.snack_bar.open = True
            populate_datatable() # Refresh table
            page.update()
        except Exception as ex:
            page.snack_bar = ft.SnackBar(ft.Text(f"Error al eliminar: {ex}"), bgcolor="red")
            page.snack_bar.open = True
            page.update()


    def open_delete_dialog(event_id):
        def on_confirm_delete(e):
            delete_event(event_id)

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

    # --- Dialog and controls for Add/Edit ---
    nombre_field = ft.TextField(label="Nombre del Evento")
    desc_field = ft.TextField(label="Descripción", multiline=True)
    lugar_field = ft.TextField(label="Lugar")
    alcance_dropdown = ft.Dropdown(
        label="Alcance",
        options=[
            ft.dropdown.Option("nacional"),
            ft.dropdown.Option("regional"),
            ft.dropdown.Option("internacional"),
        ]
    )

    def change_start_date(e):
        start_date_text.value = f"Fecha de Inicio: {start_date_picker.value.strftime('%Y-%m-%d')}"
        page.update()

    def change_end_date(e):
        end_date_text.value = f"Fecha de Fin: {end_date_picker.value.strftime('%Y-%m-%d')}"
        page.update()

    start_date_picker = ft.DatePicker(on_change=change_start_date)
    end_date_picker = ft.DatePicker(on_change=change_end_date)
    page.overlay.extend([start_date_picker, end_date_picker]) # Add to page overlay

    start_date_button = ft.ElevatedButton("Seleccionar Inicio", icon=ft.icons.CALENDAR_MONTH, on_click=lambda _: start_date_picker.pick_date())
    start_date_text = ft.Text()
    end_date_button = ft.ElevatedButton("Seleccionar Fin", icon=ft.icons.CALENDAR_MONTH, on_click=lambda _: end_date_picker.pick_date())
    end_date_text = ft.Text()


    add_dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("Crear Nuevo Evento"),
        content=ft.Column([
            nombre_field,
            desc_field,
            lugar_field,
            alcance_dropdown,
            ft.Row([start_date_button, start_date_text]),
            ft.Row([end_date_button, end_date_text]),
        ], scroll=ft.ScrollMode.AUTO, spacing=10, height=400),
        actions=[
            ft.TextButton("Cancelar", on_click=lambda e: close_dialog(e)),
            ft.FilledButton("Guardar", on_click=lambda e: save_new_event(e)),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )

    def close_dialog(e):
        add_dialog.open = False
        page.update()

    def save_new_event(e):
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
                INSERT INTO eventos (inquilino_id, nombre, descripcion, tipo, alcance, area, fecha_inicio, fecha_fin, lugar, creado_por_usuario_id)
                VALUES (?, ?, ?, 'evento', ?, ?, ?, ?, ?, ?)
                """,
                (
                    inquilino_id,
                    nombre_field.value,
                    desc_field.value,
                    alcance_dropdown.value,
                    area,
                    start_date_picker.value.strftime('%Y-%m-%d'),
                    end_date_picker.value.strftime('%Y-%m-%d') if end_date_picker.value else None,
                    lugar_field.value,
                    user_id
                )
            )
            conn.commit()
            conn.close()

            add_dialog.open = False
            page.snack_bar = ft.SnackBar(ft.Text("¡Evento creado exitosamente!"), bgcolor="green")
            page.snack_bar.open = True
            populate_datatable() # Refresh the table
            page.update()

        except Exception as ex:
            page.snack_bar = ft.SnackBar(ft.Text(f"Error al guardar: {ex}"), bgcolor="red")
            page.snack_bar.open = True
            page.update()


    def open_add_dialog(e):
        # Reset fields before opening
        nombre_field.value = ""
        desc_field.value = ""
        lugar_field.value = ""
        alcance_dropdown.value = None
        start_date_picker.value = None
        end_date_picker.value = None
        start_date_text.value = ""
        end_date_text.value = ""

        page.dialog = add_dialog
        add_dialog.open = True
        page.update()

    add_event_button = ft.ElevatedButton("Crear Nuevo Evento", icon=ft.icons.ADD, on_click=open_add_dialog)

    # Initial load
    populate_datatable()

    return ft.View(
        "/gestion_eventos",
        [
            ft.AppBar(title=ft.Text(f"Gestión de Eventos - Área {area}"), bgcolor=ft.colors.SURFACE_VARIANT),
            ft.Container(
                content=ft.Column(
                    [
                        add_event_button,
                        ft.Divider(),
                        ft.Text("Eventos Existentes", style=ft.TextThemeStyle.HEADLINE_SMALL),
                        events_datatable,
                    ],
                    scroll=ft.ScrollMode.AUTO,
                ),
                padding=20,
                expand=True
            )
        ]
    )
