import flet as ft
import sqlite3
import pandas as pd
from analysis.data_analyzer import analyze_question # Import the new analysis module

LOGO_PATH = "../../assets/logo.png"
COLOR1_HEX = "#FFD700"
COLOR2_HEX = "#00A651"

# --- Predefined Questions ---
QUESTIONS = {
    "q1": "¿Qué profesores tienen la mayor tasa de asistencia en sus clases?",
    "q2": "¿Cuáles son los 5 procesos de formación más populares (con más inscripciones)?",
    "q3": "¿Cuáles son los escenarios o partes de escenario más reservados?",
    "q4": "¿En qué días de la semana y horas hay más clases programadas (horas pico)?",
    "q5": "Identificar grupos (clusters) de alumnos según su nivel de participación (asistencias).",
    "q6": "Mostrar la distribución de alumnos por género en mi área.",
    "q7": "Mostrar la distribución de alumnos por grupo etario en mi área.",
    "q8": "¿Cuál es el promedio de clases a las que se inscribe un alumno?",
    "q9": "Listar los elementos de inventario más prestados en mi área.",
    "q10": "Analizar la correlación entre procesos de formación y escenarios utilizados."
}


def analisis_datos_view(page: ft.Page, tenant_id: int, user_id: int):

    preguntas_dropdown = ft.Dropdown(
        label="Selecciona una pregunta para analizar",
        options=[ft.dropdown.Option(key, text) for key, text in QUESTIONS.items()]
    )

    resultados_container = ft.Column(
        controls=[ft.Text("Los resultados del análisis aparecerán aquí.")],
        scroll=ft.ScrollMode.AUTO,
        expand=True
    )

    progress_indicator = ft.ProgressRing(visible=False)

    def handle_analysis(e):
        selected_q_key = preguntas_dropdown.value
        if not selected_q_key:
            return

        resultados_container.controls.clear()
        resultados_container.controls.append(ft.Text(f"Analizando: '{QUESTIONS[selected_q_key]}'"))
        progress_indicator.visible = True
        page.update()

        # --- Call the analysis module ---
        # In a real app, this should run in a separate thread
        try:
            result = analyze_question(selected_q_key, tenant_id, user_id)

            progress_indicator.visible = False
            resultados_container.controls.clear()

            # --- Render the result based on its type ---
            if result['type'] == 'text':
                resultados_container.controls.append(ft.Text(result['data']))
            elif result['type'] == 'table':
                df = pd.DataFrame(result['data'])
                columns = [ft.DataColumn(ft.Text(col)) for col in df.columns]
                rows = [ft.DataRow(cells=[ft.DataCell(ft.Text(str(val))) for val in row]) for row in df.itertuples(index=False)]
                resultados_container.controls.append(ft.DataTable(columns=columns, rows=rows))
            elif result['type'] == 'image':
                resultados_container.controls.append(ft.Image(src=result['data']))

        except Exception as ex:
            progress_indicator.visible = False
            resultados_container.controls.clear()
            resultados_container.controls.append(ft.Text(f"Ocurrió un error durante el análisis: {ex}", color="red"))

        page.update()


    return ft.View(
        "/jefe_area/analisis",
        [
            ft.AppBar(title=ft.Text("Panel de Análisis de Datos"), bgcolor=COLOR2_HEX),
            ft.Container(
                padding=20,
                expand=True,
                content=ft.Column([
                    ft.Text("Análisis de Datos del Área", size=22, weight="bold"),
                    preguntas_dropdown,
                    ft.ElevatedButton("Generar Análisis", icon=ft.icons.ANALYTICS, on_click=handle_analysis),
                    ft.Divider(height=20),
                    progress_indicator,
                    ft.Container(content=resultados_container, expand=True) # Make container scrollable
                ])
            )
        ]
    )
