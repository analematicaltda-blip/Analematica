from langchain_core.tools import tool
from typing import Any, List, Dict

class AcademicoSoldiers:
    """
    El arsenal de herramientas de ejecución (la escuadra de Soldados) para las operaciones académicas y deportivas.
    Son comandados por el Sargento Académico.
    """
    def __init__(self, api_client: Any):
        # En una aplicación real, este sería el cliente de la API de la
        # plataforma de formación (ej. self.api = FormationServices(db_session))
        self.api = api_client

    # --- Soldado #2: Soldado_Clases ---
    @tool
    def crear_clase(self, nombre_clase: str, descripcion: str, area_id: int) -> Dict:
        """
        (SOLDADO CLASES) Ejecuta la creación de una nueva clase, taller o curso en el sistema, asociándola a un área específica.
        Devuelve el ID de la nueva clase para ser usado en pasos posteriores.
        """
        print(f"--- 💥 SOLDADO (Clases): ¡ACCIÓN! Creando la clase '{nombre_clase}' en el área {area_id}. ---")
        # result = self.api.create_class(
        #     name=nombre_clase,
        #     description=descripcion,
        #     area_id=area_id
        # )
        # return result # Debería devolver algo como {"status": "success", "clase_id": 101}
        return {"status": "success", "clase_id": 101, "message": f"Clase '{nombre_clase}' creada con éxito."}

    # --- Soldado #5: Soldado_Instructores ---
    @tool
    def asignar_instructor_a_clase(self, clase_id: int, instructor_id: int) -> Dict:
        """
        (SOLDADO INSTRUCTORES) Ejecuta la asignación de un instructor específico a una clase ya creada.
        """
        print(f"--- 💥 SOLDADO (Instructores): ¡ACCIÓN! Asignando al instructor {instructor_id} a la clase {clase_id}. ---")
        # result = self.api.assign_instructor(
        #     class_id=clase_id,
        #     instructor_id=instructor_id
        # )
        # return result
        return {"status": "success", "message": f"Instructor {instructor_id} asignado correctamente a la clase {clase_id}."}

    # --- Soldado #4: Soldado_Reservas_Escenarios ---
    @tool
    def reservar_escenario_para_clase(self, clase_id: int, escenario_id: int, fecha: str, hora_inicio: str, hora_fin: str) -> Dict:
        """
        (SOLDADO RESERVAS) Ejecuta la reserva de un escenario (salón, cancha, etc.) para una clase en una fecha y horario específicos.
        """
        print(f"--- 💥 SOLDADO (Reservas): ¡ACCIÓN! Reservando escenario {escenario_id} para la clase {clase_id} el {fecha} de {hora_inicio} a {hora_fin}. ---")
        # result = self.api.book_venue(
        #     class_id=clase_id,
        #     venue_id=escenario_id,
        #     date=fecha,
        #     start_time=hora_inicio,
        #     end_time=hora_fin
        # )
        # return result
        return {"status": "success", "booking_id": "booking-555", "message": f"Escenario {escenario_id} reservado."}

    # --- Soldado #1: Soldado_Inscripciones ---
    @tool
    def abrir_inscripciones_clase(self, clase_id: int, cupos_disponibles: int) -> Dict:
        """
        (SOLDADO INSCRIPCIONES) Ejecuta la apertura del proceso de inscripción para una clase, definiendo el número de cupos.
        """
        print(f"--- 💥 SOLDADO (Inscripciones): ¡ACCIÓN! Abriendo {cupos_disponibles} cupos para la clase {clase_id}. ---")
        # result = self.api.open_enrollment(
        #     class_id=clase_id,
        #     slots=cupos_disponibles
        # )
        # return result
        return {"status": "success", "message": f"{cupos_disponibles} cupos abiertos para inscripciones en la clase {clase_id}."}

    # --- Soldado #3: Soldado_Asistencia ---
    @tool
    def registrar_asistencia_clase(self, clase_id: int, id_estudiantes_presentes: List[int]) -> Dict:
        """
        (SOLDADO ASISTENCIA) Ejecuta el registro de la asistencia para una sesión de clase finalizada, recibiendo una lista de IDs de los estudiantes que asistieron.
        """
        print(f"--- 💥 SOLDADO (Asistencia): ¡ACCIÓN! Registrando asistencia de {len(id_estudiantes_presentes)} estudiantes para la clase {clase_id}. ---")
        # result = self.api.log_attendance(
        #     class_id=clase_id,
        #     present_student_ids=id_estudiantes_presentes
        # )
        # return result
        return {"status": "success", "asistencia_registrada": len(id_estudiantes_presentes)}

    def get_all_soldiers(self) -> List:
        """
        Recluta y devuelve la Escuadra Académica completa, lista para ser comandada por el Sargento Académico.
        """
        return [
            self.crear_clase,
            self.asignar_instructor_a_clase,
            self.reservar_escenario_para_clase,
            self.abrir_inscripciones_clase,
            self.registrar_asistencia_clase
        ]
