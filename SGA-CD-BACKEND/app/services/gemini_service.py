import os
import json
import logging
from typing import Dict, Any, Optional
from app.core.config import settings

logger = logging.getLogger("gemini_service")

# Safe dynamic import of google.genai to prevent startup crashes if SDK is absent
genai_client_module = None
try:
    from google import genai
    genai_client_module = genai
except ImportError:
    logger.warning("El paquete 'google-genai' no está instalado. Se utilizarán plantillas metodológicas estructuradas de respaldo.")

class GeminiPlanService:
    def __init__(self):
        # Retrieve Gemini API Key securely from environment or settings
        self.api_key = getattr(settings, "GEMINI_API_KEY", os.getenv("GEMINI_API_KEY"))
        self.client = None
        if self.api_key and genai_client_module:
            try:
                self.client = genai_client_module.Client(api_key=self.api_key)
            except Exception as e:
                logger.error(f"Error al inicializar cliente Gemini: {e}")

    def generate_annual_work_plan(self, disciplina: str, area: str) -> Dict[str, Any]:
        """
        Genera un plan de trabajo anual (Enero a Diciembre) usando Google Gemini
        o una plantilla estructurada de respaldo si la API no estuviera disponible.
        """
        prompt = f"""
        Eres un experto director metodológico de formación en {area}.
        Crea un plan de trabajo docente estructurado para la disciplina '{disciplina}' (Área: {area}) de Enero a Diciembre.

        El proceso debe incluir:
        - Enero: Inscripción de estudiantes, diagnóstico inicial y nivelación.
        - Febrero a Noviembre: Desarrollo de unidades temáticas mensuales con objetivos, técnicas, metodología y evaluación.
        - Diciembre: Evaluación final y muestra/presentación para la 'Noche de los Mejores' (premiación y reconocimiento).

        Devuelve ÚNICAMENTE un objeto JSON válido con la siguiente estructura:
        {{
            "disciplina": "{disciplina}",
            "area": "{area}",
            "titulo_plan": "Plan Anual de Formación en {disciplina}",
            "objetivo_general": "...",
            "cronograma_mensual": [
                {{
                    "mes": "Enero",
                    "fase": "Inscripción y Diagnóstico",
                    "objetivo": "Apertura de inscripciones y caracterización de alumnos",
                    "actividades": ["Matrícula", "Prueba de entrada", "Asignación de grupo"]
                }},
                {{
                    "mes": "Febrero",
                    "fase": "Fundamentos I",
                    "objetivo": "Introducción a la técnica básica",
                    "actividades": ["Ejercicios teóricos", "Práctica guiada"]
                }},
                {{
                    "mes": "Diciembre",
                    "fase": "Noche de los Mejores y Premiación",
                    "objetivo": "Muestra final de logros, entrega de medallas y reconocimientos de gamificación",
                    "actividades": ["Gala de premiación", "Presentación pública", "Entrega de reconocimientos"]
                }}
            ],
            "criterios_premiacion": [
                "Asistencia mínima 85%",
                "Desempeño destacado en la muestra final",
                "Puntaje de gamificación y valores institucionales"
            ]
        }}
        """

        if self.client:
            models_to_try = ["gemini-1.5-flash", "gemini-2.0-flash", "gemini-pro"]
            for model_name in models_to_try:
                try:
                    response = self.client.models.generate_content(
                        model=model_name,
                        contents=prompt
                    )
                    text = response.text.strip()
                    if text.startswith("```json"):
                        text = text[7:]
                    if text.startswith("```"):
                        text = text[:-3]
                    if text.endswith("```"):
                        text = text[:-3]

                    parsed = json.loads(text.strip())
                    logger.info(f"Plan de trabajo generado exitosamente con Gemini ({model_name}) para {disciplina}")
                    return parsed
                except Exception as e:
                    logger.warning(f"Intento fallido con modelo {model_name} para {disciplina}: {e}")

        # Fallback estructurado garantizado
        logger.info(f"Utilizando plantilla estructurada para disciplina '{disciplina}'")
        return self._get_fallback_plan(disciplina, area)

    def _get_fallback_plan(self, disciplina: str, area: str) -> Dict[str, Any]:
        meses = [
            ("Enero", "Inscripción y Diagnóstico", "Convocatoria, matrícula y caracterización de habilidades de los estudiantes."),
            ("Febrero", "Fundamentos y Técnica Básica", "Acondicionamiento y dominio de conceptos fundamentales de la disciplina."),
            ("Marzo", "Desarrollo Táctico / Expresivo I", "Ejercicios de coordinación, postura y ejecución técnica inicial."),
            ("Abril", "Consolidación de Contenidos", "Integración de componentes prácticos y trabajo en equipo."),
            ("Mayo", "Evaluación de Medio Término", "Pruebas de progreso, retroalimentación individual y corrección técnica."),
            ("Junio", "Talleres Intensivos y Receso", "Repaso de módulos, clínicas especializadas y descanso pedagógico."),
            ("Julio", "Acondicionamiento y Nivel Avanzado", "Reinicio de ciclo con dinámicas complejas y preparación de repertorio/torneo."),
            ("Agosto", "Perfeccionamiento Práctico", "Simulacros de presentación/competencia y desarrollo de autonomía."),
            ("Septiembre", "Ensayos Generales / Intercambios", "Encuentros deportivos o muestras artísticas inter-grupales."),
            ("Octubre", "Selección de Proyectos y Talentos", "Identificación de estudiantes destacados para la muestra de fin de año."),
            ("Noviembre", "Ensayos Finales / Preparación Gala", "Montaje final del espectáculo artístico o torneo de cierre."),
            ("Diciembre", "Noche de los Mejores y Premiación", "Gala de premiación, entrega de medallas, reconocimientos de gamificación y clausura.")
        ]

        return {
            "disciplina": disciplina,
            "area": area,
            "titulo_plan": f"Plan Anual de Formación Metodológica en {disciplina} ({area})",
            "objetivo_general": f"Desarrollar el potencial integral de los estudiantes en {disciplina} a través de un proceso pedagógico sistemático de Enero a Diciembre.",
            "cronograma_mensual": [
                {
                    "mes": mes,
                    "fase": fase,
                    "objetivo": desc,
                    "actividades": [
                        f"Desarrollo pedagógico de {fase}",
                        f"Seguimiento de asistencia e indicadores pedagógicos",
                        f"Evaluación continua de progreso"
                    ]
                }
                for mes, fase, desc in meses
            ],
            "criterios_premiacion": [
                "Asistencia continua superior al 85%",
                "Excelencia técnica y compromiso en la disciplina",
                "Logro de insignias y medallas en el sistema de gamificación"
            ]
        }

gemini_plan_service = GeminiPlanService()
