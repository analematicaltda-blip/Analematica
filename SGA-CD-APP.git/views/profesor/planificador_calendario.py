import flet as ft
import sqlite3
import calendar
from datetime import datetime, timedelta

def planificador_calendario_view(page: ft.Page, user_id: int):

    # --- State Management ---
    current_display_date = ft.Ref[datetime](datetime.now())
    current_view_mode = ft.Ref[str]("mes") # 'semana', 'mes', 'trimestre'

    def get_month_name(month_num):
        # A simple helper to get Spanish month names
        months = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
        return months[month_num - 1]

    # --- UI Controls ---
    calendar_header = ft.Text(size=20, weight="bold")
    calendar_grid = ft.Column(spacing=5, expand=True)

    def update_calendar():
        mode = current_view_mode.current
        if mode == "mes":
            generate_monthly_view()
        elif mode == "semana":
            # Placeholder for weekly view
            calendar_grid.controls.clear()
            calendar_grid.controls.append(ft.Text("Vista semanal no implementada", text_align="center"))
            calendar_header.value = "Semana (No Implementada)"
            page.update()
        elif mode == "trimestre":
            # Placeholder for quarterly view
            calendar_grid.controls.clear()
            calendar_grid.controls.append(ft.Text("Vista trimestral no implementada", text_align="center"))
            calendar_header.value = "Trimestre (No Implementado)"
            page.update()

    def load_scheduled_topics(year, month):
        conn = sqlite3.connect("formacion.db")
        cursor = conn.cursor()
        # Get topics for the current instructor scheduled in the given month and year
        start_of_month = f"{year}-{month:02d}-01"
        end_of_month = f"{year}-{month:02d}-{calendar.monthrange(year, month)[1]}"

        cursor.execute("""
            SELECT pce.fecha_programada, pct.nombre_tema
            FROM planificador_clases_eventos pce
            JOIN plan_curricular_temas pct ON pce.tema_id = pct.id
            WHERE pce.instructor_id = ? AND pce.fecha_programada BETWEEN ? AND ?
        """, (user_id, start_of_month, end_of_month))

        scheduled_topics = {}
        for row in cursor.fetchall():
            date_str, topic_name = row
            day = datetime.strptime(date_str, '%Y-%m-%d').day
            if day not in scheduled_topics:
                scheduled_topics[day] = []
            scheduled_topics[day].append(topic_name)

        conn.close()
        return scheduled_topics

    def generate_monthly_view():
        calendar_grid.controls.clear()
        year = current_display_date.current.year
        month = current_display_date.current.month

        scheduled_topics = load_scheduled_topics(year, month)
        month_calendar = calendar.monthcalendar(year, month)

        days_of_week = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"]
        header_row = ft.Row(spacing=5, controls=[
            ft.Container(content=ft.Text(day, text_align="center", weight="bold"), expand=True, padding=5) for day in days_of_week
        ])
        calendar_grid.controls.append(header_row)

        for week in month_calendar:
            week_row = ft.Row(spacing=5, expand=True)
            for day in week:
                day_content_column = ft.Column([ft.Text(str(day) if day != 0 else "")], spacing=2, scroll=ft.ScrollMode.AUTO)

                # Add scheduled topics if they exist for this day
                if day in scheduled_topics:
                    for topic_name in scheduled_topics[day]:
                        day_content_column.controls.append(
                            ft.Container(
                                content=ft.Text(topic_name, size=10, color="white"),
                                bgcolor=ft.colors.BLUE_GREY_500,
                                border_radius=3,
                                padding=2,
                            )
                        )

                day_container = ft.Container(
                    content=day_content_column,
                    border=ft.border.all(1, ft.colors.BLACK26),
                    border_radius=5,
                    padding=5,
                    expand=True,
                    on_click=lambda e, y=year, m=month, d=day: open_schedule_dialog(datetime(y, m, d)) if d != 0 else None,
                    data=day
                )
                if day == 0:
                    day_container.bgcolor = ft.colors.BLACK12

                week_row.controls.append(day_container)
            calendar_grid.controls.append(week_row)

        calendar_header.value = f"{get_month_name(month)} {year}"
        page.update()

    def change_period(offset):
        mode = current_view_mode.current
        current_date = current_display_date.current

        if mode == "mes":
            month = current_date.month + offset
            year = current_date.year
            if month > 12:
                month = 1
                year += 1
            elif month < 1:
                month = 12
                year -= 1
            current_display_date.current = datetime(year, month, 1)

        # Add logic for week and quarter changes here later

        update_calendar()

    def switch_view_mode(e):
        current_view_mode.current = e.control.selected_key
        # Reset date to the beginning of the current month/week/quarter to avoid confusion
        today = datetime.now()
        current_display_date.current = datetime(today.year, today.month, 1)
        update_calendar()

    # --- Schedule Topic Dialog ---
    unscheduled_topics_dropdown = ft.Dropdown(label="Seleccionar Tema a Agendar")

    schedule_dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("Agendar un Tema"),
        content=ft.Column([
            unscheduled_topics_dropdown
        ]),
        actions=[
            ft.TextButton("Cancelar", on_click=lambda e: setattr(schedule_dialog, 'open', False) or page.update()),
            ft.FilledButton("Guardar", on_click=lambda e: schedule_topic(e)),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )

    def load_unscheduled_topics():
        conn = sqlite3.connect("formacion.db")
        cursor = conn.cursor()
        # Get topics for this instructor that are not yet in the planificador_clases_eventos table
        cursor.execute("""
            SELECT t.id, t.nombre_tema
            FROM plan_curricular_temas t
            JOIN plan_curricular pc ON t.plan_curricular_id = pc.id
            WHERE pc.creado_por_usuario_id = ?
            AND t.id NOT IN (SELECT tema_id FROM planificador_clases_eventos WHERE instructor_id = ?)
            ORDER BY t.orden
        """, (user_id, user_id))
        topics = cursor.fetchall()
        conn.close()
        return [ft.dropdown.Option(key=t[0], text=t[1]) for t in topics]

    def schedule_topic(e):
        selected_date = schedule_dialog.data
        topic_id = unscheduled_topics_dropdown.value

        if not selected_date or not topic_id:
            page.snack_bar = ft.SnackBar(ft.Text("Debe seleccionar un tema."), bgcolor="red")
            page.snack_bar.open = True
            page.update()
            return

        try:
            conn = sqlite3.connect("formacion.db")
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO planificador_clases_eventos (tema_id, instructor_id, fecha_programada, estado)
                VALUES (?, ?, ?, 'planificado')
                """,
                (topic_id, user_id, selected_date.strftime('%Y-%m-%d'))
            )
            conn.commit()
            conn.close()
            schedule_dialog.open = False
            page.snack_bar = ft.SnackBar(ft.Text("Tema agendado exitosamente."), bgcolor="green")
            update_calendar() # Refresh the calendar view
            page.update()
        except Exception as ex:
            page.snack_bar = ft.SnackBar(ft.Text(f"Error al agendar: {ex}"), bgcolor="red")
            page.snack_bar.open = True
            page.update()

    def open_schedule_dialog(date_obj):
        schedule_dialog.data = date_obj # Store the date object
        schedule_dialog.title = ft.Text(f"Agendar para {date_obj.strftime('%d/%m/%Y')}")

        # Populate dropdown
        unscheduled_topics_dropdown.options = load_unscheduled_topics()
        unscheduled_topics_dropdown.value = None

        page.dialog = schedule_dialog
        schedule_dialog.open = True
        page.update()

    # --- Layout Definition ---
    view_switcher = ft.SegmentedButton(
        selected_key=current_view_mode.current,
        on_change=switch_view_mode,
        segments=[
            ft.Segment(key="semana", value="Semana", icon=ft.Icon(ft.icons.VIEW_WEEK)),
            ft.Segment(key="mes", value="Mes", icon=ft.Icon(ft.icons.CALENDAR_MONTH)),
            ft.Segment(key="trimestre", value="Trimestre", icon=ft.Icon(ft.icons.CALENDAR_VIEW_DAY)),
        ]
    )

    # Initial load
    update_calendar()

    return ft.View(
        "/planificador_calendario",
        [
            ft.AppBar(title=ft.Text("Planificador de Calendario"), bgcolor=ft.colors.SURFACE_VARIANT),
            ft.Column(
                [
                    ft.Row([
                        ft.IconButton(icon=ft.icons.CHEVRON_LEFT, on_click=lambda e: change_period(-1), tooltip="Periodo Anterior"),
                        calendar_header,
                        ft.IconButton(icon=ft.icons.CHEVRON_RIGHT, on_click=lambda e: change_period(1), tooltip="Siguiente Periodo"),
                    ], alignment=ft.MainAxisAlignment.CENTER),
                    view_switcher,
                    ft.Divider(),
                    calendar_grid,
                ],
                expand=True,
                spacing=10,
                padding=10
            )
        ]
    )
