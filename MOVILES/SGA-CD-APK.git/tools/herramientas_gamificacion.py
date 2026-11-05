from langchain_core.tools import tool
from typing import Any, List, Dict

class GamificacionSoldiers:
    """
    El arsenal de herramientas de ejecución (la escuadra de Soldados) para las operaciones de Gamificación.
    Son comandados por el Sargento de Gamificación.
    """
    def __init__(self, api_client: Any):
        # En una aplicación real, este sería el cliente de la API de Gamificación.
        # ej. self.api = GamificationServices(db_session)
        self.api = api_client

    # --- Soldado #1: Soldado_Puntos ---
    @tool
    def conceder_puntos_a_estudiante(self, estudiante_id: int, cantidad_puntos: int, motivo: str) -> Dict:
        """
        (SOLDADO PUNTOS) Ejecuta la asignación de una cantidad específica de puntos a un estudiante por un motivo claro (ej. 'Asistencia perfecta', 'Tarea completada').
        """
        print(f"--- 💥 SOLDADO (Puntos): ¡ACCIÓN! Concediendo {cantidad_puntos} puntos al estudiante {estudiante_id} por '{motivo}'. ---")
        # result = self.api.grant_points(
        #     student_id=estudiante_id,
        #     points=cantidad_puntos,
        #     reason=motivo
        # )
        # return result # Debería devolver algo como {"status": "success", "new_total_points": 1150}
        return {"status": "success", "new_total_points": 1150, "message": f"{cantidad_puntos} puntos concedidos."}

    # --- Soldado #2: Soldado_Niveles ---
    @tool
    def actualizar_nivel_por_puntos(self, estudiante_id: int) -> Dict:
        """
        (SOLDADO NIVELES) Ejecuta una comprobación del total de puntos de un estudiante y, si corresponde, actualiza su nivel en el sistema.
        """
        print(f"--- 💥 SOLDADO (Niveles): ¡ACCIÓN! Verificando y actualizando el nivel para el estudiante {estudiante_id}. ---")
        # result = self.api.check_and_update_level(
        #     student_id=estudiante_id
        # )
        # return result # Podría devolver {"status": "success", "level_up": True, "new_level": 5, "unlocked_rewards": ["Acceso al Taller Avanzado"]} o {"level_up": False}
        return {"status": "success", "level_up": True, "new_level": 5, "unlocked_rewards": ["Acceso al Taller Avanzado"], "message": "¡El estudiante ha subido de nivel!"}

    # --- Soldado #3: Soldado_Medallas ---
    @tool
    def otorgar_medalla_o_logro(self, estudiante_id: int, nombre_medalla: str, descripcion_logro: str) -> Dict:
        """
        (SOLDADO MEDALLAS) Ejecuta la asignación de una medalla, insignia o logro específico a un estudiante por alcanzar un hito.
        """
        print(f"--- 💥 SOLDADO (Medallas): ¡ACCIÓN! Otorgando la medalla '{nombre_medalla}' al estudiante {estudiante_id}. ---")
        # result = self.api.award_medal(
        #     student_id=estudiante_id,
        #     medal_name=nombre_medalla,
        #     description=descripcion_logro
        # )
        # return result
        return {"status": "success", "message": f"Medalla '{nombre_medalla}' otorgada con éxito."}

    # --- Soldado #4: Soldado_Rankings ---
    @tool
    def generar_tabla_de_clasificacion(self, tipo_ranking: str, limite_resultados: int = 10) -> List[Dict]:
        """
        (SOLDADO RANKINGS) Ejecuta la generación de una tabla de clasificación (ranking). El 'tipo_ranking' puede ser 'general', 'mensual' o 'semanal'.
        """
        print(f"--- 💥 SOLDADO (Rankings): ¡ACCIÓN! Generando la tabla de clasificación '{tipo_ranking}' (Top {limite_resultados}). ---")
        # result = self.api.get_ranking(
        #     ranking_type=tipo_ranking,
        #     limit=limite_resultados
        # )
        # return result # Debería devolver una lista de objetos, ej. [{"rank": 1, "student_name": "...", "points": ...}]
        return [
            {"rank": 1, "student_name": "Valentina R.", "points": 1150},
            {"rank": 2, "student_name": "Santiago G.", "points": 1125},
            {"rank": 3, "student_name": "Mariana P.", "points": 1090}
        ]

    # --- Soldado #5: Soldado_Privacidad_Gamificación ---
    @tool
    def gestionar_privacidad_ranking(self, estudiante_id: int, mostrar_en_ranking: bool) -> Dict:
        """
        (SOLDADO PRIVACIDAD) Ejecuta la acción de configurar la preferencia de privacidad de un estudiante para aparecer o no en los rankings públicos.
        """
        accion = "incluido en" if mostrar_en_ranking else "excluido de"
        print(f"--- 💥 SOLDADO (Privacidad): ¡ACCIÓN! El estudiante {estudiante_id} será '{accion}' los rankings públicos. ---")
        # result = self.api.set_ranking_privacy(
        #     student_id=estudiante_id,
        #     show_in_rankings=mostrar_en_ranking
        # )
        # return result
        return {"status": "success", "message": f"Preferencia de privacidad actualizada. El estudiante será {accion} los rankings."}

    def get_all_soldiers(self) -> List:
        """
        Recluta y devuelve la Escuadra de Gamificación completa, lista para ser comandada por el Sargento de Gamificación.
        """
        return [
            self.conceder_puntos_a_estudiante,
            self.actualizar_nivel_por_puntos,
            self.otorgar_medalla_o_logro,
            self.generar_tabla_de_clasificacion,
            self.gestionar_privacidad_ranking
        ]
