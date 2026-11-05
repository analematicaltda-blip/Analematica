import flet as ft
import sqlite3

def seguimiento_progreso_view(page: ft.Page, user_id: int):

    status_colors = {
        "no_iniciado": ft.colors.GREY_300,
        "en_progreso": ft.colors.BLUE_100,
        "completado": ft.colors.GREEN_200,
        "necesita_refuerzo": ft.colors.AMBER_200,
    }

    def get_instructor_plans():
        conn = sqlite3.connect("formacion.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id, nombre_plan FROM plan_curricular WHERE creado_por_usuario_id = ?", (user_id,))
        plans = cursor.fetchall()
        conn.close()
        return [ft.dropdown.Option(key=p[0], text=p[1]) for p in plans]

    plan_selector = ft.Dropdown(
        label="Seleccionar Plan Curricular",
        options=get_instructor_plans(),
        on_change=lambda e: update_matrix(),
        expand=True
    )

    progress_matrix = ft.DataTable(columns=[], rows=[])

    def get_data_for_matrix(plan_id):
        conn = sqlite3.connect("formacion.db")
        cursor = conn.cursor()

        # 1. Get topics for the plan
        cursor.execute("SELECT id, nombre_tema FROM plan_curricular_temas WHERE plan_curricular_id = ? ORDER BY orden", (plan_id,))
        topics = cursor.fetchall()

        # 2. Get students enrolled with this instructor
        cursor.execute("""
            SELECT DISTINCT u.id, u.nombre_completo
            FROM usuarios u
            JOIN alumnos a ON u.id = a.usuario_id
            JOIN inscripciones i ON a.id = i.alumno_id
            JOIN clases c ON i.clase_id = c.id
            WHERE c.instructor_id = ?
        """, (user_id,))
        students = cursor.fetchall()

        # 3. Get all progress data for these students and topics
        topic_ids = [t[0] for t in topics]
        student_ids = [s[0] for s in students]

        progress_data = {}
        if topic_ids and student_ids:
            query = f"""
                SELECT alumno_usuario_id, tema_id, estado
                FROM progreso_alumno_tema
                WHERE alumno_usuario_id IN ({','.join(['?']*len(student_ids))})
                AND tema_id IN ({','.join(['?']*len(topic_ids))})
            """
            params = student_ids + topic_ids
            cursor.execute(query, params)
            for student_id, topic_id, estado in cursor.fetchall():
                if student_id not in progress_data:
                    progress_data[student_id] = {}
                progress_data[student_id][topic_id] = estado

        conn.close()
        return topics, students, progress_data

    def update_matrix():
        plan_id = plan_selector.value
        if not plan_id:
            progress_matrix.columns = []
            progress_matrix.rows = [ft.DataRow(cells=[ft.DataCell(ft.Text("Por favor, seleccione un plan para ver el progreso."))])]
            page.update()
            return

        topics, students, progress_data = get_data_for_matrix(plan_id)

        progress_matrix.columns = [ft.DataColumn(ft.Text("Alumno"))] + [
            ft.DataColumn(ft.Text(topic_name)) for _, topic_name in topics
        ]

        progress_matrix.rows = []
        for student_id, student_name in students:
            row_cells = [ft.DataCell(ft.Text(student_name))]
            for topic_id, _ in topics:
                status = progress_data.get(student_id, {}).get(topic_id, "no_iniciado")
                row_cells.append(
                    ft.DataCell(
                        ft.Container(
                            content=ft.Text(status.replace("_", " ").capitalize(), size=11),
                            bgcolor=status_colors.get(status, ft.colors.GREY),
                            padding=5,
                            border_radius=5,
                            on_click=lambda e, s_id=student_id, t_id=topic_id: open_update_dialog(s_id, t_id, status),
                            tooltip=f"Estado: {status}"
                        )
                    )
                )
            progress_matrix.rows.append(ft.DataRow(cells=row_cells))

        page.update()

    # --- Update Progress Dialog ---
    status_dropdown = ft.Dropdown(
        label="Nuevo Estado",
        options=[
            ft.dropdown.Option("no_iniciado", "No Iniciado"),
            ft.dropdown.Option("en_progreso", "En Progreso"),
            ft.dropdown.Option("completado", "Completado"),
            ft.dropdown.Option("necesita_refuerzo", "Necesita Refuerzo"),
        ]
    )
    observaciones_field = ft.TextField(label="Observaciones", multiline=True)
    evaluacion_field = ft.TextField(label="Evaluación/Nota")

    update_dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("Actualizar Progreso"),
        content=ft.Column([
            status_dropdown,
            observaciones_field,
            evaluacion_field,
        ]),
        actions_alignment=ft.MainAxisAlignment.END,
    )

    def save_progress(e, student_id, topic_id):
        from datetime import datetime
        new_status = status_dropdown.value
        if not new_status:
            page.snack_bar = ft.SnackBar(ft.Text("Debe seleccionar un estado."), bgcolor="red")
            return

        try:
            conn = sqlite3.connect("formacion.db")
            cursor = conn.cursor()
            # UPSERT logic: INSERT OR REPLACE would be simpler if we don't care about overwriting all fields
            # but ON CONFLICT is more explicit.
            cursor.execute("""
                INSERT INTO progreso_alumno_tema (alumno_usuario_id, tema_id, estado, observaciones, evaluacion, fecha_completado)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(alumno_usuario_id, tema_id) DO UPDATE SET
                estado = excluded.estado,
                observaciones = excluded.observaciones,
                evaluacion = excluded.evaluacion,
                fecha_completado = excluded.fecha_completado
            """, (
                student_id, topic_id, new_status,
                observaciones_field.value, evaluacion_field.value,
                datetime.now().strftime('%Y-%m-%d') if new_status == 'completado' else None
            ))
            conn.commit()
            conn.close()
            update_dialog.open = False
            page.snack_bar = ft.SnackBar(ft.Text("Progreso actualizado."), bgcolor="green")
            page.snack_bar.open = True
            update_matrix() # Refresh the whole matrix
        except Exception as ex:
            page.snack_bar = ft.SnackBar(ft.Text(f"Error al guardar progreso: {ex}"), bgcolor="red")
            page.snack_bar.open = True
            page.update()

    def open_update_dialog(student_id, topic_id, current_status):
        # Fetch existing data to pre-fill the dialog
        conn = sqlite3.connect("formacion.db")
        cursor = conn.cursor()
        cursor.execute(
            "SELECT estado, observaciones, evaluacion FROM progreso_alumno_tema WHERE alumno_usuario_id = ? AND tema_id = ?",
            (student_id, topic_id)
        )
        data = cursor.fetchone()
        conn.close()

        # Set initial values
        status_dropdown.value = data[0] if data else current_status
        observaciones_field.value = data[1] if data else ""
        evaluacion_field.value = data[2] if data else ""

        # Configure and open dialog
        update_dialog.actions = [
            ft.TextButton("Cancelar", on_click=lambda e: setattr(update_dialog, 'open', False) or page.update()),
            ft.FilledButton("Guardar", on_click=lambda e: save_progress(e, student_id, topic_id)),
        ]
        page.dialog = update_dialog
        update_dialog.open = True
        page.update()

    return ft.View(
        "/seguimiento_progreso",
        [
            ft.AppBar(title=ft.Text("Seguimiento de Progreso"), bgcolor=ft.colors.SURFACE_VARIANT),
            ft.Column(
                [
                    ft.Row([plan_selector]),
                    ft.Divider(),
                    ft.Container(
                        content=ft.Row([progress_matrix], scroll=ft.ScrollMode.ALWAYS),
                        expand=True,
                        padding=5
                    )
                ],
                expand=True,
                padding=10
            )
        ]
    )
