import flet as ft
import sqlite3

def get_instructor_info(user_id):
    conn = sqlite3.connect("formacion.db")
    cursor = conn.cursor()
    cursor.execute("SELECT inquilino_id, area FROM profesores WHERE usuario_id = ?", (user_id,))
    result = cursor.fetchone()
    conn.close()
    if result:
        return result[0], result[1]
    return None, None

def definir_curriculo_view(page: ft.Page, user_id: int):
    inquilino_id, area = get_instructor_info(user_id)

    if not inquilino_id:
        return ft.View("/definir_curriculo", [ft.AppBar(title=ft.Text("Error")), ft.Text("No se pudo cargar la información del instructor.")])

    # --- State Management ---
    selected_plan_id = ft.Ref[int]()

    # --- UI Controls ---
    plans_list = ft.ListView(expand=True, spacing=10)
    topics_column = ft.Column(
        expand=True,
        controls=[ft.Text("Seleccione un plan de la izquierda para ver y editar sus temas.", text_align=ft.TextAlign.CENTER)]
    )

    def load_plans():
        plans_list.controls.clear()
        conn = sqlite3.connect("formacion.db")
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, nombre_plan FROM plan_curricular WHERE creado_por_usuario_id = ?", (user_id,)
        )
        plans = cursor.fetchall()
        conn.close()
        if not plans:
            plans_list.controls.append(ft.Text("No ha creado ningún plan curricular."))
        else:
            for plan_id, plan_name in plans:
                plans_list.controls.append(
                    ft.ListTile(
                        title=ft.Text(plan_name),
                        on_click=lambda e, p_id=plan_id: select_plan(p_id),
                        leading=ft.Icon(ft.icons.BOOK),
                    )
                )
        page.update()

    def select_plan(plan_id: int):
        selected_plan_id.current = plan_id
        load_topics_for_plan(plan_id)
        page.update()

    def load_topics_for_plan(plan_id: int):
        topics_column.controls.clear()
        conn = sqlite3.connect("formacion.db")
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, nombre_tema, descripcion_tema FROM plan_curricular_temas WHERE plan_curricular_id = ? ORDER BY orden",
            (plan_id,)
        )
        topics = cursor.fetchall()
        conn.close()

        topic_cards = []
        if not topics:
            topic_cards.append(ft.Text("Este plan no tiene temas. ¡Añada el primero!"))
        else:
            for topic_id, topic_name, topic_desc in topics:
                topic_cards.append(
                    ft.Card(
                        content=ft.ListTile(
                            title=ft.Text(topic_name, weight="bold"),
                            subtitle=ft.Text(topic_desc),
                            trailing=ft.Row([
                                ft.IconButton(icon=ft.icons.ARROW_UPWARD, on_click=lambda e, t_id=topic_id: move_topic(t_id, "up"), tooltip="Mover Arriba"),
                                ft.IconButton(icon=ft.icons.ARROW_DOWNWARD, on_click=lambda e, t_id=topic_id: move_topic(t_id, "down"), tooltip="Mover Abajo"),
                                ft.IconButton(icon=ft.icons.EDIT, on_click=lambda e, t_id=topic_id: open_edit_topic_dialog(t_id), tooltip="Editar Tema"),
                                ft.IconButton(icon=ft.icons.DELETE, on_click=lambda e, t_id=topic_id: open_delete_topic_dialog(t_id), tooltip="Eliminar Tema"),
                                ft.IconButton(icon=ft.icons.ATTACH_FILE, on_click=lambda e, t_id=topic_id, t_name=topic_name: open_content_dialog(t_id, t_name), tooltip="Gestionar Contenido"),
                            ])
                        )
                    )
                )

        add_topic_button = ft.ElevatedButton("Añadir Nuevo Tema", icon=ft.icons.ADD, on_click=open_add_topic_dialog)

        topics_column.controls.extend([
            ft.Text(f"Temas del Plan", style=ft.TextThemeStyle.HEADLINE_SMALL),
            ft.Column(controls=topic_cards, scroll=ft.ScrollMode.AUTO),
            add_topic_button
        ])
        page.update()

    # --- Placeholder Dialogs and Functions ---
    # --- Add/Edit Plan Dialog ---
    plan_nombre_field = ft.TextField(label="Nombre del Plan")
    plan_desc_field = ft.TextField(label="Descripción", multiline=True)
    proceso_dropdown = ft.Dropdown(label="Proceso de Formación Asociado")

    def load_procesos_formacion():
        conn = sqlite3.connect("formacion.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id, nombre_proceso FROM procesos_formacion WHERE inquilino_id = ?", (inquilino_id,))
        procesos = cursor.fetchall()
        conn.close()
        proceso_dropdown.options = [ft.dropdown.Option(key=p[0], text=p[1]) for p in procesos]

    plan_dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("Crear Nuevo Plan Curricular"),
        content=ft.Column([
            plan_nombre_field,
            plan_desc_field,
            proceso_dropdown,
        ]),
        actions=[
            ft.TextButton("Cancelar", on_click=lambda e: close_dialog(e)),
            ft.FilledButton("Guardar", on_click=lambda e: save_new_plan(e)),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )

    def close_dialog(e):
        plan_dialog.open = False
        page.update()

    def save_new_plan(e):
        if not plan_nombre_field.value:
            page.snack_bar = ft.SnackBar(ft.Text("El nombre del plan es obligatorio."), bgcolor="red")
            page.snack_bar.open = True
            page.update()
            return

        try:
            conn = sqlite3.connect("formacion.db")
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO plan_curricular (inquilino_id, nombre_plan, descripcion, creado_por_usuario_id, proceso_id, area)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (inquilino_id, plan_nombre_field.value, plan_desc_field.value, user_id, proceso_dropdown.value, area)
            )
            conn.commit()
            conn.close()
            plan_dialog.open = False
            page.snack_bar = ft.SnackBar(ft.Text("Plan creado exitosamente."), bgcolor="green")
            load_plans() # Refresh the list
            page.update()
        except Exception as ex:
            page.snack_bar = ft.SnackBar(ft.Text(f"Error al crear el plan: {ex}"), bgcolor="red")
            page.snack_bar.open = True
            page.update()

    def open_add_plan_dialog(e):
        # Reset fields
        plan_nombre_field.value = ""
        plan_desc_field.value = ""
        load_procesos_formacion() # Load latest procesos
        proceso_dropdown.value = None

        page.dialog = plan_dialog
        plan_dialog.open = True
        page.update()

    # --- Add/Edit Topic Dialog ---
    topic_nombre_field = ft.TextField(label="Nombre del Tema")
    topic_desc_field = ft.TextField(label="Descripción del Tema", multiline=True)

    topic_dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("Añadir Nuevo Tema"),
        content=ft.Column([
            topic_nombre_field,
            topic_desc_field,
        ]),
        actions=[
            ft.TextButton("Cancelar", on_click=lambda e: close_topic_dialog(e)),
            ft.FilledButton("Guardar", on_click=lambda e: save_new_topic(e)),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )

    def close_topic_dialog(e):
        topic_dialog.open = False
        page.update()

    def save_new_topic(e):
        current_plan_id = selected_plan_id.current
        if not topic_nombre_field.value or not current_plan_id:
            page.snack_bar = ft.SnackBar(ft.Text("El nombre del tema es obligatorio."), bgcolor="red")
            page.snack_bar.open = True
            page.update()
            return

        try:
            conn = sqlite3.connect("formacion.db")
            cursor = conn.cursor()
            # Get the next order number
            cursor.execute("SELECT MAX(orden) FROM plan_curricular_temas WHERE plan_curricular_id = ?", (current_plan_id,))
            max_orden = cursor.fetchone()[0]
            next_orden = (max_orden or 0) + 1

            cursor.execute(
                """
                INSERT INTO plan_curricular_temas (plan_curricular_id, nombre_tema, descripcion_tema, orden)
                VALUES (?, ?, ?, ?)
                """,
                (current_plan_id, topic_nombre_field.value, topic_desc_field.value, next_orden)
            )
            conn.commit()
            conn.close()
            topic_dialog.open = False
            page.snack_bar = ft.SnackBar(ft.Text("Tema añadido exitosamente."), bgcolor="green")
            load_topics_for_plan(current_plan_id) # Refresh the topics list
            page.update()
        except Exception as ex:
            page.snack_bar = ft.SnackBar(ft.Text(f"Error al añadir el tema: {ex}"), bgcolor="red")
            page.snack_bar.open = True
            page.update()

    def open_add_topic_dialog(e):
        # Reset fields
        topic_nombre_field.value = ""
        topic_desc_field.value = ""

        topic_dialog.title = ft.Text("Añadir Nuevo Tema")
        topic_dialog.actions = [
            ft.TextButton("Cancelar", on_click=close_topic_dialog),
            ft.FilledButton("Guardar", on_click=save_new_topic),
        ]

        page.dialog = topic_dialog
        topic_dialog.open = True
        page.update()

    def save_edited_topic(e, topic_id):
        current_plan_id = selected_plan_id.current
        if not topic_nombre_field.value:
            page.snack_bar = ft.SnackBar(ft.Text("El nombre del tema es obligatorio."), bgcolor="red")
            return

        try:
            conn = sqlite3.connect("formacion.db")
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE plan_curricular_temas SET nombre_tema = ?, descripcion_tema = ? WHERE id = ?",
                (topic_nombre_field.value, topic_desc_field.value, topic_id)
            )
            conn.commit()
            conn.close()
            topic_dialog.open = False
            page.snack_bar = ft.SnackBar(ft.Text("Tema actualizado."), bgcolor="green")
            load_topics_for_plan(current_plan_id)
            page.update()
        except Exception as ex:
            page.snack_bar = ft.SnackBar(ft.Text(f"Error al actualizar tema: {ex}"), bgcolor="red")
            page.snack_bar.open = True
            page.update()

    def open_edit_topic_dialog(topic_id):
        conn = sqlite3.connect("formacion.db")
        cursor = conn.cursor()
        cursor.execute("SELECT nombre_tema, descripcion_tema FROM plan_curricular_temas WHERE id = ?", (topic_id,))
        topic_data = cursor.fetchone()
        conn.close()

        if topic_data:
            topic_nombre_field.value = topic_data[0]
            topic_desc_field.value = topic_data[1]
            topic_dialog.title = ft.Text("Editar Tema")
            topic_dialog.actions = [
                ft.TextButton("Cancelar", on_click=close_topic_dialog),
                ft.FilledButton("Guardar Cambios", on_click=lambda e: save_edited_topic(e, topic_id)),
            ]
            page.dialog = topic_dialog
            topic_dialog.open = True
            page.update()

    delete_topic_dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("Confirmar Eliminación"),
        content=ft.Text("¿Está seguro de que desea eliminar este tema?"),
        actions_alignment=ft.MainAxisAlignment.END,
    )

    def delete_topic(topic_id):
        current_plan_id = selected_plan_id.current
        try:
            conn = sqlite3.connect("formacion.db")
            cursor = conn.cursor()
            # Note: A more robust implementation would check if this topic is in use in the planner or progress tracker.
            # For now, we'll just delete it.
            cursor.execute("DELETE FROM plan_curricular_temas WHERE id = ?", (topic_id,))
            conn.commit()
            conn.close()
            delete_topic_dialog.open = False
            page.snack_bar = ft.SnackBar(ft.Text("Tema eliminado."), bgcolor="green")
            load_topics_for_plan(current_plan_id)
            page.update()
        except Exception as ex:
            page.snack_bar = ft.SnackBar(ft.Text(f"Error al eliminar tema: {ex}"), bgcolor="red")
            page.snack_bar.open = True
            page.update()

    def open_delete_topic_dialog(topic_id):
        delete_topic_dialog.actions = [
            ft.TextButton("Cancelar", on_click=lambda e: setattr(delete_topic_dialog, 'open', False) or page.update()),
            ft.FilledButton("Eliminar", on_click=lambda e: delete_topic(topic_id), bgcolor=ft.colors.RED),
        ]
        page.dialog = delete_topic_dialog
        delete_topic_dialog.open = True
        page.update()

    def move_topic(topic_id, direction):
        current_plan_id = selected_plan_id.current
        conn = sqlite3.connect("formacion.db")
        cursor = conn.cursor()

        try:
            # Get current topic's order
            cursor.execute("SELECT orden FROM plan_curricular_temas WHERE id = ?", (topic_id,))
            current_order = cursor.fetchone()[0]

            # Find the topic to swap with
            swap_order = current_order - 1 if direction == "up" else current_order + 1
            if swap_order <= 0: # Cannot move further up
                return

            cursor.execute(
                "SELECT id, orden FROM plan_curricular_temas WHERE plan_curricular_id = ? AND orden = ?",
                (current_plan_id, swap_order)
            )
            swap_topic = cursor.fetchone()

            if swap_topic:
                swap_topic_id, _ = swap_topic
                # Swap the 'orden' values in a single transaction
                cursor.execute("UPDATE plan_curricular_temas SET orden = -1 WHERE id = ?", (topic_id,)) # Temp value
                cursor.execute("UPDATE plan_curricular_temas SET orden = ? WHERE id = ?", (current_order, swap_topic_id))
                cursor.execute("UPDATE plan_curricular_temas SET orden = ? WHERE id = ?", (swap_order, topic_id))
                conn.commit()
                load_topics_for_plan(current_plan_id) # Refresh view

        except Exception as ex:
            conn.rollback()
            page.snack_bar = ft.SnackBar(ft.Text(f"Error al mover tema: {ex}"), bgcolor="red")
            page.snack_bar.open = True
            page.update()
        finally:
            conn.close()

    # --- Content Management Dialog ---
    def on_file_picker_result(e: ft.FilePickerResultEvent):
        topic_id = e.control.data
        if not e.files:
            return

        # This is a simulation. In a real app, the upload handler would be more complex.
        # For now, we just register the file name. A real implementation needs to handle the binary data.
        source_file = e.files[0]
        destination_path = f"uploads/{source_file.name}"

        try:
            conn = sqlite3.connect("formacion.db")
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO contenido_curricular (tema_id, tipo_contenido, titulo, ruta_archivo_o_url, subido_por_usuario_id)
                VALUES (?, ?, ?, ?, ?)
                """,
                (topic_id, "pdf", source_file.name, destination_path, user_id)
            )
            conn.commit()
            conn.close()
            page.snack_bar = ft.SnackBar(ft.Text(f"Archivo '{source_file.name}' registrado."), bgcolor="green")
            content_dialog.open = False
        except Exception as ex:
            page.snack_bar = ft.SnackBar(ft.Text(f"Error al registrar archivo: {ex}"), bgcolor="red")

        page.snack_bar.open = True
        page.update()

    file_picker = ft.FilePicker(on_result=on_file_picker_result)
    page.overlay.append(file_picker)

    content_list_view = ft.ListView(expand=True)
    link_url_field = ft.TextField(label="URL del Enlace", expand=True)
    link_title_field = ft.TextField(label="Título del Enlace", expand=True)

    def add_link():
        topic_id = content_dialog.data
        if not link_url_field.value or not link_title_field.value:
            return
        try:
            conn = sqlite3.connect("formacion.db")
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO contenido_curricular (tema_id, tipo_contenido, titulo, ruta_archivo_o_url, subido_por_usuario_id)
                VALUES (?, 'enlace', ?, ?, ?)
                """,
                (topic_id, link_title_field.value, link_url_field.value, user_id)
            )
            conn.commit()
            conn.close()
            link_url_field.value = ""
            link_title_field.value = ""
            open_content_dialog(topic_id, "")
        except Exception as ex:
            page.snack_bar = ft.SnackBar(ft.Text(f"Error al añadir enlace: {ex}"), bgcolor="red")
            page.snack_bar.open = True
            page.update()

    def delete_content(content_id):
        topic_id = content_dialog.data
        try:
            conn = sqlite3.connect("formacion.db")
            cursor = conn.cursor()
            cursor.execute("DELETE FROM contenido_curricular WHERE id = ?", (content_id,))
            conn.commit()
            conn.close()
            open_content_dialog(topic_id, "")
        except Exception as ex:
            page.snack_bar = ft.SnackBar(ft.Text(f"Error al eliminar contenido: {ex}"), bgcolor="red")
            page.snack_bar.open = True
            page.update()

    content_dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("Gestionar Contenido"),
        content=ft.Container(
            ft.Column([
                ft.Text("Contenido Existente:"),
                content_list_view,
                ft.Divider(),
                ft.Text("Añadir Nuevo Contenido:"),
                ft.Row([link_title_field, link_url_field, ft.IconButton(icon=ft.icons.ADD, on_click=lambda e: add_link(), tooltip="Añadir Enlace")]),
                ft.ElevatedButton("Subir Archivo", icon=ft.icons.UPLOAD_FILE, on_click=lambda _: file_picker.pick_files(allow_multiple=False)),
            ]),
            width=600, height=400
        ),
        actions=[ft.TextButton("Cerrar", on_click=lambda e: setattr(content_dialog, 'open', False) or page.update())]
    )

    def open_content_dialog(topic_id, topic_name):
        content_dialog.data = topic_id
        content_dialog.title = ft.Text(f"Contenido para: {topic_name}")
        file_picker.data = topic_id

        content_list_view.controls.clear()
        conn = sqlite3.connect("formacion.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id, titulo, tipo_contenido, ruta_archivo_o_url FROM contenido_curricular WHERE tema_id = ?", (topic_id,))
        contents = cursor.fetchall()
        conn.close()

        if not contents:
            content_list_view.controls.append(ft.Text("No hay contenido para este tema."))
        else:
            for c_id, title, c_type, c_path in contents:
                icon = ft.icons.LINK if c_type == 'enlace' else ft.icons.PICTURE_AS_PDF
                content_list_view.controls.append(
                    ft.ListTile(
                        leading=ft.Icon(icon),
                        title=ft.Text(title),
                        subtitle=ft.Text(c_path, no_wrap=True),
                        trailing=ft.IconButton(icon=ft.icons.DELETE_FOREVER, on_click=lambda e, c_id=c_id: delete_content(c_id))
                    )
                )
        page.dialog = content_dialog
        content_dialog.open = True
        page.update()

    # --- Main Layout ---
    add_plan_button = ft.ElevatedButton("Crear Nuevo Plan", icon=ft.icons.ADD, on_click=open_add_plan_dialog, expand=True)

    left_column = ft.Column(
        [
            ft.Text("Mis Planes Curriculares", style=ft.TextThemeStyle.HEADLINE_SMALL),
            ft.Container(content=plans_list, border=ft.border.all(1, ft.colors.BLACK26), border_radius=5, expand=True, padding=5),
            add_plan_button,
        ],
        expand=1,
        spacing=10
    )

    right_column = ft.Container(
        content=topics_column,
        expand=3,
        padding=10,
    )

    # Initial data load
    load_plans()

    return ft.View(
        "/definir_curriculo",
        [
            ft.AppBar(title=ft.Text("Definición de Currículo"), bgcolor=ft.colors.SURFACE_VARIANT),
            ft.Row(
                [
                    left_column,
                    ft.VerticalDivider(),
                    right_column,
                ],
                expand=True,
            )
        ]
    )
