from langchain_core.tools import tool
from typing import Any, List, Dict
from app.tools.herramientas_analiticas import generar_grafico_asistencia

class InteligenciaSoldiers:
    """
    El arsenal de herramientas de ejecución (la escuadra de Soldados) para las operaciones de Inteligencia.
    Son comandados por el Sargento de Inteligencia.
    """
    def __init__(self, api_client: Any):
        # En una aplicación real, este sería el cliente de la API de Analíticas y IA,
        # que se conecta a bases de datos, modelos de IA y herramientas de BI.
        # ej. self.api = IntelligenceServices(db_session, ai_model_client)
        self.api = api_client

    # --- Soldado #1: Soldado_Agente_IA ---
    @tool
    def obtener_respuesta_asistente_ia(self, pregunta_usuario: str, contexto: str = None) -> str:
        """
        (SOLDADO AGENTE IA) Ejecuta una consulta al agente de IA de bajo nivel para obtener respuestas a preguntas de soporte o conocimiento general.
        Puede recibir un 'contexto' opcional para mejorar la respuesta.
        """
        print(f"--- 💥 SOLDADO (Agente IA): ¡ACCIÓN! Procesando pregunta: '{pregunta_usuario[:30]}...'. ---")
        # response = self.api.get_ai_assistant_response(
        #     user_query=pregunta_usuario,
        #     context=contexto
        # )
        # return response
        return "Respuesta Simulada: La inscripción para los cursos de verano se abre el 15 de julio. Puede encontrar más detalles en la sección de 'Próximos Eventos'."

    # --- Soldado #2: Soldado_Analítica_y_KPIs ---
    @tool
    def calcular_kpi(self, nombre_kpi: str, parametros: Dict) -> Dict:
        """
        (SOLDADO ANALÍTICA Y KPIs) Ejecuta el cálculo de un Indicador Clave de Rendimiento (KPI) específico.
        'parametros' es un JSON con el contexto (ej. {'mes': 11, 'area_id': 3}).
        """
        print(f"--- 💥 SOLDADO (KPIs): ¡ACCIÓN! Calculando KPI '{nombre_kpi}' con parámetros {parametros}. ---")
        # kpi_result = self.api.calculate_kpi(
        #     kpi_name=nombre_kpi,
        #     params=parametros
        # )
        # return kpi_result # Debería devolver {"kpi": "Tasa de Asistencia", "valor": "92%", "tendencia": "positiva", "comparativo": "+5% vs mes anterior"}
        return {"kpi": nombre_kpi, "valor": "92%", "tendencia": "positiva", "comparativo": "+5% vs mes anterior"}

    # --- Soldado #3: Soldado_Generar_Dashboard_Personalizado ---
    @tool
    def construir_dashboard(self, nombre_dashboard: str, widgets: List[Dict]) -> Dict:
        """
        (SOLDADO DASHBOARD) Ejecuta la construcción de un nuevo dashboard de visualización de datos.
        'widgets' es una lista de diccionarios, donde cada uno define un widget (ej. {'tipo': 'kpi', 'kpi_nombre': 'tasa_asistencia'}).
        """
        print(f"--- 💥 SOLDADO (Dashboard): ¡ACCIÓN! Construyendo dashboard '{nombre_dashboard}' con {len(widgets)} widgets. ---")
        # result = self.api.build_dashboard(
        #     dashboard_name=nombre_dashboard,
        #     widget_definitions=widgets
        # )
        # return result # Debería devolver {"status": "success", "dashboard_id": "dash-xyz", "url": "/dashboards/dash-xyz"}
        return {"status": "success", "dashboard_id": "dash-xyz", "url": f"/dashboards/{nombre_dashboard.replace(' ','-').lower()}"}

    # --- Soldado #4: Soldado_Exportar_Datos_a_CSV ---
    @tool
    def exportar_reporte_a_csv(self, nombre_reporte: str, parametros: Dict) -> Dict:
        """
        (SOLDADO EXPORTAR) Ejecuta la generación y exportación de los datos de un reporte a un archivo CSV.
        'parametros' es un JSON con los filtros del reporte.
        """
        print(f"--- 💥 SOLDADO (Exportar): ¡ACCIÓN! Exportando reporte '{nombre_reporte}' a CSV. ---")
        # result = self.api.export_report_to_csv(
        #     report_name=nombre_reporte,
        #     params=parametros
        # )
        # return result # Debería devolver {"status": "success", "file_url": "/downloads/report-xyz.csv"}
        return {"status": "success", "file_url": f"/downloads/{nombre_reporte.replace(' ','-').lower()}.csv"}

    # --- Soldado #5: Soldado_Sugerir_Acciones_con_IA ---
    @tool
    def obtener_sugerencias_estrategicas_ia(self, objetivo: str) -> List[str]:
        """
        (SOLDADO SUGERENCIAS IA) Utiliza un modelo de IA estratégico para analizar un objetivo (ej. 'aumentar la retención de estudiantes') y proponer una lista de acciones sugeridas basadas en los datos de la plataforma.
        """
        print(f"--- 💥 SOLDADO (Sugerencias IA): ¡ACCIÓN! Generando sugerencias para el objetivo: '{objetivo}'. ---")
        # suggestions = self.api.get_strategic_suggestions(
        #     objective=objetivo
        # )
        # return suggestions
        return [
            "Lanzar una campaña de gamificación con medallas por asistencia consecutiva.",
            "Enviar notificaciones personalizadas a estudiantes con bajo rendimiento reciente.",
            "Crear un nuevo taller sobre 'Técnicas de Estudio Avanzadas' basado en las preguntas de soporte más frecuentes."
        ]

    # --- Soldado #6: Soldado_Visualizacion_Grafica ---
    @tool
    def generar_visualizacion_grafica(self, pregunta: str) -> Dict:
        """
        (SOLDADO VISUALIZACIÓN) Genera un gráfico para responder a una pregunta sobre datos.
        Utilízalo cuando el usuario pida comparar, analizar o ver tendencias de datos visualmente.
        Devuelve un diccionario con la URL de la imagen generada.
        """
        print(f"--- 💥 SOLDADO (Visualización): ¡ACCIÓN! Generando gráfico para la pregunta: '{pregunta}'. ---")
        try:
            # Llama a la función que hemos creado en el otro archivo
            web_path = generar_grafico_asistencia(pregunta)
            # Devuelve una respuesta estructurada
            return {
                "status": "success",
                "message": "Se ha generado un gráfico para responder a tu pregunta.",
                "image_url": web_path
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"No se pudo generar el gráfico: {e}"
            }

    def get_all_soldiers(self) -> List:
        """
        Recluta y devuelve la Escuadra de Inteligencia completa, lista para ser comandada por el Sargento de Inteligencia.
        """
        return [
            self.obtener_respuesta_asistente_ia,
            self.calcular_kpi,
            self.construir_dashboard,
            self.exportar_reporte_a_csv,
            self.obtener_sugerencias_estrategicas_ia,
            self.generar_visualizacion_grafica
        ]
