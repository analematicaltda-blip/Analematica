from langchain_core.tools import tool
from typing import Any, List, Dict

class DeportivoSoldiers:
    """
    El arsenal de herramientas de ejecución (la escuadra de Soldados) para las operaciones deportivas.
    Son comandados por el Sargento Deportivo.
    """
    def __init__(self, api_client: Any):
        self.api = api_client

    @tool
    def crear_entrenamiento(self, nombre_entrenamiento: str, descripcion: str, area_id: int) -> Dict:
        """
        (SOLDADO ENTRENAMIENTOS) Ejecuta la creación de un nuevo entrenamiento, práctica o sesión deportiva en el sistema.
        """
        print(f"--- 💥 SOLDADO (Deportivo): ¡ACCIÓN! Creando el entrenamiento '{nombre_entrenamiento}' en el área {area_id}. ---")
        return {"status": "success", "entrenamiento_id": 201, "message": f"Entrenamiento '{nombre_entrenamiento}' creado con éxito."}

    @tool
    def asignar_entrenador_a_entrenamiento(self, entrenamiento_id: int, entrenador_id: int) -> Dict:
        """
        (SOLDADO ENTRENADORES) Ejecuta la asignación de un entrenador específico a un entrenamiento ya creado.
        """
        print(f"--- 💥 SOLDADO (Deportivo): ¡ACCIÓN! Asignando al entrenador {entrenador_id} al entrenamiento {entrenamiento_id}. ---")
        return {"status": "success", "message": f"Entrenador {entrenador_id} asignado correctamente al entrenamiento {entrenamiento_id}."}

    @tool
    def reservar_escenario_deportivo(self, entrenamiento_id: int, escenario_id: int, fecha: str, hora_inicio: str, hora_fin: str) -> Dict:
        """
        (SOLDADO RESERVAS) Ejecuta la reserva de un escenario deportivo (cancha, pista, etc.) para un entrenamiento.
        """
        print(f"--- 💥 SOLDADO (Deportivo): ¡ACCIÓN! Reservando escenario {escenario_id} para el entrenamiento {entrenamiento_id} el {fecha} de {hora_inicio} a {hora_fin}. ---")
        return {"status": "success", "booking_id": "booking-deportivo-777", "message": f"Escenario deportivo {escenario_id} reservado."}

    @tool
    def abrir_inscripciones_entrenamiento(self, entrenamiento_id: int, cupos_disponibles: int) -> Dict:
        """
        (SOLDADO INSCRIPCIONES) Ejecuta la apertura del proceso de inscripción para un entrenamiento, definiendo el número de cupos.
        """
        print(f"--- 💥 SOLDADO (Deportivo): ¡ACCIÓN! Abriendo {cupos_disponibles} cupos para el entrenamiento {entrenamiento_id}. ---")
        return {"status": "success", "message": f"{cupos_disponibles} cupos abiertos para inscripciones en el entrenamiento {entrenamiento_id}."}

    @tool
    def registrar_asistencia_entrenamiento(self, entrenamiento_id: int, id_deportistas_presentes: List[int]) -> Dict:
        """
        (SOLDADO ASISTENCIA) Ejecuta el registro de la asistencia para una sesión de entrenamiento finalizada.
        """
        print(f"--- 💥 SOLDADO (Deportivo): ¡ACCIÓN! Registrando asistencia de {len(id_deportistas_presentes)} deportistas para el entrenamiento {entrenamiento_id}. ---")
        return {"status": "success", "asistencia_registrada": len(id_deportistas_presentes)}

    def get_all_soldiers(self) -> List:
        """
        Recluta y devuelve la Escuadra Deportiva completa.
        """
        return [
            self.crear_entrenamiento,
            self.asignar_entrenador_a_entrenamiento,
            self.reservar_escenario_deportivo,
            self.abrir_inscripciones_entrenamiento,
            self.registrar_asistencia_entrenamiento
        ]
