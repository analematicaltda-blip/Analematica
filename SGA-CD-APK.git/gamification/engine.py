import sqlite3
from datetime import datetime
from utils.notification_service import create_notification

class GamificationEngine:
    def __init__(self, tenant_id: int, alumno_user_id: int, pubsub_instance):
        self.tenant_id = tenant_id
        self.alumno_user_id = alumno_user_id
        self.pubsub_instance = pubsub_instance
        # We need the alumno_id (from the alumnos table), not the usuario_id
        self.conn = sqlite3.connect("formacion.db")
        self.cursor = self.conn.cursor()

        self.cursor.execute("SELECT id FROM alumnos WHERE usuario_id = ?", (self.alumno_user_id,))
        result = self.cursor.fetchone()
        self.alumno_id = result[0] if result else None

    def log_action(self, action_key: str):
        """
        Logs an action, grants points, and checks for new rewards.
        """
        if not self.alumno_id:
            print(f"Error de gamificación: no se encontró un perfil de alumno para el usuario {self.alumno_user_id}")
            return

        # 1. Get points for the action
        self.cursor.execute(
            "SELECT puntos FROM gamificacion_acciones WHERE inquilino_id = ? AND accion_key = ?",
            (self.tenant_id, action_key)
        )
        result = self.cursor.fetchone()
        if not result:
            print(f"Advertencia de gamificación: La acción '{action_key}' no está definida.")
            return

        points_to_add = result[0]

        # 2. Log the points earned
        self.cursor.execute("""
            INSERT INTO gamificacion_puntos_log (inquilino_id, alumno_id, accion_key, puntos_ganados, timestamp)
            VALUES (?, ?, ?, ?, ?)
        """, (self.tenant_id, self.alumno_id, action_key, points_to_add, datetime.now().isoformat()))

        # 3. Update the student's total points
        self.cursor.execute(
            "UPDATE alumnos SET puntos_totales = puntos_totales + ? WHERE id = ?",
            (points_to_add, self.alumno_id)
        )

        # 4. Check for new badges/levels (placeholder for now)
        self._check_for_new_medals()
        self._check_for_level_up()

        self.conn.commit()
        print(f"Acción '{action_key}' registrada para el alumno {self.alumno_id}. Puntos ganados: {points_to_add}")

    def _check_for_new_medals(self):
        """Checks if the user has earned any new medals and grants them."""
        # --- Example: Medal for First 5 Attendances ---
        MEDAL_KEY = "PRIMEROS_5_PASOS"

        # 1. Check if user already has this medal
        self.cursor.execute(
            "SELECT id FROM gamificacion_medallas_obtenidas WHERE alumno_id = ? AND medalla_key = ?",
            (self.alumno_id, MEDAL_KEY)
        )
        if self.cursor.fetchone():
            return # Already has it

        # 2. Check if the condition is met
        self.cursor.execute(
            "SELECT COUNT(*) FROM gamificacion_puntos_log WHERE alumno_id = ? AND accion_key = 'ASISTENCIA_CLASE'",
            (self.alumno_id,)
        )
        attendance_count = self.cursor.fetchone()[0]

        if attendance_count >= 5:
            # 3. Grant the medal
            self.cursor.execute(
                "INSERT INTO gamificacion_medallas_obtenidas (inquilino_id, alumno_id, medalla_key, fecha_obtencion) VALUES (?, ?, ?, ?)",
                (self.tenant_id, self.alumno_id, MEDAL_KEY, datetime.now().isoformat())
            )
            print(f"MEDAL GRANTED: User {self.alumno_id} earned medal {MEDAL_KEY}")

            # 4. Send notification
            create_notification(
                tenant_id=self.tenant_id,
                user_id=self.alumno_user_id,
                message="¡Felicidades! Has ganado la medalla 'Primeros 5 Pasos' por tu constancia.",
                pubsub_instance=self.pubsub_instance
            )


    def _check_for_level_up(self):
        """Placeholder for level-up logic."""
        # Example: Get current points and level, check against gamificacion_niveles table
        pass

    def __del__(self):
        """Ensure the connection is closed when the object is destroyed."""
        if self.conn:
            self.conn.close()

# Main function to be called from the app
def process_gamified_action(tenant_id: int, user_id: int, action_key: str, pubsub_instance):
    engine = GamificationEngine(tenant_id, user_id, pubsub_instance)
    engine.log_action(action_key)

def grant_manual_badge(tenant_id: int, actor_user_id: int, target_alumno_user_id: int, medalla_key: str, pubsub_instance):
    """Grants a medal manually and sends a notification."""
    engine = GamificationEngine(tenant_id, target_alumno_user_id, pubsub_instance)
    if not engine.alumno_id:
        return {"status": "error", "message": "Alumno no encontrado."}

    # 1. Check if user already has this medal
    engine.cursor.execute(
        "SELECT id FROM gamificacion_medallas_obtenidas WHERE alumno_id = ? AND medalla_key = ?",
        (engine.alumno_id, medalla_key)
    )
    if engine.cursor.fetchone():
        return {"status": "info", "message": "El alumno ya tiene esta medalla."}

    # 2. Grant the medal
    engine.cursor.execute(
        "INSERT INTO gamificacion_medallas_obtenidas (inquilino_id, alumno_id, medalla_key, fecha_obtencion) VALUES (?, ?, ?, ?)",
        (tenant_id, engine.alumno_id, medalla_key, datetime.now().isoformat())
    )

    # 3. Get medal name for notification
    engine.cursor.execute("SELECT nombre FROM gamificacion_medallas WHERE medalla_key = ?", (medalla_key,))
    medal_name = engine.cursor.fetchone()[0]

    # 4. Send notification
    create_notification(
        tenant_id=tenant_id,
        user_id=target_alumno_user_id,
        message=f"¡Felicidades! Tu instructor te ha otorgado la medalla '{medal_name}'.",
        pubsub_instance=pubsub_instance
    )

    engine.conn.commit()
    return {"status": "success", "message": f"Medalla '{medal_name}' otorgada con éxito."}
